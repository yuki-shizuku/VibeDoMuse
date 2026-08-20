# Do Muse Knowledge Base

> **Project**: Galgame Music Generation System
> **Engine**: Do Muse v1.6.0
> **Last Updated**: 2026-08-20

---

## Overview

Do Muse is a Galgame (visual novel) background music generation system. It uses **JSON** as an intermediate language to describe musical scores, then converts them to MIDI and renders them as WAV audio files using a SoundFont bank.

The project currently contains **144 original music pieces** across three batches, designed for AI training and game development.

---

## Project Structure

```
d:\Project\Vibe_Do_Muse/
├── bgm/                      # Batch 1: Galgame BGM (44 pieces, JSON only)
├── accompaniment/            # Batch 2: Accompaniment style (50 pieces, JSON + WAV)
├── other/                    # Batch 3: Multi-key v3 (50 pieces, JSON + WAV)
├── fluidsynth/               # Audio rendering engine (v2.5.7)
├── knowledge_base/           # You are here
├── DoMuse.exe                # Core JSON-to-MIDI engine
├── 32MbGMStereo.sf2          # General MIDI SoundFont bank
└── JSON_Format_Specification.md  # Do Muse JSON format specification
```

---

## Database Catalogs

| Batch | Document | Pieces | Category | Key Features |
|-------|----------|--------|----------|--------------|
| 1 | [01_bgm_catalog.md](database/01_bgm_catalog.md) | 44 | `galgame_bgm` | Melody-driven, multi-instrument, varied moods |
| 2 | [02_accompaniment_catalog.md](database/02_accompaniment_catalog.md) | 50 | `galgame_accompaniment` | Harmony-driven, 10 progressions x 5 patterns, piano duet |
| 3 | [03_v3_catalog.md](database/03_v3_catalog.md) | 50 | `galgame_v3` | Multi-key, 3-track (piano + strings), new textures |

---

## Technical References

| Document | Description |
|----------|-------------|
| [01_chord_progressions.md](technical/01_chord_progressions.md) | All 30 chord progressions used across all batches |
| [02_accompaniment_patterns.md](technical/02_accompaniment_patterns.md) | 15 accompaniment texture patterns |
| [03_generation_pipeline.md](technical/03_generation_pipeline.md) | JSON to MIDI to WAV conversion pipeline |
| [JSON_Format_Specification.md](specifications/JSON_Format_Specification.md) | Official Do Muse JSON format specification |

---

## Statistics

### Overall

| Metric | Count |
|--------|-------|
| Total pieces | 144 |
| JSON source files | 144 |
| WAV audio files | 100 |
| Generation scripts | 3 |
| Conversion scripts | 2 |
| Chord progressions | 30 |
| Accompaniment patterns | 15 |
| Key signatures | 10+ |

### Pieces by Category

| Category | Count | Description |
|----------|-------|-------------|
| Daily / Relaxed | 10 | Morning, school, lunch, classroom scenes |
| School / Youth | 7 | Sports festival, library, gymnasium |
| Romance / Tender | 10 | First love, starry sky, cherry blossoms |
| Melancholy / Sad | 5 | Rain, farewell, tears |
| Cheerful / Bright | 20 | Pop, uplifting, bright moods |
| Calm / Peaceful | 10 | Steady, warm, gentle moods |
| Elegant / Waltz | 10 | 3/4 time, dance-like |
| Lively / Energetic | 10 | Fast tempos, driving rhythms |
| Refreshing / Rhythmic | 10 | Syncopated, off-beat |
| Dramatic / Dark | 10 | Minor keys, intense |
| Thoughtful / Rich | 10 | Complex harmony, extended chords |
| Various | 32 | Battle, chase, dream, mystery, etc. |

### BPM Distribution

| Range | Count | Character |
|-------|-------|-----------|
| 70-79 | 10 | Slow, ballad, thoughtful |
| 80-89 | 35 | Calm, gentle, flowing |
| 90-99 | 35 | Moderate, elegant, refreshing |
| 100-109 | 35 | Lively, cheerful, steady |
| 110-130 | 29 | Energetic, uplifting, dramatic |

---

## Quick Start

### Regenerate Batch 1 (BGM, JSON only)

```bash
cd bgm
python generate_bgm.py
```

### Regenerate Batch 2 (Accompaniment, JSON + WAV)

```bash
cd accompaniment
python generate_accompaniment.py
python batch_convert_accompaniment.py
```

### Regenerate Batch 3 (v3 Multi-key, JSON + WAV)

```bash
cd other
python generate_galgame_v3.py
python batch_convert_v3.py
```

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-08-20 | v3.0 | Added 50 multi-key v3 pieces (3-track, piano + strings) |
| 2026-08-20 | v2.0 | Added 50 harmony-driven accompaniment pieces |
| 2026-08-20 | v1.0 | Initial 44 Galgame BGM pieces |