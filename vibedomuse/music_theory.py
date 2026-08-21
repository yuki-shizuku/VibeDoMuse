# -*- coding: utf-8 -*-
"""
VibeDoMuse · music_theory.py
Core music theory and generation primitives.

Provides: chord parsing, scale building, key mapping, mood profiles, and
accompaniment/melody/string-pad/drums texture generators.

v2 improvements:
- Clean key parsing (parse_key) — no more contradictory is_minor branches.
- Melody is motif-driven (repeat / sequence / variation), with leap-then-step-back
  and a cadence approach on the final phrase, instead of pure random tone picking.
- Accompaniment uses voice leading (minimal motion between successive chords).
- Phrase-level dynamic curves (crescendo -> diminuendo) instead of flat velocity.
- Measure-aligned generation helpers (beats_per_measure / align_measures).
- Cadence-aware progressions (with_cadence ends on the tonic).
- Percussion via GM pitched-percussion instruments (e.g. Timpani), because the
  DoMuse engine maps "Drum Kit" to a piano program (verified experimentally).

Every generator only emits note dicts that comply with the Do-muse JSON spec
(pitch 21-108, valid duration, velocity 0-127).
"""
import random
from dataclasses import dataclass, field

# Constants
VARIANT_MULTIPLIER = 7919  # Multiplier for generating seed variants (prime number)

# ----------------------------------------------------------------------------
# note name -> semitone offset (C = 0)
# ----------------------------------------------------------------------------
_NOTE_SEMITONE = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
    "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
}

_SEMITONE_NOTE = {
    0: "C", 1: "Db", 2: "D", 3: "Eb", 4: "E", 5: "F", 6: "F#",
    7: "G", 8: "Ab", 9: "A", 10: "Bb", 11: "B",
}

_DURATION_BEATS = {
    "whole": 4.0, "half": 2.0, "quarter": 1.0, "eighth": 0.5, "16th": 0.25,
}


def clamp_pitch(p, lo=21, hi=108):
    return max(lo, min(hi, int(round(p))))


# ----------------------------------------------------------------------------
# key / scale helpers
# ----------------------------------------------------------------------------
def parse_key(key):
    """Parse a key signature string into (root_note_name, is_minor).

    Accepts "C", "G", "F", "Bb", "F#", "Am", "Em", "Dm", "a", "e", "b", "Cmaj"...
    """
    k = str(key or "").strip().lower()
    is_minor = False
    if k.endswith("m") and not k.startswith("ma"):
        is_minor = True
        k = k[:-1]
    elif k in ("a", "e", "b"):
        is_minor = True
    root = k[0].upper()
    if len(k) > 1 and k[1] in ("#", "b"):
        root += k[1]          # keep the accidental as-is: "Bb", "F#"
    if root not in _NOTE_SEMITONE:
        root = "C"
    return root, is_minor


def build_scale(key_signature, octave=4, octaves=2):
    """Build a MIDI scale list for the key (used for BGM melody style)."""
    root, is_minor = parse_key(key_signature)
    base = (octave + 1) * 12 + _NOTE_SEMITONE[root]
    ivs = [0, 2, 3, 5, 7, 8, 10] if is_minor else [0, 2, 4, 5, 7, 9, 11]
    scale = []
    for o in range(octaves):
        for iv in ivs:
            scale.append(base + iv + o * 12)
    return scale


def normalize_key(text):
    """Infer a key_signature string (e.g. 'C' / 'Am' / 'a') from text.

    Returns (key, is_minor) or None.
    """
    t = text.lower()
    letter = None
    for L in ("c", "d", "e", "f", "g", "a", "b"):
        if L in t:
            letter = L
            break
    if letter is None:
        return None
    is_minor = ("小调" in text) or ("minor" in t) or ("マイナー" in t)
    if "大调" in text or "major" in t or "メジャー" in t:
        is_minor = False
    if is_minor:
        return (letter.upper() if letter != "a" else "a") + ("m" if letter != "a" else ""), True
    return letter.upper(), False


# ----------------------------------------------------------------------------
# chord parsing
# ----------------------------------------------------------------------------
def parse_chord(name):
    """Parse a chord name into (root note name, interval list in semitones)."""
    name = name.strip()
    i = 1
    if len(name) > 1 and name[1] in ("#", "b"):
        i = 2
    root = name[:i]
    quality = name[i:]
    if root not in _NOTE_SEMITONE:
        root, quality = "C", name

    if quality.startswith("m7b5"):
        intervals = [0, 3, 6, 10]
    elif quality.startswith("maj7"):
        intervals = [0, 4, 7, 11]
    elif quality.startswith("m7"):
        intervals = [0, 3, 7, 10]
    elif quality.startswith("dim7"):
        intervals = [0, 3, 6, 9]
    elif quality.startswith("dim"):
        intervals = [0, 3, 6]
    elif quality.startswith("aug"):
        intervals = [0, 4, 8]
    elif quality.startswith("sus4"):
        intervals = [0, 5, 7]
    elif quality.startswith("sus"):
        intervals = [0, 2, 7]
    elif quality.startswith("7"):
        intervals = [0, 4, 7, 10]
    elif quality.startswith("m"):
        intervals = [0, 3, 7]
    elif quality.startswith("6"):
        intervals = [0, 4, 7, 9]
    elif quality.startswith("9"):
        intervals = [0, 4, 7, 10, 14]
    elif quality.startswith("add9"):
        intervals = [0, 4, 7, 14]
    else:
        intervals = [0, 4, 7]
    return root, intervals


