# Accompaniment Patterns Reference

> **Total**: 15 unique patterns across all 3 batches
> **Last Updated**: 2026-08-20

---

## Overview

This document catalogs all accompaniment texture patterns used in the Do Muse project. Each pattern is defined by its note density, rhythmic structure, and dynamic range. Patterns are organized by batch.

---

## Batch 1: BGM Patterns

Batch 1 uses simple accompaniment patterns as harmonic support for the melody:

| Pattern | Description | Notes per Beat | Dynamics |
|---------|-------------|----------------|----------|
| arpeggio | Broken chord ascending/descending | 1-2 per beat | 40-50 |
| block_chord | Full chord sustained | 3 per measure | 35-45 |
| bass_note | Single bass note on beat 1 | 1 per measure | 45-55 |
| simple_pad | Sustained chord tones | 1 per 2 beats | 25-35 |

These patterns are embedded in the `generate_bgm.py` script and vary by piece.

---

## Batch 2: Accompaniment Patterns

### 1. Arpeggio 1353 (arpeggio_1353)

A standard broken chord pattern: root → 3rd → 5th → 3rd, repeated.

```
Beat:  1    &    2    &    3    &    4    &
Note:  R    3    5    3    R    3    5    3
Vel:   45   35   35   35   45   35   35   35
```

- **Time signature**: 4/4
- **Resolution**: 8th notes (2 per beat)
- **Octave**: Root in bass octave, chords in middle
- **Character**: Gentle, flowing, continuous
- **Best for**: Calm scenes, emotional moments, daily life

### 2. Block Chord (block_chord)

Full chord voicing on each beat, played in the lower octave.

```
Beat:  1        2        3        4
Note:  R-3-5    R-3-5    R-3-5    R-3-5
Vel:   40       40       40       40
```

- **Time signature**: 4/4
- **Resolution**: Quarter notes
- **Octave**: One octave below melody
- **Character**: Solid, grounded, simple
- **Best for**: Serious moments, dramatic scenes, slow sections

### 3. Waltz (waltz)

Classic 3/4 waltz pattern: bass on beat 1, chord on beats 2-3.

```
Beat:  1        2        3
Note:  Bass     R-3-5    R-3-5
Dur:   quarter. quarter  quarter
Vel:   50       35       35
```

- **Time signature**: 3/4
- **Resolution**: Quarter notes (dotted quarter on bass)
- **Octave**: Bass in low octave, chords in middle
- **Character**: Elegant, dance-like, romantic
- **Best for**: Ballroom scenes, elegant moments, romantic interludes

### 4. Alternating Bass (alternating_bass)

Root and 5th alternate on each beat, creating a walking bass feel.

```
Beat:  1        2        3        4
Note:  R        Fifth    R        Fifth
Vel:   48       42       48       42
```

- **Time signature**: 4/4
- **Resolution**: Quarter notes
- **Octave**: Bass octave (low register)
- **Character**: Lively, driving, rhythmic
- **Best for**: Upbeat scenes, walking sequences, school festivals

### 5. Syncopated (syncopated)

Off-beat chords on beats 2 and 4, creating a rhythmic push.

```
Beat:  1        2        3        4
Note:  Bass     R-3-5    (rest)   R-3-5
Vel:   48       32                32
```

- **Time signature**: 4/4
- **Resolution**: Quarter notes
- **Octave**: Bass in low octave, chords in middle
- **Character**: Refreshing, off-beat, modern
- **Best for**: Reflective scenes, city views, modern settings

---

## Batch 3: v3 Patterns

### 6. Broad Arpeggio (broad_arpeggio)

A wide-spanning arpeggio covering 2 octaves, ascending.

```
Beat:  1        2        3        4
Note:  R-12     R        3rd      5th
       5th+12   R+12     3rd+12   5th+12
```

- **Time signature**: 4/4
- **Resolution**: Quarter notes
- **Octave**: Spans 2 octaves (bass to treble)
- **Character**: Flowing, expansive, cinematic
- **Best for**: Wide landscapes, emotional climaxes, dream sequences

### 7. Syncopated Chord (syncopated_chord)

Strong beat bass notes followed by weak beat full chords.

