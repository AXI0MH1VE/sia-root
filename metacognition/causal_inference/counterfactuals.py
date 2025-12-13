from __future__ import annotations

def summarize_estimate(estimate) -> str:
    try:
        return f"Estimated causal effect: {estimate.value}"
    except Exception:
        return str(estimate)
