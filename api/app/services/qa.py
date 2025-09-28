from __future__ import annotations
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
import json
import importlib

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

def _flatten(obj: Any, prefix: str = "") -> List[str]:
    out: List[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            out.extend(_flatten(v, key))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            key = f"{prefix}[{i}]"
            out.extend(_flatten(v, key))
    else:
        out.append(f"{prefix} = {obj}")
    return out

def _load_all_json() -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    for p in DATA_DIR.glob("*.json"):
        try:
            data[p.stem] = json.loads(p.read_text())
        except Exception:
            continue
    return data

def _find_model_request() -> Optional[Callable[..., Any]]:
    candidates = [
        "api.app.services.llm",
        "api.app.services.model",
        "api.app.llm",
        "api.app.model",
        "api.app.orchestrator",
    ]
    for mod in candidates:
        try:
            m = importlib.import_module(mod)
            fn = getattr(m, "model_request", None)
            if callable(fn):
                return fn
        except Exception:
            pass
    return None

def answer(query: str, state: Dict[str, Any]) -> str:
    model_request = _find_model_request()
    if model_request is None:
        return "QA model is not wired: expose a callable `model_request(role, content)` in your swarm stack."

    flat_state = "\n".join(_flatten(state))
    flat_json = "\n".join(_flatten(_load_all_json()))

    prompt = (
        "You are the QA agent in a disaster-response swarm. "
        "Use ONLY the provided scenario data to ground your answer, and reason step-by-step internally. "
        "Respond concisely and clearly. If the user asks 'why', include a short explanation grounded in fields you used.\n\n"
        "Live plan state (key=value):\n"
        f"{flat_state}\n\n"
        "Persisted scenario JSON (key=value):\n"
        f"{flat_json}\n\n"
        "User question:\n"
        f"{query}\n"
    )

    res = model_request(role="user", content=prompt)
    if isinstance(res, dict):
        text = res.get("content") or res.get("text") or res.get("answer") or ""
        return text.strip()
    if isinstance(res, str):
        return res.strip()
    return "No text returned from model_request."
