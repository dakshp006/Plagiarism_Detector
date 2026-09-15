"""
Main Command-Line Interface (CLI) for Plagiarism / Duplicate Detector.

Provides an interactive menu for user management, document uploading,
pairwise/multi-document comparison using Rabin-Karp & KMP, history view,
report generation, and SQL analytics.
"""

import sys
import os

from database.connection import test_connection
from database import queries
from services import (
    register_new_user,
    list_users,
    find_user,
    upload_document,
    list_documents,
    find_document,
    compare_two_documents,
    compare_one_to_many,
    generate_report_file
)


def print_banner():
    print("=" * 65)
    print("        PLAGIARISM & DUPLICATE TEXT DETECTION SYSTEM        ")
    print("      Python + Data Structures & Algorithms + MySQL Database ")
    print("=" * 65)


def display_menu():
    print("\n------------------------- MAIN MENU -------------------------")
    print(" 1. Register User")
    print(" 2. Upload Document")
    print(" 3. View Documents")
    print(" 4. Search Document")
    print(" 5. Compare Two Documents")
    print(" 6. Compare One Document With Multiple Documents")
    print(" 7. View Comparison History")
    print(" 8. Generate Plagiarism Report File")
    print(" 9. Analytics & Advanced SQL Queries")
    print("10. Exit")
    print("-------------------------------------------------------------")


# ============================================================================
# MENU OPTION HANDLERS
# ============================================================================

def handle_register_user():
    print("\n--- [1] REGISTER NEW USER ---")
    name = input("Enter User/Student Full Name: ").strip()
    email = input("Enter User Email Address    : ").strip()
    
    try:
        user = register_new_user(name, email)
        print(f"\n[SUCCESS] User registered successfully! Assigned User ID: {user['user_id']}")
    except Exception as e:
        print(f"\n[ERROR] Failed to register user: {e}")


def handle_upload_document():
    print("\n--- [2] UPLOAD DOCUMENT ---")
    users = list_users()
    if not users:
        print("[WARNING] No users found in database. Please register a user first.")
        return
        
    print("\nAvailable Users:")
    for u in users:
        print(f"  ID: {u['user_id']} | Name: {u['name']} | Email: {u['email']}")
        
    try:
        user_id_input = input("\nEnter Owner User ID: ").strip()
        if not user_id_input.isdigit():
            print("[ERROR] User ID must be a numeric integer.")
            return
        user_id = int(user_id_input)
        
        file_path = input("Enter full path to .txt file: ").strip().strip('"').strip("'")
        
        doc = upload_document(user_id, file_path)
        print(f"\n[SUCCESS] Document uploaded successfully!")
        print(f"  Document ID: {doc['document_id']}")
        print(f"  File Name  : {doc['file_name']}")
        print(f"  Word Count : {doc['word_count']} words")
    except Exception as e:
        print(f"\n[ERROR] Document upload failed: {e}")


def handle_view_documents():
    print("\n--- [3] VIEW ALL UPLOADED DOCUMENTS ---")
    try:
        docs = list_documents()
        if not docs:
            print("No documents found in database.")
            return
            
        print(f"\n{'ID':<5} | {'File Name':<30} | {'Word Count':<10} | {'Owner':<20} | {'Upload Time'}")
        print("-" * 85)
        for d in docs:
            uploaded_str = str(d['uploaded_at'])
            print(f"{d['document_id']:<5} | {d['file_name']:<30} | {d['word_count']:<10} | {d['owner_name']:<20} | {uploaded_str}")
    except Exception as e:
        print(f"[ERROR] Failed to fetch documents: {e}")


def handle_search_documents():
    print("\n--- [4] SEARCH DOCUMENTS ---")
    keyword = input("Enter search keyword (file name or content): ").strip()
    if not keyword:
        print("[ERROR] Search keyword cannot be empty.")
        return
        
    try:
        docs = find_document(keyword)
        if not docs:
            print(f"No documents found matching '{keyword}'.")
            return
            
        print(f"\nSearch Results for '{keyword}':")
        print(f"{'ID':<5} | {'File Name':<30} | {'Word Count':<10} | {'Owner':<20}")
        print("-" * 70)
        for d in docs:
            print(f"{d['document_id']:<5} | {d['file_name']:<30} | {d['word_count']:<10} | {d['owner_name']:<20}")
    except Exception as e:
        print(f"[ERROR] Search failed: {e}")


