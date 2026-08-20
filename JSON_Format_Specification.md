# Do Muse JSON Format Specification

## Overview

Do Muse uses **JSON format** as the sole intermediate language between user input, AI generation, and manual editing. The program parses the JSON, builds a music21 score object, and exports it as a `.mxl` (compressed MusicXML) file.

---

## 1. Complete Example

```json
{
  "title": "Morning Improvisation",
  "composer": "Do Muse",
  "metadata": {
    "tempo_bpm": 110,
    "time_signature": "4/4",
    "key_signature": "G"
  },
  "tracks": [
    {
      "instrument": "Acoustic Grand Piano",
      "notes": [
        { "pitch": 67, "duration": "quarter", "velocity": 85, "text": "Andante" },
        { "pitch": 71, "duration": "quarter", "velocity": 85 },
        { "pitch": 74, "duration": "quarter", "velocity": 85, "tempo_change": 120 },
        { "pitch": 79, "duration": "half", "velocity": 90, "fermata": true },
        { "pitch": -1, "duration": "eighth", "velocity": 0 },
        { "pitch": 72, "duration": "eighth.", "velocity": 80, "pedal": "start" },
        { "pitch": 74, "duration": "half", "velocity": 80, "pedal": "stop" }
      ]
    },
    {
      "instrument": "Violin",
      "notes": [
        { "pitch": 48, "duration": "half", "velocity": 70 },
        { "pitch": 52, "duration": "half", "velocity": 70 },
        { "pitch": 55, "duration": "half", "velocity": 70 }
      ]
    }
  ]
}
```

---

## 2. Top-Level Structure

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | string | No | `"Untitled"` | Piece title (used as the export filename) |
| `composer` | string | No | `"Unknown"` | Composer name |
| `metadata` | object | **Yes** | — | Score metadata: tempo, time signature, etc. |
| `tracks` | array | **Yes** | — | List of tracks, each representing an instrument |
| `macros` | object | No | (none) | Named reusable note blocks, referenced via `{"ref": "name"}` (see Section 37) |

---

## 3. metadata

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `tempo_bpm` | integer | **Yes** | — | Tempo in BPM (e.g. 120 = 120 beats per minute) |
| `time_signature` | string | **Yes** | — | Time signature, format `"x/y"`, e.g. `"4/4"`, `"3/4"`, `"6/8"` |
| `key_signature` | string | No | None (C major) | Key signature, supports standard names like `"C"`, `"G"`, `"F"`, `"Bb"`, `"F#"` |

### time_signature Valid Values

| Value | Meaning |
|-------|---------|
| `"4/4"` | Common time |
| `"3/4"` | Waltz time |
| `"2/4"` | March time |
| `"6/8"` | Compound duple |
| `"12/8"` | Compound quadruple |

### key_signature Valid Values

| Value | Meaning |
|-------|---------|
| `"C"` | C major |
| `"G"` | G major (1 sharp) |
| `"D"` | D major (2 sharps) |
| `"F"` | F major (1 flat) |
| `"Bb"` | Bb major (2 flats) |
| `"a"` | A minor |
| `"e"` | E minor |

---

## 4. tracks (Array)

`tracks` is an array where each element represents an independent instrument track.

### Track Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `instrument` | string | **Yes** | Instrument name (General MIDI standard name, see mapping table) |
| `notes` | array | **Yes** | List of notes in performance order |
| `repeat_begin` | boolean | No | Repeat start marker, `true` indicates the track begins a repeat section |
| `repeat_end` | boolean | No | Repeat end marker, `true` indicates the track ends a repeat section |
| `volta` | integer | No | Volta (1st/2nd ending) number, range **1-4** |

---

## 5. notes (Array)

`notes` is an array of note objects within each track. Notes **must be strictly ordered** by their performance time.

### Note Object

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `pitch` | integer or null | **Yes** | — | MIDI pitch number, range **21-108**; `-1` or `null` indicates a rest |
| `duration` | string | **Yes** | — | Duration (see duration specification below) |
| `velocity` | integer | No | `80` | Velocity, range **0-127** (0 = quietest, 127 = loudest) |
| `tuplet` | integer | No | None | Tuplet type (see Tuplet section), e.g. `3` for triplet |
| `articulation` | string | No | None | Articulation marking (see Articulation section) |
| `dynamics` | string | No | None | Dynamics marking (see Dynamics section) |
| `tie` | string | No | None | Tie, `"start"` / `"stop"` / `"continue"` |
| `slur` | string | No | None | Slur, `"start"` / `"stop"` / `"continue"` |
| `lyric` | string | No | None | Lyric text (max 100 characters) |
| `ornament` | string | No | None | Ornament type (see Ornament section) |
| `grace_note` | object | No | None | Grace note (see Grace Note section) |
| `tempo_change` | integer | No | None | Tempo change at this note, range **20-300** BPM |
| `text` | string | No | None | Text annotation (e.g. `"Andante"`), max 200 characters |
| `fermata` | boolean | No | None | Fermata (pause), `true` means the note is held longer |
| `pedal` | string | No | None | Sustain pedal, `"start"` / `"continue"` / `"stop"` |
| `chord` | array | No | None | Chord pitch array, e.g. `[60, 64, 67]` for C major triad |
| `time_signature_change` | string | No | None | Time signature change, format `"x/y"`, e.g. `"3/4"` |
| `key_signature_change` | string | No | None | Key signature change, e.g. `"G"`, `"F"`, `"Bb"` |
| `arpeggio` | boolean | No | None | Arpeggio, `true` means the chord is played arpeggiated |
| `tremolo` | object | No | None | Tremolo, contains a `duration` field for the tremolo note value |
| `glissando` | boolean | No | None | Glissando, `true` means slide from the previous note |
| `navigation` | string | No | None | Navigation marker, `"D.C."` / `"D.S."` / `"Coda"` / `"Fine"` |
| `hairpin` | string | No | None | Hairpin (crescendo/diminuendo wedge), `"crescendo"` / `"diminuendo"` / `"stop"` |
| `tempo_gradual` | object | No | None | Gradual tempo change, contains `target_bpm` and `duration_beats` |
| `subito` | string | No | None | Subito (sudden dynamic change), e.g. `"p"`, `"f"`, `"ff"` |
| `expression` | string | No | None | Expression text, e.g. `"espressivo"`, `"con passione"`, max 200 characters |

