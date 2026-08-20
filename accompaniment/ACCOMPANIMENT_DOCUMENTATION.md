# Do Muse - Galgame Accompaniment Database

> **Category**: `galgame_accompaniment`
> **Total Pieces**: 50
> **Duration**: ~30 seconds each
> **Purpose**: AI training dataset for visual novel accompaniment-style background music generation

---

## Overview

This database contains **50 pieces** of Galgame accompaniment-style music, generated using the **Do Muse** engine. Unlike the melody-driven BGM in `DATABASE_DOCUMENTATION.md`, these pieces are built on **real chord progressions** with **textured accompaniment patterns**, producing a more harmonic and pianistic galgame sound.

### Design Philosophy

Each piece is structured as a **piano duet** with two tracks:
- **Track 1 (Melody)**: Right-hand melody derived from chord tones, using lyrical or flowing rhythmic patterns
- **Track 2 (Accompaniment)**: Left-hand accompaniment using one of 5 texture patterns (arpeggio, block chord, waltz, alternating bass, syncopated)

### Generation Pipeline

```
JSON (Score Definition) → DoMuse.exe → MIDI → fluidsynth + SoundFont → WAV
```

| Tool | Version | Purpose |
|------|---------|---------|
| DoMuse.exe | v1.6.0 | JSON → MIDI conversion |
| fluidsynth | v2.5.7 | MIDI → WAV audio rendering |
| SoundFont: 32MbGMStereo | - | General MIDI sound bank (44100 Hz, 16-bit, stereo) |

### Database Structure

```
d:\项目\Vibe_Do_Muse\
├── generate_accompaniment.py          # Accompaniment piece generation script
├── batch_convert_accompaniment.py     # Batch conversion for accompaniment files
├── output_json_accompaniment/         # 50 JSON source files
├── output_midi/                       # 50 MIDI intermediate files
└── output_wav/                        # 50 WAV audio files
```

### File Naming Convention

```
{mood}_{progression_short}.{ext}
```

- `{mood}`: `gentle` (琶音), `calm` (柱式), `elegant` (华尔兹), `lively` (交替低音), `refreshing` (切分)
- `{progression_short}`: `王道pop`, `小室`, `4516`, `副歌`, `II-V-I`, `カノン`, `小調循環`, `基本`, `extended`, `混合`

---

## Musical Architecture

### Chord Progressions (10 groups)

All progressions are in **C major** key, providing a unified tonal center:

| # | Name | Chords | Roman Numerals | Common Usage |
|---|------|--------|----------------|--------------|
| 1 | 王道ポップス | C → G → Am → F | I-V-vi-IV | Pop standard, emotional climax |
| 2 | 小室進行 | Am → F → G → C | vi-IV-V-I | Tetsuya Komuro progression, 90s J-pop |
| 3 | 4516進行 | F → G → Em → Am | IV-V-iii-vi | Japanese anime/game standard |
| 4 | 副歌進行 | C → Am → F → G | I-vi-IV-V | Chorus turnaround, bright resolution |
| 5 | II-V-I | Dm7 → G7 → Cmaj7 → Cmaj7 | ii7-V7-Imaj7 | Jazz standard, sophisticated |
| 6 | カノン進行 | C → G → Am → Em → F → C → F → G | I-V-vi-iii-IV-I-IV-V | Pachelbel canon, 8-chord epic |
| 7 | 小調循環 | Am → Dm → G → C | vi-ii-V-I | Minor cycle, melancholic |
| 8 | 基本進行 | C → F → G → C | I-IV-V-I | Basic blues/rock foundation |
| 9 | 拡張進行 | Em → Am → Dm7 → G7 | iii-vi-ii7-V7 | Extended harmony, color tones |
| 10 | 混合進行 | Cmaj7 → Am7 → Fmaj7 → G7 | Imaj7-vi7-IVmaj7-V7 | Jazz-influenced, lush |

### Accompaniment Patterns (5 types)

