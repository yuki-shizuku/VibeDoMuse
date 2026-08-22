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
from ._paths import resource_path

SPEC_PATH = resource_path("JSON_Format_Specification.md")

# Core structure sections always included regardless of the query.
# NOTE: "7. Note Positioning" is deliberately NOT included: it is a V1-vs-V2
# comparison chapter full of legacy examples that would bait the LLM into
# emitting V1 output. V2-only chapters ("6.3 V2", "39. V2") cover positioning.
_CORE_TITLES = (
    "2. Top-Level", "3. metadata", "4. tracks", "5. notes",
    "6. Duration", "6.3 V2",
    "34. Quick", "33. General MIDI", "39. V2",
)


_V1_TRACE = re.compile(
    r"\bV1\b|legacy|Legacy|顺序累加"
    r'|["\s]*pitch["\s]*:\s*-1\s*[,}\s]'
    r"|pitch:\s*null|[-–]\s*1[\s`]*or[\s`]*null|21-108[\s`]*or[\s`]*-1"
    r"|两种格式|两种机制"
)

# Sections that exist only to explain the dual-format world (V2 vs legacy).
# They would teach the model that an alternative format exists even after
# line-level scrubbing, so they are excluded from the knowledge base entirely.
_V1_BLACKLIST_PREFIX = (
    "Overview",
    "7. Note Positioning",
    "8. Rests",
    "36. Multi-Format Support",
)


def _v2_only_text(body):
    """Strip every trace of the legacy format from spec text so the LLM never
    learns that an alternative to V2 exists.

    - Skips whole sub-sections whose heading mentions V1 / legacy
      (e.g. "### 7.1 V1 — 顺序累加");
    - Drops any line that mentions V1 / legacy / sequential accumulation /
      explicit rest notation (pitch: -1 / pitch: null);
    - Collapses the blank lines left behind.
    """
    if not body:
        return body
    out = []
    in_v1 = False
    for ln in body.splitlines():
        if re.match(r"^#{1,6}\s", ln):
            in_v1 = False
            if re.search(r"\bV1\b|legacy", ln, re.I):
                in_v1 = True
                continue
        if in_v1:
            continue
        if _V1_TRACE.search(ln):
            continue
        out.append(ln)
    res = []
    prev_blank = False
    for ln in out:
        blank = not ln.strip()
        if blank and prev_blank:
            continue
        res.append(ln)
        prev_blank = blank
    return "\n".join(res)


def _v2_title(title):
    """Rewrite a spec section title so it never exposes the legacy format."""
    if not title:
        return title
    t = re.sub(r"\s*[—\-–]\s*V1\s*vs\.?\s*V2.*", " — V2（绝对定位）", title)
    t = re.sub(r"\bV1\b", "V2", t)
    t = re.sub(r"legacy", "V2", t, flags=re.I)
    t = re.sub(r"顺序累加", "绝对定位", t)
    return t


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
        if any(title.startswith(pre) for pre in _V1_BLACKLIST_PREFIX):
            continue
        body = _v2_only_text("\n".join(lines[1:]) if len(lines) > 1 else "")
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
    out = [{"title": _v2_title(s["title"]), "body": s["body"][:body_limit]} for s in selected]
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
    out = {"format": data.get("format", "v2"),
           "metadata": data.get("metadata", {}), "tracks": tracks}
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


# ----------------------------------------------------------------------------
# V2 mandate — THE ONLY FORMAT the AI may output.
# Shared verbatim by the system prompt, the score-generation user prompt and
# the follow-up user prompt so the requirement is 100% consistent everywhere.
# Legacy/V1 is DISABLED: the local validator rejects any non-V2 JSON, so the
# LLM must never fall back to V1 notation.
# ----------------------------------------------------------------------------
_V2_MANDATE = (
    "=== V2 FORMAT (MANDATORY - THE ONLY FORMAT) === "
    "V2 (absolute positioning via \"offset\") is the ONLY format that exists. "
    "Any output without \"format\": \"v2\" or missing offsets will be REJECTED. "
    "V2 rules: "
    "1) Top-level MUST contain \"format\": \"v2\" "
    "2) Every single note MUST have an \"offset\" field (number >= 0, in "
    "quarter-note units from the start of the piece) "
    "3) Rests are never written explicitly - gaps between notes are "
    "automatically filled with rests "
    "4) Notes with the same offset are automatically merged into a chord "
    "5) duration can be a string (\"whole\", \"half\", \"quarter\", \"eighth\", "
    "\"16th\", dotted variants) OR a positive number (e.g. 1.5, 1.75, 0.5) "
    "6) A numerical duration cannot be combined with tuplet "
    "7) Optional fields: \"pitch_name\" (string like \"C4\"), \"measure\" "
    "(number), \"beat\" (number), \"end_offset\" (number) "
    "Output ONLY the JSON, no explanation."
)