### pitch MIDI Reference

| MIDI Number | Note Name | Octave |
|-------------|-----------|--------|
| 21 | A0 | Lowest piano note |
| 36 | C2 | Bass |
| 48 | C3 | Below middle C |
| 60 | **C4** | **Middle C** |
| 72 | C5 | Treble |
| 84 | C6 | High treble |
| 96 | C7 | Very high |
| 108 | C8 | Highest piano note |

---

## 6. Duration String Specification

### 6.1 Base Durations

| String | Meaning | Quarter Note Units |
|--------|---------|-------------------|
| `"whole"` | Whole note | 4.0 |
| `"half"` | Half note | 2.0 |
| `"quarter"` | Quarter note | 1.0 |
| `"eighth"` | Eighth note | 0.5 |
| `"16th"` | Sixteenth note | 0.25 |
| `"32nd"` | Thirty-second note | 0.125 |
| `"64th"` | Sixty-fourth note | 0.0625 |

### 6.2 Dotted Notes

Append `.` to the base duration for a dotted note (1.5x the base duration).

| String | Meaning | Quarter Note Units |
|--------|---------|-------------------|
| `"half."` | Dotted half note | 3.0 |
| `"quarter."` | Dotted quarter note | 1.5 |
| `"eighth."` | Dotted eighth note | 0.75 |
| `"16th."` | Dotted sixteenth note | 0.375 |

---

## 7. Offset Accumulation Rule (Core Logic)

Notes in the `notes` array must be in strict performance order. The program automatically calculates each note's offset by **sequential accumulation**:

1. Initialize the track's cumulative offset to `0.0` (in quarter note units)
2. Iterate through the `notes` array:
   - Current note's start position = current cumulative offset
   - After processing, cumulative offset += current note's duration value

### Example

```json
"notes": [
  { "pitch": 60, "duration": "quarter", "velocity": 80 },  // offset=0.0, occupies 1.0 beat
  { "pitch": 62, "duration": "quarter", "velocity": 80 },  // offset=1.0, occupies 1.0 beat
  { "pitch": 64, "duration": "half",   "velocity": 80 },  // offset=2.0, occupies 2.0 beats
  { "pitch": -1, "duration": "quarter", "velocity": 0 },   // offset=4.0, rest 1.0 beat
  { "pitch": 67, "duration": "eighth.", "velocity": 80 }   // offset=5.0, occupies 0.75 beats
]
```

> Total track length: 5.75 quarter note beats.

---

## 8. Rests

| pitch Value | Meaning |
|-------------|---------|
| `-1` or `null` | Rest, duration specified by the `duration` field |

Example (quarter rest):

```json
{ "pitch": -1, "duration": "quarter", "velocity": 0 }
```

> Note: `velocity` is meaningless for rests but must be provided syntactically.

---

## 9. Tuplets

Tuplets compress multiple notes into a standard beat group. Add the `"tuplet"` field to each note.

### 9.1 Supported Tuplet Types

| tuplet Value | Name | Meaning | Actual Duration Factor |
|-------------|------|---------|----------------------|
| `3` | Triplet | 3 notes replace 2 | × 2/3 |
| `5` | Quintuplet | 5 notes replace 4 | × 4/5 |
| `6` | Sextuplet | 6 notes replace 4 | × 4/6 |
| `7` | Septuplet | 7 notes replace 4 | × 4/7 |
| `9` | Nonuplet | 9 notes replace 8 | × 8/9 |

### 9.2 Triplet Example

```json
"notes": [
  { "pitch": 60, "duration": "eighth", "velocity": 80, "tuplet": 3 },
  { "pitch": 64, "duration": "eighth", "velocity": 80, "tuplet": 3 },
  { "pitch": 67, "duration": "eighth", "velocity": 80, "tuplet": 3 }
]
```

> 3 eighth-note triplets, total duration = 1.0 quarter note (equivalent to 2 regular eighth notes).

### 9.3 Usage Rules

- **Every note** in the tuplet group must have the `tuplet` field
- All notes in a group must have the same `tuplet` value
- The `duration` field retains the base type (e.g., triplet still uses `"eighth"`)
- The program calculates actual duration: `actual = base × (normal / actual)`
- Tuplets cannot be combined with dotted notes

---

## 10. Articulation

Add the `"articulation"` field to note objects.

### 10.1 Supported Types

