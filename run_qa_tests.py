"""
Comprehensive Quality Assurance (QA) Test Suite for Plagiarism & Duplicate Text Detection System.
Tests Algorithms, Database Queries, Service Layer, API Endpoints, and Edge Cases.
"""

import os
import sys
import unittest
import tempfile
import json

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.text_cleaner import clean_text, tokenize, create_word_windows
from algorithms.rabin_karp import rabin_karp_match, compute_rolling_hash, rabin_karp_pattern_search, BASE, PRIME
from algorithms.kmp import kmp_search, compute_lps_array, verify_phrase_with_kmp
from algorithms.similarity import calculate_similarity, classify_risk
from database.connection import get_db_connection, test_connection, DB_TYPE
from database import queries
from services import (
    register_new_user,
    list_users,
    upload_document,
    list_documents,
    compare_two_documents,
    compare_one_to_many,
    generate_report_file
)
from server import app


class TestAlgorithmsQA(unittest.TestCase):
    """QA Tests for Core Algorithms (Text Cleaning, Rabin-Karp, KMP, Similarity)."""

    def test_text_cleaner_lowercasing_and_punctuation(self):
        raw = "Hello, World! THIS is a QA Test #100... WITH punctuation & CAPITALIZATION."
        cleaned = clean_text(raw)
        self.assertNotIn("!", cleaned)
        self.assertNotIn(",", cleaned)
        self.assertNotIn("#", cleaned)
        self.assertEqual(cleaned, "hello world this is a qa test 100 with punctuation capitalization")

    def test_tokenize_empty_and_whitespace(self):
        self.assertEqual(tokenize(""), [])
        self.assertEqual(tokenize("   \n\t  "), [])

    def test_rabin_karp_exact_match(self):
        text_a = "the quick brown fox jumps over the lazy dog near the river"
        tokens_a = tokenize(text_a)
        tokens_b = tokenize(text_a)
        matches = rabin_karp_match(tokens_a, tokens_b, window_size=5)
        self.assertGreater(len(matches), 0)
        score, status, total_matches, longest = calculate_similarity(tokens_a, tokens_b, matches)
        self.assertEqual(score, 100.0)
        self.assertEqual(status, "HIGH")

    def test_rabin_karp_no_match(self):
        text_a = "quantum computing uses qubits for quantum entanglement superposition"
        text_b = "baking chocolate cake requires flour sugar eggs cocoa powder butter"
        tokens_a = tokenize(text_a)
        tokens_b = tokenize(text_b)
        matches = rabin_karp_match(tokens_a, tokens_b, window_size=5)
        score, status, total_matches, longest = calculate_similarity(tokens_a, tokens_b, matches)
        self.assertEqual(score, 0.0)
        self.assertEqual(status, "LOW")
        self.assertEqual(total_matches, 0)

    def test_kmp_lps_computation(self):
        pattern = tokenize("a b a b a c")
        lps = compute_lps_array(pattern)
        # Expected LPS for 'a b a b a c': [0, 0, 1, 2, 3, 0]
        self.assertEqual(lps, [0, 0, 1, 2, 3, 0])

    def test_kmp_search_multiple_occurrences(self):
        pattern = "machine learning"
        text = "machine learning is great. machine learning is powerful. machine learning everywhere."
        matches = kmp_search(pattern, text)
        self.assertEqual(len(matches), 3)

    def test_kmp_search_no_occurrence(self):
        pattern = "deep neural network"
        text = "basic python variables and conditionals"
        matches = kmp_search(pattern, text)
        self.assertEqual(matches, [])

    def test_short_document_window_size_adaptability(self):
        short_text = "python code"
        tokens_short = tokenize(short_text)
        long_text = "python code is essential for automation"
        tokens_long = tokenize(long_text)
        matches = rabin_karp_match(tokens_short, tokens_long, window_size=5)
        score, status, total_matches, longest = calculate_similarity(tokens_short, tokens_long, matches)
        self.assertEqual(score, 100.0)
        self.assertEqual(status, "HIGH")