| Pattern | Texture | Time Signature | BPM Range | Character |
|---------|---------|----------------|-----------|-----------|
| arpeggio_1353 | Broken chord root-3rd-5th-3rd | 4/4 | 85-95 | Gentle, flowing |
| block_chord | Full chord on each beat (octave lower) | 4/4 | 75-85 | Calm, solid |
| waltz | Bass (downbeat) + chord (upbeats) | 3/4 | 95-105 | Elegant, dance-like |
| alternating_bass | Root-5th alternation | 4/4 | 105-115 | Lively, driving |
| syncopated | Off-beat chords on beats 2 & 4 | 4/4 | 90-100 | Refreshing, rhythmic |

### Mood Mapping

| Pattern | Mood (JP) | Mood (EN) | Mood (CN) | Default BPM |
|---------|-----------|-----------|-----------|-------------|
| arpeggio_1353 | 優しい | gentle | 温柔 | 90 |
| block_chord | 落ち着いた | calm | 沉稳 | 80 |
| waltz | 優雅 | elegant | 优雅 | 100 |
| alternating_bass | 軽快 | lively | 轻快 | 110 |
| syncopated | 爽やか | refreshing | 清爽 | 95 |

---

## Piece Catalog

### 1. 王道ポップス (I-V-vi-IV) — Pop Standard

| # | Name | Mood | BPM | Time | Pattern | File |
|---|------|------|-----|------|---------|------|
| 1 | gentle_王道pop | Gentle | 90 | 4/4 | Arpeggio | gentle_王道pop.json |
| 2 | calm_王道pop | Calm | 80 | 4/4 | Block chord | calm_王道pop.json |
| 3 | elegant_王道pop | Elegant | 100 | 3/4 | Waltz | elegant_王道pop.json |
| 4 | lively_王道pop | Lively | 110 | 4/4 | Alternating bass | lively_王道pop.json |
| 5 | refreshing_王道pop | Refreshing | 95 | 4/4 | Syncopated | refreshing_王道pop.json |

### 2. 小室進行 (vi-IV-V-I) — Tetsuya Komuro

| # | Name | Mood | BPM | Time | Pattern | File |
|---|------|------|-----|------|---------|------|
| 6 | gentle_小室 | Gentle | 90 | 4/4 | Arpeggio | gentle_小室.json |
| 7 | calm_小室 | Calm | 80 | 4/4 | Block chord | calm_小室.json |
| 8 | elegant_小室 | Elegant | 100 | 3/4 | Waltz | elegant_小室.json |
| 9 | lively_小室 | Lively | 110 | 4/4 | Alternating bass | lively_小室.json |
| 10 | refreshing_小室 | Refreshing | 95 | 4/4 | Syncopated | refreshing_小室.json |

### 3. 4516進行 (IV-V-iii-vi) — Anime Standard

| # | Name | Mood | BPM | Time | Pattern | File |
|---|------|------|-----|------|---------|------|
| 11 | gentle_4516 | Gentle | 90 | 4/4 | Arpeggio | gentle_4516.json |
| 12 | calm_4516 | Calm | 80 | 4/4 | Block chord | calm_4516.json |
| 13 | elegant_4516 | Elegant | 100 | 3/4 | Waltz | elegant_4516.json |
| 14 | lively_4516 | Lively | 110 | 4/4 | Alternating bass | lively_4516.json |
| 15 | refreshing_4516 | Refreshing | 95 | 4/4 | Syncopated | refreshing_4516.json |

### 4. 副歌進行 (I-vi-IV-V) — Chorus

| # | Name | Mood | BPM | Time | Pattern | File |
|---|------|------|-----|------|---------|------|
| 16 | gentle_副歌 | Gentle | 90 | 4/4 | Arpeggio | gentle_副歌.json |
| 17 | calm_副歌 | Calm | 80 | 4/4 | Block chord | calm_副歌.json |
| 18 | elegant_副歌 | Elegant | 100 | 3/4 | Waltz | elegant_副歌.json |
| 19 | lively_副歌 | Lively | 110 | 4/4 | Alternating bass | lively_副歌.json |
| 20 | refreshing_副歌 | Refreshing | 95 | 4/4 | Syncopated | refreshing_副歌.json |

### 5. II-V-I (ii7-V7-Imaj7) — Jazz Standard