| articulation Value | Name | Effect |
|-------------------|------|--------|
| `"staccato"` | Staccato | Shortened, with space between notes |
| `"staccatissimo"` | Staccatissimo | Even shorter than staccato |
| `"accent"` | Accent | Played louder |
| `"tenuto"` | Tenuto | Held to full duration |
| `"marcato"` | Marcato | Accent + staccato combination |
| `"sforzando"` | Sforzando | Sudden strong accent |

### 10.2 Example

```json
"notes": [
  { "pitch": 60, "duration": "quarter", "articulation": "staccato" },
  { "pitch": 62, "duration": "quarter", "articulation": "accent" },
  { "pitch": 64, "duration": "half", "articulation": "tenuto" }
]
```

---

## 11. Dynamics

Add the `"dynamics"` field to note objects.

### 11.1 Supported Dynamics

| dynamics Value | Name | Meaning |
|---------------|------|---------|
| `"pppp"` | Pianississimo | Extremely soft |
| `"ppp"` | Pianissimo | Very soft |
| `"pp"` | Piano | Soft |
| `"p"` | Piano | Soft |
| `"mp"` | Mezzo-piano | Moderately soft |
| `"mf"` | Mezzo-forte | Moderately loud |
| `"f"` | Forte | Loud |
| `"ff"` | Fortissimo | Very loud |
| `"fff"` | Fortississimo | Extremely loud |
| `"ffff"` | Fortississimo | Even louder |
| `"sfz"` | Sforzando | Sudden accent |
| `"sf"` | Sforzando | Sudden accent |
| `"fz"` | Forzando | Forced accent |
| `"rfz"` | Rinforzando | Reinforced |
| `"sffz"` | Sforzandissimo | Very strong accent |
| `"fp"` | Forte-piano | Loud then immediately soft |
| `"sfp"` | Sforzando-piano | Accented then soft |
| `"crescendo"` | Crescendo | Gradually louder |
| `"diminuendo"` | Diminuendo | Gradually softer |
| `"calando"` | Calando | Softer and slower |
| `"morendo"` | Morendo | Dying away |
| `"smorzando"` | Smorzando | Fading away |
| `"rinforzando"` | Rinforzando | Intensifying throughout |

### 11.2 Example

```json
"notes": [
  { "pitch": 60, "duration": "quarter", "dynamics": "p" },
  { "pitch": 62, "duration": "quarter", "dynamics": "mf" },
  { "pitch": 64, "duration": "half", "dynamics": "f" }
]
```

---

## 12. Tie

Add the `"tie"` field to connect two notes of the same pitch.

### 12.1 Values

| tie Value | Meaning |
|-----------|---------|
| `"start"` | Tie start |
| `"stop"` | Tie end |
| `"continue"` | Middle of a multi-measure tie |

### 12.2 Example

```json
"notes": [
  { "pitch": 60, "duration": "half", "tie": "start" },
  { "pitch": 60, "duration": "half", "tie": "stop" },
  { "pitch": 62, "duration": "quarter" }
]
```

---

## 13. Slur

Add the `"slur"` field to connect notes of different pitches.

### 13.1 Values

| slur Value | Meaning |
|------------|---------|
| `"start"` | Slur start |
| `"stop"` | Slur end |
| `"continue"` | Middle of a multi-note slur |

### 13.2 Example

```json
"notes": [
  { "pitch": 60, "duration": "quarter", "slur": "start" },
  { "pitch": 62, "duration": "quarter" },
  { "pitch": 64, "duration": "quarter" },
  { "pitch": 67, "duration": "quarter", "slur": "stop" }
]
```

---

## 14. Lyric

Add the `"lyric"` field to attach text to notes for vocal works.

### 14.1 Example

```json
"notes": [
  { "pitch": 60, "duration": "quarter", "lyric": "Hel" },
  { "pitch": 62, "duration": "quarter", "lyric": "lo" },
  { "pitch": 64, "duration": "half", "lyric": "world" }
]
```

---

## 15. Ornament

Add the `"ornament"` field to decorate notes.

### 15.1 Supported Types

| ornament Value | Name | Effect |
|---------------|------|--------|
| `"trill"` | Trill | Rapid alternation with the upper neighbor |
| `"mordent"` | Mordent (upper) | Main note → upper → main |
| `"inverted_mordent"` | Mordent (lower) | Main note → lower → main |
| `"turn"` | Turn | Upper → main → lower → main |
| `"inverted_turn"` | Inverted turn | Lower → main → upper → main |

### 15.2 Example

```json
"notes": [
  { "pitch": 60, "duration": "half", "ornament": "trill" },
  { "pitch": 62, "duration": "quarter", "ornament": "mordent" },
  { "pitch": 64, "duration": "half", "ornament": "turn" }
]
```

---

## 16. Grace Note

Add the `"grace_note"` object field to insert a grace note before the main note.

### 16.1 grace_note Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `pitch` | integer | **Yes** | — | Grace note pitch, range 21-108 |
| `duration` | string | No | `"16th"` | Grace note duration (does not affect main note duration) |

### 16.2 Example

```json
"notes": [
  {
    "pitch": 64,
    "duration": "quarter",
    "velocity": 80,
    "grace_note": { "pitch": 60, "duration": "16th" }
  },
  {
    "pitch": 67,
    "duration": "quarter",
    "velocity": 80,
    "grace_note": { "pitch": 62 }
  }
]
```

---

