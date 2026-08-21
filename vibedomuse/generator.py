# -*- coding: utf-8 -*-
"""
VibeDoMuse · generator.py
Composition layer: turns MusicParams into a Do-muse-compliant score JSON.
Supports 1/2/3 voices (melody / + piano accompaniment / + string pad) and an
optional pitched-percussion track (drums).

v2 improvements:
- Measure-aligned generation (whole-measure totals, per-chord measure counts).
- Cadence-aware progressions (ends on the tonic) for seamless BGM loops.
- Motif-driven melody + phrase-level dynamic curves.
- Voice leading between successive accompaniment chords.
- Optional "loop": true metadata, pitched-percussion track, and layer variants
  (calm / tense) for Galgame scene switching.
"""
import random
from dataclasses import replace

from . import music_theory as mt
from .nl_parser import MusicParams

# default percussion instrument used when drums are requested (GM pitched perc.)
DRUM_INSTRUMENT = "Timpani"

_LAYER_PROFILES = {
    "calm": {"tempo_factor": 0.82, "pattern": "ballad_arp", "vel_scale": 0.75,
             "drums": False, "label": "Calm Layer"},
    "tense": {"tempo_factor": 1.22, "pattern": "syncopated", "vel_scale": 1.12,
              "drums": True, "label": "Tense Layer"},
}


def compose(params: MusicParams, seed=None, loop=None, layer=None, vel_scale=None):
    """Generate a Do-muse score dict from parsed music parameters.

    - loop: None -> use params.loop; True -> adds top-level "loop": true and
      guarantees measure alignment + tonic ending.
    - layer: "calm" / "tense" / None — Galgame scene-switch variants.
    - vel_scale: optional global velocity multiplier.
    """
    p = params
    if layer in _LAYER_PROFILES:
        prof = _LAYER_PROFILES[layer]
        p = replace(p, tempo_bpm=max(40, min(220, int(p.tempo_bpm * prof["tempo_factor"]))),
                    pattern=prof["pattern"], drums=prof["drums"])
    bpm = p.tempo_bpm
    time_sig = p.time_sig
    key = p.key
    duration = p.duration_sec
    chords = p.progressions or [["C", "G", "Am", "F"]]
    if isinstance(chords[0], list):
        chords = chords[0]
    chords = [str(c) for c in chords]
    # cadence: end on the tonic (important for seamless loops)
    if loop is None:
        loop = p.loop
    if loop:
        chords = mt.with_cadence(chords, key)
    else:
        # still resolve to tonic if it is cheap to do so
        if len(chords) <= 8 and mt.parse_chord(chords[-1])[0] != mt.parse_key(key)[0]:
            chords = mt.with_cadence(chords, key)

    # measure-aligned total
    raw_total = mt.total_beats(bpm, duration)
    total, measures = mt.align_measures(raw_total, time_sig)
    bpm_measure = mt.beats_per_measure(time_sig)
    n = max(1, len(chords))
    per = measures // n
    rem = measures % n
    sizes = [per + (1 if i >= n - rem else 0) for i in range(n)]
    beats_list = [s * bpm_measure for s in sizes]

    scale = mt.build_scale(key, octave=4, octaves=2)
    curve = mt.dynamic_shape(n)
    rng = random.Random(seed)
    motif = mt.make_motif(chords[0], scale, rng)
    base_root = mt.chord_pitches(chords[0], octave=4)[0]
    vscale = vel_scale if vel_scale is not None else 1.0

    tracks = []
    # melody (right hand / lead)
    melody_notes = []
    for i, ch in enumerate(chords):
        root_i = mt.chord_pitches(ch, octave=4)[0]
        transpose = clamp_shift(root_i - base_root)
        melody_notes.extend(mt.gen_melody(
            ch, scale, beats_list[i], bpm, style="lyrical", seed=seed,
            phrase_index=i, n_phrases=n, curve=curve, motif=motif,
            transpose=transpose))
    tracks.append({
        "instrument": p.instrument,
        "notes": _scale_velocities(melody_notes, vscale),
    })
    # accompaniment (left hand)
    if p.tracks >= 2:
        accomp_notes = []
        prev_pitches = None
        for i, ch in enumerate(chords):
            chunk = mt.gen_accompaniment(p.pattern, ch, beats_list[i], bpm, seed=seed,
                                         prev_pitches=prev_pitches, vel_scale=vscale,
                                         measure_beats=bpm_measure)
            accomp_notes.extend(chunk)
            prev_pitches = mt.voice_lead(prev_pitches, mt.chord_pitches(ch, octave=4))
        tracks.append({
            "instrument": "Acoustic Grand Piano",
            "notes": _scale_velocities(accomp_notes, vscale),
        })
    # string pad
    if p.tracks >= 3:
        pad_notes = []
        prev_pitches = None
        for i, ch in enumerate(chords):
            chunk = mt.gen_pad(ch, beats_list[i], bpm, seed=seed,
                               prev_pitches=prev_pitches, vel_scale=vscale)
            pad_notes.extend(chunk)
            prev_pitches = mt.voice_lead(prev_pitches, mt.chord_pitches(ch, octave=4, inversion=1))
        tracks.append({
            "instrument": "String Ensemble 1",
            "notes": _scale_velocities(pad_notes, vscale),
        })
    # percussion (pitched percussion; DoMuse maps Drum Kit to piano, so Timpani)
    if p.drums:
        drums_notes = []
        for i, ch in enumerate(chords):
            drums_notes.extend(mt.gen_drums(
                "kick4" if bpm >= 100 else "soft_pulse", beats_list[i], bpm,
                seed=(seed or 0) + i * 101, instrument=DRUM_INSTRUMENT,
                measure_beats=bpm_measure))
        tracks.append({
            "instrument": DRUM_INSTRUMENT,
            "notes": _scale_velocities(drums_notes, vscale),
        })

    title = f"VibeDoMuse · {p.mood_cn} · {key}"
    if layer in _LAYER_PROFILES:
        title += " · " + _LAYER_PROFILES[layer]["label"]
    score = {
        "title": title,
        "composer": "VibeDoMuse AI",
        "metadata": {
            "tempo_bpm": int(bpm),
            "time_signature": time_sig,
            "key_signature": key,
        },
        "tracks": tracks,
    }
    if p.category:
        score["category"] = p.category
    if loop:
        score["loop"] = True
    return score


