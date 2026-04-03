import re
from typing import Dict, List


MONEY_PATTERN = re.compile(r"[₹$€]\s?\d+(?:,\d+)*(?:.\d+)?")
NAME_PATTERN = re.compile(
    r"(?:To|From|Client|Buyer)\s*:?\s*\n?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
    re.IGNORECASE,
)
DATE_PATTERN = re.compile(
    r"\b(?:"
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s*\d{4}"
    r"|\d{1,2}/\d{1,2}/\d{4}"
    r")\b",
    re.IGNORECASE,
)
ORG_PATTERN = re.compile(
    r"\b([A-Z][A-Za-z0-9&.,'-]*(?:\s+[A-Z][A-Za-z0-9&.,'-]*)*\s+(?:Pvt\s+Ltd|Ltd|Inc|Company|Corp))\b"
)
TRAILING_FIELD_LABEL_PATTERN = re.compile(r"\s+(?:To|From|Client|Buyer|Date|Amount)\s*$", re.IGNORECASE)


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def _empty_entity_result() -> Dict[str, List[str]]:
    return {
        "names": [],
        "dates": [],
        "organizations": [],
        "amounts": [],
    }


def _add_unique(items: List[str], seen: set[str], value: str) -> None:
    normalized = _normalize_text(value)
    if not normalized:
        return

    marker = normalized.lower()
    if marker in seen:
        return

    seen.add(marker)
    items.append(normalized)


def _clean_name(value: str) -> str:
    cleaned = _normalize_text(value)
    while True:
        updated = TRAILING_FIELD_LABEL_PATTERN.sub("", cleaned)
        if updated == cleaned:
            return cleaned
        cleaned = updated


def extract_entities(text: str) -> Dict[str, List[str]]:
    text = _normalize_text(text)
    if not text:
        return _empty_entity_result()

    result = _empty_entity_result()
    seen = {key: set() for key in result}

    for match in NAME_PATTERN.finditer(text):
        _add_unique(result["names"], seen["names"], _clean_name(match.group(1)))

    for match in DATE_PATTERN.finditer(text):
        _add_unique(result["dates"], seen["dates"], match.group(0))

    for match in ORG_PATTERN.finditer(text):
        _add_unique(result["organizations"], seen["organizations"], match.group(1))

    for match in MONEY_PATTERN.finditer(text):
        _add_unique(result["amounts"], seen["amounts"], match.group(0))

    return result


if __name__ == "__main__":
    sample_text = (
        "John Carter met with Microsoft on January 5, 2026 to discuss a $2.5 million investment. "
        "The agreement was later reviewed by Sarah Kim at OpenAI."
    )
    print("Entities:", extract_entities(sample_text))
