"""
Knuth-Morris-Pratt (KMP) Pattern Matching Algorithm Implementation.

This module manually implements:
1. Longest Prefix Suffix (LPS) Array computation.
2. KMP String Matching algorithm without character backtracking.
3. Phrase verification utility for document plagiarism detection.
"""


def compute_lps_array(pattern: str) -> list:
    """
    Computes the Longest Prefix Suffix (LPS) array for a given pattern.
    
    lps[i] stores the length of the longest proper prefix of pattern[0..i]
    that is also a suffix of pattern[0..i].
    
    Intuition:
    When a character mismatch occurs during pattern matching, the LPS array 
    tells us how many characters we can skip re-checking, avoiding inefficient 
    backtracking in the main text.
    
    Time Complexity: O(M) where M is pattern length.
    Space Complexity: O(M) auxiliary space for LPS array.
    
    Args:
        pattern (str): The search pattern string.
        
    Returns:
        list[int]: Computed LPS array of size len(pattern).
    """
    m = len(pattern)
    lps = [0] * m
    
    length = 0  # Length of the previous longest prefix suffix
    i = 1
    
    # Loop calculates lps[i] for i = 1 to m-1
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                # Fall back to previous longest prefix length (No index increment of i!)
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
                
    return lps


def kmp_search(pattern: str, text: str) -> list:
    """
    Searches for all occurrences of pattern in text using KMP algorithm.
    
    Time Complexity: O(N + M) worst-case (N = text length, M = pattern length).
    Space Complexity: O(M) for LPS array.
    
    Args:
        pattern (str): Substring pattern to match.
        text (str): Main body of text.
        
    Returns:
        list[int]: Starting character index positions of all pattern matches in text.
    """
    if not pattern or not text:
        return []
    
    m = len(pattern)
    n = len(text)
    
    if m > n:
        return []
    
    lps = compute_lps_array(pattern)
    match_indices = []
    
    i = 0  # Index for text[]
    j = 0  # Index for pattern[]
    
    while i < n:
        if pattern[j] == text[i]:
            i += 1
            j += 1
            
        if j == m:
            # Full pattern match found at position (i - j)
            match_indices.append(i - j)
            j = lps[j - 1]  # Reset j using LPS array to find overlapping matches
            
        elif i < n and pattern[j] != text[i]:
            # Mismatch after j matches
            if j != 0:
                j = lps[j - 1]  # Do NOT increment i, skip redundant comparisons
            else:
                i += 1
                
    return match_indices


def verify_phrase_with_kmp(phrase: str, full_document_text: str) -> list:
    """
    Secondary verification helper: Uses KMP to confirm the exact location(s)
    of a candidate matching phrase inside a document.
    
    Args:
        phrase (str): Candidate matched phrase string.
        full_document_text (str): Full normalized text of target document.
        
    Returns:
        list[int]: Character start indices where phrase occurs in target document.
    """
    return kmp_search(phrase, full_document_text)


if __name__ == "__main__":
    print("--- KMP MANUAL ALGORITHM TEST ---")
    pattern = "ABABCABAB"
    lps = compute_lps_array(pattern)
    print(f"Pattern: '{pattern}'")
    print(f"Computed LPS Array: {lps}")
    
    text = "ABABDABACDABABCABABABABCABAB"
    matches = kmp_search(pattern, text)
    print(f"\nText: '{text}'")
    print(f"KMP Search Pattern Matches at indices: {matches}")
    
    for idx in matches:
        print(f"  Verified Substring at [{idx}:{idx+len(pattern)}]: '{text[idx:idx+len(pattern)]}'")
