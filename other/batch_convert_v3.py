#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch conversion script (v3): convert JSON files in the json/ dir to WAV
"""
import json
import os
import subprocess
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
JSON_DIR = os.path.join(SCRIPT_DIR, "json")
MIDI_DIR = os.path.join(SCRIPT_DIR, "output_midi")
WAV_DIR = os.path.join(SCRIPT_DIR, "wav")
DOMUSE_EXE = os.path.join(PROJECT_ROOT, "bin", "DoMuse.exe")
FLUIDSYNTH_EXE = os.path.join(
    PROJECT_ROOT, "fluidsynth", "fluidsynth-v2.5.7-win10-x64-cpp11", "bin", "fluidsynth.exe"
)
SOUNDFONT = os.path.join(PROJECT_ROOT, "32MbGMStereo.sf2")


def convert_json_to_midi(json_path, midi_path):
    cmd = [DOMUSE_EXE, "-i", json_path, "-e", midi_path, "-f", "midi"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(f"DoMuse.exe conversion failed: {result.stderr or result.stdout}")
    return os.path.exists(midi_path)


def convert_midi_to_wav(midi_path, wav_path):
    cmd = [FLUIDSYNTH_EXE, "-F", wav_path, SOUNDFONT, midi_path]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"fluidsynth 转换失败: {result.stderr or result.stdout}")
    return os.path.exists(wav_path)


def main():
    os.makedirs(MIDI_DIR, exist_ok=True)
    os.makedirs(WAV_DIR, exist_ok=True)

    json_files = sorted([f for f in os.listdir(JSON_DIR) if f.endswith(".json")])
    total = len(json_files)
    print(f"Found {total} v3 JSON files, starting batch conversion...\n", flush=True)

    success = 0
    fail = 0
    t0 = time.time()

    for i, json_name in enumerate(json_files, 1):
        base = os.path.splitext(json_name)[0]
        json_path = os.path.join(JSON_DIR, json_name)
        midi_path = os.path.join(MIDI_DIR, f"{base}.mid")
        wav_path = os.path.join(WAV_DIR, f"{base}.wav")

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            title = data.get("title", base)
        except:
            title = base

        print(f"[{i:02d}/{total}] {title}", flush=True)
        ts = time.time()

        try:
            if not convert_json_to_midi(json_path, midi_path):
                print(f"  x JSON -> MIDI failed", flush=True)
                fail += 1
                continue
            if not convert_midi_to_wav(midi_path, wav_path):
                print(f"  x MIDI -> WAV failed", flush=True)
                fail += 1
                continue
            elapsed = time.time() - ts
            size = os.path.getsize(wav_path) / 1024
            print(f"  ✓ WAV ({size:.0f} KB, {elapsed:.1f}s)", flush=True)
            success += 1
        except Exception as e:
            print(f"  x error: {e}", flush=True)
            fail += 1

    print(f"\n{'='*50}", flush=True)
    print(f"Conversion finished!", flush=True)
    print(f"  ok: {success} / {total}", flush=True)
    print(f"  failed: {fail} / {total}", flush=True)
    print(f"  elapsed: {time.time() - t0:.1f} s", flush=True)
    print(f"  WAV output dir: {WAV_DIR}", flush=True)


if __name__ == "__main__":
    main()