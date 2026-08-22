# Do Muse JSON Format Specification

## Overview

Do Muse uses **JSON format** as the sole intermediate language between user input, AI generation, and manual editing. The program parses the JSON, builds a music21 score object, and exports it as a `.mxl` (compressed MusicXML) file.

### 两种格式（Two Formats）

> **【强制规定 · V2 Only】AI 生成一律使用 V2（绝对定位）格式。**
> 顶层 `"format": "v2"` 是唯一合法声明；legacy/V1 格式已对 AI 生成禁用。
> 任何缺少 `offset`、或使用 `pitch: -1` 写休止、或未声明 `format: "v2"` 的输出，
> 都会被本地校验器直接拒绝。本文档中的 V1/legacy 章节仅作历史背景参考，
> **禁止模仿 V1 写法**。规则引擎（非 AI）不受此限制。

Do Muse 支持 **V1（legacy）** 与 **V2（绝对定位）** 两种 JSON 格式，通过顶层字段 `format` 切换：

| 维度 | V1 · Legacy 顺序累加格式 | V2 · 绝对定位格式 |
|------|---------------------------|-------------------|
| 顶层声明 | 无（缺省即 V1） | `"format": "v2"` |
| 音符位置 | 隐式：按数组顺序累加得出 | 显式：每个音符写 `offset` |
| 休止表达 | 必须显式写 `pitch: -1` | 空隙自动补休止，无需手写 |
| 时值 | 仅字符串 | 字符串或数字（如 `1.75`） |
| 额外定位参数 | 无 | `pitch_name` / `measure` / `beat` / `end_offset` |
| 适用场景 | 严格顺序进行的音乐 | 需要精确控制每个音位置（AI 生成、手工编辑、任意时值） |

### 本文档的组织方式（How This Document Is Organized）

**绝大部分内容（顶层结构、metadata、tracks、音符表达参数、时值、各种记号等）是两种格式的通用部分**，本文档统一讲解，不再重复。凡涉及格式差异之处，章节内会以「V1」「V2」或「通用」明确标注：

- **通用** — 两种格式写法完全一致；
- **V1** — 仅顺序累加格式适用（或该格式下的特有写法）；
- **V2** — 仅绝对定位格式适用（或该格式下的特有写法）。

完整示例见 §1（V1 版与 V2 版各一份）；V2 专属时序规则见 §39（V2 专属规则）。

---

## 1. Complete Example

### 1.1 V1 (legacy) — 顺序累加，不写位置

以下 JSON 是 **V1** 写法：音符按演奏顺序排列，位置由程序自动累加；休止用 `pitch: -1` 显式写出。通用字段（title / composer / metadata / tracks / note 表达参数）在两种格式中写法一致。

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

### 1.2 V2 — 绝对定位，每个音显式写 offset

同一首曲子的 **V2** 写法：顶层声明 `"format": "v2"`，每个音符加 `offset`（四分音符单位的绝对位置），并可选 `pitch_name` / `measure` / `beat` / `end_offset`。原 V1 中的显式休止（`pitch: -1`）在 V2 中改为**直接留空**——3.5→4.0 的空隙由导出器自动补休止。

```json
{
  "format": "v2",
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
        { "pitch": 67, "duration": "quarter", "velocity": 85, "text": "Andante", "offset": 0.0, "pitch_name": "G4", "measure": 1, "beat": 1.0, "end_offset": 1.0 },
        { "pitch": 71, "duration": "quarter", "velocity": 85, "offset": 1.0, "pitch_name": "B4", "measure": 1, "beat": 2.0, "end_offset": 2.0 },
        { "pitch": 74, "duration": "quarter", "velocity": 85, "tempo_change": 120, "offset": 2.0, "pitch_name": "D5", "measure": 1, "beat": 3.0, "end_offset": 3.0 },
        { "pitch": 79, "duration": "half", "velocity": 90, "fermata": true, "offset": 3.0, "pitch_name": "G5", "measure": 1, "beat": 4.0, "end_offset": 5.0 },
        { "pitch": 72, "duration": "eighth.", "velocity": 80, "pedal": "start", "offset": 5.5, "pitch_name": "C5", "measure": 2, "beat": 2.5, "end_offset": 6.25 },
        { "pitch": 74, "duration": "half", "velocity": 80, "pedal": "stop", "offset": 6.25, "pitch_name": "D5", "measure": 2, "beat": 3.25, "end_offset": 8.25 }
      ]
    },
    {
      "instrument": "Violin",
      "notes": [
        { "pitch": 48, "duration": "half", "velocity": 70, "offset": 0.0, "pitch_name": "C3", "measure": 1, "beat": 1.0, "end_offset": 2.0 },
        { "pitch": 52, "duration": "half", "velocity": 70, "offset": 2.0, "pitch_name": "E3", "measure": 1, "beat": 3.0, "end_offset": 4.0 },
        { "pitch": 55, "duration": "half", "velocity": 70, "offset": 4.0, "pitch_name": "G3", "measure": 2, "beat": 1.0, "end_offset": 6.0 }
      ]
    }
  ]
}
```

