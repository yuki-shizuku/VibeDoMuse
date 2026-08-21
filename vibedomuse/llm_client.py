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

Streaming + inactivity timeout
------------------------------
The request is always sent with ``stream=True`` and the response is consumed
incrementally (token by token). The configured ``timeout`` is interpreted as an
**inactivity** timeout:

  * A generous grace period is allowed for the model to emit its FIRST token
    (cold model load / prefill). We must not trip the timeout while the model
    is merely "thinking" and has not produced output yet.
  * Once the first token arrives, the socket read timeout is tightened to
    ``timeout``. If no NEW token is produced for ``timeout`` seconds, the call
    is considered timed out and returns ``None``.

This replaces the old "total wall-clock budget" semantics — a model that
streams tokens continuously never trips the timeout no matter how long it runs,
but a stalled stream (no output for ``timeout`` seconds) is detected promptly.
"""
import json
import logging
import re
import socket
import time
import urllib.error
import urllib.request

from . import config as _cfg

log = logging.getLogger(__name__)


def _settings():
    return _cfg.get_llm_settings()


def _extract_content(obj):
    """Pull the text content out of one SSE JSON event.

    Prefers the streaming ``delta.content`` shape; falls back to a
    single-event ``message.content`` shape. Returns None when the event
    carries no text (e.g. role/finish_reason-only events).
    """
    try:
        choices = obj["choices"]
        if not choices:
            return None
        ch = choices[0]
        delta = ch.get("delta")
        if isinstance(delta, dict) and delta.get("content"):
            return delta["content"]
        msg = ch.get("message")
        if isinstance(msg, dict) and msg.get("content"):
            return msg["content"]
    except Exception:
        return None
    return None


def chat(prompt, system=None, max_tokens=256, timeout=None,
         base_url=None, model=None, api_key=None, on_token=None):
    """Call the local chat/completions endpoint; return text on success, None on failure.

    ``on_token`` (optional callable) is invoked with each streamed text chunk
    as it arrives, enabling real-time UI streaming; it does not change the
    returned value.

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
        "stream": True,   # always request streaming output
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + (api_key or s["api_key"]),
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
    })

    to = float(timeout or s["timeout"])

    try:
        # `to` only bounds the initial connect + headers round-trip (fast on
        # localhost). The per-token inactivity timeout is enforced inside
        # _read_sse, which also grants a generous first-token grace period.
        with urllib.request.urlopen(req, timeout=to) as r:
            ctype = r.headers.get("Content-Type", "")
            if "text/event-stream" in ctype:
                text = _read_sse(r, on_token=on_token, timeout=to)
            else:
                # Server ignored `stream` and returned a single JSON object.
                # One-shot parse (still socket-timeout bounded). This is a
                # server limitation, not the streaming path — LM Studio / OAI-
                # compatible servers return SSE and never hit this branch.
                log.info("LLM endpoint returned non-SSE response (Content-Type=%r); "
                         "parsing single JSON object (streaming unavailable).", ctype)
                text = _read_one_shot(r)
        if not text or not text.strip():
            return None
        # Strip <thinking>...</thinking> tags (common in some LLM outputs)
        text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.DOTALL).strip()
        # Also strip <Thought>...</Thought> and other common variants
        text = re.sub(r"<[Tt]hought>.*?</[Tt]hought>", "", text, flags=re.DOTALL).strip()
        # Strip <reasoning>...</reasoning> tags
        text = re.sub(r"<reasoning>.*?</reasoning>", "", text, flags=re.DOTALL).strip()
        return text
    except urllib.error.HTTPError as e:
        log.error("LLM HTTP error %s for %s", e.code, url)
        return None
    except socket.timeout:
        log.error("LLM timed out after %ss (inactivity) for %s", to, url)
        return None
    except Exception as e:
        log.error("LLM request failed: %s", e)
        return None


