"""
Similarity Calculation & Risk Level Classifier Module.

Calculates the percentage of text overlap between two documents based on matched
word sequences identified by Rabin-Karp, and classifies the result into risk levels.
"""


def classify_risk(similarity_score: float) -> str:
    """
    Classifies similarity percentage into risk categories.
    
    Project-Defined Thresholds:
      0.00%  - 19.99% --> LOW
      20.00% - 49.99% --> MEDIUM
      50.00% - 100.0% --> HIGH
      
    Note: These thresholds are project-defined for demonstration purposes
    and do not represent universal academic plagiarism standard standards.
    
    Args:
        similarity_score (float): Percentage similarity score (0.0 to 100.0).
        
    Returns:
        str: Risk classification label ('LOW', 'MEDIUM', 'HIGH').
    """
    if similarity_score < 20.0:
        return "LOW"
    elif similarity_score < 50.0:
        return "MEDIUM"
    else:
        return "HIGH"


def calculate_similarity(
    doc1_tokens: list, 
    doc2_tokens: list, 
    matching_results: list
) -> tuple:
    """
    Calculates overall similarity percentage and determines longest match statistics.
    
    Formula:
        Similarity % = ( Unique Matched Words / Min(Doc1_Word_Count, Doc2_Word_Count) ) * 100
        
    Handling Edge Cases:
    - Empty documents: Returns (0.00, 'LOW', 0, 0) safely.
    - Overlapping windows: Tracks set of unique word index positions matched in Doc 1
      to prevent inflated similarity scores caused by sliding window overlap.
    - Score capping: Caps maximum score at 100.00%.
    
    Args:
        doc1_tokens (list[str]): Tokens of Document 1.
        doc2_tokens (list[str]): Tokens of Document 2.
        matching_results (list[dict]): List of match dicts from Rabin-Karp matcher.
        
    Returns:
        tuple: (similarity_score: float, status: str, total_matches: int, longest_match: int)
    """
    len1 = len(doc1_tokens)
    len2 = len(doc2_tokens)
    
    # Handle empty or zero-word document cases
    if len1 == 0 or len2 == 0:
        return 0.0, "LOW", 0, 0
    
    min_len = min(len1, len2)
    
    if not matching_results:
        return 0.0, "LOW", 0, 0
    
    # Track unique word indices matched in Document 1 and Document 2 to avoid double counting
    matched_doc1_word_indices = set()
    matched_doc2_word_indices = set()
    longest_match_words = 0
    
    for match in matching_results:
        start_idx1 = match["position_doc1"]
        start_idx2 = match.get("position_doc2", 0)
        match_len = match["match_length"]
        
        # Track longest single matching sequence length
        if match_len > longest_match_words:
            longest_match_words = match_len
            
        # Add every word index in this matched phrase to the unique sets
        for offset in range(match_len):
            if start_idx1 + offset < len1:
                matched_doc1_word_indices.add(start_idx1 + offset)
            if start_idx2 + offset < len2:
                matched_doc2_word_indices.add(start_idx2 + offset)
                
    unique_matched_words_count = min(len(matched_doc1_word_indices), len(matched_doc2_word_indices)) if matched_doc2_word_indices else len(matched_doc1_word_indices)
    
    # Calculate percentage based on the smaller document length
    raw_percentage = (unique_matched_words_count / min_len) * 100.0
    
    # Cap score at 100.00% and round to 2 decimal places
    similarity_score = round(min(100.00, raw_percentage), 2)
    status = classify_risk(similarity_score)
    total_matches = len(matching_results)
    
    return similarity_score, status, total_matches, longest_match_words


if __name__ == "__main__":
    print("--- SIMILARITY CALCULATION TEST ---")
    doc1_words = ["machine", "learning", "is", "a", "subset", "of", "artificial", "intelligence", "systems"]
    doc2_words = ["machine", "learning", "is", "a", "subset", "of", "artificial", "intelligence", "tools"]
    
    sample_matches = [
        {
            "phrase": "machine learning is a subset of artificial intelligence",
            "position_doc1": 0,
            "position_doc2": 0,
            "match_length": 8
        }
    ]
    
    score, status, total, longest = calculate_similarity(doc1_words, doc2_words, sample_matches)
    print(f"Doc1 Word Count: {len(doc1_words)}")
    print(f"Doc2 Word Count: {len(doc2_words)}")
    print(f"Calculated Similarity Score: {score}%")
    print(f"Risk Level Status: {status}")
    print(f"Total Matching Sections: {total}")
    print(f"Longest Matching Sequence: {longest} words")
