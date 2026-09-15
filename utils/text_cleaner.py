import re


def clean_text(raw_text: str) -> str:
    """
    Normalizes raw text content.
    
    Steps:
    1. Lowercase conversion: Ensures case-insensitive matching.
    2. Punctuation removal: Replaces special characters with spaces using regular expressions.
    3. Whitespace normalization: Collapses multiple spaces, tabs, and newlines into a single space.
    
    Example:
        Input:  "Python, is a Programming Language!"
        Output: "python is a programming language"
    
    Args:
        raw_text (str): Raw string input read from file.
        
    Returns:
        str: Cleaned, normalized single-line string.
    """
    if not raw_text:
        return ""
    
    # Step 1: Lowercase conversion
    text = raw_text.lower()
    
    # Step 2: Strip punctuation and special characters (preserve letters, digits, and spaces)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    
    # Step 3: Collapse whitespace (tabs, newlines, multiple spaces) into a single space
    cleaned_text = " ".join(text.split())
    
    return cleaned_text


def tokenize(cleaned_text: str) -> list:
    """
    Tokenizes normalized text into a list of individual words.
    
    Example:
        Input:  "python is a programming language"
        Output: ["python", "is", "a", "programming", "language"]
        
    Args:
        cleaned_text (str): Cleaned string output from clean_text().
        
    Returns:
        list[str]: Ordered list of word tokens.
    """
    if not cleaned_text or not cleaned_text.strip():
        return []
    return cleaned_text.split()


def create_word_windows(tokens: list, window_size: int = 5) -> list:
    """
    Creates overlapping n-word sliding windows from a list of word tokens.
    
    For plagiarism detection, word sequence windows preserve sentence structure.
    
    Example:
        Tokens: ["python", "is", "a", "high", "level", "language"]
        window_size = 4
        Yields:
        - ("python is a high", 0)
        - ("is a high level", 1)
        - ("a high level language", 2)
        
    Args:
        tokens (list[str]): Tokenized list of words.
        window_size (int): Number of words per sequence window (default: 5).
        
    Returns:
        list[tuple[str, int]]: List of tuples containing (window_phrase_string, starting_word_index).
    """
    if not tokens:
        return []
    
    n = len(tokens)
    # If the document has fewer words than the window size, return the entire document as 1 window
    if n <= window_size:
        phrase = " ".join(tokens)
        return [(phrase, 0)]
    
    windows = []
    for i in range(n - window_size + 1):
        window_phrase = " ".join(tokens[i : i + window_size])
        windows.append((window_phrase, i))
        
    return windows


if __name__ == "__main__":
    sample_text = "Python, is a   Programming Language!\nIt is high-level and easy to learn."
    cleaned = clean_text(sample_text)
    tokens = tokenize(cleaned)
    windows = create_word_windows(tokens, window_size=5)
    
    print("--- TEXT PREPROCESSING TEST ---")
    print(f"Original Text:\n{sample_text}\n")
    print(f"Cleaned Text:\n{cleaned}\n")
    print(f"Tokenized Words ({len(tokens)} words):\n{tokens}\n")
    print(f"Word Windows (Size=5, Total={len(windows)}):")
    for w, idx in windows:
        print(f"  Pos {idx}: '{w}'")
