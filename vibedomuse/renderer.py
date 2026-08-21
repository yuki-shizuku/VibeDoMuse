# -*- coding: utf-8 -*-
"""
VibeDoMuse · renderer.py
Rendering layer: Do-muse JSON -> MIDI (DoMuse.exe) -> WAV (fluidsynth + SoundFont).

Cache-first strategy:
  - render() / render_existing_json() write artifacts to a SYSTEM TEMP cache
    directory first (merely the on-disk medium for the in-memory cache; nothing
    enters the project tree);
  - only after the user clicks "confirm save" in the GUI are the in-memory bytes
    written to vibedomuse/generated/{json,midi,wav} (persisted).
"""
import json
import os
import shutil
import subprocess
import tempfile

from ._paths import resource_path, RUNTIME_DIR

DOMUSE_EXE = resource_path(os.path.join("bin", "DoMuse.exe"))
FLUIDSYNTH_EXE = resource_path(
    os.path.join("fluidsynth", "fluidsynth-v2.5.7-win10-x64-cpp11", "bin", "fluidsynth.exe")
)
SOUNDFONT = resource_path("32MbGMStereo.sf2")

# Persistent output dirs (written only after "confirm save"); live in the
# portable runtime folder so the deployment stays self-contained.
GEN_DIR = os.path.join(RUNTIME_DIR, "generated")
JSON_DIR = os.path.join(GEN_DIR, "json")
MIDI_DIR = os.path.join(GEN_DIR, "midi")
WAV_DIR = os.path.join(GEN_DIR, "wav")

# Temp cache dirs (system temp; used during generation, never inside the project)
CACHE_ROOT = os.path.join(tempfile.gettempdir(), "vibedomuse_cache")
CACHE_JSON_DIR = os.path.join(CACHE_ROOT, "json")
CACHE_MIDI_DIR = os.path.join(CACHE_ROOT, "midi")
CACHE_WAV_DIR = os.path.join(CACHE_ROOT, "wav")


def ensure_dirs():
    """Ensure the persistent output dirs exist (called on confirm-save)."""
    for d in (JSON_DIR, MIDI_DIR, WAV_DIR):
        os.makedirs(d, exist_ok=True)


def _cache_dirs():
    for d in (CACHE_JSON_DIR, CACHE_MIDI_DIR, CACHE_WAV_DIR):
        os.makedirs(d, exist_ok=True)


