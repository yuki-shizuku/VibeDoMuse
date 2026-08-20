# -*- coding: utf-8 -*-
"""
VibeDoMuse · llm_client.py
Lightweight client for a local LLM (OpenAI-compatible /v1/chat/completions).

API configuration is entered by the user in the GUI (Settings -> LLM Settings)
and stored in plaintext in config.ini at the project root
(see vibedomuse/config.py; the file is auto-created with defaults if missing).

For testing only: the model is small (e.g. baidu.ernie-4.5-0.3b-base-pt) and is
not used for serious production work. It assists by writing/rewriting, and any
failure gracefully falls back to the rule engine (nl_parser).
"""
import json
import urllib.request

from . import config as _cfg


def _settings():
    return _cfg.get_llm_settings()


def chat(prompt, system=None, max_tokens=256, timeout=None,
         base_url=None, model=None, api_key=None):
    """Call the local chat/completions endpoint; return text on success, None on failure.

    When not passed explicitly, base_url / model / api_key / timeout are read
    from config.ini.
    """
    s = _settings()
    base = (base_url or s["base_url"]).rstrip("/")
    url = base + "/chat/completions"
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload = json.dumps({
        "model": model or s["model"],
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + (api_key or s["api_key"] or "test-key"),
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout or s["timeout"]) as r:
            data = json.loads(r.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def is_available(base_url=None, model=None, **kw):
    """Quick liveness check: reachable and returns content."""
    return chat("ping", max_tokens=4, timeout=6, base_url=base_url, model=model, **kw) is not None


_SYSTEM = (
    "You are a music request analyst. The user describes the background music they "
    "want, in Chinese or English. Rewrite the description into a clear, structured "
    "music brief: mood, key, tempo (fast/slow or explicit BPM), instruments, number "
    "of voices, and texture style. Output only the rewritten brief in the same "
    "language as the user's request, no explanation, at most 60 words."
)


def refine_intent(text, **kw):
    """Rewrite a free-form description into a structured Chinese music brief; None on failure."""
    if not text or not text.strip():
        return None
    out = chat(text, system=_SYSTEM, max_tokens=120, timeout=15, **kw)
    if out and len(out) > 2:
        return out
    return None
