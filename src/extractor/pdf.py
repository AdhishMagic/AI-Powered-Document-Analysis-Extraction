import os
import re

import pdfplumber
import pytesseract


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_pdf(file_path: str) -> str:
    extracted_parts = []

    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if not page_text.strip():
                    try:
                        image = page.to_image(resolution=300).original
                        page_text = pytesseract.image_to_string(image)
                    except Exception as ocr_error:
                        print(f"[PDF OCR ERROR]: {ocr_error}")
                        page_text = ""

                cleaned_page_text = _clean_text(page_text)
                if cleaned_page_text:
                    extracted_parts.append(cleaned_page_text)

    except Exception as error:
        print(f"[PDF ERROR]: {error}")
        return ""

    return _clean_text("\n".join(extracted_parts))


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    sample_candidates = [
        os.path.join(base_dir, "sample", "sample.pdf"),
        os.path.join(base_dir, "Sample data", "sample.pdf"),
    ]

    sample_path = next((path for path in sample_candidates if os.path.exists(path)), sample_candidates[0])
    result = extract_pdf(sample_path)
    print(result[:500])