def handle_compare_two_documents():
    print("\n--- [5] COMPARE TWO DOCUMENTS ---")
    docs = list_documents()
    if len(docs) < 2:
        print("[WARNING] At least 2 uploaded documents are required for comparison.")
        return
        
    print("\nAvailable Documents:")
    for d in docs:
        print(f"  ID: {d['document_id']} | File: {d['file_name']} (Owner: {d['owner_name']})")
        
    try:
        doc1_input = input("\nEnter Document 1 ID: ").strip()
        doc2_input = input("Enter Document 2 ID: ").strip()
        
        if not doc1_input.isdigit() or not doc2_input.isdigit():
            print("[ERROR] Document IDs must be integers.")
            return
            
        doc1_id = int(doc1_input)
        doc2_id = int(doc2_input)
        
        print("\nExecuting Rabin-Karp Rolling Hash & KMP pattern matching...")
        result = compare_two_documents(doc1_id, doc2_id, window_size=5)
        
        print("\n" + "=" * 55)
        print("              COMPARISON RESULT SUMMARY              ")
        print("=" * 55)
        print(f"  Comparison ID         : #{result['comparison_id']}")
        print(f"  Document 1            : {result['doc1_name']}")
        print(f"  Document 2            : {result['doc2_name']}")
        print(f"  Similarity Percentage : {result['similarity_score']}%")
        print(f"  Risk Level            : {result['status']}")
        print(f"  Total Matching Sections: {result['total_matches']}")
        print(f"  Longest Match Sequence: {result['longest_match']} words")
        print("=" * 55)
        
        if result["matches"]:
            print("\nMatching Phrase Sections:")
            for idx, m in enumerate(result["matches"][:5], 1):
                print(f"  {idx}. \"{m['phrase']}\" (Length: {m['match_length']} words)")
            if len(result["matches"]) > 5:
                print(f"  ... and {len(result['matches']) - 5} more matching section(s).")
                
    except Exception as e:
        print(f"\n[ERROR] Comparison failed: {e}")


def handle_compare_one_to_many():
    print("\n--- [6] COMPARE ONE DOCUMENT WITH MULTIPLE DOCUMENTS ---")
    docs = list_documents()
    if len(docs) < 2:
        print("[WARNING] At least 2 uploaded documents are required.")
        return
        
    print("\nAvailable Documents:")
    for d in docs:
        print(f"  ID: {d['document_id']} | File: {d['file_name']} (Owner: {d['owner_name']})")
        
    try:
        target_input = input("\nEnter Target Document ID to compare against all others: ").strip()
        if not target_input.isdigit():
            print("[ERROR] Document ID must be an integer.")
            return
        target_id = int(target_input)
        
        results = compare_one_to_many(target_id, window_size=5)
        
        print("\n" + "=" * 65)
        print(f"  MULTI-DOCUMENT COMPARISON RANKING (Target Doc ID: #{target_id})")
        print("=" * 65)
        print(f"{'Rank':<5} | {'Compared Document':<25} | {'Similarity %':<15} | {'Risk Level'}")
        print("-" * 65)
        for rank, res in enumerate(results, 1):
            print(f"{rank:<5} | {res['doc2_name']:<25} | {res['similarity_score']:<15}% | {res['status']}")
        print("=" * 65)
        
        highest = results[0]
        print(f"\n[SUMMARY] Highest Similarity Match: Document '{highest['doc2_name']}' with {highest['similarity_score']}% ({highest['status']} Risk).")
    except Exception as e:
        print(f"\n[ERROR] Multi-document comparison failed: {e}")


def handle_view_history():
    print("\n--- [7] VIEW COMPARISON HISTORY ---")
    try:
        history = queries.get_comparison_history()
        if not history:
            print("No past comparison records found.")
            return
            
        print(f"\n{'Comp ID':<8} | {'Doc 1':<20} | {'Doc 2':<20} | {'Score %':<10} | {'Risk Level':<10} | {'Date/Time'}")
        print("-" * 90)
        for h in history:
            print(f"{h['comparison_id']:<8} | {h['doc1_name']:<20} | {h['doc2_name']:<20} | {h['similarity_score']:<10}% | {h['status']:<10} | {str(h['compared_at'])}")
    except Exception as e:
        print(f"[ERROR] Failed to fetch history: {e}")


