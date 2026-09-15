import os
from datetime import datetime
from database import queries
from utils.text_cleaner import clean_text, tokenize
from algorithms.rabin_karp import rabin_karp_match
from algorithms.kmp import verify_phrase_with_kmp
from algorithms.similarity import calculate_similarity


def compare_two_documents(doc1_id: int, doc2_id: int, window_size: int = 5) -> dict:
    """
    Executes complete pairwise plagiarism comparison between Document 1 and Document 2.
    
    Workflow:
    1. Fetch documents from MySQL database.
    2. Normalize & tokenize text.
    3. Run Rabin-Karp algorithm with N-word rolling hashes.
    4. Verify matched sequence positions using KMP.
    5. Calculate similarity percentage and classify risk (LOW/MEDIUM/HIGH).
    6. Persist comparison, matched phrases, and report to MySQL in a transaction.
    """
    if doc1_id == doc2_id:
        raise ValueError("Cannot compare a document with itself. Please select two distinct documents.")
        
    doc1 = queries.get_document_by_id(doc1_id)
    doc2 = queries.get_document_by_id(doc2_id)
    
    if not doc1:
        raise ValueError(f"Document ID {doc1_id} does not exist.")
    if not doc2:
        raise ValueError(f"Document ID {doc2_id} does not exist.")
        
    # Preprocessing
    tokens1 = tokenize(clean_text(doc1["content"]))
    tokens2 = tokenize(clean_text(doc2["content"]))
    
    # Core Algorithmic Step 1: Rabin-Karp Matching
    matches = rabin_karp_match(tokens1, tokens2, window_size=window_size)
    
    # Core Algorithmic Step 2: KMP Verification (Confirm phrase presence in Doc 2 text)
    cleaned_doc2_str = " ".join(tokens2)
    for m in matches:
        kmp_positions = verify_phrase_with_kmp(m["phrase"], cleaned_doc2_str)
        # KMP confirms match presence
        m["kmp_verified"] = len(kmp_positions) > 0
        
    # Core Algorithmic Step 3: Similarity Percentage & Risk Level
    similarity_score, status, total_matches, longest_match = calculate_similarity(tokens1, tokens2, matches)
    
    # Core Database Step 4: Persist Results to MySQL
    comparison_id = queries.save_comparison_record(
        doc1_id=doc1_id,
        doc2_id=doc2_id,
        similarity_score=similarity_score,
        status=status,
        matching_results=matches,
        total_matches=total_matches,
        longest_match=longest_match
    )
    
    return {
        "comparison_id": comparison_id,
        "doc1_id": doc1_id,
        "doc1_name": doc1["file_name"],
        "doc2_id": doc2_id,
        "doc2_name": doc2["file_name"],
        "similarity_score": similarity_score,
        "status": status,
        "total_matches": total_matches,
        "longest_match": longest_match,
        "matches": matches
    }


def compare_one_to_many(target_doc_id: int, window_size: int = 5) -> list:
    """
    Compares a target document against all other uploaded documents in the database.
    Returns results sorted by similarity score in descending order.
    """
    all_docs = queries.get_all_documents()
    if not all_docs:
        raise ValueError("No documents stored in the database to compare against.")
        
    target_exists = any(d["document_id"] == target_doc_id for d in all_docs)
    if not target_exists:
        raise ValueError(f"Target document ID {target_doc_id} not found.")
        
    other_docs = [d for d in all_docs if d["document_id"] != target_doc_id]
    if not other_docs:
        raise ValueError("No other documents available in the database for comparison.")
        
    comparison_results = []
    for other_doc in other_docs:
        result = compare_two_documents(target_doc_id, other_doc["document_id"], window_size=window_size)
        comparison_results.append(result)
        
    # Sort descending by similarity score
    comparison_results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return comparison_results


def generate_report_file(comparison_id: int, output_dir: str = "reports") -> str:
    """
    Generates a structured text report for a comparison and saves it to disk.
    
    Returns:
        str: Absolute or relative file path of generated report.
    """
    report_data = queries.get_comparison_report_data(comparison_id)
    if not report_data:
        raise ValueError(f"No comparison record found for comparison_id = {comparison_id}")
        
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    file_path = os.path.join(output_dir, f"plagiarism_report_comp_{comparison_id}.txt")
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = []
    lines.append("======================================================================")
    lines.append("                       PLAGIARISM DETECTION REPORT                   ")
    lines.append("======================================================================")
    lines.append(f"Report ID / Comparison ID : #{comparison_id}")
    lines.append(f"Generated Date           : {now_str}")
    lines.append(f"Document 1 (Target)      : {report_data['doc1_name']} (Owner: {report_data['owner1_name']})")
    lines.append(f"Document 2 (Compared With): {report_data['doc2_name']} (Owner: {report_data['owner2_name']})")
    lines.append("----------------------------------------------------------------------")
    lines.append(f"SIMILARITY SCORE         : {report_data['similarity_score']}%")
    lines.append(f"RISK ASSESSMENT LEVEL    : {report_data['status']}")
    lines.append(f"Total Matched Sections   : {report_data['total_matches']}")
    lines.append(f"Longest Sequence Match   : {report_data['longest_match']} words")
    lines.append("======================================================================")
    lines.append("\n## DETAILED MATCHING SECTIONS / PHRASES:\n")
    
    matches = report_data.get("matching_sections", [])
    if not matches:
        lines.append("  [No matching sequence phrases detected]")
    else:
        for idx, m in enumerate(matches, 1):
            lines.append(f"  Match #{idx}:")
            lines.append(f"    Phrase        : \"{m['phrase']}\"")
            lines.append(f"    Doc 1 Position: Word index {m['position_doc1']}")
            lines.append(f"    Doc 2 Position: Word index {m['position_doc2']}")
            lines.append(f"    Word Length   : {m['match_length']} words\n")
            
    lines.append("======================================================================")
    lines.append("End of Plagiarism Report.")
    lines.append("======================================================================")
    
    report_content = "\n".join(lines)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    return file_path
