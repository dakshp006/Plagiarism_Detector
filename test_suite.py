"""
Standalone Test Suite for Plagiarism Detection Engine.

Validates text cleaner, Rabin-Karp word sequence matcher, KMP pattern search,
similarity calculation, and edge cases (identical files, partial match, unique, empty, single word).
"""

from utils.text_cleaner import clean_text, tokenize
from algorithms.rabin_karp import rabin_karp_match, rabin_karp_pattern_search
from algorithms.kmp import kmp_search, compute_lps_array
from algorithms.similarity import calculate_similarity, classify_risk


def run_tests():
    print("=" * 65)
    print("      RUNNING STANDALONE PLAGIARISM ALGORITHM TEST SUITE      ")
    print("=" * 65)
    
    # ---------------------------------------------------------
    # TEST 1: Identical Documents (~100% Similarity)
    # ---------------------------------------------------------
    text1 = "Python is a high level programming language known for clear syntax and readability."
    tokens1_a = tokenize(clean_text(text1))
    tokens1_b = tokenize(clean_text(text1))
    
    matches1 = rabin_karp_match(tokens1_a, tokens1_b, window_size=5)
    score1, status1, total1, longest1 = calculate_similarity(tokens1_a, tokens1_b, matches1)
    
    print("\n[TEST 1] Identical Documents")
    print(f"  Score: {score1}% | Status: {status1} | Expected: 100.0% HIGH")
    assert score1 == 100.0, f"Expected 100.0, got {score1}"
    assert status1 == "HIGH", f"Expected HIGH, got {status1}"
    print("  --> PASS [OK]")
    
    # ---------------------------------------------------------
    # TEST 2: Completely Different Documents (LOW Similarity)
    # ---------------------------------------------------------
    text2_a = "Machine learning focuses on building algorithms that learn from data."
    text2_b = "Photosynthesis is the biological process used by green plants to convert solar light."
    tokens2_a = tokenize(clean_text(text2_a))
    tokens2_b = tokenize(clean_text(text2_b))
    
    matches2 = rabin_karp_match(tokens2_a, tokens2_b, window_size=5)
    score2, status2, total2, longest2 = calculate_similarity(tokens2_a, tokens2_b, matches2)
    
    print("\n[TEST 2] Completely Different Documents")
    print(f"  Score: {score2}% | Status: {status2} | Expected: 0.0% LOW")
    assert score2 == 0.0, f"Expected 0.0, got {score2}"
    assert status2 == "LOW", f"Expected LOW, got {status2}"
    print("  --> PASS [OK]")
    
    # ---------------------------------------------------------
    # TEST 3: Partially Copied Document (MEDIUM/HIGH Similarity)
    # ---------------------------------------------------------
    text3_a = "Machine learning is a core branch of artificial intelligence that focuses on learning from data."
    text3_b = "Machine learning is a core branch of artificial intelligence. Statistical models predict future trends."
    tokens3_a = tokenize(clean_text(text3_a))
    tokens3_b = tokenize(clean_text(text3_b))
    
    matches3 = rabin_karp_match(tokens3_a, tokens3_b, window_size=5)
    score3, status3, total3, longest3 = calculate_similarity(tokens3_a, tokens3_b, matches3)
    
    print("\n[TEST 3] Partially Copied Documents")
    print(f"  Score: {score3}% | Status: {status3} | Matched Sections: {total3}")
    assert score3 > 0.0, "Expected non-zero similarity score"
    print("  --> PASS [OK]")
    
    # ---------------------------------------------------------
    # TEST 4: Empty Document
    # ---------------------------------------------------------
    tokens4_a = tokenize(clean_text(""))
    tokens4_b = tokenize(clean_text("Some text content"))
    matches4 = rabin_karp_match(tokens4_a, tokens4_b, window_size=5)
    score4, status4, total4, longest4 = calculate_similarity(tokens4_a, tokens4_b, matches4)
    
    print("\n[TEST 4] Empty Document Handling")
    print(f"  Score: {score4}% | Status: {status4} | Expected: 0.0% LOW")
    assert score4 == 0.0
    assert status4 == "LOW"
    print("  --> PASS [OK]")
    
    # ---------------------------------------------------------
    # TEST 5: KMP Algorithm Verification
    # ---------------------------------------------------------
    pattern = "artificial intelligence"
    text_kmp = "machine learning is a subset of artificial intelligence and deep learning"
    lps = compute_lps_array(pattern)
    kmp_matches = kmp_search(pattern, text_kmp)
    
    print("\n[TEST 5] KMP Pattern Matching & LPS Array")
    print(f"  Pattern: '{pattern}'")
    print(f"  Text   : '{text_kmp}'")
    print(f"  Matches at character indices: {kmp_matches}")
    assert len(kmp_matches) > 0, "KMP should find the pattern match"
    print("  --> PASS [OK]")
    
    # ---------------------------------------------------------
    # TEST 6: Short Document Matching (< window_size words)
    # ---------------------------------------------------------
    text6_short = "Machine learning is"
    text6_long = "Machine learning is a subset of artificial intelligence that focuses on building systems that learn."
    tokens6_short = tokenize(clean_text(text6_short))
    tokens6_long = tokenize(clean_text(text6_long))
    
    matches6 = rabin_karp_match(tokens6_short, tokens6_long, window_size=5)
    score6, status6, total6, longest6 = calculate_similarity(tokens6_short, tokens6_long, matches6)
    
    print("\n[TEST 6] Short Document Matching (< window_size)")
    print(f"  Score: {score6}% | Status: {status6} | Matched Sections: {total6}")
    assert score6 == 100.0, f"Expected 100.0% for exact short doc subset match, got {score6}"
    assert status6 == "HIGH", f"Expected HIGH, got {status6}"
    print("  --> PASS [OK]")
    
    print("\n" + "=" * 65)
    print("          ALL ALGORITHM TESTS PASSED SUCCESSFULLY!          ")
    print("=" * 65)


if __name__ == "__main__":
    run_tests()
