# Generation Pipeline

> **Last Updated**: 2026-08-20

---

## Overview

The Do Muse project uses a three-stage pipeline to convert musical descriptions into playable WAV audio files:

```
JSON (Score Definition) → DoMuse.exe → MIDI → fluidsynth + SoundFont → WAV
```

This document explains each stage in detail.

---

## Stage 1: JSON Score Definition

### Input

A JSON file that describes the musical score, including:

- **Metadata**: Title, composer, tempo, time signature, key signature
- **Tracks**: One or more instrument tracks
- **Notes**: Each note has pitch, duration, velocity, and optional decorations

### Example

> **All templates and AI-generated scores use the V2 (absolute positioning)
> format**: top-level `"format": "v2"`, every note carries an `"offset"`.
> Gaps between notes are auto-filled with rests (never write `pitch: -1`).

```json
{
  "format": "v2",
  "title": "Morning Awakening",
  "composer": "Do Muse AI",
  "metadata": {
    "tempo_bpm": 100,
    "time_signature": "4/4",
    "key_signature": "C"
  },
  "tracks": [
    {
      "instrument": "Acoustic Grand Piano",
      "notes": [
        {"pitch": 60, "duration": "quarter", "velocity": 80, "offset": 0},
        {"pitch": 64, "duration": "quarter", "velocity": 75, "offset": 1},
        {"pitch": 67, "duration": "half", "velocity": 80, "offset": 2}
      ]
    }
  ]
}
```

### Duration Values

| Value | Length | Dotted Variant |
|-------|--------|----------------|
| `whole` | 4 beats | `whole.` |
| `half` | 2 beats | `half.` |
| `quarter` | 1 beat | `quarter.` |
| `eighth` | 0.5 beat | `eighth.` |
| `16th` | 0.25 beat | (not used) |

### Generator Scripts

| Batch | Script | Output Directory |
|-------|--------|------------------|
| 1 | `bgm/generate_bgm.py` | `bgm/json/` |
| 2 | `accompaniment/generate_accompaniment.py` | `accompaniment/json/` |
| 3 | `other/generate_galgame_v3.py` | `other/json/` |

---

## Stage 2: JSON to MIDI Conversion

### Tool

**DoMuse.exe** (v1.6.0) — A desktop application that parses JSON score files and generates MusicXML/MIDI output.

### Command

```bash
DoMuse.exe -i input.json -e output.mid -f midi
```

| Flag | Description |
|------|-------------|
| `-i` | Input JSON file path |
| `-e` | Export file path |
| `-f` | Export format (`midi`, `mxl`, `ly`, `wav`) |

### Process

1. Parse JSON into a music21 score object
2. Validate note durations, pitches, and metadata
3. Build MIDI events (note on/off, program change, tempo)
4. Export as Standard MIDI File (SMF) format 1

### Notes

- DoMuse.exe supports `mxl` (compressed MusicXML), `midi`, `ly` (LilyPond), and `wav` output formats
- The MIDI file contains all tracks with their respective instrument assignments
- Tempo is embedded as a MIDI meta-event
- Key signatures are embedded as MIDI meta-events

---

## Stage 3: MIDI to WAV Rendering

### Tool

**fluidsynth** (v2.5.7) — A real-time software synthesizer based on the SoundFont 2 specification.

### SoundFont

**32MbGMStereo.sf2** — A General MIDI compatible SoundFont bank with 32 MB of instrument samples.

### Command

```bash
fluidsynth.exe -F output.wav soundfont.sf2 input.mid
```

| Flag | Description |
|------|-------------|
| `-F` | Output WAV file path |
| (last) | Input MIDI file path |
| (2nd last) | SoundFont file path |

### Process

1. Load SoundFont samples into memory
2. Play MIDI events through the synthesizer in real-time
3. Mix multiple instrument channels into stereo
4. Render as 44100 Hz, 16-bit, stereo PCM WAV

### Audio Parameters

| Parameter | Value |
|-----------|-------|
| Sample Rate | 44100 Hz |
| Bit Depth | 16-bit |
| Channels | 2 (stereo) |
| Format | WAV (PCM, Microsoft) |
| Rendering | Real-time (batch mode) |

---

## Conversion Scripts

### Batch 2 Converter

**File**: `accompaniment/batch_convert_accompaniment.py`

```python
# Core logic:
def convert_json_to_midi(json_path, midi_path):
    cmd = [DOMUSE_EXE, "-i", json_path, "-e", midi_path, "-f", "midi"]
    subprocess.run(cmd, capture_output=True, text=True, timeout=30)

def convert_midi_to_wav(midi_path, wav_path):
    cmd = [FLUIDSYNTH_EXE, "-F", wav_path, SOUNDFONT, midi_path]
    subprocess.run(cmd, capture_output=True, text=True, timeout=60)
```

### Batch 3 Converter

**File**: `other/batch_convert_v3.py`

Same logic as Batch 2 converter, with different input/output directories.

---

## Dependencies

### Core Tools

| Tool | Version | Path | Purpose |
|------|---------|------|---------|
| DoMuse.exe | 1.6.0 | `root/DoMuse.exe` | JSON → MIDI |
| fluidsynth | 2.5.7 | `root/fluidsynth/fluidsynth-v2.5.7-win10-x64-cpp11/bin/fluidsynth.exe` | MIDI → WAV |
| 32MbGMStereo.sf2 | - | `root/32MbGMStereo.sf2` | SoundFont bank |

### Python Runtime

- Python 3.10+
- Standard library only (json, os, subprocess, time, random)

---

## Pipeline Diagram

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Generator  │     │  DoMuse.exe  │     │  fluidsynth  │     │    Output    │
│  Script     │     │              │     │              │     │              │
│  (Python)   │────▶│  JSON→MIDI   │────▶│  MIDI→WAV    │────▶│  WAV Audio   │
│             │     │              │     │              │     │              │
│  *.json     │     │  *.mid       │     │  *.wav       │     │  *.wav       │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### Per-Batch Pipeline

**Batch 1 (BGM)**: Generator → JSON only (no conversion to WAV)

**Batch 2 (Accompaniment)**: 
1. `accompaniment/generate_accompaniment.py` → `accompaniment/json/*.json`
2. `accompaniment/batch_convert_accompaniment.py` → `accompaniment/wav/*.wav`

**Batch 3 (v3)**:
1. `other/generate_galgame_v3.py` → `other/json/*.json`
2. `other/batch_convert_v3.py` → `other/wav/*.wav`