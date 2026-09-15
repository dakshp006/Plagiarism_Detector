"""
Centralized Parameterized MySQL Database Queries & Transaction Management.

All SQL execution uses parameterized inputs (%s placeholders) to guarantee
protection against SQL Injection attacks and ensure ACID compliance.
"""

from mysql.connector import Error
from .connection import get_db_connection


# ============================================================================
# USER MANAGEMENT QUERIES
# ============================================================================

def add_user(name: str, email: str) -> int:
    """
    Registers a new user in the database.
    
    Returns:
        int: The newly created user_id.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "INSERT INTO users (name, email) VALUES (%s, %s);"
        cursor.execute(query, (name.strip(), email.strip().lower()))
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def get_all_users() -> list:
    """
    Fetches all registered users.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT user_id, name, email, created_at FROM users ORDER BY user_id ASC;"
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def search_users(keyword: str) -> list:
    """
    Searches users by name or email keyword.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        search_pattern = f"%{keyword.strip()}%"
        query = "SELECT user_id, name, email, created_at FROM users WHERE name LIKE %s OR email LIKE %s;"
        cursor.execute(query, (search_pattern, search_pattern))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# DOCUMENT MANAGEMENT QUERIES
# ============================================================================

def add_document(user_id: int, file_name: str, content: str, word_count: int) -> int:
    """
    Stores an uploaded document and its raw content in MySQL.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO documents (user_id, file_name, content, word_count) 
            VALUES (%s, %s, %s, %s);
        """
        cursor.execute(query, (user_id, file_name, content, word_count))
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def get_all_documents() -> list:
    """
    Retrieves all uploaded documents with associated owner names.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT d.document_id, d.file_name, d.word_count, d.uploaded_at, u.name AS owner_name, u.email
            FROM documents d
            JOIN users u ON d.user_id = u.user_id
            ORDER BY d.document_id ASC;
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_document_by_id(document_id: int) -> dict:
    """
    Fetches document content and metadata by document_id.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT document_id, user_id, file_name, content, word_count, uploaded_at FROM documents WHERE document_id = %s;"
        cursor.execute(query, (document_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def search_documents(keyword: str) -> list:
    """
    Searches documents by file_name or content keyword.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        search_pattern = f"%{keyword.strip()}%"
        query = """
            SELECT d.document_id, d.file_name, d.word_count, d.uploaded_at, u.name AS owner_name
            FROM documents d
            JOIN users u ON d.user_id = u.user_id
            WHERE d.file_name LIKE %s OR d.content LIKE %s;
        """
        cursor.execute(query, (search_pattern, search_pattern))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# COMPARISON & REPORT TRANSACTION QUERIES
# ============================================================================