def _read_sse(resp, on_token=None, timeout=None):
    """Parse an SSE stream, accumulating assistant content deltas.

    Timeout policy (see module docstring):
      * Before the first token: a generous grace period (first_grace) is allowed
        for model prefill / load. We keep waiting, but never forever — once the
        grace elapses with no token, we raise (dead server).
      * After the first token: the socket read timeout is tightened to
        ``timeout``. A gap longer than ``timeout`` between tokens raises a
        socket.timeout (true inactivity timeout), which chat() turns into None.
    """
    timeout = float(timeout or 30)
    # Generous grace for the model to emit the FIRST token (cold load / prefill).
    first_grace = min(max(timeout, 30.0), 120.0)

    sock = getattr(resp, "_sock", None)
    if sock is not None:
        try:
            sock.settimeout(first_grace)
        except Exception:
            sock = None

    parts = []
    last_token = None
    streaming = False
    first_deadline = time.monotonic() + first_grace

    while True:
        try:
            raw = resp.readline()
        except socket.timeout:
            if streaming:
                # A gap longer than `timeout` between tokens => inactivity.
                raise socket.timeout("no token received for %.0fs" % timeout)
            if time.monotonic() > first_deadline:
                raise socket.timeout("no first token within %.0fs" % first_grace)
            # Still within the grace period (model thinking) -> keep waiting.
            continue
        except Exception:
            # Any other read error aborts the stream.
            break

        if not raw:
            break  # stream closed / EOF

        line = raw.decode("utf-8", "replace").strip()
        # Skip blank lines and SSE keep-alive comments (": ping").
        if not line or line.startswith(":"):
            continue
        if not line.startswith("data:"):
            continue

        data = line[len("data:"):].strip()
        if data == "[DONE]":
            break

        try:
            obj = json.loads(data)
        except Exception:
            continue

        delta = _extract_content(obj)
        if delta:
            parts.append(delta)
            last_token = time.monotonic()
            if not streaming:
                streaming = True
                # First token arrived: tighten socket timeout to the inactivity
                # window so a stall is detected within `timeout` seconds.
                if sock is not None:
                    try:
                        sock.settimeout(timeout)
                    except Exception:
                        pass
            if on_token is not None:
                try:
                    on_token(delta)
                except Exception:
                    pass

    return "".join(parts)


def _read_one_shot(resp):
    """Fallback for a non-SSE response: read the full body and extract text."""
    try:
        body = resp.read().decode("utf-8", "replace")
        data = json.loads(body)
        return data["choices"][0]["message"]["content"]
    except Exception:
        return None


def is_available(base_url=None, model=None, **kw):
    """Quick liveness check: reachable and returns content."""
    return chat("ping", max_tokens=4, timeout=6, base_url=base_url, model=model, **kw) is not None


def test_connection(base_url=None, model=None, api_key=None, timeout=10):
    """Test LLM connection with detailed diagnostics.

    Returns a dict with:
      - ok: bool, True if connection successful
      - message: str, human-readable status message
      - details: dict, additional diagnostic information
    """
    import urllib.request
    import urllib.error

    settings = _settings()

    # Use provided values or fall back to settings
    base = (base_url or settings["base_url"]).rstrip("/")
    model_name = model or settings["model"]
    key = api_key if api_key is not None else settings["api_key"]
    to = timeout or settings.get("timeout", 10)

    result = {
        "ok": False,
        "message": "",
        "details": {
            "base_url": base,
            "model": model_name,
            "timeout": to,
        }
    }

    # Test 1: Check if endpoint is reachable
    try:
        # First, try a simple GET request to check if server is up
        health_url = base.rstrip("/") + "/health"
        req = urllib.request.Request(health_url)
        with urllib.request.urlopen(req, timeout=to) as resp:
            result["details"]["health_check_status"] = resp.status
    except urllib.error.HTTPError as e:
        # 404 on /health is OK - many servers don't have it
        result["details"]["health_check_status"] = e.code
    except urllib.error.URLError as e:
        # Server might not be running
        result["message"] = f"Cannot reach server at {base}: {e.reason}"
        result["details"]["error"] = str(e.reason)
        return result
    except Exception as e:
        result["message"] = f"Connection error: {str(e)}"
        result["details"]["error"] = str(e)
        return result

    # Test 2: Try a simple chat completion
    try:
        chat_result = chat(
            "Say 'OK' if you can hear me.",
            max_tokens=10,
            timeout=to,
            base_url=base,
            model=model_name,
            api_key=key
        )

        if chat_result and len(chat_result.strip()) > 0:
            result["ok"] = True
            result["message"] = "Connection successful!"
            result["details"]["response"] = chat_result[:100]  # Truncate for display
        else:
            result["message"] = "Server responded but with empty content"

    except Exception as e:
        result["message"] = f"Chat request failed: {str(e)}"
        result["details"]["error"] = str(e)

    return result


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


def analyze_intent(text, knowledge_context=None, on_token=None):
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
    out = chat(user_msg, system=prompt["system"], max_tokens=600, timeout=60, on_token=on_token)
    if out and len(out) > 10:
        return out
    return None


def generate_with_understanding(text, analysis, knowledge_context=None, on_token=None):
    """Second-stage: send original prompt + analysis to LLM for JSON generation.

    Returns the raw LLM output (JSON string), or None on failure.
    """
    from . import knowledge as kb
    prompt = kb.build_generation_prompt(text, analysis)
    user_msg = prompt["user"]
    if knowledge_context:
        user_msg += "\n\n" + str(knowledge_context)
    out = chat(user_msg, system=prompt["system"], max_tokens=4000, timeout=180, on_token=on_token)
    return out
