import base64
import os
from typing import Any

from fastapi import FastAPI, Header, HTTPException

try:
    from .ai.entities import extract_entities
    from .ai.sentiment import get_sentiment
    from .ai.summary import summarize
    from .extractor.docx import extract_docx
    from .extractor.image import extract_image
    from .extractor.pdf import extract_pdf
except ImportError:
    from ai.entities import extract_entities
    from ai.sentiment import get_sentiment
    from ai.summary import summarize
    from extractor.docx import extract_docx
    from extractor.image import extract_image
    from extractor.pdf import extract_pdf

app = FastAPI()

API_KEY = "sk_track2_987654321"


def save_temp_file(file_base64: str, filename: str) -> str:
    try:
        payload = file_base64.split(",", 1)[1] if "," in file_base64 else file_base64
        file_bytes = base64.b64decode(payload, validate=True)
    except Exception as error:
        raise HTTPException(status_code=400, detail="Invalid Base64 file data") from error

    temp_filename = f"temp_{os.path.basename(filename)}"
    temp_path = os.path.join(os.getcwd(), temp_filename)

    try:
        with open(temp_path, "wb") as temp_file:
            temp_file.write(file_bytes)
    except Exception as error:
        raise HTTPException(status_code=500, detail="Failed to save temporary file") from error

    return temp_path


def extract_text(file_path: str, file_type: str) -> str:
    normalized_type = (file_type or "").strip().lower()

    if normalized_type == "pdf":
        return extract_pdf(file_path)
    if normalized_type == "docx":
        return extract_docx(file_path)
    if normalized_type in {"image", "jpg", "jpeg", "png"}:
        return extract_image(file_path)

    raise HTTPException(status_code=400, detail="Unsupported file type")


@app.post("/api/document-analyze")
def document_analyze(payload: dict[str, Any], x_api_key: str = Header(default="")):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    file_name = str(payload.get("fileName", "")).strip()
    file_type = str(payload.get("fileType", "")).strip()
    file_base64 = str(payload.get("fileBase64", "")).strip()

    if not file_name or not file_type or not file_base64:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields: fileName, fileType, fileBase64",
        )

    temp_file_path = ""
    try:
        temp_file_path = save_temp_file(file_base64=file_base64, filename=file_name)
        text = extract_text(file_path=temp_file_path, file_type=file_type)

        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Extraction failed or no text found")

        summary = summarize(text)
        entities = extract_entities(text)
        sentiment = get_sentiment(text)

        return {
            "status": "success",
            "fileName": file_name,
            "summary": summary,
            "entities": entities,
            "sentiment": sentiment,
        }

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {error}") from error
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)