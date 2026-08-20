# -*- coding: utf-8 -*-
"""
VibeDoMuse · Project root entry.
Launches the Agent GUI (PyQt6 desktop app VibeDoMuse).

Run (recommended: use the isolated venv that has PyQt6 installed):
    python main.py
or double-click frontend_pyqt6/run.bat (which points here).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from vibedomuse import config  # noqa: E402
config.ensure_config_file()   # auto-create config.ini at startup if missing

from frontend_pyqt6.main import main  # noqa: E402

if __name__ == "__main__":
    main()