## 17. Tempo Change

Add the `"tempo_change"` field to change tempo at any position.

### 17.1 Example

```json
"notes": [
  { "pitch": 60, "duration": "half", "velocity": 80 },
  { "pitch": 62, "duration": "quarter", "velocity": 80 },
  { "pitch": 64, "duration": "quarter", "velocity": 80, "tempo_change": 140 },
  { "pitch": 67, "duration": "half", "velocity": 85 },
  { "pitch": 69, "duration": "quarter", "velocity": 80, "tempo_change": 100 }
]
```

---

## 18. Text Annotation

Add the `"text"` field for arbitrary text annotations.

### 18.1 Example

```json
"notes": [
  { "pitch": 60, "duration": "half", "text": "Andante" },
  { "pitch": 62, "duration": "quarter", "text": "dolce" },
  { "pitch": 64, "duration": "quarter", "text": "slowing" }
]
```

---

## 19. Fermata

Add `"fermata": true` to indicate a note should be held longer.

### 19.1 Example

```json
"notes": [
  { "pitch": 60, "duration": "half", "velocity": 85, "fermata": true },
  { "pitch": 62, "duration": "quarter", "velocity": 80 },
  { "pitch": 64, "duration": "half", "velocity": 85, "fermata": true }
]
```

---

## 20. Sustain Pedal

Add the `"pedal"` field to indicate piano sustain pedal marks.

### 20.1 Values

| pedal Value | Meaning | Notation |
|-------------|---------|----------|
| `"start"` | Press pedal | `Ped.` |
| `"continue"` | Keep pedal pressed | `Ped.` (continued) |
| `"stop"` | Release pedal | `Ped. stop` |

### 20.2 Example

```json
"notes": [
  { "pitch": 60, "duration": "half", "velocity": 80, "pedal": "start" },
  { "pitch": 62, "duration": "half", "velocity": 80, "pedal": "continue" },
  { "pitch": 64, "duration": "half", "velocity": 80 },
  { "pitch": 67, "duration": "half", "velocity": 80, "pedal": "stop" }
]
```

---

## 21. Repeat and Volta

Set repeat markers at the track level.

### 21.1 Fields

| Field | Type | Description |
|-------|------|-------------|
| `repeat_begin` | boolean | `true` marks the start of a repeat section |
| `repeat_end` | boolean | `true` marks the end of a repeat section |
| `volta` | integer | Volta (ending) number, 1-4 |

### 21.2 Example

```json
{
  "instrument": "Acoustic Grand Piano",
  "repeat_begin": true,
  "notes": [
    { "pitch": 60, "duration": "quarter" },
    { "pitch": 62, "duration": "quarter" },
    { "pitch": 64, "duration": "quarter" },
    { "pitch": 67, "duration": "quarter" }
  ],
  "repeat_end": true
}
```

---

## 22. Chord

Add the `"chord"` field (array of integers) for simultaneous notes.

### 22.1 Example

```json
"notes": [
  { "chord": [60, 64, 67], "duration": "quarter", "velocity": 80 },
  { "chord": [62, 65, 69], "duration": "quarter", "velocity": 80 },
  { "chord": [60, 63, 67], "duration": "half", "velocity": 85 }
]
```

### 22.2 Rules

- `chord` and `pitch` are mutually exclusive: if `chord` is provided, `pitch` is ignored
- The chord's `duration` applies to all notes in the chord
- Chords support articulation, dynamics, tie, fermata, etc.
- Best combined with `arpeggio: true`

---

## 23. Time Signature Change

Add the `"time_signature_change"` field to change time signature mid-piece.

### 23.1 Example

```json
"notes": [
  { "pitch": 60, "duration": "quarter" },
  { "pitch": 62, "duration": "quarter" },
  { "pitch": 64, "duration": "quarter", "time_signature_change": "3/4" },
  { "pitch": 67, "duration": "quarter" }
]
```

---

## 24. Key Signature Change

Add the `"key_signature_change"` field to change key signature mid-piece.

### 24.1 Example

```json
"notes": [
  { "pitch": 60, "duration": "half" },
  { "pitch": 62, "duration": "quarter" },
  { "pitch": 64, "duration": "quarter", "key_signature_change": "G" },
  { "pitch": 67, "duration": "half" }
]
```

---

## 25. Arpeggio

Add `"arpeggio": true` to play a chord's notes sequentially.

### 25.1 Example

```json
"notes": [
  { "chord": [60, 64, 67], "duration": "half", "velocity": 80, "arpeggio": true },
  { "chord": [62, 65, 69], "duration": "half", "velocity": 80, "arpeggio": true },
  { "pitch": 72, "duration": "whole", "velocity": 85 }
]
```

---

## 26. Tremolo

Add the `"tremolo"` object for rapid note repetition or alternation.

### 26.1 Fields

| Field | Type | Description |
|-------|------|-------------|
| `tremolo.duration` | string | Tremolo note value, default `"eighth"` |

### 26.2 Example

```json
"notes": [
  { "pitch": 60, "duration": "half", "velocity": 80, "tremolo": { "duration": "eighth" } },
  { "pitch": 62, "duration": "half", "velocity": 80, "tremolo": { "duration": "16th" } }
]
```

---

## 27. Glissando

Add `"glissando": true` to slide from the previous note to the current note.

### 27.1 Example

