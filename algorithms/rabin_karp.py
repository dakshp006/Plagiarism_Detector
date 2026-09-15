"""
Rabin-Karp Algorithm Implementation with Rolling Hash.

This module manually implements:
1. Polynomial Rolling Hash calculation.
2. Rabin-Karp single-pattern string matching.
3. Multi-word sequence window matching across documents using hash table lookups.
"""

# Constants for Rabin-Karp polynomial rolling hash
BASE = 256          # Alphabet size / base (ASCII characters)
PRIME = 1000000007  # Large prime modulus to fit in integer and reduce collisions


def compute_rolling_hash(text: str, base: int = BASE, prime: int = PRIME) -> int:
    """
    Computes initial polynomial hash value for a given string text.
    
    Formula:
        Hash = ( (c[0]*base^(m-1)) + (c[1]*base^(m-2)) + ... + c[m-1] ) mod prime
        
    Args:
        text (str): Input string phrase.
        base (int): Base radix (default 256).
        prime (int): Prime modulus (default 1000000007).
        
    Returns:
        int: Computed integer hash value.
    """
    hash_value = 0
    m = len(text)
    for i in range(m):
        hash_value = (hash_value * base + ord(text[i])) % prime
    return hash_value


def rabin_karp_pattern_search(pattern: str, text: str, base: int = BASE, prime: int = PRIME) -> list:
    """
    Standard Rabin-Karp algorithm to search for all occurrences of a pattern in a text
    using rolling hash and collision verification.
    
    Time Complexity:
        Best/Average Case: O(N + M)
        Worst Case: O(N * M) (if many hash collisions occur)
    Space Complexity:
        O(1) auxiliary memory.
        
    Args:
        pattern (str): The pattern string to search for.
        text (str): The main text to search within.
        
    Returns:
        list[int]: List of starting character index positions where pattern is found.
    """
    m = len(pattern)
    n = len(text)
    
    if m == 0 or n == 0 or m > n:
        return []
    
    match_positions = []
    
    # Calculate h = (base^(m-1)) % prime
    h = 1
    for i in range(m - 1):
        h = (h * base) % prime
        
    # Compute initial hash values for pattern and first window of text
    pattern_hash = compute_rolling_hash(pattern, base, prime)
    text_hash = compute_rolling_hash(text[:m], base, prime)
    
    # Slide the pattern over text 1 character at a time
    for i in range(n - m + 1):
        # Check if hash values match
        if pattern_hash == text_hash:
            # Hash Match -> Explicit Collision Verification (Spurious Hit Check)
            if text[i : i + m] == pattern:
                match_positions.append(i)
                
        # Calculate rolling hash for next window:
        # Remove leading digit, add trailing digit
        if i < n - m:
            text_hash = (base * (text_hash - ord(text[i]) * h) + ord(text[i + m])) % prime
            # Ensure non-negative hash value
            if text_hash < 0:
                text_hash += prime
                
    return match_positions


def rabin_karp_match(doc1_tokens: list, doc2_tokens: list, window_size: int = 5) -> list:
    """
    Document-level Rabin-Karp sequence matcher using word-window rolling hashes.
    
    Steps:
    1. Create N-word sliding windows for Doc 1 and Doc 2.
    2. Compute rolling hash for each window.
    3. Store Doc 1 window hashes in a Hash Table (Python dictionary) -> O(1) lookup.
    4. Iterate over Doc 2 windows, look up matching hash.
    5. Verify exact sequence equality to prevent hash collisions.
    6. Consolidate non-overlapping or longest matching sequences.
    
    Args:
        doc1_tokens (list[str]): List of normalized words from Document 1.
        doc2_tokens (list[str]): List of normalized words from Document 2.
        window_size (int): Word window length (default: 5).
        
    Returns:
        list[dict]: List of match records:
            [
                {
                    "phrase": str,
                    "position_doc1": int,
                    "position_doc2": int,
                    "match_length": int
                }, ...
            ]
    """
    from utils.text_cleaner import create_word_windows
    
    if not doc1_tokens or not doc2_tokens:
        return []

    effective_window_size = min(len(doc1_tokens), len(doc2_tokens), window_size)
    if effective_window_size < 1:
        return []
    
    windows_doc1 = create_word_windows(doc1_tokens, effective_window_size)
    windows_doc2 = create_word_windows(doc2_tokens, effective_window_size)
    
    if not windows_doc1 or not windows_doc2:
        return []
    
    # Hash Table mapping: hash_value -> list of tuples (phrase, doc1_word_index)
    hash_table_doc1 = {}
    for phrase, idx in windows_doc1:
        h_val = compute_rolling_hash(phrase)
        if h_val not in hash_table_doc1:
            hash_table_doc1[h_val] = []
        hash_table_doc1[h_val].append((phrase, idx))
        
    matches = []
    seen_matches = set()  # Prevent duplicate matches
    
    # Iterate through Document 2 windows and query hash table
    for phrase_doc2, idx_doc2 in windows_doc2:
        h_val_doc2 = compute_rolling_hash(phrase_doc2)
        
        if h_val_doc2 in hash_table_doc1:
            # Potential Match -> Explicit verification against hash collisions
            for phrase_doc1, idx_doc1 in hash_table_doc1[h_val_doc2]:
                if phrase_doc1 == phrase_doc2:
                    # Verified match!
                    match_key = (phrase_doc1, idx_doc1, idx_doc2)
                    if match_key not in seen_matches:
                        seen_matches.add(match_key)
                        matches.append({
                            "phrase": phrase_doc1,
                            "position_doc1": idx_doc1,
                            "position_doc2": idx_doc2,
                            "match_length": len(phrase_doc1.split())
                        })
                        
    return matches


if __name__ == "__main__":
    print("--- RABIN-KARP MANUAL ALGORITHM TEST ---")
    text = "machine learning is a subset of artificial intelligence and deep learning"
    pattern = "artificial intelligence"
    
    positions = rabin_karp_pattern_search(pattern, text)
    print(f"Text: '{text}'")
    print(f"Pattern: '{pattern}'")
    print(f"Found Pattern at character positions: {positions}")
    
    doc1 = ["machine", "learning", "is", "a", "subset", "of", "artificial", "intelligence"]
    doc2 = ["deep", "learning", "and", "machine", "learning", "is", "a", "subset", "of", "artificial", "intelligence"]
    
    word_matches = rabin_karp_match(doc1, doc2, window_size=5)
    print(f"\nWord Window Matching (Doc1 length={len(doc1)}, Doc2 length={len(doc2)}):")
    for m in word_matches:
        print(f"  Matched Phrase: '{m['phrase']}' | Doc1 Pos: {m['position_doc1']} | Doc2 Pos: {m['position_doc2']} | Length: {m['match_length']} words")
