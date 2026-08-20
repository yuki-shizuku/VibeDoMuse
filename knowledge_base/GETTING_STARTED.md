# Getting Started

> **Last Updated**: 2026-08-20

---

## Prerequisites

- **Python 3.10+** (for running generation scripts)
- **Windows OS** (DoMuse.exe is a Windows executable)
- **~2 GB free disk space** (for WAV file storage)

---

## Project Setup

The project is already fully configured. No additional setup is required.

### Directory Structure

```
d:\Project\Vibe_Do_Muse/
├── bgm/                    # Batch 1: BGM (44 JSON files)
├── accompaniment/          # Batch 2: Accompaniment (50 JSON + 50 WAV)
├── other/                  # Batch 3: v3 Multi-key (50 JSON + 50 WAV)
├── fluidsynth/             # MIDI→WAV rendering engine
├── knowledge_base/         # Documentation and references
├── DoMuse.exe              # JSON→MIDI converter
├── 32MbGMStereo.sf2        # SoundFont instrument bank
└── JSON_Format_Specification.md  # Format specification
```

---

## Viewing the Data

### JSON Source Files

JSON files contain the musical score definition. You can view them with any text editor:

```bash
# Example: view a BGM piece
cat bgm/json/morning_awakening.json

# Example: view an accompaniment piece
cat accompaniment/json/gentle_pop_standard.json
```

### WAV Audio Files

WAV files are standard audio files playable in any media player or DAW:

```bash
# List all accompaniment WAV files
dir accompaniment\wav

# List all v3 WAV files
dir other\wav
```

---

## Regenerating Music

### Batch 1: BGM (JSON only)

```bash
cd bgm
python generate_bgm.py
```

This regenerates all 44 JSON files in `bgm/json/`.

### Batch 2: Accompaniment (JSON + WAV)

```bash
cd accompaniment
python generate_accompaniment.py
python batch_convert_accompaniment.py
```

Step 1 generates 50 JSON files in `accompaniment/json/`.
Step 2 converts them to WAV in `accompaniment/wav/`.

### Batch 3: v3 Multi-key (JSON + WAV)

```bash
cd other
python generate_galgame_v3.py
python batch_convert_v3.py
```

Step 1 generates 50 JSON files in `other/json/`.
Step 2 converts them to WAV in `other/wav/`.

---

## Understanding the Output

### JSON File Structure

Each JSON file follows the Do Muse format:

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
    { "instrument": "Acoustic Grand Piano", "notes": [...] }
  ]
}
```

### WAV File Specifications

| Parameter | Batch 2 | Batch 3 |
|-----------|---------|---------|
| Format | WAV (PCM) | WAV (PCM) |
| Sample Rate | 44100 Hz | 44100 Hz |
| Bit Depth | 16-bit | 16-bit |
| Channels | Stereo | Stereo |
| Duration | ~30s | ~30s |
| Size | 5.5-16 MB | 24-28 MB |
| Tracks | 2 (piano duet) | 3 (piano + strings) |

---

## Using the Knowledge Base

The knowledge base is organized for easy reference:

```
knowledge_base/
├── INDEX.md                        # Main entry point (start here)
├── database/
│   ├── 01_bgm_catalog.md           # Batch 1 details
│   ├── 02_accompaniment_catalog.md # Batch 2 details
│   └── 03_v3_catalog.md            # Batch 3 details
├── technical/
│   ├── 01_chord_progressions.md    # All 30 progressions
│   ├── 02_accompaniment_patterns.md # All 15 patterns
│   └── 03_generation_pipeline.md   # JSON→MIDI→WAV pipeline
├── specifications/
│   └── JSON_Format_Specification.md # Full format specification
└── references/                     # Reserved for future use
```

### Quick Navigation

- **Finding a piece**: Open the appropriate batch catalog in `database/`
- **Understanding harmony**: Open `technical/01_chord_progressions.md`
- **Learning patterns**: Open `technical/02_accompaniment_patterns.md`
- **Format reference**: Open `specifications/JSON_Format_Specification.md`

---

## Troubleshooting

### DoMuse.exe fails

- Ensure the file path contains no special characters
- Check that the JSON file is valid (use `python -m json.tool file.json`)
- Run from the project root directory

### fluidsynth fails

- Ensure the SoundFont file exists at `32MbGMStereo.sf2`
- Check that the MIDI file is valid (non-zero size)
- Try running the command manually to see error output

### Script errors

- Use Python 3.10 or later
- Install no additional packages (standard library only)
- Run scripts from their respective directories
- Ensure all paths use the correct OS separator

### WAV file is silent

- Check that the MIDI file contains notes (not just rests)
- Verify the SoundFont is not corrupted
- Try a different MIDI player to test the MIDI file first