```json
"notes": [
  { "pitch": 60, "duration": "quarter", "velocity": 80 },
  { "pitch": 72, "duration": "quarter", "velocity": 80, "glissando": true },
  { "pitch": 60, "duration": "quarter", "velocity": 80 },
  { "pitch": 84, "duration": "quarter", "velocity": 80, "glissando": true }
]
```

### 27.2 Rules

- Place `glissando` on the **target note** (the note being slid to)
- The program draws a glissando line from the track's previous note to the current note
- If the current note is the first in the track, glissando is ignored

---

## 28. Navigation Markers

Add the `"navigation"` field for structural navigation.

### 28.1 Values

| navigation Value | Name | Meaning |
|-----------------|------|---------|
| `"D.C."` | Da Capo | Repeat from the beginning |
| `"D.S."` | Dal Segno | Repeat from the sign |
| `"Coda"` | Coda | Jump to the coda |
| `"Fine"` | Fine | End of piece |

### 28.2 Example

```json
"notes": [
  { "pitch": 60, "duration": "quarter", "velocity": 80 },
  { "pitch": 62, "duration": "quarter", "velocity": 80 },
  { "pitch": 64, "duration": "quarter", "velocity": 80 },
  { "pitch": 67, "duration": "half", "velocity": 85, "navigation": "D.C." },
  { "pitch": 69, "duration": "whole", "velocity": 80, "navigation": "Fine" }
]
```

---

## 29. Hairpin (Crescendo/Diminuendo Wedge)

Add the `"hairpin"` field for crescendo `<` and diminuendo `>` markings.

### 29.1 Values

| hairpin Value | Meaning |
|--------------|---------|
| `"crescendo"` | Start crescendo (`<`) |
| `"diminuendo"` | Start diminuendo (`>`) |
| `"stop"` | End current hairpin |

### 29.2 Crescendo Example

```json
"notes": [
  { "pitch": 60, "duration": "quarter", "velocity": 70, "hairpin": "crescendo" },
  { "pitch": 62, "duration": "quarter", "velocity": 75 },
  { "pitch": 64, "duration": "quarter", "velocity": 80 },
  { "pitch": 67, "duration": "quarter", "velocity": 85, "hairpin": "stop" }
]
```

### 29.3 Diminuendo Example

```json
"notes": [
  { "pitch": 72, "duration": "quarter", "velocity": 85, "hairpin": "diminuendo" },
  { "pitch": 71, "duration": "quarter", "velocity": 80 },
  { "pitch": 69, "duration": "quarter", "velocity": 75 },
  { "pitch": 67, "duration": "quarter", "velocity": 70, "hairpin": "stop" }
]
```

### 29.4 Rules

- Must be paired: start with `"crescendo"` or `"diminuendo"`, end with `"stop"`
- The wedge extends from the start note to the end note
- Best used with `velocity` changes for realistic effect

---

## 30. Gradual Tempo Change (Accelerando / Ritardando)

Add the `"tempo_gradual"` object for gradual tempo transitions.

### 30.1 Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `target_bpm` | integer | **Yes** | — | Target tempo, range **20-300** BPM |
| `duration_beats` | float | No | `4.0` | Duration of the transition in beats, range 0.1-100 |

### 30.2 Accelerando Example

```json
"notes": [
  { "pitch": 60, "duration": "quarter", "velocity": 80 },
  { "pitch": 62, "duration": "quarter", "velocity": 80, "tempo_gradual": { "target_bpm": 140, "duration_beats": 4.0 } },
  { "pitch": 64, "duration": "quarter", "velocity": 85 },
  { "pitch": 67, "duration": "quarter", "velocity": 85 },
  { "pitch": 69, "duration": "quarter", "velocity": 90 },
  { "pitch": 72, "duration": "half", "velocity": 90 }
]
```

### 30.3 Ritardando Example

```json
"notes": [
  { "pitch": 72, "duration": "quarter", "velocity": 85 },
  { "pitch": 71, "duration": "quarter", "velocity": 80, "tempo_gradual": { "target_bpm": 80, "duration_beats": 3.0 } },
  { "pitch": 69, "duration": "quarter", "velocity": 75 },
  { "pitch": 67, "duration": "half", "velocity": 70 },
  { "pitch": 60, "duration": "whole", "velocity": 65, "fermata": true }
]
```

### 30.4 Implementation

- The program inserts intermediate tempo markings during the transition
- Step count is calculated from `duration_beats` (approximately one step per 0.5 beats, max 10 steps)
- After the transition, tempo stabilizes at `target_bpm`

---

## 31. Subito (Sudden Dynamic Change)

Add the `"subito"` field for sudden dynamic changes.

### 31.1 Example

```json
"notes": [
  { "pitch": 60, "duration": "half", "velocity": 80, "dynamics": "ff" },
  { "pitch": 62, "duration": "half", "velocity": 80, "dynamics": "ff" },
  { "pitch": 64, "duration": "quarter", "velocity": 40, "subito": "p" },
  { "pitch": 67, "duration": "quarter", "velocity": 40 },
  { "pitch": 69, "duration": "half", "velocity": 90, "subito": "ff" },
  { "pitch": 72, "duration": "whole", "velocity": 90 }
]
```

---

## 32. Expression Text

Add the `"expression"` field for performance instructions.

### 32.1 Common Expression Terms

