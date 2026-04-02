from pathlib import Path


def extract_text_from_image(file_path: str) -> str:
    """Extract text from an image using OCR.

    This is a placeholder implementation. Integrate pytesseract or
    a cloud OCR provider as needed.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {file_path}")
    return ""
