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

    text_lower = text.lower()

    positive_words = [
        "good",
        "success",
        "happy",
        "growth",
        "excellent",
        "positive",
        "profit",
        "improved",
    ]
    negative_words = [
        "bad",
        "loss",
        "error",
        "failure",
        "negative",
        "issue",
        "decline",
        "problem",
    ]

    words_in_text = set(re.findall(r"\b\w+\b", text_lower))

    if any(word in words_in_text for word in positive_words):
        return "Positive"
    if any(word in words_in_text for word in negative_words):
        return "Negative"
    return "Neutral"


analyze_sentiment = get_sentiment


if __name__ == "__main__":
    sample_text = (
        "The team delivered the project ahead of schedule and the client was extremely happy with the results. "
        "There were a few minor issues, but overall the feedback was excellent."
    )
    print("Sentiment:", get_sentiment(sample_text))