def handle_generate_report():
    print("\n--- [8] GENERATE PLAGIARISM REPORT FILE ---")
    try:
        comp_input = input("Enter Comparison ID to generate report for: ").strip()
        if not comp_input.isdigit():
            print("[ERROR] Comparison ID must be an integer.")
            return
        comp_id = int(comp_input)
        
        file_path = generate_report_file(comp_id)
        print(f"\n[SUCCESS] Plagiarism Report generated successfully!")
        print(f"Report saved at: {os.path.abspath(file_path)}")
    except Exception as e:
        print(f"[ERROR] Report generation failed: {e}")


def handle_analytics():
    print("\n--- [9] SYSTEM ANALYTICS & ADVANCED SQL QUERIES ---")
    print("Choose Analytics View:")
    print("  a. SQL Aggregation Summary (COUNT, AVG, MAX, MIN)")
    print("  b. High-Similarity Users (GROUP BY + HAVING Query)")
    print("  c. Above-Average Comparisons (SUBQUERY)")
    
    choice = input("Enter sub-choice (a/b/c): ").strip().lower()
    
    try:
        if choice == 'a':
            stats = queries.get_analytics_summary()
            print("\n================ SYSTEM STATISTICAL SUMMARY ================")
            print(f"  Total Registered Users            : {stats['total_users']}")
            print(f"  Total Uploaded Documents          : {stats['total_documents']}")
            print(f"  Total Comparisons Executed        : {stats['total_comparisons']}")
            print(f"  Average Similarity Score          : {stats['avg_similarity']}%")
            print(f"  Highest Similarity Score          : {stats['max_similarity']}%")
            print(f"  Lowest Similarity Score           : {stats['min_similarity']}%")
            print(f"  HIGH Similarity Count (>=50%)     : {stats['high_count']}")
            print(f"  MEDIUM Similarity Count (20-49%)  : {stats['medium_count']}")
            print(f"  LOW Similarity Count (0-19%)      : {stats['low_count']}")
            print("============================================================")
            
        elif choice == 'b':
            print("\n--- HIGH SIMILARITY USERS (GROUP BY + HAVING) ---")
            users = queries.get_high_similarity_users()
            if not users:
                print("No users found with high-similarity comparisons.")
                return
            print(f"{'User ID':<8} | {'Name':<20} | {'Email':<25} | {'High Risk Count'}")
            print("-" * 70)
            for u in users:
                print(f"{u['user_id']:<8} | {u['name']:<20} | {u['email']:<25} | {u['high_risk_count']}")
                
        elif choice == 'c':
            print("\n--- ABOVE-AVERAGE SIMILARITY COMPARISONS (SUBQUERY) ---")
            comps = queries.get_above_average_comparisons()
            if not comps:
                print("No comparisons found above average score.")
                return
            print(f"{'Comp ID':<8} | {'Doc 1':<25} | {'Doc 2':<25} | {'Score %':<10} | {'Status'}")
            print("-" * 80)
            for c in comps:
                print(f"{c['comparison_id']:<8} | {c['doc1_name']:<25} | {c['doc2_name']:<25} | {c['similarity_score']:<10}% | {c['status']}")
        else:
            print("[ERROR] Invalid analytics sub-choice.")
    except Exception as e:
        print(f"[ERROR] Analytics failed: {e}")


# ============================================================================
# MAIN LOOP ENTRY POINT
# ============================================================================

def main():
    print_banner()
    print("Checking database connection...")
    if not test_connection():
        print("\n[CRITICAL WARNING] Database connection failed.")
        print("Make sure MySQL service is running and credentials in .env / database/connection.py are correct.")
        print("Continuing CLI in preview mode...\n")
        
    while True:
        display_menu()
        choice = input("Enter choice (1-10): ").strip()
        
        if choice == '1':
            handle_register_user()
        elif choice == '2':
            handle_upload_document()
        elif choice == '3':
            handle_view_documents()
        elif choice == '4':
            handle_search_documents()
        elif choice == '5':
            handle_compare_two_documents()
        elif choice == '6':
            handle_compare_one_to_many()
        elif choice == '7':
            handle_view_history()
        elif choice == '8':
            handle_generate_report()
        elif choice == '9':
            handle_analytics()
        elif choice == '10':
            print("\nThank you for using Plagiarism Detection System. Exiting...")
            sys.exit(0)
        else:
            print("\n[ERROR] Invalid choice! Please enter a number from 1 to 10.")


if __name__ == "__main__":
    main()