| # | Name | Mood | BPM | Time | Pattern | File |
|---|------|------|-----|------|---------|------|
| 21 | gentle_II-V-I | Gentle | 90 | 4/4 | Arpeggio | gentle_II-V-I.json |
| 22 | calm_II-V-I | Calm | 80 | 4/4 | Block chord | calm_II-V-I.json |
| 23 | elegant_II-V-I | Elegant | 100 | 3/4 | Waltz | elegant_II-V-I.json |
| 24 | lively_II-V-I | Lively | 110 | 4/4 | Alternating bass | lively_II-V-I.json |
| 25 | refreshing_II-V-I | Refreshing | 95 | 4/4 | Syncopated | refreshing_II-V-I.json |

### 6. カノン進行 (I-V-vi-iii-IV-I-IV-V) — Pachelbel Canon

| # | Name | Mood | BPM | Time | Pattern | File |
|---|------|------|-----|------|---------|------|
| 26 | gentle_カノン | Gentle | 85 | 4/4 | Arpeggio | gentle_カノン.json |
| 27 | calm_カノン | Calm | 75 | 4/4 | Block chord | calm_カノン.json |
| 28 | elegant_カノン | Elegant | 95 | 3/4 | Waltz | elegant_カノン.json |
| 29 | lively_カノン | Lively | 105 | 4/4 | Alternating bass | lively_カノン.json |
| 30 | refreshing_カノン | Refreshing | 90 | 4/4 | Syncopated | refreshing_カノン.json |

### 7. 小調循環 (vi-ii-V-I) — Minor Cycle

| # | Name | Mood | BPM | Time | Pattern | File |
|---|------|------|-----|------|---------|------|
| 31 | gentle_小調循環 | Gentle | 90 | 4/4 | Arpeggio | gentle_小調循環.json |
| 32 | calm_小調循環 | Calm | 80 | 4/4 | Block chord | calm_小調循環.json |
| 33 | elegant_小調循環 | Elegant | 100 | 3/4 | Waltz | elegant_小調循環.json |
| 34 | lively_小調循環 | Lively | 110 | 4/4 | Alternating bass | lively_小調循環.json |
| 35 | refreshing_小調循環 | Refreshing | 95 | 4/4 | Syncopated | refreshing_小調循環.json |

### 8. 基本進行 (I-IV-V-I) — Basic

| # | Name | Mood | BPM | Time | Pattern | File |
|---|------|------|-----|------|---------|------|
| 36 | gentle_基本 | Gentle | 95 | 4/4 | Arpeggio | gentle_基本.json |
| 37 | calm_基本 | Calm | 85 | 4/4 | Block chord | calm_基本.json |
| 38 | elegant_基本 | Elegant | 105 | 3/4 | Waltz | elegant_基本.json |
| 39 | lively_基本 | Lively | 115 | 4/4 | Alternating bass | lively_基本.json |
| 40 | refreshing_基本 | Refreshing | 100 | 4/4 | Syncopated | refreshing_基本.json |

### 9. 拡張進行 (iii-vi-ii7-V7) — Extended

| # | Name | Mood | BPM | Time | Pattern | File |
|---|------|------|-----|------|---------|------|
| 41 | gentle_extended | Gentle | 95 | 4/4 | Arpeggio | gentle_extended.json |
| 42 | calm_extended | Calm | 85 | 4/4 | Block chord | calm_extended.json |
| 43 | elegant_extended | Elegant | 105 | 3/4 | Waltz | elegant_extended.json |
| 44 | lively_extended | Lively | 115 | 4/4 | Alternating bass | lively_extended.json |
| 45 | refreshing_extended | Refreshing | 100 | 4/4 | Syncopated | refreshing_extended.json |

### 10. 混合進行 (Imaj7-vi7-IVmaj7-V7) — Mixed

| # | Name | Mood | BPM | Time | Pattern | File |
|---|------|------|-----|------|---------|------|
| 46 | gentle_混合 | Gentle | 90 | 4/4 | Arpeggio | gentle_混合.json |
| 47 | calm_混合 | Calm | 80 | 4/4 | Block chord | calm_混合.json |
| 48 | elegant_混合 | Elegant | 100 | 3/4 | Waltz | elegant_混合.json |
| 49 | lively_混合 | Lively | 110 | 4/4 | Alternating bass | lively_混合.json |
| 50 | refreshing_混合 | Refreshing | 95 | 4/4 | Syncopated | refreshing_混合.json |

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
| Average File Size | ~5.5 - 16 MB (WAV) |

