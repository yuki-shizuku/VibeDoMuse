# Batch 2: Accompaniment Style Catalog

> **Category**: `galgame_accompaniment`
> **Total Pieces**: 50
> **Format**: JSON + WAV
> **Duration**: ~30 seconds each
> **Purpose**: Harmony-driven Galgame accompaniment patterns for AI training

---

## Overview

This batch contains 50 pieces of harmony-driven accompaniment-style Galgame music. Each piece is built on **real chord progressions** with **textured accompaniment patterns**, creating a pianistic galgame sound. The music is structured as a **piano duet** with two tracks: melody (right hand) and accompaniment (left hand).

### Generation Tools

- **Script**: `accompaniment/generate_accompaniment.py`
- **Conversion**: `accompaniment/batch_convert_accompaniment.py`
- **Engine**: DoMuse.exe (JSON to MIDI) + fluidsynth v2.5.7 (MIDI to WAV)
- **SoundFont**: 32MbGMStereo.sf2 (44100 Hz, 16-bit, stereo)

### Design Principles

- Harmony-driven composition (real chord progressions)
- Single key: C major (unified tonal center)
- 10 chord progressions x 5 accompaniment patterns = 50 pieces
- Piano only, dual-track (melody + accompaniment)
- Tempo range: 75-115 BPM

---

## Chord Progressions (10 groups)

All progressions are in **C major** key:

| # | Name | Chords | Roman Numerals | Common Usage |
|---|------|--------|----------------|--------------|
| 1 | Pop Standard | C → G → Am → F | I-V-vi-IV | Pop standard, emotional climax |
| 2 | Komuro Progression | Am → F → G → C | vi-IV-V-I | 90s J-pop standard |
| 3 | 4516 Progression | F → G → Em → Am | IV-V-iii-vi | Japanese anime/game standard |
| 4 | Chorus Turnaround | C → Am → F → G | I-vi-IV-V | Bright resolution |
| 5 | II-V-I Jazz | Dm7 → G7 → Cmaj7 → Cmaj7 | ii7-V7-Imaj7 | Jazz standard, sophisticated |
| 6 | Canon Progression | C → G → Am → Em → F → C → F → G | I-V-vi-iii-IV-I-IV-V | Pachelbel canon, 8-chord |
| 7 | Minor Cycle | Am → Dm → G → C | vi-ii-V-I | Melancholic |
| 8 | Basic Blues | C → F → G → C | I-IV-V-I | Rock/pop foundation |
| 9 | Extended Harmony | Em → Am → Dm7 → G7 | iii-vi-ii7-V7 | Color tones |
| 10 | Mixed Jazz | Cmaj7 → Am7 → Fmaj7 → G7 | Imaj7-vi7-IVmaj7-V7 | Lush, jazz-influenced |

---

## Accompaniment Patterns (5 types)

| Pattern | Texture | Time Sig | BPM | Character |
|---------|---------|----------|-----|-----------|
| arpeggio_1353 | Broken chord root-3rd-5th-3rd | 4/4 | 85-95 | Gentle, flowing |
| block_chord | Full chord on each beat (octave lower) | 4/4 | 75-85 | Calm, solid |
| waltz | Bass (downbeat) + chord (upbeats) | 3/4 | 95-105 | Elegant, dance-like |
| alternating_bass | Root-5th alternation | 4/4 | 105-115 | Lively, driving |
| syncopated | Off-beat chords on beats 2 & 4 | 4/4 | 90-100 | Refreshing, rhythmic |

---

## Piece Catalog

### 1. Pop Standard (I-V-vi-IV)

| # | Name | Mood | BPM | Pattern |
|---|------|------|-----|---------|
| 1 | gentle_pop_standard | Gentle | 90 | Arpeggio |
| 2 | calm_pop_standard | Calm | 80 | Block chord |
| 3 | elegant_pop_standard | Elegant | 100 | Waltz |
| 4 | lively_pop_standard | Lively | 110 | Alternating bass |
| 5 | refreshing_pop_standard | Refreshing | 95 | Syncopated |

### 2. Komuro Progression (vi-IV-V-I)

| # | Name | Mood | BPM | Pattern |
|---|------|------|-----|---------|
| 6 | gentle_komuro | Gentle | 90 | Arpeggio |
| 7 | calm_komuro | Calm | 80 | Block chord |
| 8 | elegant_komuro | Elegant | 100 | Waltz |
| 9 | lively_komuro | Lively | 110 | Alternating bass |
| 10 | refreshing_komuro | Refreshing | 95 | Syncopated |

### 3. 4516 Progression (IV-V-iii-vi)

| # | Name | Mood | BPM | Pattern |
|---|------|------|-----|---------|
| 11 | gentle_4516 | Gentle | 90 | Arpeggio |
| 12 | calm_4516 | Calm | 80 | Block chord |
| 13 | elegant_4516 | Elegant | 100 | Waltz |
| 14 | lively_4516 | Lively | 110 | Alternating bass |
| 15 | refreshing_4516 | Refreshing | 95 | Syncopated |

### 4. Chorus Turnaround (I-vi-IV-V)