class TestDatabaseAndServicesQA(unittest.TestCase):
    """QA Tests for Database Operations, Parameterization, and Service Layer."""

    def setUp(self):
        test_connection()
        self.user_email = f"qa_test_{os.urandom(4).hex()}@example.com"
        self.user_name = "QA Test User"

    def test_user_registration_and_retrieval(self):
        user = register_new_user(self.user_name, self.user_email)
        self.assertIn("user_id", user)
        self.assertEqual(user["name"], self.user_name)
        self.assertEqual(user["email"], self.user_email)

        all_users = list_users()
        found = any(u["email"] == self.user_email for u in all_users)
        self.assertTrue(found)

    def test_document_upload_and_list(self):
        user = register_new_user(self.user_name, self.user_email)
        user_id = user["user_id"]
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tf:
            tf.write("Artificial intelligence and machine learning models in production.")
            tf_path = tf.name

        try:
            doc = upload_document(user_id, tf_path)
            self.assertIn("document_id", doc)
            self.assertEqual(doc["word_count"], 8)

            docs = list_documents()
            found = any(d["document_id"] == doc["document_id"] for d in docs)
            self.assertTrue(found)
        finally:
            if os.path.exists(tf_path):
                os.remove(tf_path)

    def test_comparison_service_two_documents(self):
        u1 = register_new_user("QA Student 1", f"qa1_{os.urandom(4).hex()}@test.com")
        u2 = register_new_user("QA Student 2", f"qa2_{os.urandom(4).hex()}@test.com")

        content1 = "Data structures and algorithms are fundamental to software engineering."
        content2 = "Data structures and algorithms are fundamental to computer science education."

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tf1:
            tf1.write(content1)
            tf1_path = tf1.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tf2:
            tf2.write(content2)
            tf2_path = tf2.name

        try:
            d1 = upload_document(u1["user_id"], tf1_path)
            d2 = upload_document(u2["user_id"], tf2_path)

            res = compare_two_documents(d1["document_id"], d2["document_id"], window_size=5)
            self.assertIn("similarity_score", res)
            self.assertGreater(res["similarity_score"], 0.0)
            self.assertIn("comparison_id", res)
        finally:
            if os.path.exists(tf1_path):
                os.remove(tf1_path)
            if os.path.exists(tf2_path):
                os.remove(tf2_path)

    def test_self_comparison_rejection(self):
        u = register_new_user("QA Self User", f"qa_self_{os.urandom(4).hex()}@test.com")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tf:
            tf.write("Test content for self comparison error.")
            tf_path = tf.name

        try:
            d = upload_document(u["user_id"], tf_path)
            with self.assertRaises(ValueError):
                compare_two_documents(d["document_id"], d["document_id"])
        finally:
            if os.path.exists(tf_path):
                os.remove(tf_path)

    def test_sql_injection_resilience(self):
        malicious_input = "'; DROP TABLE users; --"
        malicious_email = f"hacker_{os.urandom(4).hex()}@exploit.com"
        # Database parameterization must protect against SQL injection without crashing or corrupting DB
        user = register_new_user(malicious_input, malicious_email)
        self.assertIsNotNone(user["user_id"])
        all_users = queries.get_all_users()
        found = any(u["user_id"] == user["user_id"] and u["name"] == malicious_input for u in all_users)
        self.assertTrue(found)


class TestFlaskRestApiQA(unittest.TestCase):
    """QA Tests for Flask REST API Endpoints."""

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_api_status_endpoint(self):
        resp = self.client.get("/api/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "online")
        self.assertTrue(data["database_connected"])

    def test_api_users_get_and_post(self):
        email = f"api_qa_{os.urandom(4).hex()}@test.com"
        post_resp = self.client.post(
            "/api/users",
            data=json.dumps({"name": "API QA User", "email": email}),
            content_type="application/json"
        )
        self.assertEqual(post_resp.status_code, 201)
        post_data = post_resp.get_json()
        self.assertTrue(post_data["success"])

        get_resp = self.client.get("/api/users")
        self.assertEqual(get_resp.status_code, 200)
        get_data = get_resp.get_json()
        self.assertTrue(get_data["success"])

    def test_api_users_missing_params_validation(self):
        resp = self.client.post(
            "/api/users",
            data=json.dumps({"name": ""}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertFalse(data["success"])

    def test_api_live_text_compare(self):
        payload = {
            "text1": "Flask web server framework in python for building REST APIs.",
            "text2": "Flask web server framework in python for web development.",
            "doc1_name": "Doc A",
            "doc2_name": "Doc B",
            "window_size": 5
        }
        resp = self.client.post(
            "/api/compare",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        res = data["result"]
        self.assertIn("similarity_score", res)
        self.assertIn("algorithm_breakdown", res)
        self.assertEqual(res["algorithm_breakdown"]["window_size"], 5)

    def test_api_analytics_endpoint(self):
        resp = self.client.get("/api/analytics")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertIn("stats", data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
