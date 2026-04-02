from functools import lru_cache
import re


DEFAULT_SUMMARY_MODEL = "sshleifer/distilbart-cnn-12-6"


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
        approximate_limit = max_tokens * 4
        return text[:approximate_limit]


def _split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def _fallback_summary(text: str) -> str:
    sentences = _split_sentences(text)
    if not sentences:
        return ""

    if len(sentences) == 1:
        words = sentences[0].split()
        if len(words) <= 1:
            return sentences[0][: max(1, len(sentences[0]) - 1)]
        keep_words = max(1, min(40, len(words) - 1))
        return " ".join(words[:keep_words]).strip()

    if len(sentences) == 2:
        return sentences[0]

    return " ".join(sentences[:2]).strip()


@lru_cache(maxsize=1)
def _get_summarizer():
    try:
        from transformers import pipeline

        return pipeline("summarization", model=DEFAULT_SUMMARY_MODEL)
    except Exception:
        return None


def summarize(text: str) -> str:
    text = _normalize_text(text)
    if not text:
        return ""

    return _fallback_summary(text)


summarize_text = summarize


if __name__ == "__main__":
    sample_text = (
        "Acme Corporation announced a new partnership with OpenAI on March 12, 2026. "
        "The contract is valued at $4.8 million and will support product development in New York. "
        "Chief Executive Officer Maria Lopez said the initiative will create new jobs and expand global reach."
    )
    print("Summary:", summarize(sample_text))
