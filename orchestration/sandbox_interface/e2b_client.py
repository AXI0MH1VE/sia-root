from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass
class E2BResult:
    ok: bool
    stdout: str = ""
    stderr: str = ""

class E2BClient:
    def __init__(self):
        self.api_key = os.getenv("E2B_API_KEY", "")

    def enabled(self) -> bool:
        return bool(self.api_key)

    def run_python(self, code: str) -> E2BResult:
        if not self.enabled():
            return E2BResult(False, stderr="E2B is not configured (missing E2B_API_KEY).")
        from e2b import Sandbox  # requires `pip install e2b`
        sb = Sandbox(api_key=self.api_key)
        try:
            exec_res = sb.run_code(code, language="python")
            return E2BResult(True, stdout=exec_res.stdout or "", stderr=exec_res.stderr or "")
        finally:
            sb.close()
