# -*- coding: utf-8 -*-
"""
VibeDoMuse · json_writer.py
LLM JSON-writing layer: with the knowledge-base context (spec excerpts +
real template examples), the model directly writes a Do-muse JSON score;
the result is then extracted locally.
"""
import json
import re

from . import llm_client


def extract_json(raw):
    """Robustly extract a JSON object from raw LLM output; None on failure."""
    if not raw or not raw.strip():
        return None
    text = raw.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if m:
        text = m.group(1).strip()
    i, j = text.find("{"), text.rfind("}")
    if i != -1 and j > i:
        text = text[i:j + 1]
    try:
        return json.loads(text)
    except Exception:
        # retry with trailing commas removed
        try:
            fixed = re.sub(r",\s*([}\]])", r"\1", text)
            return json.loads(fixed)
        except Exception:
            return None


def write_score(text, prompt=None, max_tokens=4000, timeout=180, attempts=2):
    """Let the LLM write a score JSON (0.3B output is unstable, retry once).

    Returns (score_dict, error).
    """
    if prompt is None:
        from . import knowledge
        prompt = knowledge.build_prompt(text)
    last_err = "LLM no response or endpoint unavailable"
    for i in range(max(1, attempts)):
        user = prompt["user"]
        if i > 0:
            user += ("\n\n(NOTE: the previous output was incomplete or invalid. "
                     "Output a complete, valid JSON following the same requirements as before. "
                     "Make sure all braces are closed and the JSON is parseable. "
                     "Do NOT include <thinking> or any reasoning tags in your output.)")
        raw = llm_client.chat(user, system=prompt["system"], max_tokens=max_tokens, timeout=timeout)
        if not raw:
            last_err = "LLM no response or endpoint unavailable"
            continue
        score = extract_json(raw)
        if score is not None:
            return score, None
        last_err = "LLM output could not be parsed as JSON: " + raw[:160]
    return None, last_err
