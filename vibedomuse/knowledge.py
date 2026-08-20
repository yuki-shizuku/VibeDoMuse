# -*- coding: utf-8 -*-
"""
VibeDoMuse · knowledge.py
Knowledge-base retrieval layer: provides context for the LLM to write JSON.
- Parses JSON_Format_Specification.md into sections and retrieves the most
  relevant ones via TF-IDF (Chinese char bigrams + English words);
- Retrieves the most matching real JSON templates from the 144-piece library
  as imitation examples.
"""
import json
import math
import os
import re
from collections import Counter

from . import nl_parser as nlp
from . import template_db as tdb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_PATH = os.path.join(ROOT, "JSON_Format_Specification.md")

# Core structure sections always included regardless of the query
_CORE_TITLES = (
    "2. Top-Level", "3. metadata", "4. tracks", "5. notes",
    "6. Duration", "34. Quick", "33. General MIDI",
)


def _load_sections():
    try:
        with open(SPEC_PATH, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return []
    parts = re.split(r"(?m)^##\s+", text)
    sections = []
    for p in parts[1:]:
        lines = p.splitlines()
        title = lines[0].strip() if lines else ""
        body = "\n".join(lines[1:]) if len(lines) > 1 else ""
        sections.append({"title": title, "body": body})
    return sections


_SECTIONS = _load_sections()


# ----------------------------------------------------------------------------
# TF-IDF over spec sections
# ----------------------------------------------------------------------------
# Chinese music term -> English spec keywords (for TF-IDF query expansion)
_CH_ALIAS = {
    "琶音": "arpeggio", "琶": "arpeggio", "分解": "arpeggio",
    "和弦": "chord", "进行": "progression", "音符": "note", "音高": "pitch",
    "拍号": "time signature", "调号": "key signature", "力度": "velocity dynamics",
    "速度": "tempo", "旋律": "melody", "伴奏": "accompaniment",
    "装饰": "ornament", "颤音": "trill", "波音": "mordent", "回转": "turn",
    "连音": "slur", "圆滑": "slur", "延音": "tie pedal", "踏板": "pedal",
    "渐强": "crescendo", "渐弱": "diminuendo", "重复": "repeat", "反复": "repeat",
    "歌词": "lyric", "滑音": "glissando", "倚音": "grace", "震音": "tremolo",
    "断音": "staccato", "跳音": "staccato", "重音": "accent", "保持": "tenuto",
    "表情": "expression", "小节": "measure", "时长": "duration", "节奏": "rhythm",
    "鼓": "drum", "打击乐": "percussion", "循环": "loop", "终止": "cadence",
    "柱式": "block chord", "华尔兹": "waltz", "切分": "syncopated",
    "乐谱": "score", "音色": "instrument", "乐器": "instrument",
}


def _expand_aliases(tokens):
    out = list(tokens)
    for k in tokens:
        for en in _CH_ALIAS.get(k, "").split():
            if en and en not in out:
                out.append(en)
    return out


def _tokens(text):
    """Tokenize: English words + Chinese bigrams + Chinese words + aliases."""
    t = (text or "").lower()
    out = re.findall(r"[a-z][a-z0-9]{1,}", t)
    cn = re.findall(r"[\u4e00-\u9fff]", t)
    out += [cn[i] + cn[i + 1] for i in range(len(cn) - 1)]
    out += [c for c in cn]
    out = [k for k in out if len(k) >= 1]
    return _expand_aliases(out)


def _build_tfidf(sections):
    docs = []
    for s in sections:
        tok = _tokens(s["title"] + "\n" + s["body"])
        docs.append(Counter(tok))
    n_docs = max(1, len(docs))
    df = Counter()
    for d in docs:
        for k in d:
            df[k] += 1
    idf = {}
    for k, c in df.items():
        idf[k] = math.log((1 + n_docs) / (1 + c)) + 1.0
    return docs, idf


_TFIDF = _build_tfidf(_SECTIONS)


def _score_section(idx, query_tokens, docs, idf):
    q = Counter(query_tokens)
    score = 0.0
    for k, qc in q.items():
        if k in idf:
            tf = docs[idx].get(k, 0)
            score += (tf / max(1, sum(docs[idx].values()))) * idf[k] * min(3, qc)
    return score


def retrieve_sections(query, top_k=3, body_limit=500):
    """Return spec sections relevant to the query (core structure sections included).

    Strategy: first take the top-k non-core sections with a real TF-IDF match,
    then always append the core structural sections (JSON skeleton) if missing.
    """
    docs, idf = _TFIDF
    qt = _expand_aliases(_tokens(query or ""))
    ranked = []
    for i, s in enumerate(_SECTIONS):
        score = _score_section(i, qt, docs, idf)
        ranked.append((score, s))
    ranked.sort(key=lambda x: x[0], reverse=True)

    def is_core(s):
        return any(s["title"].startswith(c) for c in _CORE_TITLES)

    selected, seen = [], set()
    # 1) top-k relevant non-core sections
    for sc, s in ranked:
        if is_core(s) or sc <= 0:
            continue
        if s["title"] in seen:
            continue
        seen.add(s["title"])
        selected.append(s)
        if len(selected) >= top_k:
            break
    # 2) always include the core structural sections (dedup)
    for sc, s in ranked:
        if is_core(s) and s["title"] not in seen:
            seen.add(s["title"])
            selected.append(s)
    out = [{"title": s["title"], "body": s["body"][:body_limit]} for s in selected]
    return out[:max(top_k, 4) + 2]


def _trim_score(data, max_notes=12):
    """Trim the template JSON notes to keep the prompt compact."""
    if not isinstance(data, dict):
        return data
    tracks = []
    for tr in (data.get("tracks") or []):
        if not isinstance(tr, dict):
            continue
        t = {"instrument": tr.get("instrument", "Acoustic Grand Piano")}
        notes = tr.get("notes") or []
        t["notes"] = notes[:max_notes]
        tracks.append(t)
    out = {"metadata": data.get("metadata", {}), "tracks": tracks}
    if data.get("title"):
        out["title"] = data["title"]
    return out


def retrieve_examples(query, top_k=1):
    """Retrieve the most relevant templates using rule parsing.

    Returns (list of trimmed JSON strings, list of template records).
    """
    results = []
    try:
        params = nlp.parse(query)
        results = tdb.search(params, limit=top_k)
    except Exception:
        results = tdb.all_templates()[:top_k]
    examples = []
    for r in results:
        try:
            with open(r["path"], "r", encoding="utf-8") as f:
                data = json.load(f)
            data = _trim_score(data)
            title = data.get("title", "")
            if any(ord(c) > 127 for c in title):   # avoid non-ASCII in the prompt
                data["title"] = r["name"]
            examples.append(json.dumps(data, ensure_ascii=False, indent=1))
        except Exception:
            continue
    return examples, results


def build_prompt(text, top_sections=3, top_examples=1):
    """Assemble the LLM prompt; returns {system, user, sections, examples, templates}."""
    sections = retrieve_sections(text, top_k=top_sections)
    examples, results = retrieve_examples(text, top_k=top_examples)
    sec_txt = "\n\n".join(f"### {s['title']}\n{s['body']}" for s in sections)
    ex_txt = "\n\n".join(examples) if examples else "(no examples available; compose independently per the spec)"
    user = (
        "You are the Do-muse score generator. Create a score for the music request "
        "below, strictly following the JSON spec. Output ONLY the JSON itself "
        "(no explanation, no markdown code block).\n\n"
        f"USER REQUEST: {text}\n\n"
        f"JSON SPEC EXCERPTS:\n{sec_txt}\n\n"
        f"REAL TEMPLATE EXAMPLES (study their structure and style, but compose a "
        f"brand-new piece; do NOT return the example as-is):\n{ex_txt}\n\n"
        "HARD REQUIREMENTS:\n"
        '- Top level must contain metadata (tempo_bpm as integer, time_signature like '
        '"x/y", key_signature) and a tracks array\n'
        "- Each track must contain instrument (General MIDI name) and a notes array\n"
        '- Each note must contain pitch (integer 21-108; use -1 for rests) and duration '
        '("whole/half/quarter/eighth/16th", dotted allowed)\n'
        "- velocity is an integer 0-127; notes must be in performance order\n"
        "- 1-3 tracks, 16-40 notes per track\n"
        "Output only the JSON."
    )
    return {
        "system": "You are a Do-muse score generator expert. Output only spec-compliant JSON scores.",
        "user": user,
        "sections": sections,
        "examples": examples,
        "templates": results,
    }
