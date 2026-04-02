# AI-Powered Document Analysis & Extraction API

## Description

This project provides a FastAPI-based API for analyzing documents uploaded as Base64-encoded files. It supports PDF, DOCX, and image inputs, extracts text from each format, and applies AI/NLP processing to return structured output. The pipeline combines document parsing, OCR, summarization, entity extraction, and sentiment analysis in a single request flow.

## Features

- Multi-format document support for PDF, DOCX, and image files
- OCR support for images and scanned PDFs
- AI-powered summarization
- Named entity extraction for names, dates, organizations, and amounts
- Sentiment analysis
- REST API with API key authentication

## Tech Stack

- Backend: FastAPI (Python)
- NLP/AI:
	- Transformers for summarization and sentiment analysis
	- spaCy for entity extraction
- OCR:
	- Tesseract
- Libraries:
	- pdfplumber
	- python-docx
	- pytesseract
- Others:
	- Uvicorn

## Project Structure

```text
src/
	main.py
	ai/
		entities.py
		sentiment.py
		summary.py
	extractor/
		docx.py
		image.py
		pdf.py
```

- `src/main.py`: FastAPI application entrypoint and `/api/document-analyze` endpoint
- `src/extractor/`: Document text extraction for PDF, DOCX, and image inputs
- `src/ai/`: AI processing for summarization, entity extraction, and sentiment analysis

## Setup Instructions

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

	 ```bash
	 pip install -r requirements.txt
	 ```

4. Install the spaCy model:

	 ```bash
	 python -m spacy download en_core_web_sm
	 ```

5. Install Tesseract OCR and add it to your system PATH.
6. Run the server:

	 ```bash
	 uvicorn src.main:app --reload
	 ```

## API Usage

### Endpoint

`POST /api/document-analyze`

### Headers

```http
x-api-key: sk_track2_987654321
Content-Type: application/json
```

### Request Body Example

```json
{
	"fileName": "sample.pdf",
	"fileType": "pdf",
	"fileBase64": "JVBERi0xLjQKJ..."
}
```

### Response Example

```json
{
	"status": "success",
	"fileName": "sample.pdf",
	"summary": "The document describes a partnership agreement between two organizations.",
	"entities": {
		"names": ["John Carter"],
		"dates": ["January 5, 2026"],
		"organizations": ["Microsoft"],
		"amounts": ["$2.5 million"]
	},
	"sentiment": "Neutral"
}
```

## Approach

The API follows a simple processing pipeline:

1. Validate the API key and required request fields.
2. Decode the Base64 payload and store the file temporarily.
3. Extract text based on file type:
	 - PDF via pdfplumber, with OCR fallback for scanned pages
	 - DOCX via python-docx
	 - Images via pytesseract OCR
4. Normalize and analyze the extracted text.
5. Run summarization, entity extraction, and sentiment analysis.
6. Return structured JSON and remove the temporary file.

### Data Extraction Strategy

- **Summary generation**: The extracted text is normalized and passed to a transformer-based summarization pipeline. If the text is short, the service uses a deterministic sentence-based fallback to avoid low-value model calls. For longer text, input is truncated to a safe token window before summarization to keep processing stable.
- **Entity extraction**: The service uses spaCy `en_core_web_sm` first to identify people, dates, organizations, and monetary values. It then applies regex-based fallback logic for structured names and currency amounts, which improves coverage on forms, invoices, and partially structured documents. Duplicate values are removed and organization strings are cleaned before returning results.
- **Sentiment analysis**: The extracted text is normalized and sent to a transformer sentiment model. The result is mapped to `Positive`, `Negative`, or `Neutral`, with low-confidence outputs defaulting to `Neutral` for safer classification.

Structured text is handled directly by the NLP models and entity rules. Unstructured or partially extracted text is normalized before AI processing. Errors are surfaced through HTTP responses with clear status codes for invalid input, unsupported file types, extraction failures, and unexpected runtime issues.

## Testing

- Use Swagger UI at `/docs` to test the API interactively.
- Validate PDF, DOCX, and image inputs to confirm extraction and AI processing.
- Test edge cases such as invalid Base64 payloads, empty documents, unsupported file types, and missing API keys.

## Notes

- The first request may be slower because AI models are loaded on demand.
- Ensure Tesseract is installed and available on PATH for OCR-based extraction.