def save_comparison_record(
    doc1_id: int, 
    doc2_id: int, 
    similarity_score: float, 
    status: str, 
    matching_results: list,
    total_matches: int,
    longest_match: int
) -> int:
    """
    Executes an ACID atomic transaction to save:
    1. Entry in `comparisons` table
    2. Multiple entries in `matching_results` table
    3. Summary entry in `reports` table
    
    Returns:
        int: Created comparison_id.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Step 1: Insert into comparisons table
        query_comp = """
            INSERT INTO comparisons (document1_id, document2_id, similarity_score, status)
            VALUES (%s, %s, %s, %s);
        """
        cursor.execute(query_comp, (doc1_id, doc2_id, similarity_score, status))
        comparison_id = cursor.lastrowid
        
        # Step 2: Insert into matching_results table
        query_match = """
            INSERT INTO matching_results (comparison_id, phrase, position_doc1, position_doc2, match_length)
            VALUES (%s, %s, %s, %s, %s);
        """
        for m in matching_results:
            cursor.execute(query_match, (
                comparison_id,
                m["phrase"],
                m["position_doc1"],
                m["position_doc2"],
                m["match_length"]
            ))
            
        # Step 3: Insert into reports table
        query_report = """
            INSERT INTO reports (comparison_id, total_matches, longest_match)
            VALUES (%s, %s, %s);
        """
        cursor.execute(query_report, (comparison_id, total_matches, longest_match))
        
        # Commit transaction
        conn.commit()
        return comparison_id
    except Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def get_comparison_history() -> list:
    """
    Retrieves full history of past document comparisons using JOINs.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT 
                c.comparison_id,
                c.document1_id,
                d1.file_name AS doc1_name,
                u1.name AS u1_name,
                c.document2_id,
                d2.file_name AS doc2_name,
                u2.name AS u2_name,
                c.similarity_score,
                c.status,
                c.compared_at
            FROM comparisons c
            JOIN documents d1 ON c.document1_id = d1.document_id
            JOIN users u1 ON d1.user_id = u1.user_id
            JOIN documents d2 ON c.document2_id = d2.document_id
            JOIN users u2 ON d2.user_id = u2.user_id
            ORDER BY c.comparison_id DESC;
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_comparison_report_data(comparison_id: int) -> dict:
    """
    Fetches full detailed report data for a specific comparison_id.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query_comp = """
            SELECT 
                c.comparison_id,
                d1.file_name AS doc1_name,
                u1.name AS owner1_name,
                d2.file_name AS doc2_name,
                u2.name AS owner2_name,
                c.similarity_score,
                c.status,
                c.compared_at,
                r.total_matches,
                r.longest_match
            FROM comparisons c
            JOIN documents d1 ON c.document1_id = d1.document_id
            JOIN users u1 ON d1.user_id = u1.user_id
            JOIN documents d2 ON c.document2_id = d2.document_id
            JOIN users u2 ON d2.user_id = u2.user_id
            JOIN reports r ON c.comparison_id = r.comparison_id
            WHERE c.comparison_id = %s;
        """
        cursor.execute(query_comp, (comparison_id,))
        comp_info = cursor.fetchone()
        
        if not comp_info:
            return None
        
        query_matches = """
            SELECT phrase, position_doc1, position_doc2, match_length
            FROM matching_results
            WHERE comparison_id = %s
            ORDER BY match_id ASC;
        """
        cursor.execute(query_matches, (comparison_id,))
        matches = cursor.fetchall()
        
        comp_info["matching_sections"] = matches
        return comp_info
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# ADVANCED VIVA & ANALYTICS QUERIES
# ============================================================================

def get_high_similarity_users() -> list:
    """
    Demonstrates GROUP BY + HAVING query.
    Finds users whose documents have 1 or more HIGH similarity results.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT 
                u.user_id,
                u.name,
                u.email,
                COUNT(c.comparison_id) AS high_risk_count
            FROM users u
            JOIN documents d ON u.user_id = d.user_id
            JOIN comparisons c ON (d.document_id = c.document1_id OR d.document_id = c.document2_id)
            WHERE c.status = 'HIGH'
            GROUP BY u.user_id, u.name, u.email
            HAVING COUNT(c.comparison_id) >= 1;
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_above_average_comparisons() -> list:
    """
    Demonstrates SQL SUBQUERY.
    Finds comparisons with similarity scores greater than the global average.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT 
                c.comparison_id,
                d1.file_name AS doc1_name,
                d2.file_name AS doc2_name,
                c.similarity_score,
                c.status
            FROM comparisons c
            JOIN documents d1 ON c.document1_id = d1.document_id
            JOIN documents d2 ON c.document2_id = d2.document_id
            WHERE c.similarity_score > (
                SELECT COALESCE(AVG(similarity_score), 0) FROM comparisons
            )
            ORDER BY c.similarity_score DESC;
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_analytics_summary() -> dict:
    """
    Executes SQL Aggregate Functions (COUNT, AVG, MAX, MIN).
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) AS total_users FROM users;")
        tot_users = cursor.fetchone()["total_users"]
        
        cursor.execute("SELECT COUNT(*) AS total_docs FROM documents;")
        tot_docs = cursor.fetchone()["total_docs"]
        
        query_stats = """
            SELECT 
                COUNT(*) AS total_comparisons,
                COALESCE(AVG(similarity_score), 0.0) AS avg_similarity,
                COALESCE(MAX(similarity_score), 0.0) AS max_similarity,
                COALESCE(MIN(similarity_score), 0.0) AS min_similarity,
                SUM(CASE WHEN status = 'HIGH' THEN 1 ELSE 0 END) AS high_count,
                SUM(CASE WHEN status = 'MEDIUM' THEN 1 ELSE 0 END) AS medium_count,
                SUM(CASE WHEN status = 'LOW' THEN 1 ELSE 0 END) AS low_count
            FROM comparisons;
        """
        cursor.execute(query_stats)
        comp_stats = cursor.fetchone()
        
        return {
            "total_users": tot_users,
            "total_documents": tot_docs,
            "total_comparisons": comp_stats["total_comparisons"],
            "avg_similarity": round(float(comp_stats["avg_similarity"]), 2),
            "max_similarity": round(float(comp_stats["max_similarity"]), 2),
            "min_similarity": round(float(comp_stats["min_similarity"]), 2),
            "high_count": int(comp_stats["high_count"] or 0),
            "medium_count": int(comp_stats["medium_count"] or 0),
            "low_count": int(comp_stats["low_count"] or 0)
        }
    finally:
        cursor.close()
        conn.close()