### Musical Parameters

| Parameter | Range |
|-----------|-------|
| Tempo | 75 - 115 BPM |
| Key Signature | C (unified) |
| Time Signatures | 4/4, 3/4 |
| Instruments | Acoustic Grand Piano (dual-track) |
| Dynamics | 30 - 85 (MIDI velocity, accompaniment) / 60 - 85 (melody) |
| Chord Types | Major, minor, dominant 7, major 7, minor 7, diminished |

### Do Muse JSON Format

```json
{
  "title": "Piece Title",
  "composer": "Do Muse AI",
  "metadata": {
    "tempo_bpm": 90,
    "time_signature": "4/4",
    "key_signature": "C"
  },
  "tracks": [
    {
      "instrument": "Acoustic Grand Piano",
      "notes": [
        {"pitch": 60, "duration": "quarter", "velocity": 80}
      ]
    },
    {
      "instrument": "Acoustic Grand Piano",
      "notes": [
        {"pitch": 48, "duration": "quarter", "velocity": 40}
      ]
    }
  ]
}
```

- **Track 1 (Melody)**: Right-hand melody, chord-tone-based, lyric/flowing rhythmic patterns
- **Track 2 (Accompaniment)**: Left-hand accompaniment, texture-pattern-based

---

## Accompaniment Style Characteristics

### Chord Voicings

| Inversion | Description | Usage |
|-----------|-------------|-------|
| Root (0) | Root in bass | Default, stable |
| 1st inversion | 3rd in bass | Gentle transition |
| 2nd inversion | 5th in bass | Open, suspended feel |

### Melody Generation

| Parameter | Lyrical Style | Flowing Style |
|-----------|---------------|---------------|
| Passing tone probability | 20% | 15% |
| Velocity range | 65-85 | 60-80 |
| Rhythm patterns | Quarter/half dominated | Eighth-note dominated |
| Octave leap chance | 15% | 15% |

### Texture Patterns Detail

| Pattern | Note Density | Dynamic Range | Best For |
|---------|-------------|---------------|----------|
| arpeggio_1353 | 8 notes per 2 beats | 35-45 | Calm, emotional scenes |
| block_chord | 3 notes per beat | 40 | Serious, dramatic moments |
| waltz | 3 notes per measure | 35-50 | Romantic, elegant scenes |
| alternating_bass | 2 notes per measure | 42-48 | Upbeat, walking scenes |
| syncopated | 3 notes per 2 beats | 30 | Reflective, off-beat scenes |

---

## Usage Notes

### For AI Training

The 50 WAV files are suitable as training data for:

- **Accompaniment generation**: Teaching models to generate chord-based accompaniment patterns
- **Chord progression recognition**: Learning 10 common galgame chord progressions
- **Texture classification**: Distinguishing between 5 accompaniment texture types
- **Piano duet generation**: Understanding melody + accompaniment dual-track structure

### Comparison with DATABASE_DOCUMENTATION.md

| Aspect | DATABASE_DOCUMENTATION.md (44 pieces) | This Database (50 pieces) |
|--------|--------------------------------------|---------------------------|
| Approach | Melody-driven | Harmony-driven |
| Chord changes | Single notes | Real chord progressions |
| Texture | Various instruments | Piano only (dual-track) |
| Design | Mood-based | Progression × pattern matrix |
| Ear training | Yes | No |

### Regeneration

```bash
# Step 1: Generate JSON files
python generate_accompaniment.py

# Step 2: Convert to WAV
python batch_convert_accompaniment.py
```

### Requirements

- Python 3.10+
- DoMuse.exe (or Python source from [GitHub](https://github.com/yuki-shizuku/Do-muse/))
- fluidsynth 2.5.7+
- General MIDI SoundFont (.sf2)

---

## Version History

| Version | Date | Pieces | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-20 | 50 | Initial generation: 10 chord progressions × 5 accompaniment patterns |