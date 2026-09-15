"""
Flask REST API Server for Plagiarism & Duplicate Text Detection System.
Provides RESTful API endpoints for the web frontend interface.
"""

import os
import sys
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS

from database.connection import get_db_connection, DB_TYPE, test_connection
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
from utils.text_cleaner import clean_text, tokenize
from algorithms.rabin_karp import rabin_karp_match, compute_rolling_hash, BASE, PRIME
from algorithms.kmp import verify_phrase_with_kmp, compute_lps_array
from algorithms.similarity import calculate_similarity

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)


# Ensure static directory exists
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)


# ============================================================================
# STATIC FILES / FRONTEND ROUTE
# ============================================================================

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route("/api/status", methods=["GET"])
def get_status():
    """System health check and DB engine status."""
    connected = test_connection()
    from database.connection import DB_TYPE as current_db_type
    return jsonify({
        "status": "online",
        "database_connected": connected,
        "database_engine": current_db_type.upper() if current_db_type else "UNKNOWN",
        "system_name": "Plagiarism & Duplicate Text Detection System",
        "version": "2.0.0"
    })


@app.route("/api/users", methods=["GET", "POST"])
def handle_users():
    if request.method == "GET":
        try:
            users = list_users()
            return jsonify({"success": True, "users": users})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    elif request.method == "POST":
        data = request.get_json() or {}
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        if not name or not email:
            return jsonify({"success": False, "error": "Name and email are required."}), 400
        try:
            user = register_new_user(name, email)
            return jsonify({"success": True, "user": user}), 201
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/documents", methods=["GET"])
def get_documents():
    try:
        docs = list_documents()
        return jsonify({"success": True, "documents": docs})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/documents/upload", methods=["POST"])
