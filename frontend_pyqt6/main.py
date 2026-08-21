# -*- coding: utf-8 -*-
"""
VibeDoMuse · Main program (PyQt6 desktop app).

VibeDoMuse is an AI music-composition Agent:
  natural language -> retrieve local knowledge base (JSON spec + 144 template examples)
  -> LLM writes a brand-new Do-muse JSON with the knowledge base
  -> local validation -> render to WAV (cached in memory until user confirms saving).

v2 UI additions:
  - Piano-roll visualization of the generated score
  - Seed controls (same-seed regenerate / new-seed variant)
  - Seamless-loop playback toggle (auto-enables for loop scores)
  - Template browser ("compose on top of a real template")
  - In-session history, batch variants and calm/tense layer generation
  - Per-track mix dialog (velocity scaling + mute)
"""
import os
import re
import sys
import json
import logging
import shutil

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPlainTextEdit, QPushButton, QLineEdit, QTabWidget, QComboBox,
    QMenuBar, QStatusBar, QMessageBox, QFileDialog, QProgressBar, QSlider,
    QDialog, QInputDialog, QScrollArea, QCheckBox, QListWidget, QListWidgetItem,
)
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QUrl
from PyQt6.QtGui import QAction, QTextCursor

# ======================================================================
# i18n moved to frontend_pyqt6/i18n.py (imported below after sys.path setup)
# ======================================================================

# ---- locate project root and vibedomuse package ----
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from vibedomuse import agent, template_db, config, renderer  # noqa: E402
from vibedomuse.history_manager import history_manager  # instance, not module  # noqa: E402
from frontend_pyqt6.i18n import _, set_language, _lang  # noqa: E402
from frontend_pyqt6.widgets import JsonHighlighter, PianoRoll  # noqa: E402
from frontend_pyqt6.workers import (  # noqa: E402
    AnalyzeWorker, GenWorker, ExportWorker, RenderWorker, FollowupWorker,
)
from frontend_pyqt6.dialogs import (  # noqa: E402
    LlmSettingsDialog, UnderstandingDialog, TemplateBrowserDialog, MixDialog,
    HistoryDetailDialog,
)


def _read_bytes(path):
    """Read file bytes; return empty bytes on failure (used for in-memory cache)."""
    try:
        with open(path, "rb") as f:
            return f.read()
    except Exception:
        return b""


