# -*- coding: utf-8 -*-
"""
VibeDoMuse · json_validator.py
Local JSON validation layer: checks the LLM-produced JSON against the
Do-muse spec (checklist in section 34), fills in defaults, and derives a
MusicParams object (used for template search and display).

v2 additions:
- Semantic pairing checks: tie / slur / pedal / hairpin start-stop pairing,
  tuplet group consistency, macro rules, length limits (lyric/text/expression),
  volta range, time/key signature change formats, grace_note / tremolo shapes.
- to_params() no longer hardcodes category/duration: it reads an optional
  top-level "category" field and derives duration from the actual note stream.
"""
import re

from .nl_parser import MusicParams

DURATIONS = {
    "whole", "half", "quarter", "eighth", "16th", "32nd", "64th",
    "half.", "quarter.", "eighth.", "16th.", "32nd.",
}
TIME_SIGS = {"4/4", "3/4", "2/4", "6/8", "12/8"}
TUP = {3, 5, 6, 7, 9}
ARTICULATIONS = {"staccato", "staccatissimo", "accent", "tenuto", "marcato", "sforzando"}
DYNAMICS = {
    "pppp", "ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", "ffff",
    "sfz", "sf", "fz", "rfz", "sffz", "fp", "sfp", "crescendo", "diminuendo",
    "calando", "morendo", "smorzando", "rinforzando",
}
TIE_SLUR = {"start", "stop", "continue"}
PEDAL = {"start", "continue", "stop"}
NAVIGATION = {"D.C.", "D.S.", "Coda", "Fine"}
HAIRPIN = {"crescendo", "diminuendo", "stop"}
ORNAMENTS = {"trill", "mordent", "inverted_mordent", "turn", "inverted_turn"}
CATEGORIES = {"galgame_bgm", "galgame_accompaniment", "galgame_v3"}


def _is_pitch_ok(p):
    return p is None or p == -1 or (isinstance(p, int) and 21 <= p <= 108)


def _check_pairing(notes, field, errors, warnings, loc, require_same_pitch=False):
    """start / continue / stop pairing check for tie / slur / pedal."""
    state = None          # pitch tracked for ties
    pitch_on_start = None
    for ni, n in enumerate(notes):
        v = n.get(field)
        if v is None:
            continue
        p = n.get("pitch")
        if v == "start":
            if state is not None:
                warnings.append(f"{loc}.{field}: start again after {state} without stop")
            state = "open"
            pitch_on_start = p
        elif v == "continue":
            if state is None:
                warnings.append(f"{loc}.{field}: continue without start")
            state = "open"
        elif v == "stop":
            if state is None:
                errors.append(f"{loc}.{field}: stop without start")
            else:
                if require_same_pitch and pitch_on_start is not None and p is not None \
                        and pitch_on_start != p:
                    warnings.append(f"{loc}.{field}: start/stop pitch mismatch ({pitch_on_start} vs {p})")
            state = None
    if state is not None:
        errors.append(f"{loc}.{field}: start without matching stop")


def _check_tuplets(notes, errors, warnings, loc):
    """Consecutive notes carrying the same tuplet value form a group; validate size."""
    i = 0
    n = len(notes)
    while i < n:
        nt = notes[i]
        tup = nt.get("tuplet")
        if tup is None:
            i += 1
            continue
        if tup not in TUP:
            errors.append(f"{loc}.tuplet invalid: {tup}")
            i += 1
            continue
        if "." in str(nt.get("duration", "")):
            errors.append(f"{loc}.tuplet cannot combine with dotted note: {nt.get('duration')}")
        # find group extent (same tuplet value, contiguous)
        j = i
        while j < n and notes[j].get("tuplet") == tup:
            if "." in str(notes[j].get("duration", "")):
                errors.append(f"{loc}.tuplet cannot combine with dotted note: {notes[j].get('duration')}")
            j += 1
        size = j - i
        if size != tup:
            warnings.append(f"{loc}.tuplet={tup} group has {size} notes (expected {tup})")
        i = j


