from functools import lru_cache
import re


DEFAULT_SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def _truncate_by_tokens(text: str, tokenizer, max_tokens: int) -> str:
    if not text:
        return ""

    try:
        token_ids = tokenizer.encode(text, add_special_tokens=False)
        if len(token_ids) <= max_tokens:
            return text
        return tokenizer.decode(token_ids[:max_tokens], skip_special_tokens=True)
    except Exception:
        return text[:max_tokens * 4]


@lru_cache(maxsize=1)
def _get_sentiment_pipeline():
    try:
        from transformers import pipeline

        return pipeline("sentiment-analysis", model=DEFAULT_SENTIMENT_MODEL)
    except Exception:
        return None


def get_sentiment(text: str) -> str:
    text = _normalize_text(text)
    if not text:
        return "Neutral"

    sentiment_pipeline = _get_sentiment_pipeline()
    if sentiment_pipeline is None:
        return "Neutral"

    tokenizer = getattr(sentiment_pipeline, "tokenizer", None)
    truncated_text = _truncate_by_tokens(text, tokenizer, 512) if tokenizer is not None else text[:2048]

    try:
        result = sentiment_pipeline(truncated_text, truncation=True)
    except Exception:
        return "Neutral"

    if not result:
        return "Neutral"

    top_result = result[0]
    label = str(top_result.get("label", "")).upper()
    score = top_result.get("score")

    try:
        confidence = float(score)
    except (TypeError, ValueError):
        confidence = 0.0

    if confidence < 0.65:
        return "Neutral"

    if label in {"LABEL_1", "POSITIVE"}:
        return "Positive"
    if label in {"LABEL_0", "NEGATIVE"}:
        return "Negative"
    return "Neutral"


analyze_sentiment = get_sentiment


if __name__ == "__main__":
    sample_text = (
        "The team delivered the project ahead of schedule and the client was extremely happy with the results. "
        "There were a few minor issues, but overall the feedback was excellent."
    )
    print("Sentiment:", get_sentiment(sample_text))
