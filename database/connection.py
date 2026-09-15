import os
import sqlite3
import mysql.connector
from mysql.connector import Error

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DB_TYPE = None # 'mysql' or 'sqlite'
SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plagiarism_detector.db")


class SQLiteCursorAdapter:
    def __init__(self, sqlite_cursor, dictionary=False):
        self.cursor = sqlite_cursor
        self.dictionary = dictionary
        self.lastrowid = None

    def execute(self, query, params=None):
        # Convert MySQL %s placeholders to SQLite ? placeholders
        query_sql = query.replace("%s", "?")
        if params is None:
            self.cursor.execute(query_sql)
        else:
            self.cursor.execute(query_sql, params)
        self.lastrowid = self.cursor.lastrowid

    def fetchone(self):
        row = self.cursor.fetchone()
        if row is None:
            return None
        if self.dictionary and hasattr(row, 'keys'):
            return dict(row)
        return row

    def fetchall(self):
        rows = self.cursor.fetchall()
        if not rows:
            return []
        if self.dictionary and len(rows) > 0 and hasattr(rows[0], 'keys'):
            return [dict(r) for r in rows]
        return rows

    def close(self):
        self.cursor.close()


class SQLiteConnectionAdapter:
    def __init__(self, sqlite_conn):
        self.conn = sqlite_conn

    def cursor(self, dictionary=False):
        return SQLiteCursorAdapter(self.conn.cursor(), dictionary=dictionary)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def is_connected(self):
        return True

    def close(self):
        self.conn.close()


def _init_sqlite_db():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS documents (
            document_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            content TEXT NOT NULL,
            word_count INTEGER NOT NULL DEFAULT 0,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS comparisons (
            comparison_id INTEGER PRIMARY KEY AUTOINCREMENT,
            document1_id INTEGER NOT NULL,
            document2_id INTEGER NOT NULL,
            similarity_score REAL NOT NULL,
            status TEXT NOT NULL,
            compared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document1_id) REFERENCES documents(document_id) ON DELETE CASCADE,
            FOREIGN KEY (document2_id) REFERENCES documents(document_id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS matching_results (
            match_id INTEGER PRIMARY KEY AUTOINCREMENT,
            comparison_id INTEGER NOT NULL,
            phrase TEXT NOT NULL,
            position_doc1 INTEGER NOT NULL,
            position_doc2 INTEGER NOT NULL,
            match_length INTEGER NOT NULL,
            FOREIGN KEY (comparison_id) REFERENCES comparisons(comparison_id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS reports (
            report_id INTEGER PRIMARY KEY AUTOINCREMENT,
            comparison_id INTEGER NOT NULL UNIQUE,
            total_matches INTEGER NOT NULL DEFAULT 0,
            longest_match INTEGER NOT NULL DEFAULT 0,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (comparison_id) REFERENCES comparisons(comparison_id) ON DELETE CASCADE
        );
    """)
    
    # Check if seed data exists
    cursor.execute("SELECT COUNT(*) FROM users;")
    if cursor.fetchone()[0] == 0:
        cursor.executescript("""
            INSERT INTO users (name, email) VALUES
            ('Alice Smith', 'alice@college.edu'),
            ('Bob Johnson', 'bob@college.edu'),
            ('Charlie Brown', 'charlie@college.edu');
            
            INSERT INTO documents (user_id, file_name, content, word_count) VALUES
            (1, 'assignment_01.txt', 'Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data.', 16),
            (2, 'assignment_02.txt', 'Machine learning is a subset of artificial intelligence. It uses statistics to learn patterns from training data.', 17),
            (3, 'essay_python.txt', 'Python is a high level programming language known for readability and clear syntax.', 12);
            
            INSERT INTO comparisons (document1_id, document2_id, similarity_score, status) VALUES
            (1, 2, 64.71, 'HIGH');
            
            INSERT INTO matching_results (comparison_id, phrase, position_doc1, position_doc2, match_length) VALUES
            (1, 'machine learning is a subset of artificial intelligence', 0, 0, 8);
            
            INSERT INTO reports (comparison_id, total_matches, longest_match) VALUES
            (1, 1, 8);
        """)
        conn.commit()
    cursor.close()
    conn.close()


_MYSQL_AVAILABLE = None  # None = untried, True = connected, False = offline


def get_db_config(include_db=True):
    config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", 3306)),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "connection_timeout": 1,
        "autocommit": False
    }
    if include_db:
        config["database"] = os.getenv("DB_NAME", "plagiarism_detector")
    return config


def get_db_connection(force_check_mysql=False):
    global DB_TYPE, _MYSQL_AVAILABLE
    if force_check_mysql:
        _MYSQL_AVAILABLE = None

    if _MYSQL_AVAILABLE is not False:
        config = get_db_config(include_db=True)
        try:
            connection = mysql.connector.connect(**config)
            DB_TYPE = "mysql"
            _MYSQL_AVAILABLE = True
            return connection
        except Exception:
            _MYSQL_AVAILABLE = False

    # Fall back to SQLite
    DB_TYPE = "sqlite"
    _init_sqlite_db()
    sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    return SQLiteConnectionAdapter(sqlite_conn)


def test_connection():
    try:
        conn = get_db_connection(force_check_mysql=True)
        if conn and conn.is_connected():
            print(f"[SUCCESS] Connected to Database using engine: '{DB_TYPE.upper()}'")
            conn.close()
            return True
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing Database Connection (MySQL / SQLite Fallback)...")
    test_connection()