> V1 第 5 个音符是显式休止（offset 5.0→5.5，八分休止），V2 版本中该空隙直接不写音符（5.0→5.5），由导出器自动补休止。两种写法的乐谱结果完全一致（见 §7 位置规则）。

---

## 2. Top-Level Structure

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `format` | string | No | `"legacy"` | **V2 专用**。格式选择器：`"legacy"`（缺省）或 `"v2"`。写 `"v2"` 即启用绝对定位；未知值判为无效文档 |
| `title` | string | No | `"Untitled"` | **通用**。Piece title (used as the export filename) |
| `composer` | string | No | `"Unknown"` | **通用**。Composer name |
| `metadata` | object | **Yes** | — | **通用**。Score metadata: tempo, time signature, etc. |
| `tracks` | array | **Yes** | — | **通用**。List of tracks, each representing an instrument |
| `macros` | object | No | (none) | **通用**。Named reusable note blocks, referenced via `{"ref": "name"}` (see Section 37) |

---

## 3. metadata

> **通用** — V1 与 V2 的 `metadata` 对象完全一致。

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

> **通用** — 轨道对象结构在 V1 与 V2 中完全一致（V2 中每个声部/轨道内部使用各自的 `offset` 时间线）。

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

`notes` is an array of note objects within each track. Notes **must be strictly ordered** by their performance time (V1); in V2 the `offset` field defines the time.

> **通用** — 除行内标注「V2 专用」的字段外，下表所有音符参数在 V1 与 V2 中写法完全一致。表末 5 行为 V2 专属定位参数。

### Note Object

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `pitch` | integer or null | **Yes** | — | MIDI pitch number, range **21-108**; `-1` or `null` indicates a rest. **V2**: 可由 `pitch_name` 反推；同时出现须一致 |
| `duration` | string (V1) / string or number (V2) | **Yes** | — | Duration (see duration specification below). **V2**: 数字表示四分音符单位（如 `1.75`），不能与 `tuplet` 同用 |
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
| `offset` | number (≥ 0) | **V2 必填** | — | **V2 专用**。绝对位置，从整曲起点算起，单位为四分音符（如 `0.0`、`1.5`、`8.25`）。这是 V2 中每个音符都必须携带的位置参数 |
| `pitch_name` | string | No | None | **V2 专用**。人读音名，如 `"C4"`、`"F#3"`、`"Bb5"`。`pitch` 缺失时由它反推；两者同时出现必须一致 |
| `measure` | number (≥ 1) | No | None | **V2 专用**。小节号（人类可读位置），从 1 开始，按拍号时间线与 `offset` 交叉校验 |
| `beat` | number (≥ 0) | No | None | **V2 专用**。小节内第几拍，从 1 开始，按拍号分母单位计数（见 §39.4） |
| `end_offset` | number | No | None | **V2 专用**。结束位置，应为 `offset + 实际发声时长`（tuplet 按缩放后时长），交叉校验 |

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

### 6.3 V2 数值时值（Numeric Duration，V2 专用）

V1 的 `duration` 只能是字符串。**V2** 额外允许**数字**，直接以四分音符为单位：

```json
{ "pitch": 72, "offset": 0.0, "duration": "quarter" }   // 字符串（通用写法）
{ "pitch": 72, "offset": 1.0, "duration": 1.5 }          // 数字：1.5 个四分音符，无字符串等价物
{ "pitch": 72, "offset": 2.0, "duration": 1.75 }         // 数字：任意时值，仅 V2 可表达
```

> 数字 `duration` 不得与 `tuplet` 同时使用（连音仅作用于字符串时值）。字符串时值表（§6.1/§6.2）两种格式通用。

---

## 7. Note Positioning — V1 vs V2（位置确定规则）

音符在整首曲子中的位置，两种格式用两种机制确定：

