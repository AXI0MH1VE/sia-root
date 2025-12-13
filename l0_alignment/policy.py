from __future__ import annotations
from dataclasses import dataclass
import re

DEFAULT_BLOCKLIST = [
    r"\b(passwords?|api[-_ ]?keys?|private key|seed phrase)\b",
    r"\b(exfiltrate|steal|dump|leak)\b",
    r"\b(delete|rm -rf|format disk)\b",
]

@dataclass
class L0Decision:
    allowed: bool
    reason: str = ""
    sanitized: str = ""

class L0Policy:
    def __init__(self, block_patterns: list[str] | None = None):
        self.block_patterns = [re.compile(p, re.IGNORECASE) for p in (block_patterns or DEFAULT_BLOCKLIST)]

    def sanitize_input(self, text: str) -> str:
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def check_input(self, text: str) -> L0Decision:
        s = self.sanitize_input(text)
        for pat in self.block_patterns:
            if pat.search(s):
                return L0Decision(False, reason=f"Blocked by L0 policy pattern: {pat.pattern}", sanitized=s)
        return L0Decision(True, reason="Allowed", sanitized=s)

    def check_output(self, text: str) -> L0Decision:
        s = self.sanitize_input(text)
        return L0Decision(True, reason="Output allowed", sanitized=s)