def _validate_notes(notes, errors, warnings, loc, allow_ref=True, depth=0):
    if not isinstance(notes, list) or not notes:
        errors.append(f"{loc}.notes missing or empty")
        return
    for ni, n in enumerate(notes):
        nloc = f"{loc}.notes[{ni}]"
        if not isinstance(n, dict):
            errors.append(f"{nloc} is not an object")
            continue
        ref = n.get("ref")
        if ref is not None:
            if not allow_ref:
                errors.append(f"{nloc} nested ref not allowed inside macro")
                continue
            if not isinstance(ref, str) or not ref:
                errors.append(f"{nloc}.ref must be a string")
            if len(n) != 1:
                errors.append(f"{nloc} ref cannot coexist with other fields")
            continue
        if "pitch" not in n and not isinstance(n.get("chord"), list):
            errors.append(f"{nloc} missing pitch/chord")
        if "pitch" in n and not _is_pitch_ok(n["pitch"]):
            errors.append(f"{nloc}.pitch out of range: {n['pitch']}")
        if "chord" in n and isinstance(n["chord"], list):
            for cp in n["chord"]:
                if not _is_pitch_ok(cp):
                    errors.append(f"{nloc}.chord out of range: {cp}")
        d = n.get("duration")
        if d not in DURATIONS:
            errors.append(f"{nloc}.duration invalid: {d}")
        v = n.get("velocity")
        if v is not None and not (isinstance(v, int) and 0 <= v <= 127):
            warnings.append(f"{nloc}.velocity out of range: {v}")
        if "tuplet" in n and n["tuplet"] not in TUP:
            errors.append(f"{nloc}.tuplet invalid: {n['tuplet']}")
        if "articulation" in n and n["articulation"] not in ARTICULATIONS:
            errors.append(f"{nloc}.articulation invalid: {n['articulation']}")
        if "dynamics" in n and n["dynamics"] not in DYNAMICS:
            errors.append(f"{nloc}.dynamics invalid: {n['dynamics']}")
        for k, allowed in (("tie", TIE_SLUR), ("slur", TIE_SLUR), ("pedal", PEDAL),
                           ("navigation", NAVIGATION), ("hairpin", HAIRPIN)):
            if k in n and n[k] not in allowed:
                errors.append(f"{nloc}.{k} invalid: {n[k]}")
        if "ornament" in n and n["ornament"] not in ORNAMENTS:
            errors.append(f"{nloc}.ornament invalid: {n['ornament']}")
        for k, limit in (("lyric", 100), ("text", 200), ("expression", 200)):
            if k in n and n[k] is not None:
                if not isinstance(n[k], str):
                    errors.append(f"{nloc}.{k} must be a string")
                elif len(n[k]) > limit:
                    errors.append(f"{nloc}.{k} exceeds {limit} characters")
        if "volta" in n and (not isinstance(n["volta"], int) or not 1 <= n["volta"] <= 4):
            errors.append(f"{nloc}.volta must be an integer 1-4: {n.get('volta')}")
        if "time_signature_change" in n and not re.fullmatch(r"\d+/\d+", str(n["time_signature_change"])):
            errors.append(f"{nloc}.time_signature_change invalid format: {n['time_signature_change']}")
        if "key_signature_change" in n and not isinstance(n["key_signature_change"], str):
            errors.append(f"{nloc}.key_signature_change must be a string")
        if "grace_note" in n:
            gn = n["grace_note"]
            if not isinstance(gn, dict):
                errors.append(f"{nloc}.grace_note must be an object")
            else:
                if not _is_pitch_ok(gn.get("pitch")):
                    errors.append(f"{nloc}.grace_note.pitch missing or out of range")
                if "duration" in gn and gn["duration"] not in DURATIONS:
                    errors.append(f"{nloc}.grace_note.duration invalid: {gn['duration']}")
        if "tremolo" in n:
            tr = n["tremolo"]
            if not isinstance(tr, dict) or tr.get("duration") not in DURATIONS:
                errors.append(f"{nloc}.tremolo must be an object with valid duration")
        if "tempo_gradual" in n:
            tg = n["tempo_gradual"]
            if not isinstance(tg, dict) or not (isinstance(tg.get("target_bpm"), int)
                                                and 20 <= tg["target_bpm"] <= 300):
                errors.append(f"{nloc}.tempo_gradual must contain target_bpm(20-300)")
        for k in ("arpeggio", "glissando", "fermata"):
            if k in n and n[k] is not True:
                errors.append(f"{nloc}.{k} must be true")
        for k in ("repeat_begin", "repeat_end"):
            if k in n and n[k] is not True:
                errors.append(f"{nloc}.{k} must be true")