- **V1（legacy）**：**隐式顺序累加**。位置由程序按数组顺序累加时值得出，音符不需要也不允许写位置。
- **V2（绝对定位）**：**显式 `offset`**。每个音符必须写绝对位置，可精确落在时间线任意处。

两种机制的规则分别见下。

### 7.1 V1 — 顺序累加（Offset Accumulation）

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

### 7.2 V2 — 绝对定位（Absolute `offset`）

V2 中每个音符必须携带 `offset`（≥ 0 的数字，四分音符单位），位置完全由它决定，与数组顺序无关（校验器会按 `offset` 排序处理）：

```json
"notes": [
  { "pitch": 60, "duration": "quarter", "offset": 0.0,  "end_offset": 1.0 },   // 位置 0.0，占 1.0 拍
  { "pitch": 62, "duration": "quarter", "offset": 1.0,  "end_offset": 2.0 },   // 位置 1.0，占 1.0 拍
  { "pitch": 64, "duration": "half",    "offset": 2.0,  "end_offset": 4.0 },   // 位置 2.0，占 2.0 拍
  { "pitch": 67, "duration": "eighth.", "offset": 5.0,  "end_offset": 5.75 }   // 位置 5.0，占 0.75 拍
]
```

**关键差异（V2）**：

- 4.0→5.0 的**空隙无需写休止**，导出器自动补 1 拍休止（V1 必须写 `pitch: -1`）；
- 相同 `offset` 的多个有音高音符自动合并为**和弦**（须同 duration）；
- 一个音符严格落在另一个音符发声区间内部（**部分重叠**）判为错误——要么共用 offset 成和弦，要么放入不同声部；
- 三连音等**连音按缩放后时长**参与位置与重叠计算（详见 §39.3）；
- 还可选填 `pitch_name` / `measure` / `beat` / `end_offset` 供人类阅读与交叉校验（见 §5 表末与 §39）。

### 7.3 对比示例：同一段"不规则"音乐

顺序进行的音乐容易让人觉得 V1/V2 没区别；真正体现差异的是音符**不在整拍连续出现**的音乐——例如伴奏声部从第 3 拍才进入（4/4 拍）：

**V1** — 位置隐含，靠休止符占位推导：

```json
"notes": [
  { "pitch": -1, "duration": "half", "velocity": 0 },
  { "pitch": 64, "duration": "quarter", "velocity": 80 },
  { "pitch": 67, "duration": "quarter", "velocity": 80 },
  { "pitch": -1, "duration": "quarter", "velocity": 0 },
  { "pitch": 74, "duration": "quarter.", "velocity": 80 }
]
```

> E4 在第几拍？没有任何字段能直接回答——必须心算累加（休止 2 拍 + E4 = 第 3 拍）。这里的休止符是**占位符**而非音乐意图；少写一个休止位置就悄悄错位，且不报错。

**V2** — 位置显式，每个音自己声明 `offset`：

```json
"notes": [
  { "pitch": 64, "duration": "quarter", "offset": 2.0, "measure": 1, "beat": 3.0 },
  { "pitch": 67, "duration": "quarter", "offset": 3.0, "measure": 1, "beat": 4.0 },
  { "pitch": 74, "duration": "quarter.", "offset": 5.0, "measure": 2, "beat": 2.0 }
]
```

> 每个音自带精确时间，一眼可见；0→2、4→5 的空隙自动补休止。严谨性体现在校验：`offset` 缺失、与 `measure`/`beat` 不符、`end_offset` 不符、部分重叠——全部拦截报错。

> **严谨性对比**：V1 的位置是"推导"出来的隐含结果（写错不报错）；V2 的位置是"声明"出来的硬性事实（少写、写错、写矛盾都立即被校验器拦下）——这就是"每个音都要自己定义准确时间"的含义。

---

## 8. Rests

休止有两种表达方式，取决于格式：

- **V1（通用写法）**：显式写出 `pitch: -1` 或 `null`，时值由 `duration` 指定。
- **V2**：**不需要写休止**——音符之间的空隙由导出器自动补休止；若确实需要特定位置的休止（如乐曲开头），仍可写 `pitch: -1`（带 `offset`）。

| pitch Value | Meaning |
|-------------|---------|
| `-1` or `null` | Rest, duration specified by the `duration` field |

Example (quarter rest, V1 / 或 V2 在 offset 4.0 处)：

```json
{ "pitch": -1, "duration": "quarter", "velocity": 0 }
```