def write_json(score, name):
    _cache_dirs()
    path = os.path.join(CACHE_JSON_DIR, name + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(score, f, ensure_ascii=False, indent=2)
    return path


def json_to_midi(json_path, midi_path=None):
    if midi_path is None:
        midi_path = os.path.join(CACHE_MIDI_DIR, os.path.splitext(os.path.basename(json_path))[0] + ".mid")
    if not os.path.exists(DOMUSE_EXE):
        raise RuntimeError("DoMuse.exe not found: " + DOMUSE_EXE)
    r = subprocess.run(
        [DOMUSE_EXE, "-i", json_path, "-e", midi_path, "-f", "midi"],
        capture_output=True, text=True, timeout=120,
    )
    if r.returncode != 0:
        raise RuntimeError("DoMuse.exe failed: " + (r.stderr or r.stdout or "unknown error"))
    if not os.path.exists(midi_path) or os.path.getsize(midi_path) == 0:
        raise RuntimeError("MIDI not generated or empty")
    return midi_path


def trim_trailing_silence(wav_path, keep_sec=0.4, threshold=0.004, chunk_sec=0.05):
    """Trim trailing silence from a 16-bit PCM WAV file (in place).

    music21 pads the last partial measure with rests, so rendered WAVs usually
    end with a few seconds of silence. This scans from the end for the last
    audible block and truncates the file, keeping a short natural tail
    (keep_sec) so the piece does not cut off abruptly.
    """
    import struct
    import wave
    try:
        with wave.open(wav_path, "rb") as w:
            params = w.getparams()
            if params.sampwidth != 2:
                return wav_path  # only 16-bit PCM handled
            nch, fr, nframes = params.nchannels, params.framerate, params.nframes
            if nframes <= 0:
                return wav_path
            chunk_frames = max(1, int(fr * chunk_sec))
            pos = nframes
            end_frame = nframes
            while pos > 0:
                start = max(0, pos - chunk_frames)
                w.setpos(start)
                frames = w.readframes(pos - start)
                peak = 0
                for i in range(0, len(frames) - 1, 2):
                    s = struct.unpack_from("<h", frames, i)[0]
                    a = abs(s) / 32768.0
                    if a > peak:
                        peak = a
                if peak > threshold:
                    end_frame = min(nframes, pos + int(fr * keep_sec))
                    break
                pos = start
            if end_frame >= nframes:
                return wav_path  # already no trailing silence
            w.setpos(0)
            data = w.readframes(end_frame)
        tmp = wav_path + ".trim.tmp"
        with wave.open(tmp, "wb") as w:
            w.setparams(params)
            w.writeframes(data)
        os.replace(tmp, wav_path)
    except Exception:
        pass
    return wav_path


def midi_to_wav(midi_path, wav_path=None):
    if wav_path is None:
        wav_path = os.path.join(CACHE_WAV_DIR, os.path.splitext(os.path.basename(midi_path))[0] + ".wav")
    # Pre-flight checks: ensure fluidsynth and soundfont exist
    if not os.path.exists(FLUIDSYNTH_EXE):
        return None
    if not os.path.exists(SOUNDFONT):
        return None
    # Retry once on failure
    for attempt in range(2):
        try:
            r = subprocess.run(
                [FLUIDSYNTH_EXE, "-F", wav_path, SOUNDFONT, midi_path],
                capture_output=True, text=True, timeout=180,
            )
        except subprocess.TimeoutExpired:
            continue
        except Exception:
            continue
        if r.returncode != 0:
            continue
        if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
            trim_trailing_silence(wav_path)
            return wav_path
    return None


def _content_hash(score):
    """Content-addressed key for a score dict (dedupe identical renders)."""
    import hashlib
    raw = json.dumps(score, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()[:16]


def render(score, name):
    """Generate into the cache dirs (not into project generated/ until confirmed).

    Cache-first: identical score content reuses previously rendered MIDI/WAV.

    Returns cache artifact info (absolute paths).
    """
    _cache_dirs()
    key = _content_hash(score)
    json_path = os.path.join(CACHE_JSON_DIR, key + ".json")
    midi_path = os.path.join(CACHE_MIDI_DIR, key + ".mid")
    wav_path = os.path.join(CACHE_WAV_DIR, key + ".wav")
    cached = (os.path.exists(json_path) and os.path.getsize(json_path) > 0
              and os.path.exists(midi_path) and os.path.getsize(midi_path) > 0
              and os.path.exists(wav_path) and os.path.getsize(wav_path) > 0)
    if cached:
        return {
            "json_path": json_path,
            "midi_path": midi_path,
            "wav_path": wav_path,
            "wav_file": name + ".wav",
            "midi_file": name + ".mid",
            "json_file": name + ".json",
            "cached": True,
        }
    json_path = write_json(score, key)
    midi_path = json_to_midi(json_path)
    wav_path = midi_to_wav(midi_path)
    return {
        "json_path": json_path,
        "midi_path": midi_path,
        "wav_path": wav_path,
        "wav_file": (name + ".wav") if wav_path else None,
        "midi_file": name + ".mid",
        "json_file": name + ".json",
        "cached": False,
    }


def render_existing_json(json_path, name=None):
    """Render an existing JSON as the base, into the cache dirs."""
    _cache_dirs()
    if name is None:
        name = os.path.splitext(os.path.basename(json_path))[0]
    midi_path = json_to_midi(json_path)
    wav_path = midi_to_wav(midi_path)
    return {
        "json_path": json_path,
        "midi_path": midi_path,
        "wav_path": wav_path,
        "wav_file": os.path.basename(wav_path) if wav_path else None,
        "midi_file": os.path.basename(midi_path),
        "json_file": os.path.basename(json_path),
    }


def finalize(artifacts, name=None):
    """Confirm save: copy cache artifacts into the project generated/ dir.

    Returns the persisted artifact info.
    """
    ensure_dirs()
    if name is None:
        name = os.path.splitext(artifacts.get("json_file", "piece"))[0]
    src_j = artifacts.get("json_path")
    src_m = artifacts.get("midi_path")
    src_w = artifacts.get("wav_path")
    dst_j = os.path.join(JSON_DIR, name + ".json")
    dst_m = os.path.join(MIDI_DIR, name + ".mid")
    dst_w = os.path.join(WAV_DIR, name + ".wav")
    if src_j and os.path.exists(src_j):
        with open(src_j, "rb") as f:
            data = f.read()
        with open(dst_j, "wb") as f:
            f.write(data)
    if src_m and os.path.exists(src_m):
        with open(src_m, "rb") as f:
            data = f.read()
        with open(dst_m, "wb") as f:
            f.write(data)
    if src_w and os.path.exists(src_w):
        with open(src_w, "rb") as f:
            data = f.read()
        with open(dst_w, "wb") as f:
            f.write(data)
    return {
        "json_path": dst_j,
        "midi_path": dst_m,
        "wav_path": dst_w if (src_w and os.path.exists(src_w)) else None,
        "wav_file": os.path.basename(dst_w) if (src_w and os.path.exists(src_w)) else None,
        "midi_file": os.path.basename(dst_m),
        "json_file": os.path.basename(dst_j),
    }


# ----------------------------------------------------------------------------
# Multi-format export (user chooses the destination path and format)
# ----------------------------------------------------------------------------
def _domuse_export(json_path, out_path, fmt):
    """Export via DoMuse.exe for music21-native formats (mxl/xml/ly/midi)."""
    if not os.path.exists(DOMUSE_EXE):
        raise RuntimeError("DoMuse.exe not found: " + DOMUSE_EXE)
    r = subprocess.run(
        [DOMUSE_EXE, "-i", json_path, "-e", out_path, "-f", fmt],
        capture_output=True, text=True, timeout=120,
    )
    if r.returncode != 0 or not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
        raise RuntimeError(f"DoMuse export failed ({fmt}): " + (r.stderr or r.stdout or "unknown error"))
    return out_path


def _ffmpeg_from_wav(wav_path, out_path, fmt):
    """Re-encode the cached WAV with ffmpeg (mp3/flac/ogg)."""
    ff = shutil.which("ffmpeg")
    if not ff:
        raise RuntimeError("ffmpeg not found, cannot export " + fmt)
    codec = {"mp3": "libmp3lame", "flac": "flac", "ogg": "libvorbis"}.get(fmt)
    cmd = [ff, "-y", "-i", wav_path]
    if codec:
        cmd += ["-codec:a", codec]
    cmd += [out_path]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if r.returncode != 0 or not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
        raise RuntimeError(f"ffmpeg export failed ({fmt}): " + (r.stderr or "")[:200])
    return out_path


def export_artifacts(score, artifacts, out_path, fmt):
    """Export the generated piece to out_path in the chosen format.

    fmt in {json, mxl, xml, ly, midi, wav, mp3, flac, ogg}.
    artifacts are the cached render outputs (json_path / wav_path).
    """
    fmt = fmt.lower().lstrip(".")
    if fmt == "json":
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(score, f, ensure_ascii=False, indent=2)
        return out_path
    if fmt == "wav":
        src = artifacts.get("wav_path")
        if src and os.path.exists(src):
            shutil.copyfile(src, out_path)
            return out_path
        raise RuntimeError("WAV not available (fluidsynth unavailable or render failed)")
    if fmt in ("mxl", "xml", "ly", "midi"):
        jp = artifacts.get("json_path")
        if not jp or not os.path.exists(jp):
            raise RuntimeError("JSON cache not available for " + fmt)
        return _domuse_export(jp, out_path, fmt)
    if fmt in ("mp3", "flac", "ogg"):
        src = artifacts.get("wav_path")
        if not src or not os.path.exists(src):
            raise RuntimeError("WAV not available; cannot export " + fmt)
        return _ffmpeg_from_wav(src, out_path, fmt)
    raise ValueError("unsupported format: " + fmt)
