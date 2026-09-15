import os
from database import queries
from utils.text_cleaner import clean_text, tokenize


def register_new_user(name: str, email: str) -> dict:
    """
    Registers a new user in the system.
    """
    if not name or not name.strip():
        raise ValueError("User name cannot be empty.")
    if not email or "@" not in email:
        raise ValueError("Invalid email address provided.")
        
    user_id = queries.add_user(name, email)
    return {"user_id": user_id, "name": name, "email": email}


def list_users() -> list:
    """
    Retrieves all registered users.
    """
    return queries.get_all_users()


def find_user(keyword: str) -> list:
    """
    Searches for users by name or email.
    """
    return queries.search_users(keyword)


def upload_document(user_id: int, file_path: str) -> dict:
    """
    Reads a .txt document file, calculates word count, and persists it to MySQL database.
    
    Args:
        user_id (int): Foreign key ID of registered user.
        file_path (str): File system path to the .txt file.
        
    Returns:
        dict: Uploaded document metadata.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at path: '{file_path}'")
        
    if not file_path.lower().endswith(".txt"):
        raise ValueError("Only plain text (.txt) files are supported.")
        
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_content = f.read()
        
    if not raw_content or not raw_content.strip():
        raise ValueError("The document file is empty. Plagiarism check requires non-empty text.")
        
    cleaned = clean_text(raw_content)
    words = tokenize(cleaned)
    word_count = len(words)
    file_name = os.path.basename(file_path)
    
    doc_id = queries.add_document(user_id, file_name, raw_content, word_count)
    
    return {
        "document_id": doc_id,
        "user_id": user_id,
        "file_name": file_name,
        "word_count": word_count
    }


def list_documents() -> list:
    """
    Lists all uploaded documents.
    """
    return queries.get_all_documents()


def find_document(keyword: str) -> list:
    """
    Searches documents by keyword.
    """
    return queries.search_documents(keyword)