```json
{ "pitch": -1, "duration": "quarter", "velocity": 0, "offset": 4.0 }
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
- [ ] **V1**: `notes` are in performance order
- [ ] **V2**: every note has `offset` (number ≥ 0); numeric `duration` is allowed but not combined with `tuplet`
- [ ] **V2**: same-offset notes share the same duration; rests do not share an offset with other notes
- [ ] **V2**: no partial overlaps (note starting inside another note's span)
- [ ] **V2**: `pitch_name` agrees with `pitch` when both are present
- [ ] **V2**: `measure` / `beat` / `end_offset`, if provided, match the computed values (tolerances: beat ±0.02, end_offset ±0.01)
- [ ] **V2**: fractional triplet offsets keep full precision (e.g. `0.3333333333`, not `0.3333`)
- [ ] **V2**: 若所有音符 offset 完全连续且无空隙/和弦/数值时值/定位附加参数，判为**错误**（V2 必须体现绝对定位特点，纯顺序音乐请用 V1）
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
| V2: missing offset | `"pitch": 60, "duration": "quarter"` (format=v2) | `"pitch": 60, "duration": "quarter", "offset": 0.0` |
| V2: numeric duration + tuplet | `"duration": 1.5, "tuplet": 3` | Use string duration with tuplet, or numeric without tuplet |
| V2: pitch_name conflicts | `"pitch": 60, "pitch_name": "E4"` | `"pitch_name": "C4"` (MIDI 60) |
| V2: partial overlap | note starts inside another note's span | Same `offset` (chord) or different voice |
| V2: rounded triplet offset | `"offset": 6.3333` | `"offset": 6.3333333333` (full precision) |
| V2: invalid format value | `"format": "v3"` | `"format": "v2"` or omit the field |
| V2: purely sequential | `"format": "v2"` + offsets 0,1,2,3… (no gaps/chords/numeric durations/extras) | 改用 V1 (legacy)，或在音符上体现 V2 特点（空隙/和弦/数值时值/pitch_name 等） |

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

---

## 38. Multi-Voice Support (多声部支持)

> **通用** — `voices` 结构在 V1 与 V2 中一致。V2 中每个声部使用自己独立的 `offset` 时间线，因此不同声部的音符**允许部分重叠**（这正是 V2 中处理同时发声而不合并和弦的途径）。

### 38.1 Overview

A single track can carry more than one voice — for example the right/left
hands of a piano, or the four voices of a SATB choir. Add a `voices` array to
a track; each element becomes an independent staff (music21 `Part`) rendered
in the output.

```json
{
  "title": "Example",
  "composer": "Do Muse",
  "metadata": {
    "tempo_bpm": 120,
    "time_signature": "4/4",
    "key_signature": "C"
  },
  "tracks": [
    {
      "instrument": "Acoustic Grand Piano",
      "voices": [
        {
          "name": "右手",
          "notes": [
            { "pitch": 72, "duration": "quarter" },
            { "pitch": 74, "duration": "quarter" }
          ]
        },
        {
          "name": "左手",
          "notes": [
            { "pitch": 48, "duration": "half" },
            { "pitch": 52, "duration": "quarter" }
          ]
        }
      ]
    }
  ]
}
```

### 38.2 Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `voices` | array | No | Voice array. When present, the track's `notes` field is **ignored**. |
| `voices[].name` | string | **Yes** | Voice name (e.g. `"右手"`, `"Soprano"`). Max 50 characters. |
| `voices[].notes` | array | **Yes** | Note array for this voice, same format as a regular track's `notes`. |
| `voices[].instrument_transpose` | string | No | Per-voice transposition interval in semitones (`"-12"`..`"12"`). |
| `voices[].barline` | string | No | Per-voice final barline style (`"single"`, `"double"`, `"final"`, `"dashed"`, `"invisible"`). |

### 38.3 Clef & Staff Layout Rules

Do Muse assigns clefs and groups staves automatically based on the instrument:

- **Piano (Acoustic Grand Piano / Piano) — Grand Staff (大谱表)**
  - 2 voices → right hand = Treble clef, left hand = Bass clef, braced together.
  - 3+ voices → first two follow the same rule; extra voices use Treble clef.
- **Organ / Harp**
  - 2+ voices → grouped into a braced grand-staff group (manuals = Treble, pedal/bass = Bass).
- **Choir (Choir Aahs / Voice Oohs) — Side-by-side staves (并排谱表)**
  - 4 voices (SATB): Soprano & Alto = Treble clef, Tenor & Bass = Bass clef.
  - Other voice counts: each voice uses Treble clef (rendered as separate staves).
- **Other instruments**
  - Each voice is rendered as its own staff; clef follows the program number
    (bass instruments → Bass clef, viola → Alto clef, otherwise Treble clef).

### 38.4 Examples

**Piano four hands (四手联弹)** — one piano track, two voices (Primo / Secondo):

```json
{
  "title": "Piano Duet (Four Hands)",
  "composer": "Do Muse",
  "metadata": { "tempo_bpm": 100, "time_signature": "4/4", "key_signature": "C" },
  "tracks": [
    {
      "instrument": "Acoustic Grand Piano",
      "voices": [
        { "name": "Primo",   "notes": [ { "pitch": 72, "duration": "quarter" }, { "pitch": 84, "duration": "half", "fermata": true } ] },
        { "name": "Secondo", "notes": [ { "chord": [48, 52, 55], "duration": "half" }, { "pitch": 48, "duration": "half", "fermata": true } ] }
      ]
    }
  ]
}
```

**SATB choir (混声四部合唱)** — one choir track, four voices:

```json
{
  "title": "SATB Choir",
  "composer": "Do Muse",
  "metadata": { "tempo_bpm": 90, "time_signature": "4/4", "key_signature": "G" },
  "tracks": [
    {
      "instrument": "Choir Aahs",
      "voices": [
        { "name": "Soprano", "notes": [ { "pitch": 67, "duration": "whole" }, { "pitch": 74, "duration": "whole" } ] },
        { "name": "Alto",    "notes": [ { "pitch": 62, "duration": "whole" }, { "pitch": 66, "duration": "whole" } ] },
        { "name": "Tenor",   "notes": [ { "pitch": 59, "duration": "whole" }, { "pitch": 62, "duration": "whole" } ] },
        { "name": "Bass",    "notes": [ { "pitch": 43, "duration": "whole" }, { "pitch": 43, "duration": "whole" } ] }
      ]
    }
  ]
}
```

### 38.5 Backward Compatibility

- If a track has **no** `voices` field, it is treated as a single-voice track using its `notes` array (existing behaviour is unchanged).
- If a track **has** a `voices` field, its `notes` field is ignored.

### 38.6 Combining with Macros

Voices can reference macros just like a regular track's `notes`:

```json
{
  "macros": { "bass": [ { "pitch": 48, "duration": "quarter" }, { "pitch": 52, "duration": "quarter" } ] },
  "tracks": [
    {
      "instrument": "Acoustic Grand Piano",
      "voices": [
        { "name": "右手", "notes": [ { "ref": "bass" }, { "pitch": 72, "duration": "half" } ] },
        { "name": "左手", "notes": [ { "ref": "bass" } ] }
      ]
    }
  ]
}
```

---

## 39. V2 专属规则（V2-Specific Rules）

> **本节只讲解 V2 专属的内容。** V2 与 V1 的通用部分——顶层结构、metadata、tracks、音符表达参数、时值表、各种记号（Articulation…Expression）、多声部、宏系统——见本文档对应章节，两种格式写法一致，不再重复。
>
> 与通用章节的对应关系：
> - 顶层 `format` 字段 → §2 顶层结构表；
> - V2 新增音符参数（`offset` / `pitch_name` / `measure` / `beat` / `end_offset` / 数值 `duration`）→ §5 Note 对象表末、§6.3；
> - V2 完整示例 → §1.2。

### 39.1 设计动机（Intent）

V1（legacy）按顺序累加定位，无法表达三类需求：在休止中间/时间线任意位置开始的音符、精确控制每个音的位置（对 AI 生成与手工编辑不友好）、没有字符串等价物的时值（如 `1.75` 拍）。V2 给每个音符一个**显式的绝对位置**（`offset`），从根本上解决这些问题，且与 V1 完全向后兼容。

### 39.2 格式选择（Format Selector）

顶层声明 `"format": "v2"` 即启用（缺省为 `"legacy"`）。未知的 `format` 值判为无效文档，绝不静默降级。字段定义见 §2。

> **强制要求**：声明 `v2` 的文档必须体现 V2 的绝对定位特点——纯顺序 v2（offset 连续且无空隙/和弦/数值时值/定位附加参数）判为无效，见 §39.7。

### 39.3 时序规则（Timing Rules）

1. **空隙自动补休止（Gap → auto rest）** — 两音之间若有空隙，导出器自动插入恰好等长的休止；无需手写休止填充空间。
2. **同 offset 多音 → 和弦（Same-offset → chord）** — 多个有音高音符共享同一 `offset` 时自动合并为一个和弦；它们必须**时值相同**；休止不得与其他音符共享 `offset`。
3. **部分重叠是错误（Partial overlap → error）** — 一个音符严格落在另一个音符发声区间内部即报错；同时发声请用相同 `offset`（和弦），或放入不同声部（§38）。
4. **连音按缩放后时长计算（Tuplet interaction）** — 连音音符的真实时间线长度 = 名义时值 × 缩放系数（`3` → ×⅔，`5/6/7` → ×4/N，`9` → ×⁸⁄₉）。`offset` / `end_offset` 与重叠判定全部使用缩放后的长度，因此三连音八分音符恰好占两个八分音符的时值。

### 39.4 `measure` / `beat` 约定

- 小节（Measure）从 **1** 开始编号；
- 拍数（Beat）在小节内从 **1** 开始，按拍号**分母单位**计数：
  - `4/4` → 每小节 4 个四分音符拍（beat `1.0`、`2.0`、`3.0`、`4.0`）；
  - `6/8` → 每小节 6 个八分音符拍（每个四分音符 = 2 拍；`offset` 1.0 → beat `3.0`）。

校验器根据 `offset` 与拍号时间线（含 `time_signature_change` 变化）重算 `measure`/`beat`，声明值不一致即报错。

### 39.5 精度注意（Precision Note）

连音产生的分数位置是精确的 `1/3`（≈ `0.3333333333`）。**手写这类 `offset` 必须保留全精度小数**——四舍五入到 4 位小数（如 `6.3333`）会使 MusicXML 导出器无法表达该节奏（报 inexpressible durations）。官方转换工具与内置模板始终输出全精度。

### 39.6 配套工具（Conversion & Import）

- **Legacy → V2:** `core/format_converter.convert_legacy_to_v2(json_data)` 遍历乐谱，累加 `offset`（含连音缩放），并为每个音符填充 `end_offset` / `pitch_name` / `measure` / `beat`；支持多声部。
- **CLI:**
  - `python main.py --to-v2 -i score.json -e score_v2.json` — 把 V1 JSON 转换为 V2 并写出。
  - `python main.py -i piece.mxl --json-format v2 -e piece.json` — 直接导入 MusicXML/MIDI 为 V2（每个音符带绝对位置）。
  - `--json-format {legacy,v2}` 控制导入产出的 JSON 格式；`--to-v2` 在校验/导出前把输入转换为 V2。
- **Importer:** `core/format_importer.import_file(path, output_format="v2")` 在 `output_format="v2"` 时返回 V2 文档。
- **GUI:** *Templates* 菜单含 **"V2 绝对定位示例"**（`v2_demo`），可一键体验全部 V2 特性。

### 39.7 纯顺序 V2 是错误（V2 Must Use Absolute Positioning）

**声明 `"format": "v2"` 就必须体现 V2 的定位特点。** 一段 `offset` 依次为 0,1,2,3…、无空隙、无和弦、无数值时值、也未使用 `pitch_name`/`measure`/`beat`/`end_offset` 的 V2 文档（如手写的纯顺序旋律）**校验失败**——它完全没有用到 V2 的绝对定位能力，与 V1 写法等价，应改用 V1（或补上 V2 定位特性）。

校验错误示例：

```
Track 1: format=v2 必须体现 V2 的绝对定位特点——该轨道音符 offset 完全连续、无空隙/和弦/
数值时值，且未使用 pitch_name/measure/beat/end_offset，纯顺序音乐请改用 V1 (legacy)
```

判定规则（每条轨道/声部独立判定，**全部满足**才报错）：

1. 每个音符的 `offset` 恰好等于前一个音符的结束位置（无空隙、无重叠）；
2. 没有任何两个音符共享同一 `offset`（无和弦合并）；
3. 所有 `duration` 都是字符串（无数值时值）；
4. 没有任何音符使用 `pitch_name` / `measure` / `beat` / `end_offset`。

只要某条轨道用到了上述任一能力（哪怕一处空隙或一个 `pitch_name`），该轨道即合法。**官方工具不受影响**：`convert_legacy_to_v2` 与导入器会自动为每个音符填充 `pitch_name`/`measure`/`beat`/`end_offset`，转换产物天然满足 V2 要求。



