# Batch 3: Multi-key v3 Catalog

> **Category**: `galgame_v3`
> **Total Pieces**: 50
> **Format**: JSON + WAV
> **Duration**: ~30 seconds each
> **Purpose**: Multi-key, textured Galgame music with string pad layer for AI training

---

## Overview

This batch contains 50 pieces of multi-key Galgame-style music, representing the **third generation** of the Do Muse dataset. Key innovations include:

- **Multi-key harmony**: 10 different keys (C, G, D, F, Bb, A, Eb, Am, Em, Dm)
- **Three-track arrangement**: Piano melody + Piano accompaniment + String ensemble pad
- **New texture patterns**: 5 distinct accompaniment styles
- **Wider harmonic palette**: Major, minor, dominant 7th, and altered chords

### Generation Tools

- **Script**: `other/generate_galgame_v3.py`
- **Conversion**: `other/batch_convert_v3.py`
- **Engine**: DoMuse.exe (JSON to MIDI) + fluidsynth v2.5.7 (MIDI to WAV)
- **SoundFont**: 32MbGMStereo.sf2 (44100 Hz, 16-bit, stereo)

---

## Chord Progressions (10 groups, each in a different key)

| # | Key | Chords | Roman Numerals | Mood | Character |
|---|-----|--------|----------------|------|-----------|
| 1 | C | C → Em → F → G | I-iii-IV-V | Cheerful | Bright pop with mediant substitution |
| 2 | G | G → C → Am → D | I-IV-ii-V | Warm | Warm standard with supertonic |
| 3 | D | D → Bm → G → A | I-vi-IV-V | Uplifting | Uplifting with relative minor |
| 4 | F | F → C → Dm → Bb | I-V-ii-IV | Tender | Tender subdominant expansion |
| 5 | Bb | Bb → Gm → Eb → F | I-vi-IV-V | Smart | Jazz-influenced flat keys |
| 6 | A | A → D → F#m → E | I-IV-vi-V | Bright | Bright open strings feel |
| 7 | Eb | Eb → Cm → Ab → Bb | I-vi-IV-V | Rich | Warm flat-key harmony |
| 8 | Am | Am → Dm → E7 → Am | i-iv-V7-i | Melancholic | Harmonic minor resolution |
| 9 | Em | Em → C → G → D | i-VI-III-VII | Thoughtful | Dorian-inflected modal flavor |
| 10 | Dm | Dm → Gm → C7 → F | i-iv-V7-III | Dramatic | Minor with dominant preparation |

---

## Accompaniment Patterns (5 types)

| Pattern | Description | BPM | Character |
|---------|-------------|-----|-----------|
| broad_arpeggio | 2-octave spanning arpeggio (root-3rd-5th, ascending) | 85 | Flowing, expansive |
| syncopated_chord | Strong beat bass + weak beat full chord | 92 | Rhythmic, off-beat |
| gentle_rock | 8th-note alternating bass-chord pattern | 105 | Steady, driving |
| ballad_arp | Slow ballad arpeggio with dotted feel | 78 | Gentle, lyrical |
| pulse_chord | Sustained chord pulsing on each beat | 88 | Pulsing, atmospheric |

### String Pad Layer

The third track provides sustained string ensemble texture:

| Parameter | Value |
|-----------|-------|
| Instrument | String Ensemble 1 |
| Voicing | 1st inversion (warm) |
| Duration | Whole/half notes (sustained) |
| Velocity | 25 (very soft, background) |
| Octave | One octave below melody |

---

## Piece Catalog

### 1. C Major — Cheerful Pop (I-iii-IV-V)

| # | Name | BPM | Pattern | Character |
|---|------|-----|---------|-----------|
| 1 | c_cheerful_flowing | 85 | broad_arpeggio | Flowing, expansive |
| 2 | c_cheerful_rhythmic | 92 | syncopated_chord | Rhythmic, off-beat |
| 3 | c_cheerful_steady | 105 | gentle_rock | Steady, driving |
| 4 | c_cheerful_gentle | 78 | ballad_arp | Gentle, lyrical |
| 5 | c_cheerful_pulsing | 88 | pulse_chord | Pulsing, atmospheric |

### 2. G Major — Warm Standard (I-IV-ii-V)

| # | Name | BPM | Pattern | Character |
|---|------|-----|---------|-----------|
| 6 | g_warm_flowing | 85 | broad_arpeggio | Flowing, expansive |
| 7 | g_warm_rhythmic | 92 | syncopated_chord | Rhythmic, off-beat |
| 8 | g_warm_steady | 105 | gentle_rock | Steady, driving |
| 9 | g_warm_gentle | 78 | ballad_arp | Gentle, lyrical |
| 10 | g_warm_pulsing | 88 | pulse_chord | Pulsing, atmospheric |

### 3. D Major — Uplifting (I-vi-IV-V)

| # | Name | BPM | Pattern | Character |
|---|------|-----|---------|-----------|
| 11 | d_uplifting_flowing | 85 | broad_arpeggio | Flowing, expansive |
| 12 | d_uplifting_rhythmic | 92 | syncopated_chord | Rhythmic, off-beat |
| 13 | d_uplifting_steady | 105 | gentle_rock | Steady, driving |
| 14 | d_uplifting_gentle | 78 | ballad_arp | Gentle, lyrical |
| 15 | d_uplifting_pulsing | 88 | pulse_chord | Pulsing, atmospheric |

### 4. F Major — Tender (I-V-ii-IV)

