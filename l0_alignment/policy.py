from __future__ import annotations
from dataclasses import dataclass
import re

DEFAULT_BLOCKLIST = [
    r"\b(passwords?|api[-_ ]?keys?|private key|seed phrase)\b",
    r"\b(exfiltrate|steal|dump|leak)\b",
    r"\b(delete|rm -rf|format disk)\b",
    r"\b(insider trading|market manipulation|fraud)\b", # Added financial/legal risks
]

@dataclass
class L0Decision:
    allowed: bool
    reason: str = ""
    sanitized: str = ""

class L0Policy:
    """
    The L0 Alignment Policy (Temple) is the first line of defense, ensuring
    both user input and system output adhere to safety and ethical guidelines.
    It is designed to be deterministic and "fail closed."
    """
    def __init__(self, block_patterns: list[str] | None = None):
        self.block_patterns = [re.compile(p, re.IGNORECASE) for p in (block_patterns or DEFAULT_BLOCKLIST)]
        # A separate, stricter blocklist for system output
        self.output_block_patterns = [
            re.compile(r"\b(execute|run|shell|command|system call)\b", re.IGNORECASE),
            re.compile(r"\b(harm|damage|destroy|attack)\b", re.IGNORECASE),
        ]

    def sanitize_input(self, text: str) -> str:
        """Removes control characters and normalizes whitespace."""
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def check_input(self, text: str) -> L0Decision:
        """Checks user input against the blocklist."""
        s = self.sanitize_input(text)
        for pat in self.block_patterns:
            if pat.search(s):
                return L0Decision(False, reason=f"Blocked by L0 policy pattern: {pat.pattern}", sanitized=s)
        return L0Decision(True, reason="Allowed", sanitized=s)

    def check_output(self, text: str) -> L0Decision:
        """Checks system output against a stricter blocklist."""
        s = self.sanitize_input(text)
        
        # Check against the general blocklist
        for pat in self.block_patterns:
            if pat.search(s):
                return L0Decision(False, reason=f"Blocked by L0 policy (output) pattern: {pat.pattern}", sanitized=s)

        # Check against the stricter output blocklist
        for pat in self.output_block_patterns:
            if pat.search(s):
                return L0Decision(False, reason=f"Blocked by L0 policy (output command) pattern: {pat.pattern}", sanitized=s)

        return L0Decision(True, reason="Output allowed", sanitized=s)
