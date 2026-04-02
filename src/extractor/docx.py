import os
import re

from docx import Document


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_docx(file_path: str) -> str:
    try:
        doc = Document(file_path)
        paragraphs = [_clean_text(paragraph.text) for paragraph in doc.paragraphs]
        text = "\n".join(paragraph for paragraph in paragraphs if paragraph)
        return _clean_text(text)

    except Exception as error:
        print(f"[DOCX ERROR]: {error}")
        return ""


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    sample_candidates = [
        os.path.join(base_dir, "sample", "sample.docx"),
        os.path.join(base_dir, "Sample data", "sample.docx"),
    ]

    sample_path = next((path for path in sample_candidates if os.path.exists(path)), sample_candidates[0])
    result = extract_docx(sample_path)
    print(result[:500])