def validate(score):
    """Validate against the spec; return (ok, errors, warnings)."""
    errors, warnings = [], []
    if not isinstance(score, dict):
        return False, ["top-level is not a JSON object"], []

    # top-level extension fields
    if "loop" in score and score["loop"] is not True:
        errors.append("top-level loop must be true (or omitted)")
    if "category" in score and score["category"] not in CATEGORIES:
        errors.append(f"top-level category invalid: {score['category']}")

    # macros
    macros = score.get("macros")
    if macros is not None:
        if not isinstance(macros, dict):
            errors.append("macros must be an object")
        else:
            for mname, mnotes in macros.items():
                if not isinstance(mnotes, list) or not mnotes:
                    errors.append(f"macros.{mname} must be a non-empty array")
                    continue
                _validate_notes(mnotes, errors, warnings, f"macros.{mname}", allow_ref=False, depth=1)

    meta = score.get("metadata")
    if not isinstance(meta, dict):
        errors.append("missing metadata object")
    else:
        if not isinstance(meta.get("tempo_bpm"), int):
            errors.append("metadata.tempo_bpm missing or not an integer")
        if meta.get("time_signature") not in TIME_SIGS:
            warnings.append(f"metadata.time_signature recommended: {sorted(TIME_SIGS)}")
        if not meta.get("key_signature"):
            warnings.append("metadata.key_signature missing (default C)")

    tracks = score.get("tracks")
    if not isinstance(tracks, list) or not tracks:
        errors.append("tracks missing or empty array")
        return not errors, errors, warnings

    # collect refs for macro existence check
    defined_macros = set(macros) if isinstance(macros, dict) else set()

    for ti, tr in enumerate(tracks):
        if not isinstance(tr, dict):
            errors.append(f"tracks[{ti}] is not an object")
            continue
        if not isinstance(tr.get("instrument"), str) or not tr["instrument"]:
            errors.append(f"tracks[{ti}] missing instrument string")
        notes = tr.get("notes")
        if not isinstance(notes, list) or not notes:
            errors.append(f"tracks[{ti}].notes missing or empty")
            continue
        tloc = f"tracks[{ti}]"
        _validate_notes(notes, errors, warnings, tloc)
        for ni, n in enumerate(notes):
            if isinstance(n, dict) and n.get("ref") is not None:
                if n["ref"] not in defined_macros:
                    errors.append(f"tracks[{ti}].notes[{ni}] references undefined macro: {n['ref']}")
        # semantic pairing checks per field
        _check_pairing(notes, "tie", errors, warnings, tloc, require_same_pitch=True)
        _check_pairing(notes, "slur", errors, warnings, tloc)
        _check_pairing(notes, "pedal", errors, warnings, tloc)
        _check_pairing(notes, "hairpin", errors, warnings, tloc)
        _check_tuplets(notes, errors, warnings, tloc)
        # navigation: D.C./D.S. should be followed by Fine/Coda somewhere
        navs = [n.get("navigation") for n in notes if isinstance(n, dict) and n.get("navigation")]
        if navs and not ({"Fine", "Coda"} & set(navs)):
            warnings.append(f"tracks[{ti}] has {navs} but no Fine/Coda in the piece")

    return not errors, errors, warnings