| Term | Meaning | Use Case |
|------|---------|----------|
| `"espressivo"` | Expressive | Melodic passages |
| `"dolce"` | Sweet, gentle | Lyrical passages |
| `"con passione"` | With passion | Climactic passages |
| `"agitato"` | Agitated | Tense passages |
| `"tranquillo"` | Calm | Peaceful passages |
| `"maestoso"` | Majestic | Opening/closing |
| `"rubato"` | Free tempo | Improvisatory passages |
| `"cantabile"` | Singing style | Melodic playing |
| `"leggiero"` | Light | Fast passages |
| `"appassionato"` | Passionate | Intense emotional passages |
| `"doloroso"` | Sad, sorrowful | Melancholic passages |
| `"giocoso"` | Playful, joyful | Cheerful passages |
| `"con fuoco"` | With fire | Intense passages |
| `"sostenuto"` | Sustained | Slowing, extending |
| `"calando"` | Slowing and softening | Section endings |

### 32.2 Example: Emotional Arc

```json
"notes": [
  { "pitch": 60, "duration": "half", "velocity": 60, "expression": "tranquillo" },
  { "pitch": 62, "duration": "quarter", "velocity": 65 },
  { "pitch": 64, "duration": "quarter", "velocity": 70, "expression": "espressivo" },
  { "pitch": 67, "duration": "half", "velocity": 80, "expression": "con passione",
    "hairpin": "crescendo", "dynamics": "crescendo" },
  { "pitch": 72, "duration": "half", "velocity": 90, "hairpin": "stop" },
  { "pitch": 76, "duration": "whole", "velocity": 95, "expression": "maestoso",
    "fermata": true },
  { "pitch": 67, "duration": "half", "velocity": 50, "subito": "p",
    "expression": "dolce" }
]
```

---

## 33. General MIDI Instrument Names (Common)

| Instrument Name | Program Number | Description |
|----------------|----------------|-------------|
| Acoustic Grand Piano | 0 | Grand piano (default) |
| Bright Acoustic Piano | 1 | Bright piano |
| Electric Grand Piano | 2 | Electric grand |
| Honky-tonk Piano | 3 | Honky-tonk piano |
| Electric Piano 1 | 4 | Electric piano 1 |
| Violin | 40 | Violin |
| Viola | 41 | Viola |
| Cello | 42 | Cello |
| Contrabass | 43 | Double bass |
| Trumpet | 56 | Trumpet |
| Trombone | 57 | Trombone |
| French Horn | 60 | French horn |
| Tuba | 58 | Tuba |
| Alto Sax | 65 | Alto saxophone |
| Tenor Sax | 66 | Tenor saxophone |
| Oboe | 68 | Oboe |
| Flute | 73 | Flute |
| Piccolo | 72 | Piccolo |
| Clarinet | 71 | Clarinet |
| Bassoon | 70 | Bassoon |

> Full 128 General MIDI instrument set is supported. Unrecognized names default to Acoustic Grand Piano.

---

## 34. Quick Validation Checklist

Before submitting JSON, verify:

- [ ] `metadata` exists with `tempo_bpm` (integer) and `time_signature` (format `"x/y"`)
- [ ] `tracks` is a non-empty array
- [ ] Each track has `instrument` (string) and `notes` (non-empty array)
- [ ] Each note has `pitch` (integer, 21-108 or -1) and `duration` (valid duration)
- [ ] `velocity` if provided, is in 0-127 range
- [ ] `tuplet` if provided, must be `3`, `5`, `6`, `7`, or `9`
- [ ] `articulation` if provided, must be a valid articulation type
- [ ] `dynamics` if provided, must be a valid dynamics marking
- [ ] `tie` if provided, must be `"start"`, `"stop"`, or `"continue"`
- [ ] `slur` if provided, must be `"start"`, `"stop"`, or `"continue"`
- [ ] `lyric` if provided, must be a string ≤ 100 characters
- [ ] `ornament` if provided, must be a valid ornament type
- [ ] `grace_note` if provided, must contain `pitch` field
- [ ] `tempo_change` if provided, must be 20-300
- [ ] `text` if provided, must be a string ≤ 200 characters
- [ ] `fermata` if provided, must be boolean `true`
- [ ] `pedal` if provided, must be `"start"`, `"continue"`, or `"stop"`
- [ ] `chord` if provided, must be an array of integers (21-108)
- [ ] `time_signature_change` if provided, format must be `"x/y"`
- [ ] `key_signature_change` if provided, must be a string (e.g. `"G"`, `"F"`)
- [ ] `arpeggio` if provided, must be boolean `true`
- [ ] `tremolo` if provided, must be an object with `duration` field
- [ ] `glissando` if provided, must be boolean `true`
- [ ] `navigation` if provided, must be `"D.C."`, `"D.S."`, `"Coda"`, or `"Fine"`
- [ ] `hairpin` if provided, must be `"crescendo"`, `"diminuendo"`, or `"stop"` (paired)
- [ ] `tempo_gradual` if provided, must be an object with `target_bpm` (20-300) and optional `duration_beats`
- [ ] `subito` if provided, must be a valid dynamics marking
- [ ] `expression` if provided, must be a string ≤ 200 characters
- [ ] `repeat_begin` / `repeat_end` if provided, must be boolean
- [ ] `volta` if provided, must be 1-4
- [ ] `notes` are in performance order
- [ ] No stray commas, mismatched quotes, or other JSON syntax errors

---

## 35. Common Errors

