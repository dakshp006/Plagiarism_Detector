# Plagiarism & Duplicate Text Detector

A college-grade, modular **Plagiarism and Duplicate Text Detection System** built using **Python 3**, **Flask REST API**, **Data Structures & Algorithms (Rabin-Karp Rolling Hash & KMP Pattern Matching)**, and a **Dual Database Architecture (MySQL + Zero-Config SQLite Fallback)**.

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Key Features](#2-key-features)
3. [Technology Stack & Architecture](#3-technology-stack--architecture)
4. [Data Structures & Algorithms (DSA)](#4-data-structures--algorithms-dsa)
5. [Database Architecture & Schema](#5-database-architecture--schema)
6. [Project Directory Layout](#6-project-directory-layout)
7. [How to Run Locally](#7-how-to-run-locally)
8. [Automated One-Click Startup Scripts](#8-automated-one-click-startup-scripts)
9. [Running Tests](#9-running-tests)
10. [CLI Application vs Web Interface](#10-cli-application-vs-web-interface)
11. [Troubleshooting Guide](#11-troubleshooting-guide)
12. [Time & Space Complexity Analysis](#12-time--space-complexity-analysis)
13. [Limitations & Future Enhancements](#13-limitations--future-enhancements)
14. [Viva Voce Questions & Answers (25 Q&A)](#14-viva-voce-questions--answers-25-qa)

---

## 1. Project Overview

Educational institutions require a transparent, algorithm-driven tool to verify the uniqueness of submitted assignments and detect duplicate word sequences across student submissions.

This project implements a **Rabin-Karp Rolling Hash Engine** with **KMP (Knuth-Morris-Pratt)** phrase verification. It tokenizes raw document text, computes windowed polynomial rolling hashes, detects overlapping sequence matches, calculates a similarity percentage, classifies risk levels into **LOW**, **MEDIUM**, or **HIGH**, and persists all records, user info, and detailed reports into a database.

---

## 2. Key Features

- **Web Dashboard & REST API**: Modern web interface running locally on `http://127.0.0.1:5000` with real-time text/document comparison, phrase highlighting, and algorithm breakdown visualizations.
- **Interactive CLI Menu**: Terminal-based console application for command-line management.
- **User Management**: Register users, view registered users, search users by email/name.
- **Document Management**: Upload `.txt` files, extract raw text, compute word count, store timestamps, search stored documents.
- **Pairwise Comparison (Doc A vs Doc B)**: Compare any 2 documents using Rabin-Karp word-window rolling hashes & KMP phrase verification.
- **One-to-Many Comparison (Doc A vs All)**: Compare one target document against all uploaded database documents and rank by similarity score.
- **Live Text Comparison**: Instant side-by-side comparison of arbitrary raw text inputs without prior database upload.
- **Matched Sequence Extraction**: Displays exact matching word phrases, word positions in Doc 1 and Doc 2, word sequence length, and longest matched section.
- **Plagiarism Report File Generation**: Exports formatted `.txt` reports containing detailed match metrics and phrase positions.
- **Dual Database Engine**: Automatic fallback to built-in SQLite (`plagiarism_detector.db`) when MySQL is not present, ensuring zero-configuration local setup.

---

## 3. Technology Stack & Architecture

- **Backend**: Python 3.10+, Flask REST API server (`server.py`), `flask-cors`
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla ES6) served directly by Flask at `http://127.0.0.1:5000`
- **Database Options**:
  - **SQLite**: Built-in zero-config database (`plagiarism_detector.db`)
  - **MySQL**: Relational database Server 8.0+ via `mysql-connector-python`
- **Configuration**: `python-dotenv` for `.env` credentials

---

## 4. Data Structures & Algorithms (DSA)

| DSA Concept | Implementation File | Usage & Purpose |
| :--- | :--- | :--- |
| **Arrays / Lists** | [`utils/text_cleaner.py`](file:///c:/Users/Daksh%20Prajapati/Desktop/anpd_project/utils/text_cleaner.py) | Stores tokenized words allowing $O(1)$ index access for window creation. |
| **Hash Tables / Dictionaries** | [`algorithms/rabin_karp.py`](file:///c:/Users/Daksh%20Prajapati/Desktop/anpd_project/algorithms/rabin_karp.py) | Maps computed window hashes to list of phrases for $O(1)$ average time lookup. |
| **Sets** | [`algorithms/similarity.py`](file:///c:/Users/Daksh%20Prajapati/Desktop/anpd_project/algorithms/similarity.py) | Tracks unique matched word indices in Document 1 to eliminate double-counting overlapping windows. |
| **Rabin-Karp (Rolling Hash)** | [`algorithms/rabin_karp.py`](file:///c:/Users/Daksh%20Prajapati/Desktop/anpd_project/algorithms/rabin_karp.py) | Calculates initial polynomial hash in $O(k)$ time and updates sliding window in $O(1)$ constant time. |
| **KMP Algorithm (LPS Array)** | [`algorithms/kmp.py`](file:///c:/Users/Daksh%20Prajapati/Desktop/anpd_project/algorithms/kmp.py) | Uses Longest Prefix Suffix (LPS) array for $O(N + M)$ phrase verification without character backtracking. |

---

## 5. Database Architecture & Schema

Database Name: `plagiarism_detector` (MySQL) or `plagiarism_detector.db` (SQLite fallback)

1. **`users`**: `user_id` (PK, AUTO_INCREMENT), `name`, `email` (UNIQUE), `created_at`
2. **`documents`**: `document_id` (PK, AUTO_INCREMENT), `user_id` (FK -> users.user_id ON DELETE CASCADE), `file_name`, `content` (LONGTEXT), `word_count`, `uploaded_at`
3. **`comparisons`**: `comparison_id` (PK, AUTO_INCREMENT), `document1_id` (FK), `document2_id` (FK), `similarity_score` (DECIMAL(5,2)), `status` (VARCHAR(20)), `compared_at`
4. **`matching_results`**: `match_id` (PK, AUTO_INCREMENT), `comparison_id` (FK -> comparisons.comparison_id ON DELETE CASCADE), `phrase`, `position_doc1`, `position_doc2`, `match_length`
5. **`reports`**: `report_id` (PK, AUTO_INCREMENT), `comparison_id` (FK, UNIQUE), `total_matches`, `longest_match`, `generated_at`

---

## 6. Project Directory Layout

```
anpd_project/
├── main.py                     # CLI Interactive Menu Entry Point
├── server.py                   # Flask REST API Server & Web Server
├── run_web.py                  # Web Application Launcher
├── run_qa_tests.py             # End-to-End QA Test Suite
├── test_suite.py               # Standalone Algorithmic Test Suite
├── requirements.txt            # Python Dependencies
├── .env.example                # Database Environment Variables Template
├── README.md                   # Project Documentation
├── run.bat                     # Windows CMD One-Click Launcher
├── run.ps1                     # Windows PowerShell One-Click Launcher
├── start.sh                    # Linux/macOS One-Click Launcher
│
├── static/                     # Web Frontend UI Files
│   ├── index.html              # Single Page Dashboard
│   ├── css/styles.css          # Custom Styling
│   └── js/app.js               # Frontend JavaScript API Integrations
│
├── sql/
│   └── database.sql            # MySQL Schema DDL & Sample Seed Data
│
├── database/
│   ├── __init__.py
│   ├── connection.py           # Database Connection & Dual Engine Adapter
│   └── queries.py              # Parameterized SQL Queries & Analytics
│
├── algorithms/
│   ├── __init__.py
│   ├── rabin_karp.py           # Rabin-Karp Rolling Hash Engine
│   ├── kmp.py                  # KMP Pattern Matcher & LPS Array
│   └── similarity.py           # Similarity % & Risk Classification
│
├── services/
│   ├── __init__.py
│   ├── document_service.py     # User Registration & Document Upload
│   └── comparison_service.py   # Comparison Engine & Report Exporter
│
├── utils/
│   ├── __init__.py
│   └── text_cleaner.py         # Text Preprocessing & Tokenization
│
├── documents/                  # Sample Text Documents
└── reports/                    # Output Generated Text Reports
```

---

## 7. How to Run Locally

Follow these step-by-step commands to get the application running on your computer.

### Quick Workflow Overview
1. Clone / download project repository
2. Open terminal in the project folder
3. Create Python virtual environment (`venv`)
4. Activate virtual environment
5. Install dependencies (`pip install -r requirements.txt`)
6. Configure `.env` (optional for MySQL; SQLite works out of the box)
7. Set up Database (SQLite auto-initializes; MySQL optional via `sql/database.sql`)
8. Run tests (`python test_suite.py` / `python run_qa_tests.py`)
9. Start Web Application (`python run_web.py`)
10. Open `http://127.0.0.1:5000` in your web browser

---

### Step 1: Open Terminal in Project Folder
Navigate to the root directory of `anpd_project`:
```bash
cd "c:\Users\Daksh Prajapati\Desktop\anpd_project"
```

---

### Step 2: Create Virtual Environment

**Windows PowerShell:**
```powershell
python -m venv venv
```

**Windows CMD:**
```cmd
python -m venv venv
```

**Linux / macOS:**
```bash
python3 -m venv venv
```

---

### Step 3: Activate Virtual Environment

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```
*(If PowerShell blocks script execution, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

**Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

---

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 5: Database Setup

#### Option A: Zero-Config SQLite (Default — Recommended for Quick Start)
No installation or database creation required! The system automatically creates and initializes [`plagiarism_detector.db`](file:///c:/Users/Daksh%20Prajapati/Desktop/anpd_project/plagiarism_detector.db) in the project directory when launched.

#### Option B: MySQL Database (Optional)
If you prefer running against a local MySQL Server:

1. Copy `.env.example` to `.env`:
   - **Windows:** `copy .env.example .env`
   - **Linux/macOS:** `cp .env.example .env`

2. Edit `.env` with your local MySQL password:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_actual_mysql_password
   DB_NAME=plagiarism_detector
   ```

3. Import the database schema into MySQL:
   - **Windows PowerShell:** `Get-Content sql\database.sql | mysql -u root -p`
   - **Windows CMD:** `mysql -u root -p < sql\database.sql`
   - **Linux / macOS:** `mysql -u root -p < sql/database.sql`

---

### Step 6: Start the Web Application

To start the local web backend & frontend server:
```bash
python run_web.py
```
*Or directly via server:*
```bash
python server.py
```

The Flask server will start on:
👉 **Local Web Interface**: **`http://127.0.0.1:5000`**

Open `http://127.0.0.1:5000` in any web browser (Chrome, Edge, Firefox, Safari) to use the system!

---

## 8. Automated One-Click Startup Scripts

For convenience, ready-to-run startup scripts are provided in the repository root:

- **Windows CMD**: Double-click or run [`run.bat`](file:///c:/Users/Daksh%20Prajapati/Desktop/anpd_project/run.bat)
- **Windows PowerShell**: Run [`.\run.ps1`](file:///c:/Users/Daksh%20Prajapati/Desktop/anpd_project/run.ps1)
- **Linux / macOS**: Run [`./start.sh`](file:///c:/Users/Daksh%20Prajapati/Desktop/anpd_project/start.sh) *(chmod +x start.sh if needed)*

These scripts automatically create the virtual environment, install missing dependencies, and launch the web server on `http://127.0.0.1:5000`.

---

## 9. Running Tests

The project includes two independent testing tools that run without requiring MySQL:

### A. Standalone Algorithm Test Suite
Validates text cleaner tokenization, Rabin-Karp rolling hashes, KMP pattern search, and similarity calculation:
```bash
python test_suite.py
```

### B. End-to-End QA Test Suite
Executes 18 comprehensive tests across Algorithms, Database Queries, Service Layer, API endpoints, SQL injection resilience, and edge cases:
```bash
python run_qa_tests.py
```

---

## 10. CLI Application vs Web Interface

The project includes **two full user interfaces**:

1. **Web Interface (Recommended)**:
   - Launched via `python run_web.py`
   - Available at `http://127.0.0.1:5000`
   - Supports drag-and-drop document upload, live side-by-side text comparison with highlight overlays, interactive algorithm breakdown diagrams, and downloadable text reports.

2. **Interactive CLI Application**:
   - Launched via `python main.py`
   - Terminal menu supporting user registration, document upload, pairwise comparison, 1-to-N comparisons, report export, and raw SQL analytics queries.

---

## 11. Troubleshooting Guide

### Issue 1: `python: command not found` or `python is not recognized`
- **Cause**: Python 3 is either not installed or not added to your system PATH.
- **Fix**: Reinstall Python 3 from [python.org](https://www.python.org/) and check the box **"Add Python to PATH"** during setup. On Linux/macOS, try using `python3` instead of `python`.

### Issue 2: `pip: command not found`
- **Fix**: Ensure virtual environment is activated (`source venv/bin/activate` or `venv\Scripts\activate.bat`), or run `python -m pip install -r requirements.txt`.

### Issue 3: `ModuleNotFoundError: No module named 'flask'` or `mysql.connector`
- **Cause**: Dependencies were not installed in the active environment.
- **Fix**: Ensure your virtual environment is active, then execute:
  ```bash
  pip install -r requirements.txt
  ```

### Issue 4: MySQL Connection Error (`Can't connect to MySQL server`)
- **Cause**: MySQL service is stopped, password in `.env` is incorrect, or database was not created.
- **Fix**:
  1. Ensure MySQL Server service is running.
  2. Verify credentials in `.env`.
  3. **Zero-Config Fallback**: If MySQL is unavailable, delete or rename `.env` (or leave `DB_PASSWORD` blank) — the application will automatically fall back to SQLite (`plagiarism_detector.db`) without failing.

### Issue 5: Port 5000 Already in Use
- **Cause**: Another process or AirPlay / web server is using port 5000.
- **Fix**: Specify a custom port in `.env` (e.g. `PORT=5001`), or pass environment variable:
  ```bash
  PORT=5001 python server.py
  ```

### Issue 6: `Execution of scripts is disabled on this system` (PowerShell)
- **Fix**: Run PowerShell as Administrator or execute in current shell:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```

---

## 12. Time & Space Complexity Analysis

| Component / Algorithm | Best / Average Time | Worst Case Time | Space Complexity | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Text Preprocessing** | $O(N)$ | $O(N)$ | $O(N)$ | $N$ is character length. Lowercases, strips punctuation, tokenizes words. |
| **Rabin-Karp Hash** | $O(W \cdot k)$ | $O(W \cdot k)$ | $O(W)$ | $W$ is window count, $k$ is window word size (5). Polynomial rolling hash. |
| **Rabin-Karp Match** | $O(W_1 + W_2)$ | $O(W_1 \cdot W_2)$ | $O(W_1 + W_2)$ | Hash table map lookup gives $O(1)$ average window comparison time. |
| **KMP Pattern Search** | $O(N + M)$ | $O(N + M)$ | $O(M)$ | $M$ is pattern length, $N$ is text length. Precomputes LPS array for matching without text backtracking. |
| **Similarity Score** | $O(M \cdot k)$ | $O(M \cdot k)$ | $O(U)$ | $M$ is match count, $U$ is unique matched word set size. |

---

## 13. Limitations & Future Enhancements

### Limitations
1. **Paraphrasing**: Pure word-sequence matching does not detect heavy semantic sentence restructuring or synonym substitution.
2. **File Types**: Built-in support for plain text `.txt` files (or raw text copy-paste via Web UI).

### Future Enhancements
- **PDF & DOCX Support**: Integrate `PyPDF2` or `python-docx` for automated text extraction.
- **NLP & TF-IDF / Cosine Similarity**: Incorporate TF-IDF vectorization and Cosine Similarity for semantic matching.
- **Transformer Embeddings**: Integrate BERT sentence embeddings for paraphrased plagiarism detection.

---

## 14. Viva Voce Questions & Answers (25 Q&A)

#### Q1: Why did you choose Rabin-Karp as the primary algorithm for this project?
**Answer**: Rabin-Karp is ideal for document comparison because it utilizes a **Rolling Hash**. By sliding a fixed word window across a document, Rabin-Karp updates the hash value for the next window in $O(1)$ constant time instead of recomputing the hash from scratch. Storing Document 1's window hashes in a Hash Table (Python dictionary) enables $O(1)$ average lookup time per window.

#### Q2: Why not simply compare strings character-by-character?
**Answer**: Character-by-character naive string comparison takes $O(N \times M)$ time, which is computationally expensive for large text documents. Rabin-Karp reduces integer hash comparisons to $O(1)$ average time, performing character verification only when a hash match occurs.

#### Q3: What is a Rolling Hash and how does it work?
**Answer**: A rolling hash is a hash function where the input is hashed in a window that moves (slides) through the input. Instead of calculating the hash of the new window from scratch ($O(k)$ time), the rolling hash formula subtracts the contribution of the outgoing word from the high-order position and adds the incoming word at the low-order position in $O(1)$ constant time.

#### Q4: What is a hash collision and how does your code handle it?
**Answer**: A hash collision occurs when two different text phrases produce the exact same integer hash value ($H(A) = H(B)$ where $A \neq B$). Our system handles collisions via **Explicit Verification (Spurious Hit Check)**: whenever two hashes match, the code explicitly compares the raw word strings (`phrase1 == phrase2`). If they are identical, it is a true match; if not, it is ignored as a collision.

#### Q5: What is the Knuth-Morris-Pratt (KMP) algorithm and why is it useful?
**Answer**: KMP is a linear-time string matching algorithm ($O(N + M)$) that uses a precomputed **Longest Prefix Suffix (LPS)** array. When a character mismatch occurs, KMP uses the LPS array to determine how many characters to shift the pattern without ever backtracking the text pointer index $i$.

#### Q6: What is the LPS Array in KMP?
**Answer**: The LPS array (`lps[i]`) stores the length of the longest proper prefix of `pattern[0..i]` that is also a suffix of `pattern[0..i]`. It tells KMP the exact index position in the pattern to resume matching after a mismatch.

#### Q7: What is the difference between Rabin-Karp and KMP?
**Answer**: Rabin-Karp uses rolling hashes and works best for multi-pattern or sequence-window matching across documents. KMP uses prefix-suffix structure and works best for verifying single exact pattern/phrase occurrences within a body of text without backtracking.

#### Q8: What Data Structures are used in this project?
**Answer**:
1. **Lists/Arrays**: To store tokenized words and LPS arrays.
2. **Hash Tables (Python `dict`)**: To store window hashes for $O(1)$ lookup.
3. **Sets**: To track unique matched word positions and eliminate duplicate counting.

#### Q9: How does the database engine handle SQLite vs MySQL?
**Answer**: The system features a dual database adapter ([`database/connection.py`](file:///c:/Users/Daksh%20Prajapati/Desktop/anpd_project/database/connection.py)). If MySQL connection fails or credentials are absent, it automatically connects to a local SQLite database file ([`plagiarism_detector.db`](file:///c:/Users/Daksh%20Prajapati/Desktop/anpd_project/plagiarism_detector.db)), adapting SQL syntax (%s to ?) seamlessly.

#### Q10: Why use Foreign Keys with `ON DELETE CASCADE`?
**Answer**: Foreign Keys enforce referential integrity. `ON DELETE CASCADE` ensures that if a user or document is deleted, all related document records, comparisons, matching results, and reports are automatically cleaned up to prevent orphaned records.

#### Q11: What is Database Normalization and how is it applied here?
**Answer**: Database normalization organizes tables to reduce redundancy. Here, user info is stored in `users`, documents in `documents`, comparison metadata in `comparisons`, phrase matches in `matching_results`, and report statistics in `reports`, adhering to 3rd Normal Form (3NF).

#### Q12: Where did you use SQL JOIN queries in the project?
**Answer**: In [`database/queries.py`](file:///c:/Users/Daksh%20Prajapati/Desktop/anpd_project/database/queries.py), `JOIN` queries combine data across `comparisons`, `documents`, `users`, and `reports` to display student names, document filenames, and comparison metrics in a single query result.

#### Q13: Where did you use SQL `GROUP BY` and `HAVING`?
**Answer**: In function `get_high_similarity_users()`, we group comparisons by `user_id` (`GROUP BY u.user_id`) and filter for users involved in multiple `HIGH` risk comparisons using `HAVING COUNT(c.comparison_id) >= 1`.

#### Q14: Why is `HAVING` used instead of `WHERE` for aggregate filtering?
**Answer**: `WHERE` filters individual table rows *before* aggregation occurs. `HAVING` filters group summaries *after* the `GROUP BY` clause has aggregated the rows (e.g. filtering on `COUNT(*)`).

#### Q15: What is a Subquery and where is it used in your project?
**Answer**: A subquery is a nested SQL query inside a main query. In `get_above_average_comparisons()`, a subquery `(SELECT AVG(similarity_score) FROM comparisons)` computes the global average similarity score, and the outer query filters comparisons exceeding this average.

#### Q16: What is the Time Complexity of Rabin-Karp?
**Answer**:
- **Average/Best Case**: $O(N + M)$ where $N$ is text length and $M$ is pattern length.
- **Worst Case**: $O(N \times M)$ if every window produces a hash collision.

#### Q17: How is similarity percentage calculated in your project?
**Answer**:
$$\text{Similarity \%} = \frac{\text{Unique Matched Words Count}}{\min(\text{WordCount}(\text{Doc1}), \text{WordCount}(\text{Doc2}))} \times 100$$
Using the minimum document length prevents large documents from artificially diluting the similarity percentage of a smaller copied text.

#### Q18: Are the similarity thresholds (0-19% LOW, 20-49% MEDIUM, 50-100% HIGH) universal academic standards?
**Answer**: No. These thresholds are project-defined for demonstration purposes. Academic plagiarism standards vary by institution and academic field.

#### Q19: How do you prevent SQL Injection in Python?
**Answer**: By strictly using **Parameterized Queries** (`cursor.execute(query, (val1, val2))`). Parameters are sent separately from the SQL command structure, rendering injection attempts ineffective.

#### Q20: How do you handle empty or very small documents?
**Answer**: In [`utils/text_cleaner.py`](file:///c:/Users/Daksh%20Prajapati/Desktop/anpd_project/utils/text_cleaner.py) and [`algorithms/similarity.py`](file:///c:/Users/Daksh%20Prajapati/Desktop/anpd_project/algorithms/similarity.py), empty documents return 0 words, 0% similarity, and 'LOW' risk safely without throwing division-by-zero runtime exceptions. If a document has fewer words than window size (5 words), the entire document is treated as a single window.

#### Q21: What happens if both documents are identical?
**Answer**: All word windows match, the unique matched word set covers 100% of Document 1's words, and the similarity score returns `100.00%` with `HIGH` risk status.

#### Q22: What happens if the user attempts to compare a document with itself?
**Answer**: The service layer ([`services/comparison_service.py`](file:///c:/Users/Daksh%20Prajapati/Desktop/anpd_project/services/comparison_service.py)) checks `if doc1_id == doc2_id` and raises a clear `ValueError` preventing self-comparison.

#### Q23: What are the main limitations of this system?
**Answer**: It relies on exact word-sequence matching. It does not detect heavy paraphrased text, synonym substitutions, or translated plagiarism.

#### Q24: How would you scale this system for millions of documents?
**Answer**:
1. Implement inverted indexing (e.g. Elasticsearch or Redis Hash set).
2. Use MinHash and Locality-Sensitive Hashing (LSH) for sub-linear similarity candidate retrieval.
3. Add database indexing on `file_name` and foreign keys.
4. Distribute matching workloads using Celery/RabbitMQ async task queues.

#### Q25: How do you handle database credentials safely?
**Answer**: Database credentials are loaded dynamically from environment variables using `python-dotenv` (`.env` file) rather than hardcoding passwords inside source code repositories.