def clamp_shift(s):
    return max(-24, min(24, s))


def _scale_velocities(notes, factor):
    if factor is None or abs(factor - 1.0) < 1e-9:
        return notes
    out = []
    for n in notes:
        n = dict(n)
        if "velocity" in n:
            n["velocity"] = max(1, min(127, int(n["velocity"] * factor)))
        out.append(n)
    return out


def gen_variants(params: MusicParams, n=4, seed=None):
    """Generate n distinct variants of the same request (different seeds)."""
    base_seed = seed if seed is not None else random.randint(0, 1_000_000)
    out = []
    for i in range(max(1, n)):
        s = (base_seed + i * 7919) % 1_000_000
        out.append(compose(params, seed=s, loop=params.loop))
    return out


def gen_layers(params: MusicParams, seed=None):
    """Generate calm/tense layer variants of the same theme (Galgame scene switch)."""
    base_seed = seed if seed is not None else random.randint(0, 1_000_000)
    return [
        {"layer": "calm", "label": "Calm Layer", "score": compose(params, seed=base_seed, layer="calm", loop=params.loop)},
        {"layer": "tense", "label": "Tense Layer", "score": compose(params, seed=base_seed, layer="tense", loop=params.loop)},
    ]


def slug(params: MusicParams):
    return f"{params.mood}_{params.key}_{params.pattern}"