def chord_pitches(name, octave=4, inversion=0, shift=0):
    """Return the absolute MIDI pitches of a chord.
    octave: scientific pitch octave (C4=60). inversion: 0/1/2. shift: extra octaves."""
    root, intervals = parse_chord(name)
    base = (octave + 1) * 12 + _NOTE_SEMITONE[root] + shift * 12
    pitches = [base + iv for iv in intervals]
    n = len(pitches)
    if inversion == 1 and n >= 3:
        pitches = [pitches[1], pitches[2], pitches[0] + 12]
    elif inversion == 2 and n >= 3:
        pitches = [pitches[2], pitches[0] + 12, pitches[1] + 12]
    return pitches


def _root_of(chord):
    return parse_chord(str(chord))[0]


def _name_from_semitones(s):
    return _SEMITONE_NOTE[s % 12]


def with_cadence(progression, key, max_len=8):
    """Append a cadence (IV-V-I / V-I) so the progression ends on the tonic.

    No-op if the progression already ends on the tonic or is already long.
    """
    root, is_minor = parse_key(key)
    prog = [str(c) for c in progression]
    if prog and _root_of(prog[-1]) == root:
        return prog
    if len(prog) >= max_len:
        return prog
    fourth = _name_from_semitones(_NOTE_SEMITONE[root] + 5)
    fifth = _name_from_semitones(_NOTE_SEMITONE[root] + 7)
    sub = fourth + ("m" if is_minor else "")
    dom = fifth + "7"
    cand = prog + [sub, dom, root]
    if len(cand) > max_len:
        cand = prog + [dom, root]
    return cand


