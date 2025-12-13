from __future__ import annotations
from dataclasses import dataclass
import os
import requests
from pydantic import BaseModel, Field

class InferenceRequest(BaseModel):
    prompt: str
    max_tokens: int = Field(default=512, ge=1, le=4096)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    stop: list[str] | None = None

@dataclass
class LlamaCppClient:
    url: str

    def complete(self, req: InferenceRequest) -> str:
        payload = {
            "prompt": req.prompt,
            "n_predict": req.max_tokens,
            "temperature": req.temperature,
            "top_p": req.top_p,
        }
        if req.stop:
            payload["stop"] = req.stop
        r = requests.post(self.url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        if "content" in data and isinstance(data["content"], str):
            return data["content"]
        if "choices" in data and data["choices"]:
            ch = data["choices"][0]
            return ch.get("text", "") or ch.get("content", "")
        if "text" in data and isinstance(data["text"], str):
            return data["text"]
        return str(data)

def load_inference_client() -> LlamaCppClient:
    url = os.getenv("LLAMA_CPP_URL", "http://127.0.0.1:8080/completion")
    return LlamaCppClient(url=url)
