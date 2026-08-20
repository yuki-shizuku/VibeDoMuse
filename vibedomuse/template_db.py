# -*- coding: utf-8 -*-
"""
VibeDoMuse · template_db.py
Database layer: indexes the 144 Do-muse templates (bgm / accompaniment / other)
and ranks them by MusicParams, letting the Agent "find the right template with
natural language". Also used as the knowledge base for LLM examples.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CATALOG_DIRS = {
    "galgame_bgm": os.path.join(ROOT, "bgm", "json"),
    "galgame_accompaniment": os.path.join(ROOT, "accompaniment", "json"),
    "galgame_v3": os.path.join(ROOT, "other", "json"),
}

# generation scripts (with PIECES metadata) to enrich mood/pattern/progression
_GEN_MODULES = {
    "galgame_bgm": os.path.join(ROOT, "bgm", "generate_bgm.py"),
    "galgame_accompaniment": os.path.join(ROOT, "accompaniment", "generate_accompaniment.py"),
    "galgame_v3": os.path.join(ROOT, "other", "generate_galgame_v3.py"),
}


def _load_piece_lookup():
    """Build a name_en -> metadata lookup from the PIECES of the three scripts."""
    lookup = {}
    for cat, mod_path in _GEN_MODULES.items():
        if not os.path.exists(mod_path):
            continue
        dir_ = os.path.dirname(mod_path)
        mod_name = os.path.splitext(os.path.basename(mod_path))[0]
        try:
            if dir_ not in sys.path:
                sys.path.insert(0, dir_)
            mod = __import__(mod_name, fromlist=["PIECES"])
            for p in getattr(mod, "PIECES", []):
                lookup[p.get("name_en")] = p
        except Exception:
            pass
    return lookup


_PIECE_LOOKUP = _load_piece_lookup()
_INDEX = None


def _build_index():
    global _INDEX
    if _INDEX is not None:
        return _INDEX
    idx = []
    for category, d in CATALOG_DIRS.items():
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".json"):
                continue
            path = os.path.join(d, fn)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                continue
            meta = data.get("metadata", {}) or {}
            tracks = data.get("tracks", []) or []
            name = os.path.splitext(fn)[0]
            piece = _PIECE_LOOKUP.get(name, {})
            rec = {
                "name": name,
                "file": fn,
                "path": path,
                "category": category,
                "title": data.get("title", name),
                "composer": data.get("composer", ""),
                "tempo_bpm": int(meta.get("tempo_bpm", 0) or 0),
                "time_signature": meta.get("time_signature", ""),
                "key_signature": meta.get("key_signature", ""),
                "instruments": [t.get("instrument", "") for t in tracks],
                "track_count": len(tracks),
                "mood": piece.get("mood", ""),
                "pattern": piece.get("pattern", ""),
                "progression": piece.get("chords", []),
                "duration_est": "",
            }
            idx.append(rec)
    _INDEX = idx
    return _INDEX


def all_templates():
    return _build_index()


def get_by_name(name):
    for r in _build_index():
        if r["name"] == name or r["file"] == name:
            return r
    return None


def _score(rec, params):
    if params is None:
        return 0.0, []
    s = 0.0
    reasons = []
    if params.key and rec["key_signature"]:
        if rec["key_signature"].lower() == params.key.lower():
            s += 3.0
            reasons.append("调性匹配")
        elif rec["key_signature"][0].upper() == params.key[0].upper():
            s += 1.5
            reasons.append("根音相同")
    if params.mood and rec["mood"] and rec["mood"] == params.mood:
        s += 3.0
        reasons.append("情绪匹配")
    if rec["category"] == params.category:
        s += 1.0
        reasons.append("风格类别匹配")
    if params.instrument in rec["instruments"]:
        s += 1.0
        reasons.append("乐器匹配")
    if rec["track_count"] == params.tracks:
        s += 1.0
        reasons.append("声部数匹配")
    if params.pattern and rec["pattern"] == params.pattern:
        s += 1.0
        reasons.append("织体匹配")
    if rec["tempo_bpm"] and params.tempo_bpm:
        d = abs(rec["tempo_bpm"] - params.tempo_bpm)
        s += max(0.0, (1.0 - min(1.0, d / 60.0))) * 2.0
    return s, reasons


def search(params, limit=8, category=None, mood=None, key=None):
    """Rank templates by MusicParams (or filter); return a list sorted by score desc."""
    idx = _build_index()
    results = []
    for rec in idx:
        if category and rec["category"] != category:
            continue
        if mood and rec["mood"] != mood:
            continue
        if key and rec["key_signature"].lower() != key.lower():
            continue
        s, reasons = _score(rec, params)
        if s <= 0 and not (category or mood or key):
            s = 0.01
        results.append((s, reasons, rec))
    results.sort(key=lambda x: x[0], reverse=True)
    out = []
    for s, reasons, rec in results[:limit]:
        item = dict(rec)
        item["score"] = round(s, 2)
        item["reasons"] = reasons
        out.append(item)
    return out


def stats():
    idx = _build_index()
    by_cat = {}
    for r in idx:
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + 1
    return {"total": len(idx), "by_category": by_cat}
