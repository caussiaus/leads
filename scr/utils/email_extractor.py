import re

_RAW_EMAIL = re.compile(
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
)

_OBFUSCATED = re.compile(
    r"([a-zA-Z0-9_.+-]+)\s*(?:\[at\]|\(at\)|\{at\}|\s+at\s+|\s*@\s*)"
    r"\s*([a-zA-Z0-9-]+)\s*(?:\[dot\]|\(dot\)|\{dot\}|\s*dot\s*|\s*\.\s*)"
    r"([a-zA-Z]{2,})",
    re.IGNORECASE,
)

def _normalize(m: re.Match) -> str:
    user = m.group(1)
    domain = m.group(2)
    tld = m.group(3).replace(" dot ", ".").replace("[dot]", ".").replace("(dot)", ".")
    return f"{user}@{domain}.{tld}"

def _is_valid(email: str) -> bool:
    # Must contain exactly one @ and at least one dot after it
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return False
    if len(email) > 254:
        return False
    if any(c in email for c in [' ', '..']):
        return False
    return True

def extract_emails(text: str) -> set:
    raw = set(e.rstrip(".,;:!?") for e in _RAW_EMAIL.findall(text))
    deobf = set(_normalize(m) for m in _OBFUSCATED.finditer(text))
    all_emails = raw.union(deobf)

    return {
        e.lower() for e in all_emails
        if _is_valid(e)
    }
