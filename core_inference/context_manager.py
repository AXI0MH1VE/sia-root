from __future__ import annotations
from dataclasses import dataclass, field
from typing import Deque
from collections import deque

@dataclass
class ContextManager:
    max_turns: int = 24
    turns: Deque[tuple[str, str]] = field(default_factory=deque)

    def add(self, role: str, content: str) -> None:
        self.turns.append((role, content))
        while len(self.turns) > self.max_turns:
            self.turns.popleft()

    def render(self) -> str:
        out = []
        for role, content in self.turns:
            out.append(f"[{role.upper()}]\n{content.strip()}\n")
        return "\n".join(out).strip()
