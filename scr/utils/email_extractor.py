import re

_RAW_EMAIL  = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
_OBFUSCATED = re.compile(
    r"([a-zA-Z0-9_.+-]+)\s*(?:\[at\]|\(at\)|\{at\}|\s+at\s+|\s*@\s*)"
    r"\s*([a-zA-Z0-9-]+)\s*(?:\[dot\]|\(dot\)|\{dot\}|\s*dot\s*|\s*\.\s*)"
    r"([a-zA-Z0-9-.]+)",
    re.IGNORECASE
)

def _normalize(m: re.Match):
    user, host, tld = m.group(1), m.group(2), m.group(3)
    tld = tld.replace(" dot ", ".").replace("[dot]", ".").replace("(dot)", ".")
    return f"{user}@{host}.{tld}"

def extract_emails(text: str):
    found = set(_RAW_EMAIL.findall(text))
    for m in _OBFUSCATED.finditer(text):
        found.add(_normalize(m))
    return found
