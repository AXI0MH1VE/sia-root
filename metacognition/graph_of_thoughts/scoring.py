from __future__ import annotations
from dataclasses import dataclass

@dataclass
class HeuristicScorer:
    risk_words: tuple[str, ...] = ("illegal", "bribe", "insider trading", "exfiltrate", "fraud")
    clarity_words: tuple[str, ...] = ("because", "therefore", "tradeoff", "risk", "mitigation", "assumption")

    def score(self, text: str) -> float:
        t = text.lower()
        risk_pen = sum(1 for w in self.risk_words if w in t) * 1.5
        clarity = sum(1 for w in self.clarity_words if w in t) * 0.5
        length = min(len(text) / 800.0, 1.0)
        return float(0.5 + clarity + length - risk_pen)
