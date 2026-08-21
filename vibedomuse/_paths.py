# -*- coding: utf-8 -*-
"""
VibeDoMuse · _paths.py
Portable path resolution that works in BOTH:
  - development (source checkout, run with `python main.py`)
  - PyInstaller frozen builds (--onedir / --onefile)

Two kinds of locations are distinguished:

  APP_BASE    : where *bundled, read-only* data lives
                (JSON spec, template json dirs, binaries, soundfont).
                In frozen mode this is the PyInstaller extraction folder
                (sys._MEIPASS for --onefile, or the executable's folder /
                its `_internal` subfolder for --onedir).

  RUNTIME_DIR : where *writable* app state lives
                (config.ini, generated/{json,midi,wav}).
                In frozen mode this is the folder that contains the .exe,
                so the whole deployment is self-contained and portable:
                you can move the `windows/` folder anywhere and it just runs.

The resolver searches a list of candidate base directories so it is robust
to PyInstaller's exact onedir layout (top-level vs `_internal`).
"""
import os
import sys

_FROZEN = getattr(sys, "frozen", False)


def _candidate_bases():
    bases = []
    # 1) onefile extraction dir (only set in --onefile mode)
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        bases.append(meipass)
    # 2) folder containing the executable (--onedir top level, and a safe
    #    fallback for --onefile where the exe sits in the temp dir too)
    exe = getattr(sys, "executable", "")
    if exe:
        exe_dir = os.path.dirname(os.path.abspath(exe))
        bases.append(exe_dir)
        # PyInstaller 6+ may place collected files in an `_internal` subfolder
        bases.append(os.path.join(exe_dir, "_internal"))
    # 3) development: project root = parent of the vibedomuse package
    bases.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # de-dup while preserving order
    seen = set()
    out = []
    for b in bases:
        if b and b not in seen:
            seen.add(b)
            out.append(b)
    return out


_CANDIDATES = _candidate_bases()


def resource_path(rel):
    """Resolve a bundled read-only data file, given its repo-relative path.

    Returns the first existing candidate; if none exist yet (e.g. the file is
    created at runtime) it returns the preferred base (executable folder).
    """
    for base in _CANDIDATES:
        p = os.path.join(base, rel)
        if os.path.exists(p):
            return p
    return os.path.join(_CANDIDATES[0], rel)


def runtime_dir():
    """Writable folder for config.ini and generated outputs."""
    if _FROZEN:
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


RUNTIME_DIR = runtime_dir()
