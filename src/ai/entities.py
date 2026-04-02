from typing import Dict, List


def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extract named entities from text.

    Placeholder implementation for entity extraction.
    """
    if not text:
        return {}
    return {"PERSON": [], "ORG": [], "LOCATION": []}