def normalize(score):
    """Fill in defaults and sanitize field formats so DoMuse.exe accepts the score."""
    if not isinstance(score, dict):
        score = {}
    score.setdefault("title", "Untitled")
    score.setdefault("composer", "VibeDoMuse")
    meta = score.get("metadata")
    if not isinstance(meta, dict):
        meta = {}
        score["metadata"] = meta
    ts = str(meta.get("time_signature") or "4/4").replace(" ", "")
    meta["time_signature"] = ts if ts in TIME_SIGS else "4/4"
    try:
        tb = int(meta.get("tempo_bpm"))
    except (TypeError, ValueError):
        tb = 90
    meta["tempo_bpm"] = max(40, min(220, tb))
    key = str(meta.get("key_signature") or "C").strip()
    meta["key_signature"] = key if key else "C"
    for tr in score.get("tracks", []):
        if not isinstance(tr, dict):
            continue
        tr.setdefault("instrument", "Acoustic Grand Piano")
        for n in tr.get("notes", []):
            if isinstance(n, dict):
                n.setdefault("velocity", 80)
    return score


# ----------------------------------------------------------------------------
# duration estimation (quarter-note units) for a note list
# ----------------------------------------------------------------------------
_DUR_Q = {
    "whole": 4.0, "half": 2.0, "quarter": 1.0, "eighth": 0.5, "16th": 0.25,
    "32nd": 0.125, "64th": 0.0625,
    "half.": 3.0, "quarter.": 1.5, "eighth.": 0.75, "16th.": 0.375, "32nd.": 0.1875,
}
TUP_FACTOR = {3: 2 / 3, 5: 4 / 5, 6: 4 / 6, 7: 4 / 7, 9: 8 / 9}


def _notes_duration_q(notes):
    total = 0.0
    for n in notes:
        if not isinstance(n, dict):
            continue
        if n.get("ref") is not None:
            continue
        d = _DUR_Q.get(n.get("duration"), 1.0)
        tup = n.get("tuplet")
        if tup in TUP_FACTOR:
            d *= TUP_FACTOR[tup]
        total += d
    return total


def to_params(score):
    """Derive MusicParams from a validated score (for template search and display).

    v2: category comes from an optional top-level "category" field (inferred from
    track count / instruments otherwise); duration is computed from the note stream.
    """
    meta = score.get("metadata", {}) or {}
    key = meta.get("key_signature") or "C"
    tracks = score.get("tracks") or []
    inst = "Acoustic Grand Piano"
    if tracks and isinstance(tracks[0], dict) and tracks[0].get("instrument"):
        inst = tracks[0]["instrument"]

    category = score.get("category")
    if category not in CATEGORIES:
        n_tracks = len([t for t in tracks if isinstance(t, dict)])
        insts = [str(t.get("instrument", "")).lower()
                 for t in tracks if isinstance(t, dict)]
        has_strings = any("string" in i or "ensemble" in i or "violin" in i or "cello" in i
                          for i in insts)
        if n_tracks >= 3 or has_strings:
            category = "galgame_v3"
        elif n_tracks == 1:
            category = "galgame_bgm"
        else:
            category = "galgame_accompaniment"

    bpm = int(meta.get("tempo_bpm") or 90)
    # duration: beats of the first non-empty track -> seconds
    duration_sec = 30
    for tr in tracks:
        if isinstance(tr, dict) and tr.get("notes"):
            q = _notes_duration_q(tr["notes"])
            if q > 0:
                duration_sec = int(round(q * 60.0 / bpm))
            break
    duration_sec = max(5, min(300, duration_sec))

    return MusicParams(
        text="",
        mood="gentle",
        key=str(key),
        is_minor=str(key).endswith("m") or str(key).islower(),
        tempo_bpm=bpm,
        time_sig=meta.get("time_signature") or "4/4",
        instrument=inst,
        tracks=max(1, len([t for t in tracks if isinstance(t, dict)])),
        category=category,
        duration_sec=duration_sec,
        drums=any("timpani" in str(t.get("instrument", "")).lower()
                  or "taiko" in str(t.get("instrument", "")).lower()
                  for t in tracks if isinstance(t, dict)),
        loop=bool(score.get("loop")),
    )
