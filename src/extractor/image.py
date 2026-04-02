import os
import re

import pytesseract
from PIL import Image


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_image(file_path: str) -> str:
    try:
        with Image.open(file_path) as img:
            text = pytesseract.image_to_string(img)
            return _clean_text(text)

    except Exception as error:
        print(f"[IMAGE OCR ERROR]: {error}")
        return ""


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    sample_candidates = [
        os.path.join(base_dir, "sample", "sample.jpg"),
        os.path.join(base_dir, "sample", "sample.png"),
        os.path.join(base_dir, "Sample data", "sample.jpg"),
        os.path.join(base_dir, "Sample data", "sample.png"),
    ]

    sample_path = next((path for path in sample_candidates if os.path.exists(path)), sample_candidates[0])
    result = extract_image(sample_path)
    print(result[:500])