# ----------------------------------------------------------------------------
# measure alignment & dynamics helpers
# ----------------------------------------------------------------------------
def beats_per_measure(time_sig):
    """Quarter-note beats per measure for a time signature like '4/4', '6/8'."""
    try:
        num, den = [int(x) for x in str(time_sig).split("/")]
        return max(1, num * 4 // den)
    except Exception:
        return 4


def align_measures(total_beats, time_sig):
    """Round a beat total up/down to whole measures.

    Returns (aligned_beats, measures).
    """
    bpm_ = beats_per_measure(time_sig)
    measures = max(1, round(total_beats / bpm_))
    return measures * bpm_, measures


def dynamic_shape(n_phrases, peak=0.6):
    """Return a per-phrase velocity multiplier list (rise to a peak, then fall)."""
    if n_phrases <= 1:
        return [1.0]
    out = []
    p = max(0.1, min(0.9, peak))
    for i in range(n_phrases):
        t = i / max(1, n_phrases - 1)
        if t <= p:
            m = 0.72 + 0.28 * (t / p)
        else:
            m = 1.0 - 0.32 * ((t - p) / max(1e-9, 1 - p))
        out.append(max(0.55, min(1.0, m)))
    return out


# ----------------------------------------------------------------------------
# voice leading (minimal motion between consecutive chords)
# ----------------------------------------------------------------------------
def voice_lead(prev_pitches, next_pitches):
    """Map next_pitches to stay as close as possible to prev_pitches.

    Returns a reordered / octave-adjusted voicing of next_pitches.
    """
    if not prev_pitches:
        return sorted(next_pitches)
    next_pitches = list(next_pitches)
    used = [False] * len(next_pitches)
    result = [None] * len(next_pitches)
    order = sorted(range(len(prev_pitches)),
                   key=lambda k: min(abs(p - prev_pitches[k]) for p in next_pitches))
    for k in order:
        best = None
        best_d = None
        for i, np_ in enumerate(next_pitches):
            if used[i]:
                continue
            cand = min((np_ + 12 * o for o in (-1, 0, 1)),
                       key=lambda x: abs(x - prev_pitches[k]))
            d = abs(cand - prev_pitches[k])
            if best_d is None or d < best_d:
                best, best_d = i, d
        if best is not None:
            np_ = next_pitches[best]
            result[k] = min((np_ + 12 * o for o in (-1, 0, 1)),
                            key=lambda x: abs(x - prev_pitches[k]))
            used[best] = True
    # remaining unassigned notes (next has more voices than prev)
    anchor = sum(prev_pitches) / len(prev_pitches)
    for i, np_ in enumerate(next_pitches):
        if not used[i]:
            result[i] = min((np_ + 12 * o for o in (-1, 0, 1)),
                            key=lambda x: abs(x - anchor))
    return sorted(r for r in result if r is not None)


# ----------------------------------------------------------------------------
# melody helpers
# ----------------------------------------------------------------------------
def _pick_near(pitch, scale, step):
    """Return a scale note `step` positions away from pitch (bounded)."""
    if pitch not in scale:
        pitch = min(scale, key=lambda s: abs(s - pitch))
    idx = scale.index(pitch)
    return scale[max(0, min(len(scale) - 1, idx + step))]


def _nearest_duration(beats):
    best = "16th"
    for d, v in sorted(_DURATION_BEATS.items(), key=lambda x: x[1]):
        if v <= beats + 1e-9:
            best = d
    return best


def make_motif(chord_name, scale, rng, length=None):
    """Build a short melodic motif (2-4 notes) from chord tones + scale steps."""
    tones = sorted({clamp_pitch(p, 48, 96)
                    for p in chord_pitches(chord_name, octave=4)
                    + [p + 12 for p in chord_pitches(chord_name, octave=4)]})
    length = length or rng.choice([2, 3, 4])
    motif = []
    for i in range(length):
        if i == 0:
            p = rng.choice(tones)
        else:
            prev = motif[-1]
            if rng.random() < 0.65:
                p = _pick_near(prev, scale, rng.choice([-2, -1, 1, 2]))
            else:
                p = rng.choice(tones)
        motif.append(clamp_pitch(p, 48, 96))
    return motif


def _continue_melody(last, tones, scale, rng):
    """Pick the next melodic note near `last`, preferring small scale steps."""
    if last in scale:
        idx = scale.index(last)
        cands = []
        for step in (1, 2, -1, -2):
            j = idx + step
            if 0 <= j < len(scale):
                cands.append(scale[j])
        if rng.random() < 0.45 and tones:
            cands.append(rng.choice(tones))
        return rng.choice(cands) if cands else last
    return min(tones, key=lambda t: abs(t - last)) if tones else last


def gen_melody(chord_name, scale, beats, bpm, style="lyrical", seed=None,
               phrase_index=0, n_phrases=1, curve=None, motif=None, transpose=0):
    """Generate a melody phrase.

    - motif: optional motif (absolute pitches) reused / transposed per phrase.
    - transpose: semitone shift applied to the motif for this phrase.
    - curve: list of per-phrase velocity multipliers.
    - The final phrase ends by approaching the tonic.
    """
    rng = random.Random((seed or 0) + phrase_index * VARIANT_MULTIPLIER)
    pitches = chord_pitches(chord_name, octave=4)
    root = pitches[0]
    third = pitches[1] if len(pitches) > 1 else root + 4
    fifth = pitches[2] if len(pitches) > 2 else root + 7
    tones = sorted({clamp_pitch(p, 48, 96)
                    for p in [root, third, fifth, root + 12, third + 12, fifth + 12]})
    if len(pitches) >= 4:
        tones.append(clamp_pitch(pitches[3], 48, 96))
        tones = sorted(set(tones))
    mult = (curve[phrase_index] if curve and phrase_index < len(curve) else 1.0)

    pools = {
        "flowing": ["eighth", "eighth", "quarter", "quarter"],
        "lyrical": ["quarter", "quarter", "eighth", "eighth", "half"],
        "sparse": ["half", "quarter", "quarter", "half"],
    }
    pool = pools.get(style, pools["lyrical"])

    notes = []
    pos = 0.0
    idx = 0
    last_pitch = None
    max_iter = 200
    it = 0
    while pos < beats - 1e-9 and it < max_iter:
        it += 1
        dur = rng.choice(pool)
        dv = _DURATION_BEATS[dur]
        if pos + dv > beats + 1e-9:
            dv = max(0.0, beats - pos)
            dur = _nearest_duration(dv)
            dv = _DURATION_BEATS[dur]
            if dv < 0.2:
                break
        # pitch selection: motif cycle -> continuation
        if motif and idx < len(motif):
            p = clamp_pitch(motif[idx] + (transpose or 0), 48, 96)
            if rng.random() < 0.2:
                p = clamp_pitch(p + (12 if rng.random() < 0.5 else -12), 48, 96)
        elif motif:
            p = _continue_melody(last_pitch or motif[-1], tones, scale, rng)
        else:
            p = rng.choice(tones)
        # leap-then-step-back: after a big leap, prefer stepping back
        if last_pitch is not None and abs(p - last_pitch) > 7 and rng.random() < 0.7:
            p = _pick_near(last_pitch, scale, rng.choice([-1, 1]))
        p = clamp_pitch(p, 48, 96)
        last_pitch = p
        v = int(rng.randint(60, 85) * mult)
        v = max(1, min(127, v))
        notes.append({"pitch": p, "duration": dur, "velocity": v})
        pos += dv
        idx += 1
    # final phrase: resolve to the tonic on the last note
    if notes and phrase_index == max(0, n_phrases - 1):
        last = notes[-1]
        notes[-1] = {"pitch": clamp_pitch(root, 48, 96), "duration": last["duration"],
                     "velocity": last["velocity"]}
    return notes


# ----------------------------------------------------------------------------
# accompaniment textures (voice-leading aware)
# ----------------------------------------------------------------------------
def gen_accompaniment(pattern, chord_name, beats, bpm, seed=None, prev_pitches=None,
                      vel_scale=1.0, measure_beats=4):
    rng = random.Random(seed)
    pitches = chord_pitches(chord_name, octave=4)
    voicing = voice_lead(prev_pitches, pitches)
    root = voicing[0]
    third = voicing[1] if len(voicing) > 1 else root + 4
    fifth = voicing[2] if len(voicing) > 2 else root + 7
    notes = []
    beats = int(round(beats))

    def V(v):
        return max(1, min(127, int(v * vel_scale)))

    if pattern == "arpeggio_1353":
        arp = [root - 12, root, third, fifth, third, root, third, fifth]
        for i in range(min(beats * 2, 64)):
            p = arp[i % len(arp)]
            vel = 45 if p < 48 else 35
            notes.append({"pitch": clamp_pitch(p), "duration": "eighth", "velocity": V(vel)})
    elif pattern == "block_chord":
        for _ in range(max(1, beats)):
            for p in [root - 12, third - 12, fifth - 12]:
                notes.append({"pitch": clamp_pitch(p), "duration": "quarter", "velocity": V(40)})
    elif pattern == "waltz":
        step = 3
        for _ in range(max(1, beats // step + (1 if beats % step else 0))):
            notes.append({"pitch": clamp_pitch(root - 12), "duration": "quarter.", "velocity": V(50)})
            notes.append({"pitch": clamp_pitch(third), "duration": "quarter", "velocity": V(35)})
            notes.append({"pitch": clamp_pitch(fifth), "duration": "quarter", "velocity": V(35)})
    elif pattern == "alternating_bass":
        for _ in range(max(1, beats // 2)):
            notes.append({"pitch": clamp_pitch(root - 12), "duration": "half", "velocity": V(48)})
            notes.append({"pitch": clamp_pitch(fifth - 12), "duration": "half", "velocity": V(42)})
    elif pattern == "syncopated":
        chord_notes = [root - 12, third, fifth]
        for _ in range(max(1, beats // 2)):
            for p in chord_notes:
                notes.append({"pitch": clamp_pitch(p), "duration": "quarter", "velocity": V(30)})
            for p in chord_notes:
                notes.append({"pitch": clamp_pitch(p), "duration": "quarter", "velocity": V(30)})
    elif pattern == "broad_arpeggio":
        arp = [root - 12, root, third, fifth, root + 12, third + 12, fifth + 12, root + 12]
        for i in range(min(beats, 48)):
            p = arp[i % len(arp)]
            vel = 42 if p < 60 else 35
            notes.append({"pitch": clamp_pitch(p), "duration": "quarter", "velocity": V(vel)})
    elif pattern == "syncopated_chord":
        for beat in range(max(1, beats)):
            if beat % 2 == 0:
                notes.append({"pitch": clamp_pitch(root - 12), "duration": "quarter", "velocity": V(48)})
            else:
                for p in [root, third, fifth]:
                    notes.append({"pitch": clamp_pitch(p), "duration": "quarter", "velocity": V(32)})
    elif pattern == "gentle_rock":
        for _ in range(max(1, beats)):
            notes.append({"pitch": clamp_pitch(root - 12), "duration": "eighth", "velocity": V(45)})
            for p in [third, fifth]:
                notes.append({"pitch": clamp_pitch(p), "duration": "eighth", "velocity": V(30)})
    elif pattern == "ballad_arp":
        arp_seq = [root - 12, third, root, fifth, root, third, fifth, root + 12]
        dur_seq = ["eighth", "eighth", "quarter", "quarter", "eighth", "eighth", "quarter", "quarter"]
        for i in range(min(beats * 2, 64)):
            notes.append({"pitch": clamp_pitch(arp_seq[i % len(arp_seq)]),
                          "duration": dur_seq[i % len(dur_seq)],
                          "velocity": V(40 if arp_seq[i % len(arp_seq)] < 60 else 32)})
    elif pattern == "pulse_chord":
        for _ in range(max(1, beats)):
            for p in [root - 12, third - 12, fifth - 12]:
                notes.append({"pitch": clamp_pitch(p), "duration": "quarter", "velocity": V(38)})
    else:
        for _ in range(max(1, beats)):
            for p in [root - 12, third - 12, fifth - 12]:
                notes.append({"pitch": clamp_pitch(p), "duration": "quarter", "velocity": V(40)})
    return notes


def gen_pad(chord_name, beats, bpm, seed=None, prev_pitches=None, vel_scale=1.0):
    pitches = voice_lead(prev_pitches, chord_pitches(chord_name, octave=4, inversion=1))
    notes = []
    beats = int(round(beats))
    for i in range(0, max(2, beats), 2):
        remaining = beats - i
        dur = "whole" if remaining >= 4 else ("half" if remaining >= 2 else "quarter")
        for p in pitches[:3]:
            pad_p = p - 12
            if pad_p < 36:
                pad_p = p
            v = max(1, min(127, int(25 * vel_scale)))
            notes.append({"pitch": clamp_pitch(pad_p), "duration": dur, "velocity": v})
    return notes


# ----------------------------------------------------------------------------
# percussion (GM pitched percussion: Timpani etc.)
# ----------------------------------------------------------------------------
PERCUSSION_INSTRUMENTS = ("Timpani", "Taiko Drum", "Melodic Tom", "Synth Drum", "Woodblock")


def gen_drums(pattern, beats, bpm, seed=None, instrument="Timpani", measure_beats=4):
    """Generate a percussion track using a pitched percussion instrument.

    NOTE: the DoMuse engine maps "Drum Kit" to a piano program, so true GM drums
    are unavailable; pitched percussion (Timpani default) is used instead.
    """
    rng = random.Random(seed)
    notes = []
    beats = int(round(beats))
    mb = max(1, measure_beats or 4)
    if pattern in ("kick4", "rock_drums"):
        pos = 0.0
        i = 0
        while pos < beats - 1e-9 and i < 256:
            i += 1
            in_m = pos % mb
            if pattern == "kick4":
                if abs(in_m) < 0.05 or abs(in_m - 2.0) < 0.05:
                    notes.append({"pitch": 38, "duration": "quarter", "velocity": 96})
                else:
                    notes.append({"pitch": 41, "duration": "eighth", "velocity": 72})
            else:
                if abs(in_m - 2.0) < 0.05:
                    notes.append({"pitch": 41, "duration": "eighth", "velocity": 84})
                elif abs(in_m - 3.5) < 0.05:
                    notes.append({"pitch": 41, "duration": "eighth", "velocity": 76})
                else:
                    notes.append({"pitch": 38, "duration": "eighth", "velocity": 88})
            pos += 0.5
    else:  # soft pulse
        for b in range(max(1, beats)):
            vel = 84 if b % mb == 0 else 60
            notes.append({"pitch": 38, "duration": "quarter", "velocity": vel})
    return notes


# ----------------------------------------------------------------------------
# mood profiles
# ----------------------------------------------------------------------------
@dataclass
class MoodProfile:
    mood: str
    cn: str
    jp: str
    pattern: str          # default accompaniment texture
    tempo: int
    time_sig: str
    instrument: str       # melody instrument
    tracks: int           # 1 / 2 / 3
    mode: str             # major / minor
    category: str         # galgame_bgm / galgame_accompaniment / galgame_v3
    progressions: list = field(default_factory=list)  # default chord progressions
    desc: str = ""


MOOD_PROFILES = {
    "gentle": MoodProfile("gentle", "温柔", "優しい", "arpeggio_1353", 90, "4/4",
                           "Acoustic Grand Piano", 2, "major", "galgame_accompaniment",
                           [["C", "G", "Am", "F"], ["C", "Am", "F", "G"], ["C", "G", "Am", "Em", "F", "C", "F", "G"]],
                           "温柔舒缓的钢琴琶音"),
    "calm": MoodProfile("calm", "沉稳", "落ち着いた", "block_chord", 80, "4/4",
                        "Acoustic Grand Piano", 2, "major", "galgame_accompaniment",
                        [["C", "F", "G", "C"], ["F", "G", "Em", "Am"]], "沉稳的柱式和弦"),
    "elegant": MoodProfile("elegant", "优雅", "優雅", "waltz", 100, "3/4",
                           "Acoustic Grand Piano", 2, "major", "galgame_accompaniment",
                           [["C", "G", "Am", "Em", "F", "C", "F", "G"], ["C", "F", "G", "C"]], "优雅的华尔兹"),
    "lively": MoodProfile("lively", "轻快", "軽快", "alternating_bass", 110, "4/4",
                          "Acoustic Grand Piano", 2, "major", "galgame_accompaniment",
                          [["C", "F", "G", "C"], ["G", "D", "Em", "C"]], "轻快的交替低音"),
    "refreshing": MoodProfile("refreshing", "清爽", "爽やか", "syncopated", 95, "4/4",
                              "Acoustic Grand Piano", 2, "major", "galgame_accompaniment",
                              [["C", "G", "Am", "F"], ["Am", "F", "G", "C"]], "清爽的切分节奏"),
    "cheerful": MoodProfile("cheerful", "欢快", "明るい", "broad_arpeggio", 100, "4/4",
                            "Acoustic Grand Piano", 3, "major", "galgame_v3",
                            [["C", "Em", "F", "G"], ["G", "C", "Am", "D"]], "欢快明亮的织体"),
    "warm": MoodProfile("warm", "温暖", "温かい", "ballad_arp", 90, "4/4",
                        "Acoustic Grand Piano", 3, "major", "galgame_v3",
                        [["F", "C", "Dm", "Bb"], ["C", "F", "G", "C"]], "温暖的民谣琶音"),
    "uplifting": MoodProfile("uplifting", "激昂", "高揚", "gentle_rock", 105, "4/4",
                             "Acoustic Grand Piano", 3, "major", "galgame_v3",
                             [["D", "Bm", "G", "A"], ["C", "G", "Am", "F"]], "激昂稳健的律动"),
    "tender": MoodProfile("tender", "温柔", "優しい", "ballad_arp", 82, "4/4",
                          "Acoustic Grand Piano", 3, "major", "galgame_v3",
                          [["F", "C", "Dm", "Bb"], ["C", "Am", "F", "G"]], "温柔的抒情"),
    "smart": MoodProfile("smart", "潇洒", "洒落", "syncopated_chord", 92, "4/4",
                         "Acoustic Grand Piano", 3, "major", "galgame_v3",
                         [["Bb", "Gm", "Eb", "F"], ["Cmaj7", "Am7", "Fmaj7", "G7"]], "潇洒的爵士切分"),
    "rich": MoodProfile("rich", "丰富", "豊か", "pulse_chord", 90, "4/4",
                        "Acoustic Grand Piano", 3, "major", "galgame_v3",
                        [["Eb", "Cm", "Ab", "Bb"], ["C", "F", "G", "C"]], "丰富的和声铺底"),
    "bright": MoodProfile("bright", "明亮", "明るい", "broad_arpeggio", 100, "4/4",
                          "Acoustic Grand Piano", 3, "major", "galgame_v3",
                          [["A", "D", "F#m", "E"], ["C", "G", "Am", "F"]], "明亮的开放和声"),
    "melancholic": MoodProfile("melancholic", "忧伤", "物悲しい", "ballad_arp", 78, "4/4",
                               "Acoustic Grand Piano", 3, "minor", "galgame_v3",
                               [["Am", "Dm", "E7", "Am"], ["Am", "Em", "F", "G"]], "忧伤的小调抒情"),
    "thoughtful": MoodProfile("thoughtful", "沉思", "思案", "pulse_chord", 88, "4/4",
                              "Acoustic Grand Piano", 3, "minor", "galgame_v3",
                              [["Em", "C", "G", "D"], ["Am", "Em", "F", "G"]], "沉思的小调氛围"),
    "dramatic": MoodProfile("dramatic", "戏剧", "劇的", "gentle_rock", 100, "4/4",
                            "Acoustic Grand Piano", 3, "minor", "galgame_v3",
                            [["Dm", "Gm", "C7", "F"], ["Am", "Dm", "E7", "Am"]], "戏剧性的小调推进"),
    "sad": MoodProfile("sad", "悲伤", "悲しい", "block_chord", 70, "4/4",
                       "Acoustic Grand Piano", 2, "minor", "galgame_bgm",
                       [["Am", "Em", "F", "G"], ["Dm", "G", "C", "Am"]], "悲伤的下行旋律"),
    "romantic": MoodProfile("romantic", "浪漫", "ロマンチック", "arpeggio_1353", 82, "4/4",
                            "Violin", 2, "major", "galgame_bgm",
                            [["C", "Am", "F", "G"], ["G", "Em", "Am", "C"]], "浪漫的弦乐/钢琴"),
    "dreamy": MoodProfile("dreamy", "梦幻", "夢", "arpeggio_1353", 80, "3/4",
                          "Music Box", 2, "major", "galgame_bgm",
                          [["C", "Em", "F", "G"], ["F", "G", "Em", "Am"]], "梦幻的八音盒"),
    "tense": MoodProfile("tense", "紧张", "緊張", "syncopated", 95, "4/4",
                         "Acoustic Grand Piano", 2, "minor", "galgame_bgm",
                         [["Am", "Em", "F", "E"], ["Dm", "A", "Bb", "A"]], "紧张的半音动机"),
    "intense": MoodProfile("intense", "激烈", "激しい", "alternating_bass", 140, "4/4",
                           "Acoustic Grand Piano", 2, "major", "galgame_bgm",
                           [["C", "G", "Am", "F"], ["G", "D", "Em", "C"]], "激烈的强奏"),
    "nostalgic": MoodProfile("nostalgic", "怀旧", "懐かしい", "ballad_arp", 75, "4/4",
                             "Acoustic Grand Piano", 2, "major", "galgame_bgm",
                             [["C", "F", "G", "C"], ["G", "Em", "Am", "C"]], "怀旧的慢板"),
    "peaceful": MoodProfile("peaceful", "宁静", "穏やか", "block_chord", 72, "4/4",
                            "Acoustic Grand Piano", 2, "major", "galgame_bgm",
                            [["C", "F", "G", "C"], ["F", "C", "Dm", "G"]], "宁静的夜色"),
    "hopeful": MoodProfile("hopeful", "希望", "希望", "broad_arpeggio", 100, "4/4",
                           "Acoustic Grand Piano", 2, "major", "galgame_bgm",
                           [["C", "G", "Am", "F"], ["F", "G", "Em", "C"]], "充满希望的明亮"),
    "playful": MoodProfile("playful", "俏皮", "いたずら", "waltz", 110, "4/4",
                           "Music Box", 2, "major", "galgame_bgm",
                           [["C", "G", "Am", "F"], ["G", "D", "Em", "C"]], "俏皮的跳跃"),
    "energetic": MoodProfile("energetic", "活力", "元気", "gentle_rock", 130, "4/4",
                             "Acoustic Grand Piano", 2, "major", "galgame_bgm",
                             [["C", "G", "Am", "F"], ["G", "D", "Em", "C"]], "充满活力的节奏"),
}

# natural language keywords -> mood (Chinese / Japanese / English); first match wins.
MOOD_KEYWORDS = [
    ("温柔", "gentle"), ("柔和", "gentle"), ("優しい", "gentle"), ("gentle", "gentle"),
    ("沉稳", "calm"), ("平静", "calm"), ("落ち着", "calm"), ("calm", "calm"), ("安稳", "calm"),
    ("优雅", "elegant"), ("優雅", "elegant"), ("华尔兹", "elegant"), ("waltz", "elegant"), ("elegant", "elegant"),
    ("轻快", "lively"), ("軽快", "lively"), ("lively", "lively"), ("跳动", "lively"),
    ("清爽", "refreshing"), ("爽やか", "refreshing"), ("切分", "refreshing"), ("syncopat", "refreshing"), ("refreshing", "refreshing"),
    ("欢快", "cheerful"), ("明るい", "cheerful"), ("cheerful", "cheerful"), ("元气", "cheerful"), ("活泼", "cheerful"),
    ("温暖", "warm"), ("温かい", "warm"), ("warm", "warm"),
    ("激昂", "uplifting"), ("高揚", "uplifting"), ("uplifting", "uplifting"),
    ("潇洒", "smart"), ("洒落", "smart"), ("爵士", "smart"), ("smart", "smart"), ("jazz", "smart"),
    ("丰富", "rich"), ("豊か", "rich"), ("rich", "rich"),
    ("明亮", "bright"), ("明るい", "bright"), ("bright", "bright"),
    ("忧伤", "melancholic"), ("物悲しい", "melancholic"), ("melancholic", "melancholic"), ("忧郁", "melancholic"),
    ("沉思", "thoughtful"), ("思案", "thoughtful"), ("thoughtful", "thoughtful"),
    ("戏剧", "dramatic"), ("劇的", "dramatic"), ("dramatic", "dramatic"),
    ("悲伤", "sad"), ("悲しい", "sad"), ("伤感", "sad"), ("sad", "sad"),
    ("浪漫", "romantic"), ("ロマンチック", "romantic"), ("恋爱", "romantic"), ("romantic", "romantic"),
    ("梦幻", "dreamy"), ("夢", "dreamy"), ("梦境", "dreamy"), ("dreamy", "dreamy"),
    ("紧张", "tense"), ("緊張", "tense"), ("悬疑", "tense"), ("tense", "tense"),
    ("激烈", "intense"), ("激しい", "intense"), ("战斗", "intense"), ("intense", "intense"),
    ("怀旧", "nostalgic"), ("懐かしい", "nostalgic"), ("nostalgic", "nostalgic"),
    ("宁静", "peaceful"), ("穏やか", "peaceful"), ("peaceful", "peaceful"),
    ("希望", "hopeful"), ("hopeful", "hopeful"),
    ("俏皮", "playful"), ("いたずら", "playful"), ("playful", "playful"), ("调皮", "playful"),
    ("活力", "energetic"), ("元気", "energetic"), ("energetic", "energetic"), ("运动", "energetic"),
]

# instrument aliases -> GM instrument names (extended to cover the common 128-set)
INSTRUMENT_ALIASES = {
    "钢琴": "Acoustic Grand Piano", "piano": "Acoustic Grand Piano", "琴": "Acoustic Grand Piano",
    "大钢琴": "Acoustic Grand Piano", "三角钢琴": "Acoustic Grand Piano",
    "电钢琴": "Electric Piano 1", "ep": "Electric Piano 1", "电钢": "Electric Piano 1",
    "风琴": "Church Organ", "管风琴": "Church Organ", "organ": "Church Organ",
    "手风琴": "Accordion", "accordion": "Accordion",
    "口琴": "Harmonica", "harmonica": "Harmonica",
    "小提琴": "Violin", "violin": "Violin", "弦乐独奏": "Violin",
    "中提琴": "Viola", "viola": "Viola",
    "大提琴": "Cello", "cello": "Cello", "低音提琴": "Contrabass", "contrabass": "Contrabass",
    "弦乐合奏": "String Ensemble 1", "弦乐团": "String Ensemble 1", "strings": "String Ensemble 1",
    "竖琴": "Orchestral Harp", "harp": "Orchestral Harp",
    "八音盒": "Music Box", "音乐盒": "Music Box", "music box": "Music Box", "八音": "Music Box",
    "钢片琴": "Celesta", "celesta": "Celesta",
    "钟琴": "Glockenspiel", "glockenspiel": "Glockenspiel",
    "木琴": "Xylophone", "xylophone": "Xylophone",
    "马林巴": "Marimba", "marimba": "Marimba",
    "吉他": "Acoustic Guitar (nylon)", "吉它": "Acoustic Guitar (nylon)", "木吉他": "Acoustic Guitar (steel)",
    "原声吉他": "Acoustic Guitar (steel)", "acoustic guitar": "Acoustic Guitar (nylon)",
    "电吉他": "Electric Guitar (jazz)", "electric guitar": "Electric Guitar (jazz)",
    "贝斯": "Electric Bass (pick)", "bass guitar": "Electric Bass (finger)", "电贝斯": "Electric Bass (pick)",
    "长笛": "Flute", "flute": "Flute", "短笛": "Piccolo", "piccolo": "Piccolo",
    "排箫": "Pan Flute", "pan flute": "Pan Flute",
    "陶笛": "Ocarina", "ocarina": "Ocarina",
    "双簧管": "Oboe", "oboe": "Oboe",
    "单簧管": "Clarinet", "clarinet": "Clarinet",
    "巴松": "Bassoon", "bassoon": "Bassoon",
    "萨克斯": "Alto Sax", "saxophone": "Tenor Sax", "萨克斯风": "Alto Sax",
    "小号": "Trumpet", "trumpet": "Trumpet", "喇叭": "Trumpet",
    "长号": "Trombone", "trombone": "Trombone",
    "圆号": "French Horn", "french horn": "French Horn", "法国号": "French Horn",
    "大号": "Tuba", "tuba": "Tuba",
    "合唱": "Choir Aahs", "choir": "Choir Aahs", "人声": "Choir Aahs",
    "定音鼓": "Timpani", "timpani": "Timpani", "鼓": "Timpani",
    "合成器": "Synth Strings 1", "synth": "Synth Strings 1", "电子合成": "Synth Strings 1",
    "钢鼓": "Steel Drums", "steel drums": "Steel Drums",
    "西塔琴": "Sitar", "sitar": "Sitar",
    "班卓琴": "Banjo", "banjo": "Banjo",
    "唢呐": "Oboe",
}

# texture aliases -> internal pattern names
PATTERN_ALIASES = {
    "琶音": "arpeggio_1353", "arpeggio": "arpeggio_1353", "分解和弦": "arpeggio_1353",
    "柱式和弦": "block_chord", "柱式": "block_chord", "block": "block_chord", "和弦": "block_chord",
    "华尔兹": "waltz", "waltz": "waltz", "圆舞曲": "waltz",
    "交替低音": "alternating_bass", "低音": "alternating_bass", "bass": "alternating_bass",
    "切分": "syncopated", "syncopated": "syncopated",
    "宽琶音": "broad_arpeggio", "broad": "broad_arpeggio", "大琶音": "broad_arpeggio",
    "摇滚": "gentle_rock", "rock": "gentle_rock", "律动": "gentle_rock",
    "民谣": "ballad_arp", "ballad": "ballad_arp", "抒情琶音": "ballad_arp",
    "脉冲": "pulse_chord", "pulse": "pulse_chord",
}

VALID_PATTERNS = set(PATTERN_ALIASES.values())


def total_beats(bpm, seconds=30):
    return (bpm / 60.0) * seconds
