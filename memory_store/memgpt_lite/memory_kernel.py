from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import numpy as np
import lancedb
import json

@dataclass
class MemoryHit:
    text: str
    score: float
    meta: dict[str, Any]

class LanceMemory:
    def __init__(self, path: str):
        self.db = lancedb.connect(path)
        if "documents" not in self.db.table_names():
            self.table = self.db.create_table(
                "documents",
                schema={
                    "id": "string",
                    "text": "string",
                    "embedding": "vector<float32>",
                    "meta": "string",
                },
                mode="create",
            )
        else:
            self.table = self.db.open_table("documents")

    def upsert(self, doc_id: str, text: str, embedding: np.ndarray, meta: dict[str, Any] | None = None) -> None:
        meta_s = json.dumps(meta or {}, ensure_ascii=False)
        self.table.add([{
            "id": doc_id,
            "text": text,
            "embedding": embedding.astype(np.float32).tolist(),
            "meta": meta_s,
        }], mode="append")

    def search(self, embedding: np.ndarray, k: int = 5) -> list[MemoryHit]:
        res = self.table.search(embedding.astype(np.float32).tolist()).limit(k).to_list()
        hits = []
        for r in res:
            meta = {}
            try:
                meta = json.loads(r.get("meta", "{}"))
            except Exception:
                meta = {}
            hits.append(MemoryHit(text=r["text"], score=float(r.get("_distance", 0.0)), meta=meta))
        return hits