| # | Name | BPM | Pattern | Character |
|---|------|-----|---------|-----------|
| 16 | f_tender_flowing | 85 | broad_arpeggio | Flowing, expansive |
| 17 | f_tender_rhythmic | 92 | syncopated_chord | Rhythmic, off-beat |
| 18 | f_tender_steady | 105 | gentle_rock | Steady, driving |
| 19 | f_tender_gentle | 78 | ballad_arp | Gentle, lyrical |
| 20 | f_tender_pulsing | 88 | pulse_chord | Pulsing, atmospheric |

### 5. Bb Major — Smart Jazz (I-vi-IV-V)

| # | Name | BPM | Pattern | Character |
|---|------|-----|---------|-----------|
| 21 | bb_smart_flowing | 85 | broad_arpeggio | Flowing, expansive |
| 22 | bb_smart_rhythmic | 92 | syncopated_chord | Rhythmic, off-beat |
| 23 | bb_smart_steady | 105 | gentle_rock | Steady, driving |
| 24 | bb_smart_gentle | 78 | ballad_arp | Gentle, lyrical |
| 25 | bb_smart_pulsing | 88 | pulse_chord | Pulsing, atmospheric |

### 6. A Major — Bright (I-IV-vi-V)

| # | Name | BPM | Pattern | Character |
|---|------|-----|---------|-----------|
| 26 | a_bright_flowing | 85 | broad_arpeggio | Flowing, expansive |
| 27 | a_bright_rhythmic | 92 | syncopated_chord | Rhythmic, off-beat |
| 28 | a_bright_steady | 105 | gentle_rock | Steady, driving |
| 29 | a_bright_gentle | 78 | ballad_arp | Gentle, lyrical |
| 30 | a_bright_pulsing | 88 | pulse_chord | Pulsing, atmospheric |

### 7. Eb Major — Rich (I-vi-IV-V)

| # | Name | BPM | Pattern | Character |
|---|------|-----|---------|-----------|
| 31 | eb_rich_flowing | 85 | broad_arpeggio | Flowing, expansive |
| 32 | eb_rich_rhythmic | 92 | syncopated_chord | Rhythmic, off-beat |
| 33 | eb_rich_steady | 105 | gentle_rock | Steady, driving |
| 34 | eb_rich_gentle | 78 | ballad_arp | Gentle, lyrical |
| 35 | eb_rich_pulsing | 88 | pulse_chord | Pulsing, atmospheric |

### 8. A Minor — Melancholic (i-iv-V7-i)

| # | Name | BPM | Pattern | Character |
|---|------|-----|---------|-----------|
| 36 | am_melancholic_flowing | 85 | broad_arpeggio | Flowing, expansive |
| 37 | am_melancholic_rhythmic | 92 | syncopated_chord | Rhythmic, off-beat |
| 38 | am_melancholic_steady | 105 | gentle_rock | Steady, driving |
| 39 | am_melancholic_gentle | 78 | ballad_arp | Gentle, lyrical |
| 40 | am_melancholic_pulsing | 88 | pulse_chord | Pulsing, atmospheric |

### 9. E Minor — Thoughtful (i-VI-III-VII)

| # | Name | BPM | Pattern | Character |
|---|------|-----|---------|-----------|
| 41 | em_thoughtful_flowing | 85 | broad_arpeggio | Flowing, expansive |
| 42 | em_thoughtful_rhythmic | 92 | syncopated_chord | Rhythmic, off-beat |
| 43 | em_thoughtful_steady | 105 | gentle_rock | Steady, driving |
| 44 | em_thoughtful_gentle | 78 | ballad_arp | Gentle, lyrical |
| 45 | em_thoughtful_pulsing | 88 | pulse_chord | Pulsing, atmospheric |

### 10. D Minor — Dramatic (i-iv-V7-III)

| # | Name | BPM | Pattern | Character |
|---|------|-----|---------|-----------|
| 46 | dm_dramatic_flowing | 85 | broad_arpeggio | Flowing, expansive |
| 47 | dm_dramatic_rhythmic | 92 | syncopated_chord | Rhythmic, off-beat |
| 48 | dm_dramatic_steady | 105 | gentle_rock | Steady, driving |
| 49 | dm_dramatic_gentle | 78 | ballad_arp | Gentle, lyrical |
| 50 | dm_dramatic_pulsing | 88 | pulse_chord | Pulsing, atmospheric |

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
| Average File Size | ~24 - 28 MB (3-track) |

### Musical Parameters

| Parameter | Range |
|-----------|-------|
| Tempo | 78 - 105 BPM |
| Key Signatures | C, G, D, F, Bb, A, Eb (major) / Am, Em, Dm (minor) |
| Time Signatures | 4/4 |
| Instruments | Piano (2 tracks) + String Ensemble 1 (1 track) |
| Chord Types | M, m, 7, M7, m7, dim, m7b5 |
| Dynamics | 25 - 88 (MIDI velocity) |

### Track Structure

| Track | Instrument | Role | Velocity Range |
|-------|------------|------|----------------|
| 1 | Acoustic Grand Piano | Melody (right hand) | 60-88 |
| 2 | Acoustic Grand Piano | Accompaniment (left hand) | 30-48 |
| 3 | String Ensemble 1 | Pad / atmosphere | 25 (sustained) |

### File Locations

| Item | Path |
|------|------|
| JSON files | `other/json/*.json` |
| WAV files | `other/wav/*.wav` |
| Generator script | `other/generate_galgame_v3.py` |
| Converter script | `other/batch_convert_v3.py` |
| Documentation | `other/GALGAME_V3_DOCUMENTATION.md` |

### Regeneration

```bash
cd other
python generate_galgame_v3.py
python batch_convert_v3.py
```