```
Beat:  1        2        3        4
Note:  Bass     R-3-5    Bass     R-3-5
Vel:   48       32       48       32
```

- **Time signature**: 4/4
- **Resolution**: Quarter notes
- **Octave**: Bass in low octave, chords in middle
- **Character**: Rhythmic, off-beat, jazzy
- **Best for**: Urban scenes, evening walks, cafe settings

### 8. Gentle Rock (gentle_rock)

An 8th-note alternating bass-chord pattern with a rock feel.

```
Beat:  1   &   2   &   3   &   4   &
Note:  R   Ch  R   Ch  R   Ch  R   Ch
Vel:   45  30  45  30  45  30  45  30
```

- **Time signature**: 4/4
- **Resolution**: 8th notes
- **Octave**: Bass in low octave, chords in middle
- **Character**: Steady, driving, energetic
- **Best for**: Active scenes, travel sequences, sports events

### 9. Ballad Arpeggio (ballad_arp)

A slow, lyrical arpeggio with mixed durations and a dotted feel.

```
Pattern: [R-12] [3rd] [R] [5th] [R] [3rd] [5th] [R+12]
Dur:     8th    8th   qtr  qtr   8th  8th    qtr   qtr
```

- **Time signature**: 4/4
- **Resolution**: Mixed (8th and quarter notes)
- **Octave**: Spans 1-2 octaves
- **Character**: Gentle, lyrical, expressive
- **Best for**: Ballad scenes, emotional confessions, quiet moments

### 10. Pulse Chord (pulse_chord)

Sustained chords played on each beat, creating a pulsing atmosphere.

```
Beat:  1        2        3        4
Note:  R-3-5    R-3-5    R-3-5    R-3-5
Vel:   38       38       38       38
(1st inversion, one octave lower)
```

- **Time signature**: 4/4
- **Resolution**: Quarter notes
- **Octave**: One octave below melody (1st inversion)
- **Character**: Pulsing, atmospheric, meditative
- **Best for**: Ambient scenes, contemplative moments, introspective sequences

---

## Pattern Comparison Table

### By Note Density

| Pattern | Notes per Beat | Density | Batch |
|---------|----------------|---------|-------|
| gentle_rock | 2 | High | 3 |
| arpeggio_1353 | 2 | High | 2 |
| ballad_arp | 1.5 | Medium-High | 3 |
| syncopated_chord | 1.5 | Medium | 3 |
| broad_arpeggio | 1 | Medium | 3 |
| alternating_bass | 1 | Medium | 2 |
| syncopated | 1 | Medium | 2 |
| block_chord | 1 | Medium | 2 |
| pulse_chord | 1 | Medium | 3 |
| waltz | 0.75 | Low | 2 |

### By Dynamic Range

| Pattern | Min Vel | Max Vel | Range | Batch |
|---------|---------|---------|-------|-------|
| waltz | 35 | 50 | 15 | 2 |
| syncopated | 32 | 48 | 16 | 2 |
| gentle_rock | 30 | 45 | 15 | 3 |
| syncopated_chord | 32 | 48 | 16 | 3 |
| alternating_bass | 42 | 48 | 6 | 2 |
| broad_arpeggio | 35 | 42 | 7 | 3 |
| block_chord | 40 | 40 | 0 | 2 |
| pulse_chord | 38 | 38 | 0 | 3 |
| arpeggio_1353 | 35 | 45 | 10 | 2 |
| ballad_arp | 32 | 40 | 8 | 3 |

### By Tempo Suitability

| Pattern | Min BPM | Max BPM | Optimal BPM | Batch |
|---------|---------|---------|-------------|-------|
| ballad_arp | 70 | 90 | 78 | 3 |
| block_chord | 75 | 90 | 80 | 2 |
| broad_arpeggio | 78 | 95 | 85 | 3 |
| arpeggio_1353 | 85 | 100 | 90 | 2 |
| pulse_chord | 80 | 95 | 88 | 3 |
| syncopated | 90 | 105 | 95 | 2 |
| waltz | 95 | 110 | 100 | 2 |
| syncopated_chord | 85 | 100 | 92 | 3 |
| gentle_rock | 100 | 115 | 105 | 3 |
| alternating_bass | 105 | 120 | 110 | 2 |