_V2_EXAMPLE = (
    '{"format": "v2", "metadata": {"tempo_bpm": 120, "time_signature": "4/4", '
    '"key_signature": "C"}, "tracks": [{"instrument": "Acoustic Grand Piano", '
    '"notes": [{"pitch": 60, "duration": "quarter", "offset": 0}, '
    '{"pitch": 64, "duration": "quarter", "offset": 1}, '
    '{"pitch": 67, "duration": "half", "offset": 2}]}]}'
)

_V2_CHECKLIST = (
    "=== V2 FORMAT CHECKLIST (verify every item before outputting) === "
    "- [ ] Top-level has \"format\": \"v2\" "
    "- [ ] Every note has \"offset\" (number >= 0) "
    "- [ ] Rests are never written (gaps are auto-filled) "
    "- [ ] duration is a string or a positive number "
    "- [ ] Every note uses absolute \"offset\" positioning "
    "- [ ] Output ONLY the JSON, no explanation."
)

# Shared system prompt for the score-generation stage (used by both the
# one-stage and two-stage generation prompts).
_SYSTEM_PROMPT = (
    "You are a Do-muse score generator expert. "
    "=== LANGUAGE DETECTION === "
    "First, detect the language of the user's request. Then output your "
    "JSON score following these rules: "
    "JSON keys are always in English; all text fields (title, composer, lyric, "
    "instrument names) MUST be in the SAME language as the user's request. "
    "If the user writes in Chinese, text fields MUST be in Chinese. "
    "Output only spec-compliant JSON scores. "
    "You MUST follow the user's instruction EXACTLY for the number of tracks, "
    "instruments, and tempo. Do not reduce or simplify the user's requirements. "
    "Do NOT include <thinking> or any reasoning tags. "
    + _V2_MANDATE
    + " "
    + "=== V2 EXAMPLE (study this structure) === "
    + _V2_EXAMPLE
    + " "
    + _V2_CHECKLIST
)


def _assemble_score_user(text, sec_txt, ex_txt, analysis=None):
    """Assemble the score-generation user message.

    ``analysis`` (optional) inserts the stage-1 LLM understanding paragraph
    (two-stage flow); both flows share the same structure and hard requirements.
    """
    user = (
        "=== LANGUAGE DETECTION ===\n"
        "Read the 'USER REQUEST' below and detect its language. "
        "Your entire output MUST follow these rules:\n"
        "1. JSON keys (metadata, tracks, notes, pitch, duration, etc.) are always in English.\n"
        "2. All text content (title, composer, lyric, instrument names, comments) MUST be "
        "in the SAME language as the user's request.\n"
        "3. If the user writes in Chinese, all text fields MUST be in Chinese. "
        "If the user writes in English, all text fields MUST be in English.\n"
        "========================\n\n"
        "You are the Do-muse score generator. Create a score for the music request "
        "below, strictly following the JSON spec. Output ONLY the JSON itself "
        "(no explanation, no markdown code block).\n\n"
        f"USER REQUEST: {text}\n\n"
    )
    if analysis:
        user += f"INTENT ANALYSIS (use this understanding to guide your composition):\n{analysis}\n\n"
    user += (
        f"JSON SPEC EXCERPTS:\n{sec_txt}\n\n"
        f"REAL TEMPLATE EXAMPLES (study their structure and style, but compose a "
        f"brand-new piece; do NOT return the example as-is):\n{ex_txt}\n\n"
        "=== V2 FORMAT REQUIREMENTS (MANDATORY - verify each item) ===\n"
        + _V2_MANDATE
        + "\n"
        "8. velocity is an integer 0-127\n"
        "=== STRUCTURE REQUIREMENTS ===\n"
        '- Top level must contain "format": "v2", metadata (tempo_bpm as integer, '
        'time_signature like "x/y", key_signature) and a tracks array\n'
        "- Each track must contain instrument (General MIDI name) and a notes array\n"
        '- Each note must contain pitch (integer 21-108) and duration\n'
        "- The number of tracks MUST match the user's request exactly. "
        "If the user asks for 3 tracks, output exactly 3 tracks. Do not reduce or simplify.\n"
        "- The instrument for each track MUST match the user's request or the genre convention.\n"
        "- The tempo (BPM) MUST match the user's request as closely as possible.\n"
        "CRITICAL: The user's track count, instruments, and tempo are MANDATORY. "
        "Do not change or simplify them. Output exactly what the user asked for.\n"
        "Do NOT include <thinking> or any reasoning tags in your output.\n"
        "Output only the JSON."
    )
    return user


