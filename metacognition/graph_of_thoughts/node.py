from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import uuid
import time

@dataclass
class ThoughtNode:
    content: str
    parent_id: str | None = None
    node_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    score: float = 0.0
    meta: dict[str, Any] = field(default_factory=dict)
    created_ts: float = field(default_factory=time.time)