| Error | Incorrect | Correct |
|-------|-----------|---------|
| Time signature format | `"time_signature": "4/4/4"` | `"time_signature": "4/4"` |
| Pitch out of range | `"pitch": 200` | `"pitch": 72` |
| Invalid duration | `"duration": "triplet"` | `"duration": "quarter"` |
| Velocity out of range | `"velocity": 999` | `"velocity": 100` |
| Missing instrument | `{}` | `{"instrument": "Piano", "notes": [...]}` |
| Empty notes | `"notes": []` | `"notes": [{"pitch": 60, "duration": "quarter"}]` |
| Invalid tuplet | `"tuplet": 4` | `"tuplet": 3` (triplet) or remove field |
| Invalid articulation | `"articulation": "legato"` | `"articulation": "tenuto"` |
| Invalid dynamics | `"dynamics": "forte"` | `"dynamics": "f"` |
| Wrong tie value | `"tie": "begin"` | `"tie": "start"` |
| Ornament misspelling | `"ornament": "tremolo"` | `"ornament": "trill"` |
| Grace note missing pitch | `"grace_note": {}` | `"grace_note": {"pitch": 60}` |
| Tempo change out of range | `"tempo_change": 500` | `"tempo_change": 140` (20-300) |
| Wrong fermata type | `"fermata": "yes"` | `"fermata": true` |
| Wrong pedal value | `"pedal": "on"` | `"pedal": "start"` / `"continue"` / `"stop"` |
| Repeat not boolean | `"repeat_begin": 1` | `"repeat_begin": true` |
| Chord not an array | `"chord": "60,64,67"` | `"chord": [60, 64, 67]` |
| Chord pitch out of range | `"chord": [60, 200]` | `"chord": [60, 72]` |
| Time sig change format | `"time_signature_change": "3/4/4"` | `"time_signature_change": "3/4"` |
| Arpeggio not boolean | `"arpeggio": "yes"` | `"arpeggio": true` |
| Tremolo not an object | `"tremolo": "eighth"` | `"tremolo": {"duration": "eighth"}` |
| Glissando not boolean | `"glissando": "yes"` | `"glissando": true` |
| Navigation invalid | `"navigation": "Repeat"` | `"navigation": "D.C."` |
| Hairpin invalid | `"hairpin": "forte"` | `"hairpin": "crescendo"` |
| Tempo gradual missing target | `"tempo_gradual": {}` | `"tempo_gradual": {"target_bpm": 140}` |
| Subito invalid | `"subito": "loud"` | `"subito": "f"` |
| Expression too long | `"expression": "..." (>200 chars)` | Shorten to 200 characters or fewer |

---

## 36. Multi-Format Support

Do Muse now supports multiple input and output formats beyond JSON.

### 36.1 Input Formats (Import)

| Format | Extension | Description | Supported via |
|--------|-----------|-------------|---------------|
| JSON | `.json` | Native Do Muse score format | Direct read |
| MusicXML | `.xml`, `.mxl` | Industry standard music notation format | music21 converter |
| MIDI | `.mid`, `.midi` | Universal digital music interface format | music21 converter |

### 36.2 Output Formats (Export)

| Format | Extension | Description | Export Key |
|--------|-----------|-------------|------------|
| MXL | `.mxl` | Compressed MusicXML (default) | `mxl` |
| MIDI | `.mid` | Standard MIDI File | `midi` |
| MusicXML | `.xml` | Uncompressed MusicXML | `xml` |
| LilyPond | `.ly` | LilyPond music notation file | `ly` |
| MP3 | `.mp3` | MPEG Layer III (lossy compressed audio) | `mp3` |
| WAV | `.wav` | RIFF Waveform (uncompressed audio) | `wav` |
| FLAC | `.flac` | Free Lossless Audio Codec | `flac` |
| OGG | `.ogg` | OGG Vorbis (lossy compressed audio) | `ogg` |

### 36.3 How Import Works

1. MusicXML or MIDI file is parsed by music21's `converter.parse()`
2. Parts, notes, dynamics, articulations, ties, lyrics, ornaments, etc. are extracted
3. The data is converted to the standard Do Muse JSON format (see Sections 1-35)
4. The JSON is loaded into the editor for review and validation
5. Limited metadata (title, composer, tempo, time signature, key signature) is extracted from the first part

### 36.4 How Export Works

	1. JSON content is validated using the same validation rules (Section 34)
	2. A music21 Score object is built via `_build_score()` (shared by all exporters)
	3. The Score is written to the target format:
	   - **MXL**: MusicXML → DOCTYPE removed → compressed into `.mxl` ZIP
	   - **MIDI**: Direct music21 `score.write('midi', fp=...)`
	   - **MusicXML**: MusicXML → DOCTYPE removed → saved as `.xml`
	   - **LilyPond**: Direct music21 `score.write('lilypond', fp=...)`
	   - **Audio (MP3/WAV/FLAC/OGG)**: MusicXML → DOCTYPE removed → MuseScore CLI renders to audio via `MuseScore4 -o output.mp3 -b 192 input.xml`

### 36.5 Audio Export Dependencies

Audio export (MP3, WAV, FLAC, OGG) requires **MuseScore Studio 4** to be installed on the system. Do Muse locates the MuseScore executable via:

1. `shutil.which()` — searches PATH for `MuseScore4`, `MuseScore3`, `musescore`
2. Hardcoded candidate paths on Windows, Linux, and macOS

