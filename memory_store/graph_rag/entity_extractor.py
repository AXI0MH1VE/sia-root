from __future__ import annotations
import re
from dataclasses import dataclass

ENTITY_RE = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b")
PREDICATES = [
    ("acquired", "ACQUIRED"),
    ("sues", "SUES"),
    ("regulates", "REGULATES"),
    ("owns", "OWNS"),
    ("partners with", "PARTNERS_WITH"),
]

@dataclass
class Triplet:
    subject: str
    predicate: str
    obj: str

def extract_entities(text: str) -> list[str]:
    ents = ENTITY_RE.findall(text)
    seen = set()
    out = []
    for e in ents:
        if e not in seen:
            seen.add(e)
            out.append(e)
    return out[:50]

def extract_triplets(text: str) -> list[Triplet]:
    t = text.strip()
    triplets: list[Triplet] = []
    low = t.lower()
    for phrase, pred in PREDICATES:
        if phrase in low:
            parts = re.split(re.escape(phrase), t, flags=re.IGNORECASE)
            if len(parts) >= 2:
                left_ents = extract_entities(parts[0])
                right_ents = extract_entities(parts[1])
                if left_ents and right_ents:
                    triplets.append(Triplet(left_ents[-1], pred, right_ents[0]))
    return triplets
