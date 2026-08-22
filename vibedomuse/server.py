# -*- coding: utf-8 -*-
"""
VibeDoMuse · server.py
Optional REST backend built on Python's stdlib http.server:
  - GET  /                    API info
  - GET  /api/stats           knowledge-base statistics
  - GET  /api/templates       template search (q, or category/mood/key filters)
  - GET  /api/params          parse-only preview of natural language
  - POST /api/generate        full creation (parse -> search -> compose -> render);
                              supports mode=rule|llm|llm_v2|variants|layers, use_template,
                              seed, loop
                              (llm_v2 = two-stage: intent analysis -> JSON generation;
                              this is the recommended AI channel — output is forced to V2)
  - GET  /api/audio/<file>    serve generated WAV
  - GET  /api/json/<file>     serve generated JSON
Zero external dependencies, fully offline.

v2: token auth (config.ini [server] token), binds 127.0.0.1 by default, and the
generate endpoint now supports the LLM channel, seed variants and layers.
"""
import os
import sys
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from ._paths import RUNTIME_DIR

GEN_WAV_DIR = os.path.join(RUNTIME_DIR, "generated", "wav")
GEN_JSON_DIR = os.path.join(RUNTIME_DIR, "generated", "json")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vibedomuse import agent as agent_mod
from vibedomuse import template_db as tdb
from vibedomuse import nl_parser as nlp
from vibedomuse.nl_parser import MusicParams


def _read_body(handler):
    length = int(handler.headers.get("Content-Length", 0) or 0)
    if length == 0:
        return {}
    raw = handler.rfile.read(length)
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return {}


def _send_json(handler, obj, code=200):
    data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _params_from_filters(q, category, mood, key):
    if q:
        return nlp.parse(q)
    return MusicParams(category=category or "galgame_accompaniment", mood=mood or "gentle", key=key or "C")


class Handler(BaseHTTPRequestHandler):
    token = ""  # filled from config in main()

    def log_message(self, *args):
        pass  # silent logging

    def _authed(self):
        """Token check: Authorization: Bearer <t> | X-Api-Key: <t> | ?token=<t>."""
        if not self.token:
            return True
        h = self.headers.get("Authorization", "") or ""
        if h.lower().startswith("bearer ") and h[7:].strip() == self.token:
            return True
        if self.headers.get("X-Api-Key") == self.token:
            return True
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if (qs.get("token") or [""])[0] == self.token:
            return True
        return False

    def do_GET(self):
        if not self._authed():
            return _send_json(self, {"error": "unauthorized"}, code=401)
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            return _send_json(self, {
                "name": "VibeDoMuse API",
                "note": "The frontend is a PyQt6 desktop app (frontend_pyqt6/main.py). "
                        "This service is an optional REST backend.",
                "endpoints": ["/api/stats", "/api/params", "/api/templates",
                              "/api/generate", "/api/audio/<file>"],
            })

        if path == "/api/stats":
            return _send_json(self, tdb.stats())

        if path == "/api/templates":
            q = (qs.get("q") or [""])[0]
            category = (qs.get("category") or [""])[0] or None
            mood = (qs.get("mood") or [""])[0] or None
            key = (qs.get("key") or [""])[0] or None
            limit = int((qs.get("limit") or ["12"])[0])
            params = _params_from_filters(q, category, mood, key)
            res = tdb.search(params, limit=limit, category=category, mood=mood, key=key)
            return _send_json(self, {"count": len(res), "templates": res})

        if path == "/api/params":
            q = (qs.get("q") or [""])[0] or (qs.get("text") or [""])[0] or ""
            return _send_json(self, agent_mod.parse_only(q))

        if path.startswith("/api/audio/"):
            fname = urllib.parse.unquote(path[len("/api/audio/"):])
            fpath = os.path.normpath(os.path.join(GEN_WAV_DIR, fname))
            if fpath.startswith(GEN_WAV_DIR) and os.path.isfile(fpath):
                return self._serve_file(fpath, "audio/wav")
            return self._send_404()

        if path.startswith("/api/json/"):
            fname = urllib.parse.unquote(path[len("/api/json/"):])
            fpath = os.path.normpath(os.path.join(GEN_JSON_DIR, fname))
            if fpath.startswith(GEN_JSON_DIR) and os.path.isfile(fpath):
                return self._serve_file(fpath, "application/json; charset=utf-8")
            return self._send_404()

        return self._send_404()

    def do_POST(self):
        if not self._authed():
            return _send_json(self, {"error": "unauthorized"}, code=401)
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path == "/api/generate":
            body = _read_body(self)
            text = body.get("text", "")
            use_template = body.get("use_template")
            seed = body.get("seed")
            mode = (body.get("mode") or "rule").lower()
            n = int(body.get("n") or 4)
            try:
                if mode == "llm_v2":
                    # Two-stage AI channel: intent analysis first, then JSON
                    # generation (forced to V2 format). Falls back to one-stage
                    # run_llm when the analysis stage produces no output.
                    analysis = agent_mod.analyze(text)
                    if analysis:
                        result = agent_mod.run_llm_v2(text, analysis, seed=seed)
                    else:
                        result = agent_mod.run_llm(text, use_template=use_template, seed=seed)
                elif mode == "llm":
                    result = agent_mod.run_llm(text, use_template=use_template, seed=seed)
                elif mode == "variants":
                    result = {"ok": True, "mode": "variants",
                              "items": agent_mod.run_variants(text, n=n, seed=seed)}
                elif mode == "layers":
                    result = agent_mod.run_layers(text, seed=seed)
                else:
                    result = agent_mod.run(text, use_template=use_template, seed=seed)
                if isinstance(result, dict):
                    result.setdefault("mode", mode)
                return _send_json(self, result)
            except Exception as e:
                return _send_json(self, {"ok": False, "error": str(e)}, code=500)
        return self._send_404()

    def _serve_file(self, fpath, ctype):
        try:
            with open(fpath, "rb") as f:
                data = f.read()
        except Exception:
            return self._send_404()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def _send_404(self):
        _send_json(self, {"error": "not found"}, code=404)


def main():
    from vibedomuse import config as cfg
    cfg.ensure_config_file()
    srv = cfg.get_server_settings()
    Handler.token = srv["token"]
    os.makedirs(GEN_WAV_DIR, exist_ok=True)
    os.makedirs(GEN_JSON_DIR, exist_ok=True)
    # warm up the template index
    try:
        tdb.stats()
    except Exception:
        pass
    server = ThreadingHTTPServer((srv["bind"], srv["port"]), Handler)
    auth_note = "(token auth enabled)" if srv["token"] else "(no auth — recommended: set a token in config.ini [server])"
    print(f"VibeDoMuse backend started: http://{srv['bind']}:{srv['port']} {auth_note}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
