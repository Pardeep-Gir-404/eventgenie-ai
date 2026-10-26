import re
from typing import Tuple

BLOCKED_PATTERNS = [
    r"\b(bomb|weapon|explosive|firearm|assault|narcotic|heroin|cocaine|meth|kidnap|riot|extortion)\b",
    r"\b(hate\s*speech|racist|terrorist|jihad|extremist|white\s*supremac)\b",
    r"\b(ignore\s+(all\s+)?previous\s+instructions)\b",
    r"\b(system\s+prompt\s+override)\b",
    r"\b(jailbreak|dan\s+mode)\b",
]

COMPILED_BLOCKED = [re.compile(p, re.IGNORECASE) for p in BLOCKED_PATTERNS]

def sanitize_text(text: str, max_chars: int = 500) -> str:
    """Sanitizes text by stripping harmful markup, excessive whitespace, and capping length."""
    if not text:
        return ""
    # Strip script tags or html tags
    cleaned = re.sub(r"<[^>]+>", " ", text)
    # Strip dangerous curly braces or prompt delimiters
    cleaned = re.sub(r"[\{\}\[\]\<\>]", " ", cleaned)
    # Normalize spaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:max_chars]

def check_event_safety(city: str, theme: str = "", special_requests: str = "", cultural_prefs: str = "") -> Tuple[bool, str]:
    """
    Validates user inputs against safety guardrails.
    Returns (is_safe, error_message).
    """
    combined = f"{city} {theme} {special_requests} {cultural_prefs}"
    
    for pat in COMPILED_BLOCKED:
        if pat.search(combined):
            return False, "This request contains content that violates EventGenie AI's safety guidelines. Please submit an appropriate celebratory or community event."
            
    return True, ""