| # | Name | Mood | BPM | Pattern |
|---|------|------|-----|---------|
| 16 | gentle_chorus | Gentle | 90 | Arpeggio |
| 17 | calm_chorus | Calm | 80 | Block chord |
| 18 | elegant_chorus | Elegant | 100 | Waltz |
| 19 | lively_chorus | Lively | 110 | Alternating bass |
| 20 | refreshing_chorus | Refreshing | 95 | Syncopated |

### 5. II-V-I Jazz (ii7-V7-Imaj7)

| # | Name | Mood | BPM | Pattern |
|---|------|------|-----|---------|
| 21 | gentle_ii_v_i | Gentle | 90 | Arpeggio |
| 22 | calm_ii_v_i | Calm | 80 | Block chord |
| 23 | elegant_ii_v_i | Elegant | 100 | Waltz |
| 24 | lively_ii_v_i | Lively | 110 | Alternating bass |
| 25 | refreshing_ii_v_i | Refreshing | 95 | Syncopated |

### 6. Canon Progression (I-V-vi-iii-IV-I-IV-V)

| # | Name | Mood | BPM | Pattern |
|---|------|------|-----|---------|
| 26 | gentle_canon | Gentle | 85 | Arpeggio |
| 27 | calm_canon | Calm | 75 | Block chord |
| 28 | elegant_canon | Elegant | 95 | Waltz |
| 29 | lively_canon | Lively | 105 | Alternating bass |
| 30 | refreshing_canon | Refreshing | 90 | Syncopated |

### 7. Minor Cycle (vi-ii-V-I)

| # | Name | Mood | BPM | Pattern |
|---|------|------|-----|---------|
| 31 | gentle_minor_cycle | Gentle | 90 | Arpeggio |
| 32 | calm_minor_cycle | Calm | 80 | Block chord |
| 33 | elegant_minor_cycle | Elegant | 100 | Waltz |
| 34 | lively_minor_cycle | Lively | 110 | Alternating bass |
| 35 | refreshing_minor_cycle | Refreshing | 95 | Syncopated |

### 8. Basic Blues (I-IV-V-I)

| # | Name | Mood | BPM | Pattern |
|---|------|------|-----|---------|
| 36 | gentle_basic | Gentle | 95 | Arpeggio |
| 37 | calm_basic | Calm | 85 | Block chord |
| 38 | elegant_basic | Elegant | 105 | Waltz |
| 39 | lively_basic | Lively | 115 | Alternating bass |
| 40 | refreshing_basic | Refreshing | 100 | Syncopated |

### 9. Extended Harmony (iii-vi-ii7-V7)

| # | Name | Mood | BPM | Pattern |
|---|------|------|-----|---------|
| 41 | gentle_extended | Gentle | 95 | Arpeggio |
| 42 | calm_extended | Calm | 85 | Block chord |
| 43 | elegant_extended | Elegant | 105 | Waltz |
| 44 | lively_extended | Lively | 115 | Alternating bass |
| 45 | refreshing_extended | Refreshing | 100 | Syncopated |

### 10. Mixed Jazz (Imaj7-vi7-IVmaj7-V7)

| # | Name | Mood | BPM | Pattern |
|---|------|------|-----|---------|
| 46 | gentle_mixed_jazz | Gentle | 90 | Arpeggio |
| 47 | calm_mixed_jazz | Calm | 80 | Block chord |
| 48 | elegant_mixed_jazz | Elegant | 100 | Waltz |
| 49 | lively_mixed_jazz | Lively | 110 | Alternating bass |
| 50 | refreshing_mixed_jazz | Refreshing | 95 | Syncopated |

---

## Technical Specifications

### Audio Format

| Parameter | Value |
|-----------|-------|
| Format | WAV (PCM) |
| Sample Rate | 44100 Hz |
| Bit Depth | 16-bit |
| Channels | Stereo |
| Average Duration | 30 seconds |
| Average File Size | ~5.5 - 16 MB |

### Musical Parameters

| Parameter | Range |
|-----------|-------|
| Tempo | 75 - 115 BPM |
| Key Signature | C (unified) |
| Time Signatures | 4/4, 3/4 |
| Instruments | Acoustic Grand Piano (2 tracks) |
| Dynamics | 30 - 85 (accompaniment) / 60 - 85 (melody) |
| Chord Types | Major, minor, dom7, maj7, min7, diminished |

### Track Structure

| Track | Role | Velocity Range |
|-------|------|----------------|
| 1 | Melody (right hand) | 60-88 |
| 2 | Accompaniment (left hand) | 30-48 |

### File Locations

| Item | Path |
|------|------|
| JSON files | `accompaniment/json/*.json` |
| WAV files | `accompaniment/wav/*.wav` |
| Generator script | `accompaniment/generate_accompaniment.py` |
| Converter script | `accompaniment/batch_convert_accompaniment.py` |
| Documentation | `accompaniment/ACCOMPANIMENT_DOCUMENTATION.md` |

### Regeneration

```bash
cd accompaniment
python generate_accompaniment.py
python batch_convert_accompaniment.py
```