def _read_text(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


# ======================================================================
# QSS themes (from Do-muse style.qss / style_dark.qss)
# In light theme all fonts are black (#000000) for readability.
# ======================================================================
LIGHT_BASE = """
QMainWindow { background-color: #f5f5f5; }
QMenuBar { background-color: #ffffff; border-bottom: 1px solid #e0e0e0; padding: 2px; }
QMenuBar::item { color: #1976d2; padding: 4px 8px; border-radius: 4px; }
QMenuBar::item:selected { background-color: #e3f2fd; color: #1976d2; }
QMenu { background-color: #ffffff; border: 1px solid #e0e0e0; }
QMenu::item { color: #1976d2; padding: 6px 24px; }
QMenu::item:selected { background-color: #e3f2fd; color: #1976d2; }
QPushButton { background-color: #1976d2; color: white; border: none; padding: 6px 16px; border-radius: 4px; font-size: 13px; }
QPushButton:hover { background-color: #1565c0; }
QPushButton:pressed { background-color: #0d47a1; }
QPushButton:disabled { background-color: #bdbdbd; color: #ffffff; }
QPushButton#stopButton { background-color: #d32f2f; }
QPushButton#stopButton:hover { background-color: #c62828; }
QPushButton#secondary { background-color: #f5f5f5; color: #1976d2; border: 1px solid #1976d2; }
QPushButton#secondary:hover { background-color: #e3f2fd; }
QPlainTextEdit { background-color: #ffffff; color: #000000; border: 1px solid #e0e0e0; border-radius: 4px; font-family: "Consolas", "Microsoft YaHei", monospace; font-size: 13px; padding: 8px; }
QPlainTextEdit#logConsole { background-color: #1e1e1e; color: #d4d4d4; font-family: "Consolas", monospace; font-size: 12px; }
QTabWidget::pane { border: 1px solid #e0e0e0; border-radius: 4px; background-color: #ffffff; }
QTabBar::tab { background-color: #f5f5f5; color: #000000; border: 1px solid #e0e0e0; padding: 8px 20px; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
QTabBar::tab:selected { background-color: #ffffff; color: #000000; border-bottom: 2px solid #1976d2; }
QProgressBar { border: 1px solid #e0e0e0; border-radius: 4px; text-align: center; background-color: #f5f5f5; color: #000000; }
QProgressBar::chunk:indeterminate { background-color: #1976d2; width: 20px; }
QLabel { color: #000000; }
QLineEdit { border: 1px solid #e0e0e0; border-radius: 4px; padding: 6px; background-color: #ffffff; color: #000000; }
QDialog { background-color: #ffffff; }
QListWidget { background-color: #ffffff; color: #000000; border: 1px solid #e0e0e0; border-radius: 4px; }
QComboBox { background-color: #ffffff; color: #000000; border: 1px solid #e0e0e0; border-radius: 4px; padding: 4px 8px; }
QComboBox:disabled { background-color: #f5f5f5; color: #bdbdbd; }
QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 20px; border-left: 1px solid #e0e0e0; }
QComboBox::down-arrow { width: 10px; height: 6px; }
QComboBox QAbstractItemView { background-color: #ffffff; color: #000000; border: 1px solid #e0e0e0; selection-background-color: #e3f2fd; selection-color: #000000; }
QComboBox QAbstractItemView::item:disabled { color: #bdbdbd; }
QSlider::groove:horizontal { border: 1px solid #e0e0e0; height: 6px; border-radius: 3px; background: #f5f5f5; }
QSlider::sub-page:horizontal { background: #1976d2; border-radius: 3px; }
QSlider::handle:horizontal { background: #1976d2; width: 14px; margin: -5px 0; border-radius: 7px; }
QMessageBox { background-color: #ffffff; }
QMessageBox QLabel { color: #000000; }
"""
DARK_BASE = """
QMainWindow { background-color: #1e1e1e; }
QMenuBar { background-color: #2d2d2d; border-bottom: 1px solid #383838; padding: 2px; }
QMenuBar::item { color: #64b5f6; padding: 4px 8px; border-radius: 4px; }
QMenuBar::item:selected { background-color: #37474f; color: #90caf9; }
QMenu { background-color: #2d2d2d; border: 1px solid #383838; }
QMenu::item { color: #64b5f6; padding: 6px 24px; }
QMenu::item:selected { background-color: #37474f; color: #90caf9; }
QPushButton { background-color: #1976d2; color: white; border: none; padding: 6px 16px; border-radius: 4px; font-size: 13px; }
QPushButton:hover { background-color: #1565c0; }
QPushButton:pressed { background-color: #0d47a1; }
QPushButton:disabled { background-color: #424242; color: #757575; }
QPushButton#stopButton { background-color: #d32f2f; }
QPushButton#stopButton:hover { background-color: #c62828; }
QPushButton#secondary { background-color: #2d2d2d; color: #64b5f6; border: 1px solid #64b5f6; }
QPushButton#secondary:hover { background-color: #37474f; }
QPlainTextEdit { background-color: #1a1a1a; color: #e0e0e0; border: 1px solid #383838; border-radius: 4px; font-family: "Consolas", "Microsoft YaHei", monospace; font-size: 13px; padding: 8px; }
QPlainTextEdit#logConsole { background-color: #1e1e1e; color: #d4d4d4; font-family: "Consolas", monospace; font-size: 12px; }
QTabWidget::pane { border: 1px solid #383838; border-radius: 4px; background-color: #1e1e1e; }
QTabBar::tab { background-color: #2d2d2d; color: #b0bec5; border: 1px solid #383838; padding: 8px 20px; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
QTabBar::tab:selected { background-color: #1e1e1e; color: #64b5f6; border-bottom: 2px solid #1976d2; }
QProgressBar { border: 1px solid #383838; border-radius: 4px; text-align: center; background-color: #2d2d2d; color: #e0e0e0; }
QProgressBar::chunk:indeterminate { background-color: #1976d2; width: 20px; }
QLabel { color: #e0e0e0; }
QLineEdit { border: 1px solid #383838; border-radius: 4px; padding: 6px; background-color: #1a1a1a; color: #e0e0e0; }
QDialog { background-color: #2d2d2d; }
QListWidget { background-color: #1a1a1a; color: #e0e0e0; border: 1px solid #383838; border-radius: 4px; }
QComboBox { background-color: #1a1a1a; color: #e0e0e0; border: 1px solid #383838; border-radius: 4px; padding: 4px 8px; }
QComboBox:disabled { background-color: #2d2d2d; color: #757575; }
QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 20px; border-left: 1px solid #383838; }
QComboBox::down-arrow { width: 10px; height: 6px; }
QComboBox QAbstractItemView { background-color: #1a1a1a; color: #e0e0e0; border: 1px solid #383838; selection-background-color: #37474f; selection-color: #90caf9; }
QComboBox QAbstractItemView::item:disabled { color: #555555; }
QSlider::groove:horizontal { border: 1px solid #383838; height: 6px; border-radius: 3px; background: #2d2d2d; }
QSlider::sub-page:horizontal { background: #1976d2; border-radius: 3px; }
QSlider::handle:horizontal { background: #64b5f6; width: 14px; margin: -5px 0; border-radius: 7px; }
QMessageBox { background-color: #2d2d2d; }
QMessageBox QLabel { color: #e0e0e0; }
QSplitter::handle { background-color: #383838; }
"""

EXTRA_LIGHT = """
QTextEdit { background-color:#ffffff; color:#000000; border:1px solid #e0e0e0; border-radius:4px; font-family:"Microsoft YaHei","Consolas"; font-size:13px; padding:6px; }
"""
EXTRA_DARK = """
QTextEdit { background-color:#1a1a1a; color:#e0e0e0; border:1px solid #383838; border-radius:4px; font-family:"Microsoft YaHei","Consolas"; font-size:13px; padding:6px; }
"""


def qss_for(theme: str) -> str:
    if theme == "dark":
        return DARK_BASE + EXTRA_DARK
    return LIGHT_BASE + EXTRA_LIGHT


# ======================================================================
# JsonHighlighter / PianoRoll moved to frontend_pyqt6/widgets.py
# ======================================================================


# ======================================================================
# Worker threads moved to frontend_pyqt6/workers.py
# ======================================================================


# ======================================================================
# Dialogs moved to frontend_pyqt6/dialogs.py
# ======================================================================


# ======================================================================
# Logging -> GUI bridge
# ======================================================================
class _LogEmitter(QObject):
    """QObject carrier for the log signal (kept separate so the logging.Handler
    stays a pure-Python object that is safe to close() during interpreter
    shutdown)."""
    message = pyqtSignal(str)


class QtLogHandler(logging.Handler):
    """Route Python logging records into the GUI Log tab (thread-safe).

    Emits a queued signal from whatever thread logged the record; the main
    window connects it to the log console, which must be touched only from
    the GUI thread. Access the signal via ``handler.emitter.message``.
    """

    def __init__(self, level=logging.INFO):
        super().__init__(level)
        self.emitter = _LogEmitter()
        self.setFormatter(logging.Formatter(
            "[%(asctime)s] %(levelname)s %(name)s: %(message)s", datefmt="%H:%M:%S"))

    def emit(self, record):
        try:
            self.emitter.message.emit(self.format(record))
        except Exception:  # noqa: BLE001
            pass


# ======================================================================
# Main window
# ======================================================================
class VibeDoMuse(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(_("VibeDoMuse · AI Music Agent"))
        self.resize(1280, 840)

        self.theme = self._load_theme()
        config.ensure_config_file()   # create config.ini if missing
        self._last_generated = None
        self._current_wav = None         # absolute path for playback
        self._current_json_path = None   # absolute path for saving
        self._worker = None
        self._player = None
        self._audio = None
        self._seeking = False
        self._cache_artifacts = {}
        self._wav_bytes = b""
        self._midi_bytes = b""
        self._json_text = ""
        self._last_seed = None
        self._current_analysis = None    # Store AI understanding for follow-ups
        self._current_history_id = None  # Track current history item ID
        self._setup_player()

        self._build_ui()
        self._update_input_mode()  # set initial prompt/follow-up label from history state
        self._apply_theme(self.theme)
        self._refresh_stats()

        # Route Python logging into the Log tab so LLM / render failures and
        # rule-engine fallbacks become visible in the GUI (thread-safe via signal).
        self._qt_log_handler = QtLogHandler()
        self._qt_log_handler.emitter.message.connect(self._append_log)
        logging.getLogger().addHandler(self._qt_log_handler)

    def _append_log(self, msg):
        self.log_view.appendPlainText(msg)

    # ---------- player ----------
    def _setup_player(self):
        try:
            from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
            self._player = QMediaPlayer()
            self._audio = QAudioOutput()
            self._player.setAudioOutput(self._audio)
            self._player.mediaStatusChanged.connect(self._on_media_status)
            self._player.positionChanged.connect(self._on_position)
            self._player.durationChanged.connect(self._on_duration)
        except Exception:  # noqa: BLE001
            self._player = None

    def _on_media_status(self, status):
        from PyQt6.QtMultimedia import QMediaPlayer
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self.chk_loop.isChecked() and self._current_wav:
                self._player.play()
                return
            self._set_play_ui(False)

    def _on_position(self, pos):
        if self._seeking or not self._player:
            return
        dur = self._player.duration()
        if dur > 0:
            self.play_slider.setValue(int(pos / dur * 1000))
        self._update_time(pos, dur)

    def _on_duration(self, dur):
        if self._player:
            self._update_time(self._player.position(), dur)

    def _update_time(self, pos, dur):
        def fmt(ms):
            return f"{ms // 60000}:{(ms // 1000) % 60:02d}"
        self.time_label.setText(f"{fmt(pos)} / {fmt(dur)}")

    def _seek_to(self, value):
        if self._player:
            dur = self._player.duration()
            if dur > 0:
                self._player.setPosition(int(value / 1000 * dur))

    # ---------- UI construction ----------
    def _build_ui(self):
        mb = self.menuBar()
        file_menu = mb.addMenu(_("File"))
        act_exit = QAction(_("Exit"), self)
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        theme_menu = mb.addMenu(_("Theme"))
        act_light = QAction(_("Light"), self)
        act_light.triggered.connect(lambda: self._apply_theme("light"))
        act_dark = QAction(_("Dark"), self)
        act_dark.triggered.connect(lambda: self._apply_theme("dark"))
        theme_menu.addAction(act_light)
        theme_menu.addAction(act_dark)

        settings_menu = mb.addMenu(_("Settings"))
        act_llm = QAction(_("LLM Settings"), self)
        act_llm.triggered.connect(self._llm_settings)
        settings_menu.addAction(act_llm)
        act_lang = QAction(_("Language"), self)
        act_lang.triggered.connect(self._language_settings)
        settings_menu.addAction(act_lang)

        tools_menu = mb.addMenu(_("Tools"))
        act_tpl = QAction(_("Template Browser (144 pieces)"), self)
        act_tpl.triggered.connect(self._open_template_browser)
        tools_menu.addAction(act_tpl)
        act_mix = QAction(_("Mix Adjustment\u2026"), self)
        act_mix.triggered.connect(self._open_mix)
        tools_menu.addAction(act_mix)

        central = QWidget()
        self.setCentralWidget(central)
        root_v = QVBoxLayout(central)

        title = QLabel(_("VibeDoMuse · AI Music Agent (Natural Language \u2192 Knowledge Base \u2192 Score Generation)"))
        title.setStyleSheet("font-size:16px; font-weight:bold; padding:4px 2px;")
        root_v.addWidget(title)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        root_v.addWidget(splitter, 1)

        # ---- left panel ----
        left = QWidget()
        left_v = QVBoxLayout(left)
        left_v.setContentsMargins(4, 4, 4, 4)

        self.nl_input_label = QLabel(_("Natural Language Description"))
        left_v.addWidget(self.nl_input_label)
        self.nl_input = QTextEdit()
        self.nl_input.setPlaceholderText(_("Placeholder_Example"))
        self.nl_input.setMinimumHeight(110)
        left_v.addWidget(self.nl_input, 1)

        row1 = QHBoxLayout()
        self.btn_generate = QPushButton(_("Generate Song"))
        self.btn_generate.clicked.connect(self._on_generate)
        row1.addWidget(self.btn_generate, 1)
        self.btn_same_seed = QPushButton(_("Re-generate (same seed)"))
        self.btn_same_seed.setObjectName("secondary")
        self.btn_same_seed.setEnabled(False)
        self.btn_same_seed.clicked.connect(self._on_same_seed)
        row1.addWidget(self.btn_same_seed, 1)
        left_v.addLayout(row1)

        row2 = QHBoxLayout()
        self.btn_variant = QPushButton(_("Change Seed Variant"))
        self.btn_variant.setObjectName("secondary")
        self.btn_variant.clicked.connect(self._on_variant)
        row2.addWidget(self.btn_variant, 1)
        self.btn_layers = QPushButton(_("Layer Variation"))
        self.btn_layers.setObjectName("secondary")
        self.btn_layers.clicked.connect(self._on_layers)
        row2.addWidget(self.btn_layers, 1)
        left_v.addLayout(row2)

        # Export format selector (always visible; drives the chosen export format)
        fmt_row = QHBoxLayout()
        fmt_row.addWidget(QLabel(_("Export Format")))
        self.export_format = QComboBox()
        self._build_export_formats()
        fmt_row.addWidget(self.export_format, 1)
        left_v.addLayout(fmt_row)

        row3 = QHBoxLayout()
        self.btn_batch = QPushButton(_("Batch Variants\u2026"))
        self.btn_batch.setObjectName("secondary")
        self.btn_batch.clicked.connect(self._on_batch)
        row3.addWidget(self.btn_batch, 1)
        self.btn_export = QPushButton(_("Export\u2026"))
        self.btn_export.setEnabled(False)
        self.btn_export.clicked.connect(self._on_export)
        row3.addWidget(self.btn_export, 1)
        left_v.addLayout(row3)

        # Temperature slider (live-adjustable LLM temperature, 0.0 - 2.0)
        temp_row = QHBoxLayout()
        temp_row.addWidget(QLabel(_("Temperature")))
        self.temp_slider = QSlider(Qt.Orientation.Horizontal)
        self.temp_slider.setRange(0, 20)            # 0.0 - 2.0 in 0.1 steps
        self.temp_slider.setSingleStep(1)
        self.temp_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.temp_slider.setTickInterval(2)
        _init_temp = int(round(config.get_llm_settings().get("temperature", 0.3) * 10))
        self.temp_slider.setValue(_init_temp)
        temp_row.addWidget(self.temp_slider, 1)
        self.temp_value = QLabel(f"{self.temp_slider.value() / 10:.1f}")
        self.temp_value.setMinimumWidth(28)
        self.temp_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        temp_row.addWidget(self.temp_value)
        left_v.addLayout(temp_row)
        self.temp_slider.valueChanged.connect(self._on_temperature_changed)

        self.progress = QProgressBar()
        self.progress.setTextVisible(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        left_v.addWidget(self.progress)

        self.seed_label = QLabel("Seed: -")
        self.seed_label.setStyleSheet("color:#888888; font-size:12px;")
        left_v.addWidget(self.seed_label)

        # ---- right panel ----
        right = QWidget()
        right_v = QVBoxLayout(right)
        right_v.setContentsMargins(4, 4, 4, 4)

        self.tabs = QTabWidget()
        self.json_view = QPlainTextEdit()
        self.json_view.setObjectName("jsonView")
        self._hl = JsonHighlighter(self.json_view.document(), self.theme)
        self.roll_view = PianoRoll()
        self.roll_scroll = QScrollArea()
        self.roll_scroll.setWidget(self.roll_view)
        self.roll_scroll.setWidgetResizable(True)
        self.log_view = QPlainTextEdit()
        self.log_view.setObjectName("logConsole")
        self.log_view.setReadOnly(True)
        self.tabs.addTab(self.json_view, _("JSON Preview"))
        self.tabs.addTab(self.roll_scroll, _("Piano Roll"))
        self.tabs.addTab(self.log_view, _("Log"))

        # History tab
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self._on_history_item_selected)
        self.history_scroll = QScrollArea()
        self.history_scroll.setWidget(self.history_list)
        self.history_scroll.setWidgetResizable(True)
        self.tabs.addTab(self.history_scroll, _("History"))
        self.tabs.currentChanged.connect(self._on_tab_changed)

        right_v.addWidget(self.tabs, 1)

        play_row = QHBoxLayout()
        self.btn_play = QPushButton("\u25b6 " + _("Play"))
        self.btn_play.clicked.connect(self._play)
        self.btn_play.setEnabled(False)
        self.btn_stop = QPushButton("\u25a0 " + _("Stop"))
        self.btn_stop.setObjectName("stopButton")
        self.btn_stop.clicked.connect(self._stop)
        self.btn_stop.setEnabled(False)
        self.chk_loop = QCheckBox(_("Loop"))
        self.chk_loop.setToolTip(_("Loop playback: seamless background music loop"))
        self.play_status = QLabel(_("Not generated yet"))
        play_row.addWidget(self.btn_play)
        play_row.addWidget(self.btn_stop)
        play_row.addWidget(self.chk_loop)
        play_row.addWidget(self.play_status, 1)
        right_v.addLayout(play_row)

        seek_row = QHBoxLayout()
        self.play_slider = QSlider(Qt.Orientation.Horizontal)
        self.play_slider.setRange(0, 1000)
        self.play_slider.setValue(0)
        self.play_slider.setEnabled(False)
        self.play_slider.sliderPressed.connect(lambda: setattr(self, "_seeking", True))
        self.play_slider.sliderReleased.connect(lambda: setattr(self, "_seeking", False))
        self.play_slider.sliderMoved.connect(self._seek_to)
        self.time_label = QLabel("0:00 / 0:00")
        seek_row.addWidget(self.play_slider, 1)
        seek_row.addWidget(self.time_label)
        right_v.addLayout(seek_row)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([430, 850])

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    # ---------- theme ----------
    def _load_theme(self):
        return config.get_theme()

    def _save_theme(self, theme):
        config.set_theme(theme)

    def _apply_theme(self, theme):
        self.theme = theme
        QApplication.instance().setStyleSheet(qss_for(theme))
        if hasattr(self, "_hl"):
            self._hl.set_theme(theme)
        self._save_theme(theme)

    # ---------- actions ----------
    def _refresh_stats(self):
        try:
            st = template_db.stats()
            self.status_bar.showMessage(
                f"KB: {st['total']} templates + JSON spec 37 sections ｜ LLM config in Settings"
            )
        except Exception as e:  # noqa: BLE001
            self.status_bar.showMessage(f"KB load failed: {e}")

    def _set_busy(self, busy):
        self.btn_generate.setEnabled(not busy)
        self.btn_export.setEnabled(not busy)
        self.btn_same_seed.setEnabled(not busy and self._last_seed is not None)
        self.btn_variant.setEnabled(not busy)
        self.btn_batch.setEnabled(not busy)
        self.btn_layers.setEnabled(not busy)
        if busy:
            self.progress.setRange(0, 0)
            self.progress.setValue(0)
            self.status_bar.showMessage("Agent is searching the knowledge base and creating...")
        else:
            self.progress.setRange(0, 100)
            self.progress.setValue(100)
            self._refresh_stats()

    def _llm_settings(self):
        dlg = LlmSettingsDialog(self)
        dlg.exec()

    def _language_settings(self):
        current = _lang()
        keys = ["en", "zh"]
        labels = [_("English"), _("Chinese")]
        dlg = QDialog(self)
        dlg.setWindowTitle(_("Language"))
        dlg.setMinimumWidth(300)
        v = QVBoxLayout(dlg)
        v.addWidget(QLabel(_("Language") + ":"))
        combo = QListWidget()
        for lab in labels:
            item = QListWidgetItem(lab)
            if keys[labels.index(lab)] == current:
                combo.setCurrentItem(item)
            combo.addItem(item)
        combo.setCurrentRow(keys.index(current) if current in keys else 0)
        v.addWidget(combo)
        btns = QHBoxLayout()
        ok_btn = QPushButton(_("OK"))
        ok_btn.clicked.connect(dlg.accept)
        cancel_btn = QPushButton(_("Cancel"))
        cancel_btn.clicked.connect(dlg.reject)
        # Language dialog buttons always use black text (light theme)
        ok_btn.setStyleSheet("color: #000000; background-color: #e0e0e0; border: 1px solid #ccc; padding: 6px 16px; border-radius: 4px;")
        cancel_btn.setStyleSheet("color: #000000; background-color: #e0e0e0; border: 1px solid #ccc; padding: 6px 16px; border-radius: 4px;")
        btns.addStretch()
        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)
        v.addLayout(btns)
        if dlg.exec():
            sel = combo.currentRow()
            if 0 <= sel < len(keys):
                set_language(keys[sel])
                QMessageBox.information(self, _("Language"), _("Settings saved. Restart required for some changes to take effect."))

    def _open_template_browser(self):
        dlg = TemplateBrowserDialog(self)
        if dlg.exec() and dlg.selected:
            self._set_busy(True)
            text = self.nl_input.toPlainText().strip()
            if not text:
                text = "Create a piece in the same style based on this template"
            self._run_agent(text, mode="rule", use_template=dlg.selected)

    def _open_mix(self):
        if not self._last_generated or not self._last_generated.get("score"):
            QMessageBox.warning(self, _("Mix Adjustment"), _("No score loaded yet."))
            return
        dlg = MixDialog(self._last_generated.get("score"), self)
        if dlg.exec():
            score = dlg.result_score()
            self._set_busy(True)
            self.log_view.appendPlainText("Re-rendering the adjusted score...")
            self._render_worker = RenderWorker(score, "mixed_" + str(self._last_generated.get("seed", 0)))
            self._render_worker.finished.connect(self._on_render_done)
            self._render_worker.error.connect(self._on_worker_error)
            self._render_worker.start()

    def _on_generate(self):
        text = self.nl_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, _("Generate Song"), _("Please enter a natural language description first."))
            return
        # After the first generation the main field acts as a modify / follow-up
        # input (history is non-empty) -> run a follow-up on the last result.
        if history_manager.get_history() and self._last_generated and self._last_generated.get("score"):
            self._run_followup(text)
            return
        self._set_busy(True)
        self.log_view.clear()
        self.log_view.appendPlainText("Stage 1: Analyzing your request (LLM considers spec sections, templates)...")
        self._analyze_worker = AnalyzeWorker(text)
        self._analyze_worker.token.connect(self._on_analysis_token)
        self._analyze_worker.finished.connect(self._on_analyze_finished)
        self._analyze_worker.error.connect(self._on_worker_error)
        self._analyze_worker.start()

    def _on_analyze_finished(self, analysis_text):
        self._set_busy(False)
        self.log_view.appendPlainText("LLM understanding received. Showing confirmation dialog...")
        dialog = UnderstandingDialog(analysis_text, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # User confirmed - proceed to Stage 2 generation
            # Get the user's modified understanding
            user_analysis = dialog.get_analysis()
            self._set_busy(True)
            self.json_view.clear()
            self._worker = GenWorker(
                self.nl_input.toPlainText().strip(),
                mode="llm_v2",
                analysis=user_analysis
            )
            self._worker.log.connect(self.log_view.appendPlainText)
            self._worker.token.connect(self._on_token)
            self._worker.finished.connect(self._on_worker_finished)
            self._worker.error.connect(self._on_worker_error)
            self._worker.start()
        else:
            # User wants to modify the description - focus back on input
            self.nl_input.setFocus()
            self.log_view.appendPlainText("Please modify your description and click 'Generate Song' again.")

    def _on_same_seed(self):
        text = self.nl_input.toPlainText().strip() or (self._last_generated or {}).get("text", "")
        if not text:
            QMessageBox.warning(self, _("Generate Song"), _("Please enter a natural language description first."))
            return
        self._run_agent(text, mode="llm", seed=self._last_seed)

    def _on_variant(self):
        text = self.nl_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, _("Generate Song"), _("Please enter a natural language description first."))
            return
        self._run_agent(text, mode="rule")

    def _on_layers(self):
        text = self.nl_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, _("Generate Song"), _("Please enter a natural language description first."))
            return
        self._run_agent(text, mode="layers")

    def _on_batch(self):
        text = self.nl_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, _("Generate Song"), _("Please enter a natural language description first."))
            return
        n, ok = QInputDialog.getInt(self, _("Batch Variants"), _("How many variants (2-8)?"), 4, 2, 8, 1)
        if not ok:
            return
        self._run_agent(text, mode="variants", n=n)

    def _run_agent(self, text, mode="llm", seed=None, use_template=None, n=4):
        self._set_busy(True)
        self.log_view.clear()
        self.json_view.clear()
        self._worker = GenWorker(text, seed=seed, mode=mode, use_template=use_template, n=n)
        self._worker.log.connect(self.log_view.appendPlainText)
        self._worker.token.connect(self._on_token)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.error.connect(self._on_worker_error)
        self._worker.start()

    def _run_followup(self, feedback):
        """Run a follow-up / modification generation using the main input text.

        Invoked from _on_generate when history is non-empty (modify / follow-up mode).
        """
        if not self._last_generated or not self._last_generated.get("score"):
            QMessageBox.warning(self, _("Follow-up Generation"),
                                _("Please generate a song first before using follow-up."))
            return
        if not feedback:
            QMessageBox.warning(self, _("Follow-up Generation"),
                                _("Please enter your feedback on the generated music."))
            return

        original_text = self._last_generated.get("text", "")
        original_analysis = self._current_analysis
        current_score = self._last_generated.get("score", {})

        self._set_busy(True)
        self.log_view.clear()
        self.json_view.clear()
        self.log_view.appendPlainText(_("Follow-up Generation") + "...")
        self.log_view.appendPlainText(_("User Feedback") + ": " + feedback)

        from frontend_pyqt6.workers import FollowupWorker
        self._worker = FollowupWorker(original_text, original_analysis, current_score, feedback)
        self._worker.log.connect(self.log_view.appendPlainText)
        self._worker.token.connect(self._on_token)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.error.connect(self._on_worker_error)
        self._worker.start()

    def _on_history_item_selected(self, item):
        """Handle history item double-click - show details dialog."""
        history_item = item.data(Qt.ItemDataRole.UserRole)
        if history_item:
            dlg = HistoryDetailDialog(history_item, self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                # Load the result into the main view
                if history_item.score:
                    mock_result = {
                        "ok": True,
                        "text": history_item.user_text,
                        "score": history_item.score,
                        "seed": history_item.seed,
                        "method": history_item.method,
                        "generated": {},
                    }
                    self._load_result(mock_result)
                    self.log_view.appendPlainText(_("Loaded result from history"))

    def _update_input_mode(self):
        """Relabel the primary input between 'prompt' and 'modify / follow-up'
        based on whether any generation history exists (empty-history check).

        - Empty history  -> first input: treat as a fresh prompt field.
        - Non-empty hist. -> subsequent input: treat as a modify / follow-up field
          (and clear any leftover text so the user starts a fresh modification).
        """
        has_history = bool(history_manager.get_history())
        if has_history:
            self.nl_input_label.setText(_("Modify / Follow-up Input"))
            self.nl_input.setPlaceholderText(_("Modify_Followup_Placeholder"))
            self.nl_input.clear()
        else:
            self.nl_input_label.setText(_("Natural Language Description"))
            self.nl_input.setPlaceholderText(_("Placeholder_Example"))

    def _on_temperature_changed(self, value):
        """Persist the slider value as the LLM temperature (0.0 - 2.0)."""
        temp = value / 10.0
        self.temp_value.setText(f"{temp:.1f}")
        config.set_temperature(temp)

    def _update_history_list(self):
        """Update the history list widget with current history items."""
        self.history_list.clear()
        items = history_manager.get_history()
        if not items:
            empty_item = QListWidgetItem(_("No history yet"))
            empty_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.history_list.addItem(empty_item)
            return

        for item in items:
            timestamp_str = self._format_timestamp(item.timestamp)
            summary = item.summary or item.user_text[:50]
            seed_str = str(item.seed) if item.seed else "N/A"
            display_text = f"{timestamp_str} | Seed: {seed_str} | {summary[:60]}..."
            
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            self.history_list.addItem(list_item)

    def _format_timestamp(self, timestamp):
        """Format Unix timestamp to readable string."""
        from datetime import datetime
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def _on_tab_changed(self, index):
        """Handle tab widget change - update history list when history tab is selected."""
        if self.tabs.tabText(index) == _("History"):
            self._update_history_list()

    # ---------- live streaming (on_token) ----------
    def _on_token(self, chunk):
        """Live LLM JSON streaming -> show it in the JSON Preview tab as it writes."""
        if chunk:
            self.json_view.moveCursor(QTextCursor.MoveOperation.End)
            self.json_view.insertPlainText(chunk)
            if self.tabs.currentWidget() is not self.json_view:
                self.tabs.setCurrentWidget(self.json_view)

    def _on_analysis_token(self, chunk):
        """Live stage-1 analysis streaming -> show it in the Log tab."""
        if chunk:
            self.log_view.moveCursor(QTextCursor.MoveOperation.End)
            self.log_view.insertPlainText(chunk)

    # ---------- results ----------
    def _on_worker_finished(self, payload):
        self._set_busy(False)
        kind = payload.get("kind", "single")
        if kind == "variants":
            items = payload.get("items") or []
            self.log_view.appendPlainText(f"Batch complete: {len(items)} variants")
            for it in items:
                self.log_view.appendPlainText(
                    f"  #{it.get('variant')} seed {it.get('seed')} ｜ {it.get('summary', '')} ｜ "
                    f"{it.get('elapsed_sec', '?')}s")
            if items:
                self._load_result(items[0])
                self.status_bar.showMessage(f"Batch generation complete ({len(items)} variants, see log)")
            return
        if kind == "layers":
            data = payload.get("data") or {}
            layers = data.get("layers") or []
            self.log_view.appendPlainText("Layer variation complete:")
            for lr in layers:
                self.log_view.appendPlainText(
                    f"  {lr.get('layer_label')} ({lr.get('layer')}) seed {lr.get('seed')} ｜ {lr.get('summary', '')}")
            if layers:
                self._load_result(layers[0])
                self.status_bar.showMessage("Layer variation complete (calm / tense, see log)")
            return
        res = payload.get("data") or {}
        self._load_result(res)

    def _load_result(self, res):
        self._last_generated = res
        self._last_seed = res.get("seed")
        self.seed_label.setText(_("Seed:") + " " + str(self._last_seed))
        self.btn_same_seed.setEnabled(self._last_seed is not None)
        gp = res.get("generated", {})
        self._cache_artifacts = gp
        self._wav_bytes = _read_bytes(gp.get("wav_path"))
        self._midi_bytes = _read_bytes(gp.get("midi_path"))
        self._json_text = _read_text(gp.get("json_path"))
        self.btn_export.setEnabled(True)
        self._update_export_availability()
        jpath = gp.get("json_path")
        if jpath and os.path.exists(jpath):
            try:
                with open(jpath, "r", encoding="utf-8") as f:
                    self.json_view.setPlainText(f.read())
                self._current_json_path = jpath
            except Exception:
                self.json_view.setPlainText(json.dumps(res.get("score"), ensure_ascii=False, indent=2))
        else:
            self.json_view.setPlainText(json.dumps(res.get("score"), ensure_ascii=False, indent=2))
        self.roll_view.set_score(res.get("score"))
        # auto loop toggle for loop scores
        if isinstance(res.get("score"), dict) and res["score"].get("loop"):
            self.chk_loop.setChecked(True)
        wav_rel = gp.get("wav_path")
        if wav_rel and os.path.exists(wav_rel):
            abs_wav = wav_rel if os.path.isabs(wav_rel) else os.path.join(ROOT, wav_rel)
            self._current_wav = abs_wav
            self.btn_play.setEnabled(True)
        else:
            self._current_wav = None
            self.btn_play.setEnabled(False)
            if not wav_rel and gp.get("midi_path"):
                self.log_view.appendPlainText("Audio render unavailable (fluidsynth/SoundFont not found). MIDI generated successfully.")
        self._set_play_ui(False)
        cached = " (cached)" if gp.get("cached") else ""

        # Save to history if this is a successful generation
        if res.get("ok") and res.get("score"):
            method = res.get("method", "")
            # Determine parent ID for follow-ups
            parent_id = self._current_history_id if method == "followup" else None
            # Save to history
            history_id = history_manager.add_generation(
                user_text=res.get("text", ""),
                result=res,
                analysis=self._current_analysis,
                parent_id=parent_id
            )
            self._current_history_id = history_id
            # Update history list UI if it exists
            if hasattr(self, "_update_history_list"):
                self._update_history_list()
            self.log_view.appendPlainText(f"Saved to history (ID: {history_id}){cached}")
            # History is now non-empty -> switch the prompt field to modify / follow-up mode.
            self._update_input_mode()
        loop_s = " | loop" if isinstance(res.get("score"), dict) and res["score"].get("loop") else ""
        wav_label = gp.get("wav_file", "") or "MIDI only"
        self.play_status.setText(
            f"Generated{cached}: {wav_label} ({res.get('elapsed_sec','?')}s{loop_s})")
        method = res.get("method", "llm")
        if method == "llm":
            self.log_view.appendPlainText("Method: LLM + local knowledge base")
            if res.get("llm_warnings"):
                self.log_view.appendPlainText("  Validation warnings: " + "; ".join(res["llm_warnings"][:3]))
        elif method == "llm_v2":
            self.log_view.appendPlainText("Method: LLM v2 (two-stage understanding + generation)")
            if res.get("llm_warnings"):
                self.log_view.appendPlainText("  Validation warnings: " + "; ".join(res["llm_warnings"][:3]))
            v2a = res.get("v2_analysis")
            if v2a:
                truncated = v2a[:200] + ("..." if len(v2a) > 200 else "")
                self.log_view.appendPlainText("  LLM understanding: " + truncated)
        elif method == "fallback":
            self.log_view.appendPlainText("Fell back to rule engine: " + (res.get("llm_error") or "unknown"))
        elif method == "fallback_v2":
            self.log_view.appendPlainText("Fell back to rule engine (v2): " + (res.get("llm_error") or "unknown"))
            v2a = res.get("v2_analysis")
            if v2a:
                truncated = v2a[:200] + ("..." if len(v2a) > 200 else "")
                self.log_view.appendPlainText("  LLM original understanding: " + truncated)
        elif method == "layers":
            self.log_view.appendPlainText("Method: Layer variation (rule engine)")
        else:
            self.log_view.appendPlainText("Method: Rule engine")
        ks = res.get("knowledge_sections")
        if ks:
            self.log_view.appendPlainText("  Spec sections: " + " | ".join(ks[:4]))
        ke = res.get("knowledge_examples")
        if ke:
            self.log_view.appendPlainText("  Template examples: " + " | ".join(ke[:2]))
        self.log_view.appendPlainText(
            f"\nComplete | Seed: {res.get('seed','')} | "
            f"Elapsed: {res.get('elapsed_sec','?')}s")
        self.status_bar.showMessage(f"Generated: {gp.get('wav_file','')}")

    def _on_render_done(self, payload):
        self._set_busy(False)
        res = dict(self._last_generated or {})
        res["score"] = payload["score"]
        res["generated"] = payload["generated"]
        res["method"] = "mix"
        self.log_view.appendPlainText("✔ " + _("Remix completed"))
        self._load_result(res)

    def _on_worker_error(self, msg):
        self._set_busy(False)
        self.play_status.setText(_("Generation failed"))
        self.log_view.appendPlainText("✘ " + _("Error:") + " " + msg)
        QMessageBox.critical(self, _("Generation failed"), msg)

    # ---------- export ----------
    def _build_export_formats(self):
        """Populate the export-format combo with the supported formats and
        disable those whose required backend is missing.

        backend:
          - "always"  JSON (from the score, no external tool)
          - "domuse"  MusicXML / MIDI / LilyPond (need DoMuse.exe)
          - "ffmpeg"  MP3 / FLAC / OGG (need ffmpeg + a rendered WAV)
          - "wav"     WAV (need a rendered WAV in the current artifacts)
        """
        self._domuse_ok = os.path.exists(renderer.DOMUSE_EXE)
        self._ffmpeg_ok = renderer.get_ffmpeg_path() is not None
        self._EXPORT_FORMATS = [
            (_("MusicXML (.mxl)"), "mxl", "domuse"),
            (_("MIDI (.mid)"), "mid", "domuse"),
            (_("LilyPond (.ly)"), "ly", "domuse"),
            (_("WAV (.wav)"), "wav", "wav"),
            (_("MP3 (.mp3)"), "mp3", "ffmpeg"),
            (_("FLAC (.flac)"), "flac", "ffmpeg"),
            (_("OGG (.ogg)"), "ogg", "ffmpeg"),
            (_("JSON (.json)"), "json", "always"),
        ]
        self.export_format.clear()
        for label, ext, _backend in self._EXPORT_FORMATS:
            self.export_format.addItem(label, ext)
        self._update_export_availability()

    def _update_export_availability(self):
        """Enable/disable format entries based on backend availability.

        domuse/ffmpeg dependencies are static (known at startup); the WAV-based
        formats additionally require a freshly rendered WAV in the current
        generation's artifacts.
        """
        arts = getattr(self, "_cache_artifacts", None) or {}
        has_wav = bool(arts.get("wav_path") and os.path.exists(arts["wav_path"]))
        model = self.export_format.model()
        for i, (_label, _ext, backend) in enumerate(self._EXPORT_FORMATS):
            if backend == "always":
                ok = True
            elif backend == "domuse":
                ok = self._domuse_ok
            elif backend == "wav":
                ok = has_wav
            elif backend == "ffmpeg":
                ok = self._ffmpeg_ok and has_wav
            else:
                ok = True
            item = model.item(i)
            if item is not None:
                item.setEnabled(ok)
        # Make sure the current selection is enabled; otherwise fall back to the
        # first available format.
        cur = self.export_format.currentIndex()
        cur_item = model.item(cur) if cur >= 0 else None
        if cur_item is None or not cur_item.isEnabled():
            for i in range(self.export_format.count()):
                if model.item(i).isEnabled():
                    self.export_format.setCurrentIndex(i)
                    break

    def _on_export(self):
        if not self._last_generated or not self._cache_artifacts:
            QMessageBox.warning(self, _("Export\u2026"), _("Please generate a song first before exporting."))
            return
        idx = self.export_format.currentIndex()
        item = self.export_format.model().item(idx)
        if item is None or not item.isEnabled():
            QMessageBox.warning(
                self, _("Export\u2026"),
                _("The selected export format is unavailable.\n")
                + _("Reason: required backend (DoMuse.exe / ffmpeg / rendered WAV) not found.")
            )
            return
        fmt = self.export_format.itemData(idx)
        base = os.path.splitext(self._cache_artifacts.get("json_file", "piece"))[0]
        default_path = os.path.join(os.path.expanduser("~"), base + "." + fmt)
        # The format is chosen via the combo box, so the save dialog only asks
        # for a location (generic filter). The extension is appended below.
        path, _sel_filter = QFileDialog.getSaveFileName(
            self, _("Export Song"), default_path, _("All Files (*)")
        )
        if not path:
            return
        if os.path.splitext(path)[1].lower() != "." + fmt:
            path += "." + fmt
        self.btn_export.setEnabled(False)
        self.progress.setRange(0, 0)
        self.progress.setValue(0)
        self.status_bar.showMessage(f"Exporting {fmt.upper()}...")
        self._export_worker = ExportWorker(
            self._last_generated.get("score"), self._cache_artifacts, path, fmt
        )
        self._export_worker.finished.connect(self._on_export_done)
        self._export_worker.error.connect(self._on_export_error)
        self._export_worker.start()

    def _on_export_done(self, path):
        self.btn_export.setEnabled(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.log_view.appendPlainText(f"Exported: {path}")
        self.status_bar.showMessage("Exported: " + path)
        QMessageBox.information(self, _("Export Complete"), _("Exported to:") + "\n" + path)

    def _on_export_error(self, msg):
        self.btn_export.setEnabled(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.log_view.appendPlainText("Export failed: " + msg)
        self.status_bar.showMessage("Export failed")
        QMessageBox.critical(self, _("Export Error"), msg)

    # ---------- playback ----------
    def _set_play_ui(self, playing):
        self.btn_play.setEnabled(bool(self._current_wav) and os.path.exists(self._current_wav or ""))
        self.play_slider.setEnabled(playing)
        if not playing:
            self.btn_stop.setEnabled(False)
            self.play_slider.setValue(0)
            self.time_label.setText("0:00 / 0:00")
            if self._current_wav:
                self.play_status.setText(_("Ready:") + " " + os.path.basename(self._current_wav))
        else:
            self.btn_stop.setEnabled(True)
            self.play_status.setText(_("Playing..."))

    def _play(self):
        if not self._player or not self._current_wav or not os.path.exists(self._current_wav):
            QMessageBox.warning(self, _("Playback"), _("No audio available. Please generate a song first."))
            return
        self._player.setSource(QUrl.fromLocalFile(self._current_wav))
        self._player.play()
        self._set_play_ui(True)

    def _stop(self):
        if self._player:
            self._player.stop()
        self._set_play_ui(False)
        self.play_status.setText(_("Stopped:") + " " + os.path.basename(self._current_wav or ""))


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    app = QApplication(sys.argv)
    win = VibeDoMuse()
    win.show()
    # LLM 配置检查已延迟到运行时：用户点击"生成"时若 LLM 不可用，
    # worker 线程会自然报错并降级到规则引擎，不会在启动时弹窗干扰。
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
