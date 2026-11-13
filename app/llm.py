"""Optional language-model reader. It turns a messy message into facts; it never writes advice.

Merge rule ("monotone"): the model can ADD a danger sign, a snake mention or a thing
already done, but it can never remove anything the keyword parser found. If the model
is slow, down, unconfigured or returns anything off-schema, the keyword facts are used.
"""
from __future__ import annotations

import json
import os
import time

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout

import httpx

from .content import RED_FLAGS
from .parser import Facts

PROVIDER_URL = os.environ.get("DANSH_LLM_URL", "https://api.anthropic.com/v1/messages")
MODEL = os.environ.get("DANSH_LLM_MODEL", "claude-haiku-4-5")
TIMEOUT = float(os.environ.get("DANSH_LLM_TIMEOUT", "2.5"))  # total wall-clock budget, enforced below
_pool = ThreadPoolExecutor(max_workers=4)

BOOL_KEYS = ["snake", "bite", "unknown_bite", "occult_krait", "prevention", "self_harm", "swelling",
             "done_tourniquet", "done_cut", "done_healer", "done_ate", "done_walked", "done_catch", "child", "pregnant"]

SYSTEM = (
    "You read one message about a possible snakebite in India (English, Hindi or Hinglish) and output ONLY a JSON "
    "object. You do not give advice. Keys: " + ", ".join(BOOL_KEYS) + " (booleans); red_flags (array, values from "
    + json.dumps(list(RED_FLAGS)) + "); other_animal (string or null); minutes_since (integer or null); "
    "state (Indian state, lowercase, or null). Set a boolean true only if the message says so or clearly implies "
    "it. occult_krait = symptoms after sleeping on the floor / at night with no bite seen. A red flag is a symptom "
    "the message reports as present now (not denied)."
)


def enabled() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def read(message: str) -> tuple[dict | None, dict]:
    """Returns (facts_dict_or_None, meta). Never blocks longer than TIMEOUT seconds in total."""
    fut = _pool.submit(_read, message)
    try:
        return fut.result(timeout=TIMEOUT)
    except FutureTimeout:
        return None, {"provider": "anthropic", "model": None, "ok": False, "ms": int(TIMEOUT * 1000),
                      "error": "deadline"}


def _read(message: str) -> tuple[dict | None, dict]:
    meta = {"provider": "anthropic", "model": None, "ok": False, "ms": 0}
    if not enabled():
        meta["provider"] = None
        return None, meta
    t0 = time.time()
    try:
        r = httpx.post(
            PROVIDER_URL,
            headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
            json={"model": MODEL, "max_tokens": 300, "system": SYSTEM, "temperature": 0,
                  "messages": [{"role": "user", "content": message[:1500]}]},
            timeout=TIMEOUT,
        )
        meta["ms"] = int((time.time() - t0) * 1000)
        r.raise_for_status()
        body = r.json()
        meta["model"] = body.get("model")  # record which model actually answered
        txt = "".join(b.get("text", "") for b in body.get("content", []) if b.get("type") == "text")
        start, end = txt.find("{"), txt.rfind("}")
        data = json.loads(txt[start:end + 1])
        meta["ok"] = isinstance(data, dict)
        return (data if meta["ok"] else None), meta
    except Exception as e:  # noqa: BLE001 - any failure falls back to keywords
        meta["ms"] = int((time.time() - t0) * 1000)
        meta["error"] = type(e).__name__
        return None, meta


def merge(base: Facts, extra: dict | None) -> tuple[Facts, list[str]]:
    """Monotone merge. Returns the merged facts and a list of what the model added."""
    added: list[str] = []
    if not extra:
        return base, added
    for k in BOOL_KEYS:
        if extra.get(k) is True and not getattr(base, k):
            setattr(base, k, True)
            added.append(k)
    for flag in extra.get("red_flags") or []:
        if flag in RED_FLAGS and flag not in base.red_flags and flag not in base.negated:
            base.red_flags.append(flag)
            added.append(f"red_flag:{flag}")
    # other_animal is deliberately NOT taken from the model: it would move a message away from the
    # snakebite protocol (less care), which the model is never allowed to do.
    if base.minutes_since is None and isinstance(extra.get("minutes_since"), int) and 0 <= extra["minutes_since"] < 10080:
        base.minutes_since = extra["minutes_since"]
        added.append("minutes_since")
    if not base.state and isinstance(extra.get("state"), str):
        base.state = extra["state"].strip().lower()[:40] or None
        if base.state:
            added.append("state")
    return base, added