The MuseScore CLI determines the output format from the file extension and uses its built-in SoundFont synthesizer for audio rendering. The `-b` flag sets the MP3 bitrate (default: 192 kbit/s).

If MuseScore is not found, audio export raises an `OSError` with a message prompting the user to install MuseScore Studio 4.

### 36.6 Import Limitations
	
	- **MIDI files may lack dynamics, articulation, and notation details** since MIDI only stores note-on/note-off events and velocity
	- **MusicXML**: Grace notes, complex ornaments, and hairpins may not be fully preserved
	- **Metadata** (title, composer) is only available if the source file includes it
	- Instruments are mapped via General MIDI program numbers; unrecognized instruments default to "Acoustic Grand Piano"
	
	---
	
	## 37. Macro System (宏系统)
	
	### 37.1 Overview
	
	The Macro System allows defining reusable note blocks at the top level of the JSON
	and referencing them throughout the `notes` arrays. This avoids repeating the same
	note sequences multiple times, making the JSON more concise and maintainable.
	
	Macros are expanded **at validation time** — after expansion, the rest of the
	pipeline (export, preview) works with the fully expanded notes without any
	knowledge of macros.
	
	### 37.2 Macro Definition
	
	Add a `"macros"` field at the top level of the JSON. Each key is a macro name
	(string), and each value is an array of note objects:
	
	```json
	"macros": {
	  "bass_line": [
	    { "pitch": 36, "duration": "quarter", "velocity": 75 },
	    { "pitch": 43, "duration": "quarter", "velocity": 75 },
	    { "pitch": 40, "duration": "quarter", "velocity": 75 },
	    { "pitch": 48, "duration": "quarter", "velocity": 75 }
	  ],
	  "chord_hit": [
	    { "chord": [60, 64, 67], "duration": "half", "velocity": 85, "arpeggio": true }
	  ]
	}
	```
	
	### 37.3 Macro Reference
	
	Use `{"ref": "macro_name"}` as a note object in the `notes` array to reference
	a macro. The reference is replaced with the macro's notes array inline:
	
	```json
	"notes": [
	  { "ref": "bass_line" },
	  { "ref": "chord_hit" },
	  { "ref": "bass_line" },
	  { "pitch": 72, "duration": "whole", "velocity": 90 }
	]
	```
	
	After expansion, the above is equivalent to:
	```json
	"notes": [
	  { "pitch": 36, "duration": "quarter", "velocity": 75 },
	  { "pitch": 43, "duration": "quarter", "velocity": 75 },
	  { "pitch": 40, "duration": "quarter", "velocity": 75 },
	  { "pitch": 48, "duration": "quarter", "velocity": 75 },
	  { "chord": [60, 64, 67], "duration": "half", "velocity": 85, "arpeggio": true },
	  { "pitch": 36, "duration": "quarter", "velocity": 75 },
	  { "pitch": 43, "duration": "quarter", "velocity": 75 },
	  { "pitch": 40, "duration": "quarter", "velocity": 75 },
	  { "pitch": 48, "duration": "quarter", "velocity": 75 },
	  { "pitch": 72, "duration": "whole", "velocity": 90 }
	]
	```
	
	### 37.4 Validation Rules
	
	| Rule | Description |
	|------|-------------|
	| `macros` must be an object | Each key is a string, each value is a non-empty array |
	| Each macro must be a non-empty array | Empty macros are invalid |
	| Each macro note must have `pitch` or `chord` | Follows the same rules as regular notes |
	| Macro notes cannot contain `ref` | Nested macro references are not allowed |
	| `ref` references must be defined | Referencing an undefined macro name is an error |
	| `ref` cannot coexist with other fields | `{"ref": "x", "pitch": 60}` is invalid |
	| `ref` value must be a string | Non-string ref values are rejected |
	
	### 37.5 Complete Example
	
	```json
	{
	  "title": "Macro Demo",
	  "composer": "Do Muse",
	  "metadata": {
	    "tempo_bpm": 120,
	    "time_signature": "4/4",
	    "key_signature": "C"
	  },
	  "macros": {
	    "bass_line": [
	      { "pitch": 36, "duration": "quarter", "velocity": 75 },
	      { "pitch": 43, "duration": "quarter", "velocity": 75 },
	      { "pitch": 40, "duration": "quarter", "velocity": 75 },
	      { "pitch": 48, "duration": "quarter", "velocity": 75 }
	    ],
	    "chord_hit": [
	      { "chord": [60, 64, 67], "duration": "half", "velocity": 85, "arpeggio": true }
	    ]
	  },
	  "tracks": [
	    {
	      "instrument": "Acoustic Grand Piano",
	      "notes": [
	        { "ref": "bass_line" },
	        { "ref": "chord_hit" },
	        { "ref": "bass_line" },
	        { "ref": "chord_hit" },
	        { "pitch": 72, "duration": "whole", "velocity": 90 }
	      ]
	    }
	  ]
	}
	```
	
	### 37.6 Use Cases
	
	- **Ostinato / Bass lines**: Repeated bass patterns across multiple tracks
	- **Chord progressions**: Common harmonic sequences repeated throughout
	- **Scale runs**: Technical passages that appear in multiple sections
	- **Rhythmic patterns**: Drum or accompaniment patterns reused
	- **Section repeats**: Entire musical phrases reused in different parts of the piece