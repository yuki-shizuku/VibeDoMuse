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
import re
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
        "temperature": s.get("temperature", 0.3),
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + (api_key or s["api_key"]),
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout or s["timeout"]) as r:
            data = json.loads(r.read().decode("utf-8"))
        text = data["choices"][0]["message"]["content"].strip()
        # Strip <thinking>...</thinking> tags (common in some LLM outputs)
        text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.DOTALL).strip()
        # Also strip <Thought>...</Thought> and other common variants
        text = re.sub(r"<[Tt]hought>.*?</[Tt]hought>", "", text, flags=re.DOTALL).strip()
        # Strip <reasoning>...</reasoning> tags
        text = re.sub(r"<reasoning>.*?</reasoning>", "", text, flags=re.DOTALL).strip()
        return text
    except Exception:
        return None


def is_available(base_url=None, model=None, **kw):
    """Quick liveness check: reachable and returns content."""
    return chat("ping", max_tokens=4, timeout=6, base_url=base_url, model=model, **kw) is not None


_SYSTEM = (
    "=== LANGUAGE DETECTION === "
    "First, detect the language of the user's request. "
    "Then rewrite the description into a clear, structured music brief "
    "in that SAME language. "
    "If the user writes in Chinese, your output MUST be in Chinese. "
    "If the user writes in English, your output MUST be in English. "
    "Cover: mood, key, tempo (fast/slow or explicit BPM), instruments, "
    "number of voices, and texture style. "
    "No explanation, at most 60 words. "
    "Do NOT include <thinking> tags."
)


def refine_intent(text, **kw):
    """Rewrite a free-form description into a structured Chinese music brief; None on failure."""
    if not text or not text.strip():
        return None
    out = chat(text, system=_SYSTEM, max_tokens=120, timeout=15, **kw)
    if out and len(out) > 2:
        return out
    return None


def analyze_intent(text, knowledge_context=None):
    """First-stage: send the user's prompt to LLM for intent analysis.

    The LLM thinks about the request, considers what knowledge/templates
    would be relevant, and outputs a natural-language understanding paragraph.
    Returns the analysis text, or None on failure.
    """
    from . import knowledge as kb
    prompt = kb.build_analysis_prompt(text)
    user_msg = prompt["user"]
    if knowledge_context:
        user_msg += "\n\n" + str(knowledge_context)
    out = chat(user_msg, system=prompt["system"], max_tokens=600, timeout=60)
    if out and len(out) > 10:
        return out
    return None


def generate_with_understanding(text, analysis, knowledge_context=None):
    """Second-stage: send original prompt + analysis to LLM for JSON generation.

    Returns the raw LLM output (JSON string), or None on failure.
    """
    from . import knowledge as kb
    prompt = kb.build_generation_prompt(text, analysis)
    user_msg = prompt["user"]
    if knowledge_context:
        user_msg += "\n\n" + str(knowledge_context)
    out = chat(user_msg, system=prompt["system"], max_tokens=4000, timeout=180)
    return out
