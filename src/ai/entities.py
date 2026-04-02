from functools import lru_cache
import re
from typing import Dict, List


ENTITY_KEYS = {
    "PERSON": "names",
    "DATE": "dates",
    "ORG": "organizations",
    "MONEY": "amounts",
}

INVALID_DATES = {"today", "yesterday", "tomorrow"}
MONEY_PATTERN = re.compile(r"[₹$€]\s?\d+(?:,\d+)*(?:\.\d+)?", re.IGNORECASE)
STRUCTURED_NAME_PATTERN = re.compile(
    r"(?:To|From|Client|Buyer)\s*:?\s*\n?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+?)(?=\s+[A-Z][A-Za-z ]{1,40}\s*:|$)",
    re.IGNORECASE,
)
ORG_SUFFIX_PATTERN = re.compile(r"\b(?:Pvt\s+Ltd|Ltd|Inc|LLC|Corp|Corporation|Company)\b", re.IGNORECASE)
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


def _normalize_money(value: str) -> str:
    value = _normalize_text(value)
    return re.sub(r"([₹$€])\s+", r"\1", value)


def _amount_key(value: str) -> str:
    return re.sub(r"[^\d.]", "", value)


def _add_unique(items: List[str], seen: set[str], value: str) -> None:
    normalized = _normalize_text(value)
    if not normalized:
        return

    marker = normalized.lower()
    if marker in seen:
        return

    seen.add(marker)
    items.append(normalized)


def _merge_amount(items: List[str], seen: dict[str, str], value: str) -> None:
    normalized = _normalize_money(value)
    if not normalized:
        return

    key = _amount_key(normalized)
    if not key:
        return

    existing = seen.get(key)
    if existing is None:
        seen[key] = normalized
        items.append(normalized)
        return

    existing_has_symbol = bool(re.match(r"^[₹$€]", existing))
    candidate_has_symbol = bool(re.match(r"^[₹$€]", normalized))
    if candidate_has_symbol and not existing_has_symbol:
        index = items.index(existing)
        items[index] = normalized
        seen[key] = normalized


def _looks_like_organization(value: str) -> bool:
    return bool(ORG_SUFFIX_PATTERN.search(value))


def _is_valid_structured_name(value: str) -> bool:
    normalized = _normalize_text(value)
    parts = normalized.split()
    if len(parts) < 2:
        return False

    if _looks_like_organization(normalized):
        return False

    for part in parts:
        if not re.fullmatch(r"[A-Z][a-z]+(?:[-'][A-Z][a-z]+)?", part):
            return False

    return True


def _extract_structured_names(text: str) -> List[str]:
    names: List[str] = []
    seen: set[str] = set()

    for match in STRUCTURED_NAME_PATTERN.finditer(text):
        value = _normalize_text(match.group(1))
        if not _is_valid_structured_name(value):
            continue

        marker = value.lower()
        if marker in seen:
            continue

        seen.add(marker)
        names.append(value)

    return names


def _clean_organization_value(value: str) -> str:
    cleaned = _normalize_text(value)
    while True:
        updated = TRAILING_FIELD_LABEL_PATTERN.sub("", cleaned)
        if updated == cleaned:
            return cleaned
        cleaned = updated


@lru_cache(maxsize=1)
def _get_nlp():
    try:
        import spacy

        return spacy.load("en_core_web_sm")
    except Exception:
        return None


def extract_entities(text: str) -> Dict[str, List[str]]:
    text = _normalize_text(text)
    if not text:
        return _empty_entity_result()

    nlp = _get_nlp()
    if nlp is None:
        return _empty_entity_result()

    try:
        doc = nlp(text)
    except Exception:
        return _empty_entity_result()

    result = _empty_entity_result()
    seen = {key: set() for key in result if key != "amounts"}
    amount_seen: dict[str, str] = {}

    for match in MONEY_PATTERN.finditer(text):
        _merge_amount(result["amounts"], amount_seen, match.group(0))

    for entity in doc.ents:
        target_key = ENTITY_KEYS.get(getattr(entity, "label_", ""))
        if not target_key:
            continue

        value = _normalize_text(entity.text)
        if not value:
            continue

        if target_key == "dates" and value.lower() in INVALID_DATES:
            continue

        if target_key == "amounts":
            _merge_amount(result["amounts"], amount_seen, value)
            continue

        if target_key == "organizations":
            value = _clean_organization_value(value)
            if not value:
                continue

        marker = value.lower()
        if marker in seen[target_key]:
            continue

        _add_unique(result[target_key], seen[target_key], value)

    for name in _extract_structured_names(text):
        _add_unique(result["names"], seen["names"], name)

    return result


if __name__ == "__main__":
    sample_text = (
        "John Carter met with Microsoft on January 5, 2026 to discuss a $2.5 million investment. "
        "The agreement was later reviewed by Sarah Kim at OpenAI."
    )
    print("Entities:", extract_entities(sample_text))
