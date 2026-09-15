-- ============================================================================
-- DATABASE SCRIPT: Plagiarism & Duplicate Text Detection System
-- Database Name: plagiarism_detector
-- Description: DDL schema creation and sample seed data insertion.
-- ============================================================================

-- 1. Create Database
CREATE DATABASE IF NOT EXISTS plagiarism_detector;
USE plagiarism_detector;

-- 2. Drop existing tables (in reverse order of dependencies) to ensure clean setup
DROP TABLE IF EXISTS reports;
DROP TABLE IF EXISTS matching_results;
DROP TABLE IF EXISTS comparisons;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS users;

-- ============================================================================
-- TABLE 1: users
-- Stores details of students/users who upload documents for checking.
-- ============================================================================
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- TABLE 2: documents
-- Stores uploaded documents, their raw text content, word count, and owner.
-- ============================================================================
CREATE TABLE documents (
    document_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    content LONGTEXT NOT NULL,
    word_count INT NOT NULL DEFAULT 0,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_documents_user FOREIGN KEY (user_id) 
        REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- TABLE 3: comparisons
-- Stores metadata and overall similarity results of document pair comparisons.
-- ============================================================================
CREATE TABLE comparisons (
    comparison_id INT AUTO_INCREMENT PRIMARY KEY,
    document1_id INT NOT NULL,
    document2_id INT NOT NULL,
    similarity_score DECIMAL(5, 2) NOT NULL, -- percentage e.g. 85.50
    status VARCHAR(20) NOT NULL,              -- 'LOW', 'MEDIUM', 'HIGH'
    compared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_comparisons_doc1 FOREIGN KEY (document1_id) 
        REFERENCES documents(document_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_comparisons_doc2 FOREIGN KEY (document2_id) 
        REFERENCES documents(document_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_similarity_score CHECK (similarity_score >= 0.00 AND similarity_score <= 100.00),
    CONSTRAINT chk_status CHECK (status IN ('LOW', 'MEDIUM', 'HIGH'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- TABLE 4: matching_results
-- Stores exact matching phrases/sequences found between Document 1 and Document 2.
-- ============================================================================
CREATE TABLE matching_results (
    match_id INT AUTO_INCREMENT PRIMARY KEY,
    comparison_id INT NOT NULL,
    phrase TEXT NOT NULL,
    position_doc1 INT NOT NULL,  -- word index starting position in doc 1
    position_doc2 INT NOT NULL,  -- word index starting position in doc 2
    match_length INT NOT NULL,   -- number of matching words in sequence
    CONSTRAINT fk_matching_results_comparison FOREIGN KEY (comparison_id) 
        REFERENCES comparisons(comparison_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- TABLE 5: reports
-- Stores generated report summaries associated with comparisons.
-- ============================================================================
CREATE TABLE reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    comparison_id INT NOT NULL UNIQUE,
    total_matches INT NOT NULL DEFAULT 0,
    longest_match INT NOT NULL DEFAULT 0,  -- longest matching phrase in words
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reports_comparison FOREIGN KEY (comparison_id) 
        REFERENCES comparisons(comparison_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- ============================================================================
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_documents_user ON documents(user_id);
CREATE INDEX idx_comparisons_doc1 ON comparisons(document1_id);
CREATE INDEX idx_comparisons_doc2 ON comparisons(document2_id);
CREATE INDEX idx_comparisons_status ON comparisons(status);

-- ============================================================================
-- SAMPLE SEED DATA FOR VERIFICATION & DEMO
-- ============================================================================

-- Insert sample users
INSERT INTO users (name, email) VALUES
('Alice Smith', 'alice@college.edu'),
('Bob Johnson', 'bob@college.edu'),
('Charlie Brown', 'charlie@college.edu');

-- Insert sample documents
INSERT INTO documents (user_id, file_name, content, word_count) VALUES
(1, 'assignment_01.txt', 'Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data.', 16),
(2, 'assignment_02.txt', 'Machine learning is a subset of artificial intelligence. It uses statistics to learn patterns from training data.', 17),
(3, 'essay_python.txt', 'Python is a high level programming language known for readability and clear syntax.', 12);

-- Insert sample comparison
INSERT INTO comparisons (document1_id, document2_id, similarity_score, status) VALUES
(1, 2, 64.71, 'HIGH');

-- Insert sample matching phrase
INSERT INTO matching_results (comparison_id, phrase, position_doc1, position_doc2, match_length) VALUES
(1, 'machine learning is a subset of artificial intelligence', 0, 0, 8);

-- Insert sample report
INSERT INTO reports (comparison_id, total_matches, longest_match) VALUES
(1, 1, 8);
