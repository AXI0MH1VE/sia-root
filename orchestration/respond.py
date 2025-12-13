from __future__ import annotations
from core_inference.model_loader import load_inference_client, InferenceRequest

SYSTEM_PROMPT = """You are SIA (Strategic Insider Assistant).
Rules:
- Be precise and operational.
- If evidence is missing, say what's missing and propose how to obtain it.
- Do NOT claim you accessed external systems unless the provided context includes it.
- Prefer structured outputs: bullets, checklists, and concise decision points.
"""

def respond_node(state):
    client = load_inference_client()
    retrieved = state.get("retrieved", {})
    plan = state.get("plan", "")

    context_parts = []
    if retrieved:
        context_parts.append("## Retrieved Memory\n" + str(retrieved))
    if plan:
        context_parts.append("## GoT Plan\n" + plan)

    ctx = "\n\n".join(context_parts).strip()

    prompt = f"""{SYSTEM_PROMPT}

User query:
{state['user_query']}

{ctx}

Now produce the best answer."""

    text = client.complete(InferenceRequest(prompt=prompt, max_tokens=700, temperature=0.2))
    state["response"] = text.strip()
    return state
