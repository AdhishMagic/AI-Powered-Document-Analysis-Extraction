from pathlib import Path


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file.

    This is a placeholder implementation. Integrate python-docx or
    docx2txt as needed.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"DOCX file not found: {file_path}")
    return ""