def _score_prompt_common(text, sec_txt, ex_txt, sections, examples, results, analysis=None):
    """Shared result shape for the one-stage / two-stage generation prompts."""
    return {
        "system": _SYSTEM_PROMPT,
        "user": _assemble_score_user(text, sec_txt, ex_txt, analysis=analysis),
        "sections": sections,
        "examples": examples,
        "templates": results,
    }


def build_prompt(text, top_sections=3, top_examples=1):
    """Assemble the LLM prompt; returns {system, user, sections, examples, templates}."""
    sections = retrieve_sections(text, top_k=top_sections)
    examples, results = retrieve_examples(text, top_k=top_examples)
    sec_txt = "\n\n".join(f"### {s['title']}\n{s['body']}" for s in sections)
    ex_txt = "\n\n".join(examples) if examples else "(no examples available; compose independently per the spec)"
    return _score_prompt_common(text, sec_txt, ex_txt, sections, examples, results, analysis=None)


def build_analysis_prompt(text):
    """Build the prompt for the first-stage intent analysis.

    The raw user prompt is passed directly to the LLM WITHOUT any pre-filtering
    of the knowledge base. The LLM autonomously considers the full list of
    available spec sections and decides which are relevant to the user's request.
    The output is a natural-language understanding paragraph, NOT JSON.
    """
    # List all available spec section titles so the LLM can decide which to use
    # (titles are rewritten so the legacy format is never exposed)
    all_titles = [_v2_title(s["title"]) for s in _SECTIONS]
    all_titles_str = "\n".join(f"  - {t}" for t in all_titles)

    user = (
        "=== LANGUAGE DETECTION ===\n"
        "Read the user's request below and detect its language. "
        "Your entire output MUST be written in the SAME language as the user's request. "
        "For example, if the user writes in Chinese, you MUST respond in Chinese. "
        "If the user writes in English, you MUST respond in English.\n"
        "========================\n\n"
        "You are a music analysis assistant. Read the user's request below "
        "and think about what kind of music they want to create.\n\n"
        "First, consider which parts of the Do-muse JSON specification are "
        "relevant to this request. The full spec section list is:\n"
        f"{all_titles_str}\n\n"
        "Think about which sections would be most useful for creating this score. "
        "Consider metadata, tracks, instruments, notes, and any advanced features "
        "that might apply (ties, slurs, dynamics, tuplets, ornaments, repeats, "
        "lyrics, arpeggios, chords, etc.).\n\n"
        "Then, write a clear, concise natural-language understanding of the "
        "user's intent. Cover ALL of these aspects:\n"
        "- Mood / emotion of the piece\n"
        "- Key (major/minor) and tonality\n"
        "- Tempo (speed, BPM if specified)\n"
        "- Instruments to use\n"
        "- Number of tracks/voices\n"
        "- Texture style (arpeggio, block chords, etc.)\n"
        "- Duration (how long the piece should be)\n"
        "- Category (BGM, accompaniment, multi-key, etc.)\n"
        "- Any special features (loop, drums, seamless, etc.)\n\n"
        "Output ONLY the understanding paragraph in natural language. "
        "Do NOT output JSON. Do NOT write the score yet. "
        "Do NOT include <thinking> or any reasoning tags.\n\n"
        f"USER REQUEST: {text}"
    )
    return {
        "system": "You are a music analysis expert. "
        "=== LANGUAGE DETECTION === "
        "First, detect the language of the user's request. Then output your "
        "understanding in that SAME language. If the user writes in Chinese, "
        "you MUST write in Chinese. If the user writes in English, you MUST "
        "write in English. "
        "Given a user's music request, autonomously consider the full list of "
        "Do-muse JSON specification sections above and decide which are relevant. "
        "Then output a natural-language understanding of what music they want. "
        "Cover mood, key, tempo, instruments, track count, texture, duration, "
        "and category. "
        "Do NOT include <thinking> or any reasoning tags in your output.",
        "user": user,
    }