def upload_doc():
    """Uploads document via raw text content or file parameter."""
    try:
        user_id = request.form.get("user_id") or (request.json and request.json.get("user_id"))
        file_name = request.form.get("file_name") or (request.json and request.json.get("file_name")) or "document.txt"
        content = request.form.get("content") or (request.json and request.json.get("content"))
        
        # Handle file upload if provided
        if "file" in request.files:
            file_obj = request.files["file"]
            file_name = file_obj.filename
            content = file_obj.read().decode("utf-8", errors="ignore")

        if not user_id or not content:
            return jsonify({"success": False, "error": "User ID and content are required."}), 400

        user_id = int(user_id)
        word_count = len(tokenize(clean_text(content)))
        
        doc_id = queries.add_document(user_id, file_name, content, word_count)
        return jsonify({
            "success": True,
            "document": {
                "document_id": doc_id,
                "user_id": user_id,
                "file_name": file_name,
                "word_count": word_count,
                "content_preview": content[:100] + "..." if len(content) > 100 else content
            }
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/compare", methods=["POST"])
def compare_docs():
    """
    Supports two comparison modes:
    1. Stored DB Documents: json containing { doc1_id, doc2_id, window_size }
    2. Live Text Input: json containing { text1, text2, doc1_name, doc2_name, window_size }
    """
    data = request.get_json() or {}
    window_size = int(data.get("window_size", 5))

    # Mode 1: DB Document IDs
    if "doc1_id" in data and "doc2_id" in data:
        try:
            doc1_id = int(data["doc1_id"])
            doc2_id = int(data["doc2_id"])
            res = compare_two_documents(doc1_id, doc2_id, window_size=window_size)
            
            # Fetch document text contents for side-by-side highlighting
            doc1 = queries.get_document_by_id(doc1_id)
            doc2 = queries.get_document_by_id(doc2_id)
            res["doc1_content"] = doc1["content"] if doc1 else ""
            res["doc2_content"] = doc2["content"] if doc2 else ""
            
            return jsonify({"success": True, "result": res})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

    # Mode 2: Direct Live Text Compare
    elif "text1" in data and "text2" in data:
        text1 = data["text1"]
        text2 = data["text2"]
        doc1_name = data.get("doc1_name", "Text 1")
        doc2_name = data.get("doc2_name", "Text 2")

        tokens1 = tokenize(clean_text(text1))
        tokens2 = tokenize(clean_text(text2))

        matches = rabin_karp_match(tokens1, tokens2, window_size=window_size)
        cleaned_doc2_str = " ".join(tokens2)
        for m in matches:
            kmp_pos = verify_phrase_with_kmp(m["phrase"], cleaned_doc2_str)
            m["kmp_verified"] = len(kmp_pos) > 0

        score, status, total_matches, longest_match = calculate_similarity(tokens1, tokens2, matches)

        # Generate algorithm visualization breakdown payload
        rk_samples = []
        if len(tokens1) >= window_size:
            w_tokens = tokens1[:window_size]
            w_str = " ".join(w_tokens)
            h_val = compute_rolling_hash(w_str)
            rk_samples.append({
                "window": w_str,
                "hash_val": h_val,
                "index": 0
            })
            if len(tokens1) > window_size:
                w2_tokens = tokens1[1:1 + window_size]
                w2_str = " ".join(w2_tokens)
                h_val2 = compute_rolling_hash(w2_str)
                rk_samples.append({
                    "window": w2_str,
                    "hash_val": h_val2,
                    "index": 1
                })

        # Sample KMP LPS array calculation for top match phrase
        sample_lps = []
        if matches and matches[0].get("phrase"):
            top_phrase = matches[0]["phrase"]
            phrase_tokens = tokenize(top_phrase)
            if phrase_tokens:
                lps_arr = compute_lps_array(phrase_tokens)
                sample_lps = [{"token": t, "lps": l} for t, l in zip(phrase_tokens, lps_arr)]

        return jsonify({
            "success": True,
            "result": {
                "doc1_name": doc1_name,
                "doc2_name": doc2_name,
                "doc1_content": text1,
                "doc2_content": text2,
                "tokens1": tokens1,
                "tokens2": tokens2,
                "similarity_score": score,
                "status": status,
                "total_matches": total_matches,
                "longest_match": longest_match,
                "matches": matches,
                "algorithm_breakdown": {
                    "window_size": window_size,
                    "hash_base": BASE,
                    "hash_mod": PRIME,
                    "rk_samples": rk_samples,
                    "kmp_lps_sample": sample_lps
                }
            }
        })
    else:
        return jsonify({"success": False, "error": "Please provide either doc1_id/doc2_id OR text1/text2."}), 400


@app.route("/api/compare/one-to-many", methods=["POST"])
def compare_one_many():
    data = request.get_json() or {}
    target_id = data.get("target_doc_id")
    window_size = int(data.get("window_size", 5))

    if not target_id:
        return jsonify({"success": False, "error": "target_doc_id is required."}), 400

    try:
        results = compare_one_to_many(int(target_id), window_size=window_size)
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/history", methods=["GET"])
def get_history():
    try:
        history = queries.get_comparison_history()
        return jsonify({"success": True, "history": history})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/reports/<int:comparison_id>", methods=["GET"])
def get_report(comparison_id):
    try:
        report_data = queries.get_comparison_report_data(comparison_id)
        if not report_data:
            return jsonify({"success": False, "error": f"Report #{comparison_id} not found."}), 404
        return jsonify({"success": True, "report": report_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/reports/download/<int:comparison_id>", methods=["GET"])
def download_report(comparison_id):
    try:
        file_path = generate_report_file(comparison_id)
        return send_file(file_path, as_attachment=True, download_name=f"plagiarism_report_{comparison_id}.txt")
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    try:
        stats = queries.get_analytics_summary()
        high_risk_users = queries.get_high_similarity_users()
        above_avg_comps = queries.get_above_average_comparisons()
        return jsonify({
            "success": True,
            "stats": stats,
            "high_risk_users": high_risk_users,
            "above_average_comparisons": above_avg_comps
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# SERVER LAUNCH
# ============================================================================

if __name__ == "__main__":
    test_connection()
    port = int(os.getenv("PORT", 5000))
    print(f"\n==================================================================")
    print(f"   PLAGIARISM DETECTOR WEB SERVER STARTED ON http://127.0.0.1:{port}")
    print(f"==================================================================\n")
    app.run(host="0.0.0.0", port=port, debug=True)
