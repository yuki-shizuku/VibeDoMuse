# Do Muse - Galgame BGM Database

> **Category**: `galgame_bgm`
> **Total Pieces**: 44
> **Duration**: ~30 seconds each
> **Purpose**: AI training dataset for visual novel background music generation

---

## Overview

This database contains **44 pieces** of Galgame (Japanese Visual Novel) BGM-style music, generated using the **Do Muse** engine. Each piece is approximately 30 seconds in duration, designed for AI training, style transfer, and music generation fine-tuning.

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
├── generate_bgm.py          # Piece generation script (Python)
├── batch_convert.py         # Batch conversion script (JSON → MIDI → WAV)
├── output_json/             # 44 JSON source files
├── output_midi/             # 44 MIDI intermediate files
└── output_wav/              # 44 WAV audio files (~278 MB total)
```

### File Naming Convention

```
{melody_summary}.{ext}
```

Where `melody_summary` is a concise English descriptor reflecting the piece's character and mood.

---

## Piece Catalog

### 1. Daily Life / Relaxed (4 pieces)

| # | Name | Title (JP) | BPM | Key | Time | Instrument | Mood |
|---|------|------------|-----|-----|------|------------|------|
| 1 | morning_awakening | 朝の目覚め | 100 | C | 4/4 | Piano | Bright |
| 2 | school_road_scenery | 通学路の風景 | 110 | G | 4/4 | Music Box | Cheerful |
| 3 | classroom_daily | 教室の日常 | 90 | C | 4/4 | Piano | Gentle |
| 4 | lunch_break_moment | 昼休みのひととき | 105 | D | 4/4 | Piano | Cheerful |

### 2. School / Youth (4 pieces)

| # | Name | Title (JP) | BPM | Key | Time | Instrument | Mood |
|---|------|------------|-----|-----|------|------------|------|
| 5 | youth_footsteps | 青春の足音 | 120 | C | 4/4 | Piano | Bright |
| 6 | library_silence | 図書館の静けさ | 70 | C | 4/4 | Piano | Peaceful |
| 7 | gymnasium_echo | 体育館の響き | 130 | G | 4/4 | Piano | Energetic |
| 8 | school_festival_prep | 学園祭の準備 | 115 | C | 4/4 | Piano | Cheerful |

### 3. Romance / Tenderness (5 pieces)

| # | Name | Title (JP) | BPM | Key | Time | Instrument | Mood |
|---|------|------------|-----|-----|------|------------|------|
| 9 | first_love_melody | 初恋のメロディ | 85 | G | 4/4 | Violin | Romantic |
| 10 | starry_sky_promise | 星空の約束 | 75 | D | 4/4 | Piano | Romantic |
| 11 | under_cherry_tree | 桜の木の下で | 80 | C | 3/4 | Piano | Romantic |
| 12 | rain_then_confession | 雨のち告白 | 90 | F | 4/4 | Piano | Romantic |
| 13 | holding_hands | 手をつないで | 95 | G | 4/4 | Piano | Romantic |

### 4. Sadness / Melancholy (3 pieces)

| # | Name | Title (JP) | BPM | Key | Time | Instrument | Mood |
|---|------|------------|-----|-----|------|------------|------|
| 14 | reason_for_tears | 涙の理由 | 65 | a | 4/4 | Piano | Sad |
| 15 | farewell_station | 別れの駅 | 60 | a | 4/4 | Piano | Sad |
| 16 | endless_rain | 終わらない雨 | 70 | a | 4/4 | Piano | Melancholic |

### 5. Mystery / Dream (5 pieces)

| # | Name | Title (JP) | BPM | Key | Time | Instrument | Mood |
|---|------|------------|-----|-----|------|------------|------|
| 17 | into_dream_world | 夢の世界へ | 80 | C | 3/4 | Celesta | Dreamy |
| 18 | moonlight_waltz | 月明かりのワルツ | 85 | D | 3/4 | Piano | Dreamy |
| 19 | fairy_mischief | 妖精のいたずら | 110 | C | 4/4 | Music Box | Playful |
| 20 | starfall_fantasy | 星降る夜の幻想 | 75 | F | 4/4 | Piano | Dreamy |

### 6. Suspense / Tension (4 pieces)

| # | Name | Title (JP) | BPM | Key | Time | Instrument | Mood |
|---|------|------------|-----|-----|------|------------|------|
| 21 | mystery_room | 謎の部屋 | 90 | a | 4/4 | Piano | Mysterious |
| 22 | chase_theme | 追跡のテーマ | 140 | G | 4/4 | Piano | Tense |
| 23 | footsteps_in_dark | 暗闇の足音 | 95 | a | 4/4 | Piano | Tense |

### 7. Battle / Intense (4 pieces)

| # | Name | Title (JP) | BPM | Key | Time | Instrument | Mood |
|---|------|------------|-----|-----|------|------------|------|
| 24 | battle_determination | 決意の戦い | 140 | C | 4/4 | Piano | Intense |
| 25 | rising_courage | 立ち上がる勇気 | 130 | G | 4/4 | Trumpet | Intense |
| 26 | power_of_bonds | 絆の力 | 120 | C | 4/4 | Piano | Intense |
| 27 | comeback_moment | 逆転の瞬間 | 140 | G | 4/4 | Piano | Intense |

### 8. Nostalgia / Memory (4 pieces)

| # | Name | Title (JP) | BPM | Key | Time | Instrument | Mood |
|---|------|------------|-----|-----|------|------------|------|
| 28 | distant_promise | 遠い日の約束 | 75 | C | 4/4 | Piano | Nostalgic |
| 29 | old_album | 古びたアルバム | 70 | G | 4/4 | Piano | Nostalgic |
| 30 | childhood_dream | 子供時代の夢 | 85 | C | 3/4 | Music Box | Nostalgic |
| 31 | seasons_passed | 過ぎ去りし季節 | 70 | a | 4/4 | Piano | Nostalgic |

### 9. Night / Peace (5 pieces)

| # | Name | Title (JP) | BPM | Key | Time | Instrument | Mood |
|---|------|------------|-----|-----|------|------------|------|
| 32 | night_breeze_whisper | 夜風のささやき | 65 | C | 4/4 | Piano | Peaceful |
| 33 | moonlight_beach | 月明かりの浜辺 | 70 | G | 4/4 | Piano | Peaceful |
| 34 | lullaby | 子守唄 | 60 | C | 4/4 | Piano | Peaceful |
| 35 | midnight_piano | 真夜中のピアノ | 70 | D | 4/4 | Piano | Peaceful |
| 36 | star_twinkle | 星の瞬き | 75 | C | 4/4 | Piano | Peaceful |

### 10. Hope / Light (3 pieces)

| # | Name | Title (JP) | BPM | Key | Time | Instrument | Mood |
|---|------|------------|-----|-----|------|------------|------|
| 37 | new_beginning | 新しい始まり | 100 | C | 4/4 | Piano | Hopeful |
| 38 | light_shining_future | 光射す未来 | 110 | G | 4/4 | Piano | Hopeful |
| 39 | flower_of_hope | 希望の花 | 90 | F | 4/4 | Piano | Hopeful |

### 11. Warmth / Healing (5 pieces)

| # | Name | Title (JP) | BPM | Key | Time | Instrument | Mood |
|---|------|------------|-----|-----|------|------------|------|
| 40 | sunbeam_cat | 陽だまりの猫 | 85 | C | 4/4 | Piano | Warm |
| 41 | tea_time | お茶の時間 | 80 | G | 4/4 | Piano | Warm |
| 42 | family_dinner_table | 家族の食卓 | 90 | C | 4/4 | Piano | Warm |
| 43 | friends_smile | 友達との笑顔 | 100 | G | 4/4 | Piano | Cheerful |
| 44 | warm_memories | 温もりの記憶 | 75 | D | 4/4 | Piano | Warm |

---

## Excluded Pieces

### Batch 1 — Medieval modal character (5 pieces)

Removed due to medieval/modal melodic patterns dominating the piece:

| File | Instrument | Mood | Reason |
|------|------------|------|--------|
| after_school_lingering | Violin | Gentle | Solo violin + stepwise pattern = medieval ballad |
| creeping_shadow | Cello | Tense | Solo cello + chromatic motion = modal plainsong character |
| door_to_tomorrow | Flute | Hopeful | Solo flute + scalar melody = medieval pipe |
| beyond_rainbow | Piano | Hopeful | Scalar ascending pattern without harmonic grounding |
| final_blow | Piano | Intense | Simple leaps produced archaic feel |

### Batch 2 — Medieval/classical solo instrument character (6 pieces)

Removed because solo instruments with scalar/modal melody templates produced a distinctly medieval or classical sound, unsuitable for galgame BGM:

| File | Instrument | Mood | Reason |
|------|------------|------|--------|
| rooftop_view | Flute | Gentle | Flute + stepwise = medieval shepherd's pipe |
| lost_memories | Cello | Sad | Cello + scalar descending = medieval lament |
| winter_loneliness | Violin | Sad | Violin + scalar descending = medieval ballad |
| magical_forest | Flute | Mysterious | Flute + chromatic = modal folk melody |
| truth_door | Cello | Mysterious | Cello + chromatic = Phrygian/modal chant |
| sunset_way_home | Violin | Nostalgic | Violin + scalar descending = medieval troubadour |

### Pieces Retained (Rationale)

- **Piano pieces**: Retained because piano provides left-hand accompaniment (chordal/harmonic context), which grounds the melody in modern harmony rather than modal/medieval tonality.
- **Music Box, Celesta pieces**: Retained due to modern/cute timbre that is distinctly non-medieval.
- **Trumpet piece**: Retained because the intense/leaping template sounds modern, not medieval.
- **Violin (romantic)**: `first_love_melody` retained because the romantic template uses arpeggiated patterns, not scalar, and sounds more like a modern romantic violin line.

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
| Average File Size | ~5.6 MB (WAV) |

### Musical Parameters

| Parameter | Range |
|-----------|-------|
| Tempo | 60 - 140 BPM |
| Key Signatures | C, G, D, F (major) / a, e (minor) |
| Time Signatures | 4/4, 3/4 |
| Instruments | Piano, Music Box, Violin, Celesta, Trumpet |
| Dynamics | 1 - 127 (MIDI velocity) |

### Do Muse JSON Format

```json
{
  "title": "Piece Title",
  "composer": "Do Muse AI",
  "metadata": {
    "tempo_bpm": 120,
    "time_signature": "4/4",
    "key_signature": "C"
  },
  "tracks": [
    {
      "instrument": "Acoustic Grand Piano",
      "notes": [
        {"pitch": 60, "duration": "quarter", "velocity": 80},
        ...
      ]
    }
  ]
}
```

- **tracks**: Array of instrument tracks (supports multi-track)
- **notes.pitch**: MIDI note number (0-127, 60 = Middle C; -1 = rest)
- **notes.duration**: Note length (whole, half, quarter, eighth, 16th)
- **notes.velocity**: Note volume (1-127)

---

## Usage Notes

### For AI Training

The 44 WAV files are suitable as training data for:
- **Style transfer**: Galgame BGM genre classification
- **Fine-tuning**: Music generation LoRA for visual novel soundtracks
- **Mood classification**: Emotional tagging of BGM pieces
- **Instrument recognition**: Identifying piano vs. ensemble textures

### Galgame BGM Style Characteristics

The retained 44 pieces exhibit the following galgame BGM style traits:
- **Piano-driven**: Most pieces use piano as the primary instrument with harmonic accompaniment
- **Emotional clarity**: Each piece has a clear mood (romantic, sad, cheerful, peaceful, etc.)
- **Modern harmony**: Chordal accompaniment provides tonal grounding
- **Atmospheric**: Suitable as background music for visual novel scenes
- **Variety**: 11 mood categories cover typical galgame emotional arcs

### Regeneration

```bash
# Step 1: Generate JSON files
python generate_bgm.py

# Step 2: Convert to WAV
python batch_convert.py
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
| 1.0 | 2026-08-20 | 55 | Initial generation |
| 1.1 | 2026-08-20 | 50 | Removed 5 medieval-sounding pieces (Batch 1) |
| 1.2 | 2026-08-20 | 44 | Removed 6 solo-instrument medieval/classical pieces (Batch 2); added `galgame_bgm` category tag |