def build_generation_prompt(text, analysis, top_sections=3, top_examples=1):
    """Build the prompt for the second-stage JSON generation.

    Combines the original user request with the LLM's own understanding analysis
    from stage 1, plus the knowledge base context, to produce the final JSON score.
    """
    sections = retrieve_sections(text, top_k=top_sections)
    examples, results = retrieve_examples(text, top_k=top_examples)
    sec_txt = "\n\n".join(f"### {s['title']}\n{s['body']}" for s in sections)
    ex_txt = "\n\n".join(examples) if examples else "(no examples available; compose independently per the spec)"
    return _score_prompt_common(text, sec_txt, ex_txt, sections, examples, results, analysis=analysis)


def build_followup_prompt(original_text, original_analysis, current_json, user_feedback, top_sections=3, top_examples=1):
    """Build the prompt for follow-up generation.

    Combines system prompt + original request + initial understanding + current JSON + user feedback.
    This allows users to refine the generated music based on their feedback.
    """
    # Retrieve relevant spec sections based on original text (to maintain context)
    sections = retrieve_sections(original_text, top_k=top_sections)
    examples, results = retrieve_examples(original_text, top_k=top_examples)
    sec_txt = "\n\n".join(f"### {s['title']}\n{s['body']}" for s in sections)
    ex_txt = "\n\n".join(examples) if examples else "(no examples available; compose independently per the spec)"

    # Build follow-up user prompt
    user = (
        "=== LANGUAGE DETECTION ===\n"
        "Read the original user request below and detect its language. "
        "Your entire output MUST follow these rules:\n"
        "1. JSON keys (metadata, tracks, notes, pitch, duration, etc.) are always in English.\n"
        "2. All text content (title, composer, lyric, instrument names, comments) MUST be "
        "in the SAME language as the original user request.\n"
        "3. If the original request was in Chinese, all text fields MUST be in Chinese. "
        "If the original request was in English, all text fields MUST be in English.\n"
        "========================\n\n"
        "You are the Do-muse score generator. The user has provided feedback on the music you generated. "
        "Create a NEW score that addresses the user's feedback while preserving the good aspects.\n\n"
        
        "ORIGINAL USER REQUEST:\n"
        f"{original_text}\n\n"
        
        "AI INITIAL UNDERSTANDING:\n"
        f"{original_analysis}\n\n"
        
        "CURRENT GENERATED SCORE:\n"
        f"{json.dumps(current_json, ensure_ascii=False, indent=2)}\n\n"
        
        "USER FEEDBACK:\n"
        f"{user_feedback}\n\n"
        
        "INSTRUCTIONS:\n"
        "- Analyze the user's feedback and identify what needs to be changed\n"
        "- Create a NEW score that addresses the feedback while maintaining the structure\n"
        "- Preserve essential parameters like tempo, key, time signature unless the feedback explicitly asks to change them\n"
        "- If the feedback asks for specific changes, make those changes precisely\n"
        "- If the feedback is general, interpret it reasonably and make appropriate improvements\n"
        "- Output ONLY the JSON score, no explanation or markdown code blocks\n\n"
        
        "JSON SPEC EXCERPTS:\n"
        f"{sec_txt}\n\n"
        
        "REAL TEMPLATE EXAMPLES (study their structure and style):\n"
        f"{ex_txt}\n\n"
        
        "=== V2 FORMAT REQUIREMENTS (MANDATORY) ===\n"
        + _V2_MANDATE
        + "\n"
        "=== STRUCTURE REQUIREMENTS ===\n"
        "- Top level must have \"format\": \"v2\", metadata, and tracks\n"
        "- JSON keys must be in English\n"
        "- Text content must match original request language\n"
        "- Pitch range: 21-108\n"
        "- Velocity range: 0-127\n"
        "- Output only the JSON itself, no explanations"
    )

    return {
        "system": _SYSTEM_PROMPT,
        "user": user,
        "sections": sections,
        "examples": examples,
        "templates": results,
    }
