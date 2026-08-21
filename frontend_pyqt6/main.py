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

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPlainTextEdit, QPushButton, QLineEdit, QTabWidget,
    QMenuBar, QStatusBar, QMessageBox, QFileDialog, QProgressBar, QSlider,
    QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QDialogButtonBox, QListWidget, QCheckBox,
    QListWidgetItem, QInputDialog, QScrollArea,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QAction, QFont, QColor, QSyntaxHighlighter, QTextCharFormat, QPainter, QPen, QPainterPath

# ======================================================================
# i18n — lightweight translation layer
# ======================================================================
_LANG = None  # cached after first call

def _lang():
    global _LANG
    if _LANG is None:
        from vibedomuse import config as _cfg
        _LANG = _cfg.get_language()
    return _LANG

def _reload_lang():
    global _LANG
    from vibedomuse import config as _cfg
    _LANG = _cfg.get_language()

_T = {
    # Window / title
    "VibeDoMuse · AI Music Agent": "VibeDoMuse · AI 音乐创作 Agent",
    "VibeDoMuse · AI Music Agent (Natural Language → Knowledge Base → Score Generation)":
        "VibeDoMuse · AI 音乐创作 Agent（自然语言 → 知识库 → 乐谱生成）",

    # Menu — File
    "File": "文件",
    "Exit": "退出",

    # Menu — Theme
    "Theme": "主题",
    "Light": "浅色",
    "Dark": "暗色",

    # Menu — Settings
    "Settings": "设置",
    "LLM Settings": "LLM 设置",
    "Language": "语言",
    "English": "English",
    "Chinese": "中文",

    # Menu — Tools
    "Tools": "工具",
    "Template Browser (144 pieces)": "模板库浏览器（144 首）",
    "Mix Adjustment\u2026": "混音调整\u2026",

    # Left panel
    "Natural Language Description": "自然语言描述",
    "Placeholder_Example": "例如：来一首忧伤的 a 小调慢速钢琴曲\n"
                           "例如：我想要一首温柔的 C 大调钢琴伴奏，琶音风格，90 速度\n"
                           "例如：生成一段忧伤的 Dm 小调戏剧性三轨弦乐铺垫，脉冲织体\n"
                           "提示：加「循环」生成无缝循环 BGM；加「鼓」添加打击乐轨",
    "Generate Song": "生成歌曲",
    "Re-generate (same seed)": "同种子再生成",
    "Change Seed Variant": "换种子变体",
    "Layer Variation": "分层变奏",
    "Batch Variants\u2026": "批量变体\u2026",
    "Export\u2026": "导出\u2026",

    # Tabs
    "JSON Preview": "JSON 预览",
    "Piano Roll": "钢琴卷帘",
    "Log": "日志",

    # Player
    "Play": "试听",
    "Stop": "停止",
    "Loop": "循环",
    "Not generated yet": "尚未生成",
    "Loop playback: seamless background music loop": "循环播放：无缝循环 BGM 模式",

    # Status bar
    "KB items": "KB 项",
    "templates": "个模板",
    "Creating\u2026": "创作中\u2026",
    "Ready. Enter a description and click Generate.": "就绪。输入描述后点击生成歌曲。",

    # LLM Settings dialog
    "LLM Settings (plaintext in root config.ini)": "LLM 设置（明文存于根目录 config.ini）",
    "API Base URL": "API Base URL",
    "Model Name": "模型名称",
    "API Key": "API Key",
    "Timeout (s)": "超时(秒)",
    "Temperature": "Temperature",
    "Higher values make the model more creative/random. Lower values make it more deterministic. (0.0 - 2.0)":
        "值越高模型越随机/有创意，值越低越确定（0.0 - 2.0）",
    "Test Connection": "测试连接",
    "Save": "保存",
    "Cancel": "取消",
    "Connection OK": "连接成功",
    "Connection failed": "连接失败",
    "OK": "确定",
    "Settings saved. Restart required for some changes to take effect.":
        "设置已保存。部分更改需重启后生效。",

    # Template Browser dialog
    "Template Browser": "模板浏览器",
    "Filter\u2026": "过滤\u2026",
    "Preview": "预览",
    "Close": "关闭",
    "Filter templates by keyword\u2026": "按关键词过滤模板\u2026",
    "tracks": "音轨",
    "Generate from this template": "以该模板为基础生成",
    "No templates match.": "无匹配模板。",

    # Mix dialog
    "Mix Adjustment": "混音调整",
    "No score loaded yet.": "尚未加载乐谱。",
    "Mute": "静音",
    "Apply & Re-render": "应用并重新渲染",
    "Mix": "混音",
    "Volume": "音量",

    # Understanding dialog
    "Confirm AI Understanding": "确认 AI 理解",
    "The AI understands your request as follows. Confirm to proceed, or modify the description.":
        "AI 对您的请求理解如下。确认后继续生成，或修改描述。",
    "Confirm & Generate": "确认并生成",
    "Modify Description": "修改描述",

    # Generation status
    "Analysis complete\u2026": "分析完成\u2026",
    "Generating\u2026": "生成中\u2026",
    "Generated": "已生成",
    "Error": "错误",
    "Parse Preview": "解析预览",
    "Please enter a natural language description first.": "请先输入自然语言描述。",
    "Please generate a song first before exporting.": "请先生成歌曲，再导出。",
    "How many variants (2-8)?": "生成几个变体（2-8）？",

    # Log
    "LOG_CLEAR": "清除日志",
    "LOG_PREVIEW": "预览",
    "LOG_UNDERSTANDING": "AI 理解分析",
    "LOG_GENERATION": "生成",
}

def _(key):
    """Translate an English UI string to the current language.

    Returns the English string by default; returns the Chinese translation
    when the language is set to 'zh'.
    """
    if _lang() == "zh":
        return _T.get(key, key)
    return key


def set_language(lang):
    """Change the UI language at runtime."""
    from vibedomuse import config as _cfg
    _cfg.set_language(lang)
    _reload_lang()

# ---- locate project root and vibedomuse package ----
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from vibedomuse import agent, template_db, config  # noqa: E402


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
# JSON syntax highlighter
# ======================================================================
class JsonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent, theme="light"):
        super().__init__(parent)
        self._theme = theme
        self._rules = []
        self._build()

    def _fmt(self, color, bold=False):
        f = QTextCharFormat()
        f.setForeground(QColor(color))
        if bold:
            f.setFontWeight(QFont.Weight.Bold)
        return f

    def _build(self):
        if self._theme == "dark":
            key_c, str_c, num_c, bool_c = "#9cdcfe", "#ce9178", "#b5cea8", "#569cd6"
        else:
            key_c, str_c, num_c, bool_c = "#000000", "#000000", "#000000", "#000000"
        self._rules = [
            (r'"(?:\\.|[^"\\])*"(?=\s*:)', self._fmt(key_c, True)),
            (r'"(?:\\.|[^"\\])*"', self._fmt(str_c)),
            (r'\b-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b', self._fmt(num_c)),
            (r'\b(?:true|false|null)\b', self._fmt(bool_c)),
        ]

    def set_theme(self, theme):
        self._theme = theme
        self._build()
        self.rehighlight()

    def highlightBlock(self, text):
        import re
        for pattern, fmt in self._rules:
            for m in re.finditer(pattern, text):
                self.setFormat(m.start(), m.end() - m.start(), fmt)


class PianoRoll(QWidget):
    """Piano-roll style visualization of the generated score.

    Each track is rendered as a horizontal lane with the instrument name
    on the left. Notes are drawn as colored horizontal bars positioned
    by pitch (y-axis) and time (x-axis). Beat grid lines and beat
    numbers are shown for reference.

    Architecture:
      set_score()  calls  _parse_score()  →  stores structured data
      paintEvent() calls  _draw_grid() / _draw_notes() / _draw_labels()
    """

    _DUR_BEATS = {
        "whole": 4.0, "half": 2.0, "quarter": 1.0, "eighth": 0.5, "16th": 0.25,
        "32nd": 0.125, "64th": 0.0625, "half.": 3.0, "quarter.": 1.5, "eighth.": 0.75,
        "16th.": 0.375, "32nd.": 0.1875,
    }
    _TUP_F = {3: 2 / 3, 5: 4 / 5, 6: 4 / 6, 7: 4 / 7, 9: 8 / 9}
    # Track colors (distinct pastel hues)
    _TRACK_COLORS = [
        "#4A90D9", "#E67E22", "#2ECC71", "#E74C3C", "#9B59B6",
        "#1ABC9C", "#F39C12", "#3498DB", "#E91E63", "#00BCD4",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tracks_data = []    # [(instrument_name, [(beat, pitch, dur_str, velocity), ...])]
        self._total_beats = 1.0
        self._beat_width = 80
        self._note_min_height = 10   # min px height per note bar
        self._note_pitch_range = 48  # default visible pitch range (4 octaves)
        self._track_spacing = 8      # px gap between tracks
        self._left_margin = 100      # space for instrument label
        self._right_margin = 16
        self._top_margin = 32        # space for beat numbers
        self._min_pitch = 128
        self._max_pitch = 0
        self.setMinimumHeight(200)

    # ------------------------------------------------------------------
    # Data parsing
    # ------------------------------------------------------------------
    def _parse_score(self, score):
        """Extract track data from a score dict into structured internal format.

        Returns (tracks_data, total_beats, min_pitch, max_pitch).
        tracks_data is a list of (instrument_name, [(beat, pitch, dur_str, velocity), ...]).
        """
        tracks = (score or {}).get("tracks") or []
        tracks_data = []
        total = 0.0
        min_p = 128
        max_p = 0
        for tr in tracks:
            notes_data = []
            off = 0.0
            for n in (tr.get("notes") or []):
                if not isinstance(n, dict):
                    continue
                if n.get("ref") is not None:
                    off += 1.0
                    continue
                d = self._DUR_BEATS.get(n.get("duration"), 1.0)
                if n.get("tuplet") in self._TUP_F:
                    d *= self._TUP_F[n["tuplet"]]
                dur_str = n.get("duration", "quarter")
                vel = n.get("velocity", 80)
                if isinstance(n.get("chord"), list):
                    for p in n["chord"]:
                        if isinstance(p, int) and p > 0:
                            notes_data.append((off, p, dur_str, vel))
                            min_p = min(min_p, p)
                            max_p = max(max_p, p)
                elif isinstance(n.get("pitch"), int) and n["pitch"] > 0:
                    notes_data.append((off, n["pitch"], dur_str, vel))
                    min_p = min(min_p, n["pitch"])
                    max_p = max(max_p, n["pitch"])
                off += d
            total = max(total, off)
            tracks_data.append((str(tr.get("instrument", "")), notes_data))
        if min_p > max_p:
            min_p, max_p = 60, 72  # fallback C4-C5
        return tracks_data, max(1.0, total), min_p, max_p

    def set_score(self, score):
        """Parse a score dict and update the widget layout."""
        self._tracks_data, self._total_beats, self._min_pitch, self._max_pitch = self._parse_score(score)
        # Expand pitch range slightly for visual padding
        pr = max(16, self._max_pitch - self._min_pitch + 4)
        nph = max(self._note_min_height, int(pr * 1.0))
        track_h = nph * 2 + 16  # pitch range per track + padding
        content_w = self._left_margin + int(self._total_beats * self._beat_width) + self._right_margin
        content_h = (self._top_margin
                     + len(self._tracks_data) * (track_h + self._track_spacing)
                     + 20)
        self._note_pitch_range = nph
        self._track_height = track_h
        self.setMinimumSize(content_w, max(200, content_h))
        self.update()

    # ------------------------------------------------------------------
    # Paint
    # ------------------------------------------------------------------
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.fillRect(0, 0, self.width(), self.height(), QColor("#ffffff"))

        for ti, (inst_name, notes) in enumerate(self._tracks_data):
            track_top = self._top_margin + ti * (self._track_height + self._track_spacing)
            track_left = self._left_margin
            track_right = max(self.width(), self.minimumWidth()) - self._right_margin
            track_bottom = track_top + self._track_height

            self._draw_track_bg(p, ti, track_top, track_left, track_right, track_bottom, inst_name)
            self._draw_grid(p, track_top, track_left, track_right, track_bottom)
            self._draw_notes(p, ti, notes, track_top, track_left, track_right, track_bottom)
        p.end()

    # ------------------------------------------------------------------
    # Drawing primitives
    # ------------------------------------------------------------------
    def _draw_track_bg(self, p, ti, track_top, track_left, track_right, track_bottom, inst_name):
        """Draw the track background, instrument label, and pitch range markers."""
        # Alternating background
        bg = QColor("#F8F9FA") if ti % 2 == 0 else QColor("#FFFFFF")
        p.fillRect(int(track_left), int(track_top),
                   int(track_right - track_left), int(track_bottom - track_top), bg)

        # Instrument label
        label_font = QFont("Microsoft YaHei", 9)
        p.setFont(label_font)
        p.setPen(QColor("#333333"))
        p.drawText(4, int(track_top + 14), inst_name)

        # Pitch range labels (highest and lowest)
        pitch_font = QFont("Microsoft YaHei", 7)
        p.setFont(pitch_font)
        p.setPen(QColor("#999999"))
        p.drawText(4, int(track_top + 28), f"↑{self._midi_note_name(self._max_pitch)}")
        p.drawText(4, int(track_bottom - 4), f"↓{self._midi_note_name(self._min_pitch)}")

    @staticmethod
    def _midi_note_name(pitch):
        """Convert MIDI pitch to note name (e.g. 60 -> C4)."""
        names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        return f"{names[pitch % 12]}{pitch // 12 - 1}"

    def _draw_grid(self, p, track_top, track_left, track_right, track_bottom):
        """Draw vertical beat grid lines and beat numbers."""
        beat_font = QFont("Microsoft YaHei", 7)
        p.setFont(beat_font)
        for beat in range(0, int(self._total_beats) + 1):
            beat_ratio = beat / self._total_beats if self._total_beats > 0 else 0
            bx = track_left + int(beat_ratio * (track_right - track_left))
            # Beat number (only at top)
            p.setPen(QColor("#AAAAAA"))
            p.drawText(int(bx - 4), int(track_top - 4), str(beat))
            # Grid line
            is_bar = beat % 4 == 0
            p.setPen(QPen(QColor("#DDDDDD") if is_bar else QColor("#EEEEEE"), 1))
            p.drawLine(int(bx), int(track_top), int(bx), int(track_bottom))

    def _draw_notes(self, p, ti, notes, track_top, track_left, track_right, track_bottom):
        """Draw all notes as colored horizontal bars."""
        if not notes:
            return
        color = QColor(self._TRACK_COLORS[ti % len(self._TRACK_COLORS)])
        pr = max(1, self._max_pitch - self._min_pitch)
        for (beat, pitch, dur, vel) in notes:
            # Duration in pixels
            d = self._DUR_BEATS.get(dur, 1.0)
            beat_ratio = beat / self._total_beats if self._total_beats > 0 else 0
            dur_ratio = d / self._total_beats if self._total_beats > 0 else 0
            nx = track_left + int(beat_ratio * (track_right - track_left))
            nw = max(3, int(dur_ratio * (track_right - track_left)))
            # Pitch → y position (higher pitch = higher on screen)
            pitch_ratio = (pitch - self._min_pitch) / pr
            ny = track_bottom - int(pitch_ratio * (track_bottom - track_top)) - 4
            nh = max(4, int(self._note_pitch_range / pr))

            # Draw note bar with alpha based on velocity
            alpha = max(40, int(vel / 127 * 220))
            c = QColor(color)
            c.setAlpha(alpha)
            p.fillRect(int(nx), int(ny), int(nw), int(nh), c)
            # Border
            p.setPen(QPen(color, 1))
            p.drawRect(int(nx), int(ny), int(nw), int(nh))


# ======================================================================
# Worker threads
# ======================================================================
class AnalyzeWorker(QThread):
    """First-stage: sends user prompt to LLM for intent analysis."""
    finished = pyqtSignal(str)  # analysis text
    error = pyqtSignal(str)

    def __init__(self, text):
        super().__init__()
        self.text = text

    def run(self):
        try:
            analysis = agent.analyze(self.text)
            if analysis:
                self.finished.emit(analysis)
            else:
                self.error.emit("LLM analysis returned no result. Check your LLM configuration.")
        except Exception as e:
            self.error.emit(str(e))


class GenWorker(QThread):
    """Runs the Agent in the background; emits {kind, ...} results."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, text, seed=None, mode="llm", use_template=None, n=4, analysis=None):
        super().__init__()
        self.text = text
        self.seed = seed
        self.mode = mode
        self.use_template = use_template
        self.n = n
        self.analysis = analysis

    def run(self):
        try:
            if self.mode == "llm_v2":
                self.log.emit("Stage 2: Generating score with original prompt + understanding...")
                res = agent.run_llm_v2(self.text, self.analysis, seed=self.seed)
                self.finished.emit({"kind": "single", "data": res})
                return
            if self.mode == "variants":
                self.log.emit(f"Generating {self.n} variants (rule engine, different seeds)...")
                items = agent.run_variants(self.text, n=self.n, seed=self.seed)
                self.finished.emit({"kind": "variants", "items": items})
                return
            if self.mode == "layers":
                self.log.emit("Generating calm / tense layers of the same theme...")
                data = agent.run_layers(self.text, seed=self.seed)
                self.finished.emit({"kind": "layers", "data": data})
                return
            if self.mode == "rule":
                self.log.emit("Rule engine composing...")
                res = agent.run(self.text, seed=self.seed, use_template=self.use_template)
                self.finished.emit({"kind": "single", "data": res})
                return
            self.log.emit("Step 1: Retrieving local knowledge base (JSON spec sections + template examples)...")
            res = agent.run_llm(self.text, seed=self.seed)
            self.log.emit("Step 2: LLM writes Do-muse JSON with knowledge base, local validation...")
            self.log.emit("Step 3: Rendering MIDI / WAV...")
            self.finished.emit({"kind": "single", "data": res})
        except Exception as e:  # noqa: BLE001
            self.error.emit(str(e))


class ExportWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, score, artifacts, out_path, fmt):
        super().__init__()
        self.score = score
        self.artifacts = artifacts
        self.out_path = out_path
        self.fmt = fmt

    def run(self):
        try:
            from vibedomuse import renderer as rnd
            rnd.export_artifacts(self.score, self.artifacts, self.out_path, self.fmt)
            self.finished.emit(self.out_path)
        except Exception as e:  # noqa: BLE001
            self.error.emit(str(e))


class RenderWorker(QThread):
    """Re-renders an edited score (e.g. after mixing) in the background."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, score, name):
        super().__init__()
        self.score = score
        self.name = name

    def run(self):
        try:
            from vibedomuse import renderer as rnd
            rendered = rnd.render(self.score, self.name)
            self.finished.emit({"score": self.score, "generated": rendered})
        except Exception as e:  # noqa: BLE001
            self.error.emit(str(e))


# ======================================================================
# Dialogs
# ======================================================================
class LlmSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("LLM Settings (plaintext in root config.ini)"))
        self.setMinimumWidth(480)
        s = config.get_llm_settings()

        form = QFormLayout(self)
        self.ed_base = QLineEdit(s["base_url"])
        self.ed_model = QLineEdit(s["model"])
        self.ed_key = QLineEdit(s["api_key"])
        self.ed_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.sp_timeout = QSpinBox()
        self.sp_timeout.setRange(3, 120)
        self.sp_timeout.setValue(s["timeout"])
        self.sp_temp = QDoubleSpinBox()
        self.sp_temp.setRange(0.0, 2.0)
        self.sp_temp.setSingleStep(0.1)
        self.sp_temp.setDecimals(1)
        self.sp_temp.setValue(s["temperature"])
        self.sp_temp.setToolTip("Higher values make the model more creative/random. Lower values make it more deterministic. (0.0 - 2.0)")
        form.addRow(_("API Base URL"), self.ed_base)
        form.addRow(_("Model Name"), self.ed_model)
        form.addRow(_("API Key"), self.ed_key)
        form.addRow(_("Timeout (s)"), self.sp_timeout)
        form.addRow(_("Temperature"), self.sp_temp)

        btns = QDialogButtonBox()
        self.btn_test = btns.addButton(_("Test Connection"), QDialogButtonBox.ButtonRole.ActionRole)
        self.btn_test.clicked.connect(self._test)
        self.btn_save = btns.addButton(_("Save"), QDialogButtonBox.ButtonRole.AcceptRole)
        self.btn_save.clicked.connect(self._save)
        self.btn_cancel = btns.addButton(_("Cancel"), QDialogButtonBox.ButtonRole.RejectRole)
        self.btn_cancel.clicked.connect(self.reject)
        form.addRow(btns)

    def _values(self):
        return {
            "base_url": self.ed_base.text().strip(),
            "model": self.ed_model.text().strip(),
            "api_key": self.ed_key.text().strip(),
            "timeout": str(self.sp_timeout.value()),
            "temperature": str(self.sp_temp.value()),
        }

    def _test(self):
        from vibedomuse import llm_client
        v = self._values()
        ok = llm_client.is_available(
            base_url=v["base_url"] or None,
            model=v["model"] or None,
            api_key=v["api_key"] or None,
        )
        QMessageBox.information(
            self, "测试结果",
            "连接成功，模型可用 ✔" if ok else "连接失败：端点不可达或模型不可用 ✘",
        )

    def _save(self):
        cfg = config.load_config()
        cfg["llm"].update(self._values())
        config.save_config(cfg)
        QMessageBox.information(self, "已保存", f"配置已写入：\n{config.CONFIG_PATH}")
        self.accept()


class UnderstandingDialog(QDialog):
    """Shows the LLM's understanding of the user's request and asks for confirmation."""

    def __init__(self, analysis, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Understanding Confirmation")
        self.setMinimumSize(520, 380)
        self.setStyleSheet("""
            QDialog { background-color: #ffffff; }
            QLabel { color: #000000; }
            QTextEdit { background-color: #f5f5f5; color: #212121; border: 1px solid #e0e0e0; border-radius: 4px; }
            QPushButton { background-color: #1976d2; color: #ffffff; border: none;
                          padding: 8px 24px; border-radius: 4px; font-size: 14px; }
            QPushButton:hover { background-color: #1565c0; }
            QPushButton#secondary { background-color: #e0e0e0; color: #212121; }
            QPushButton#secondary:hover { background-color: #bdbdbd; }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("The LLM has analyzed your request. Here is its understanding:")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)

        self.analysis_view = QTextEdit()
        self.analysis_view.setPlainText(analysis)
        self.analysis_view.setReadOnly(True)
        self.analysis_view.setMinimumHeight(200)
        layout.addWidget(self.analysis_view, 1)

        hint = QLabel("If the understanding is correct, click \"Confirm & Generate\" to proceed.\n"
                       "Otherwise, click \"Modify Description\" to refine your request.")
        hint.setStyleSheet("color: #666666; font-size: 12px;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        btn_row = QHBoxLayout()
        self.btn_confirm = QPushButton("Confirm & Generate")
        self.btn_confirm.clicked.connect(self.accept)
        self.btn_modify = QPushButton("Modify Description")
        self.btn_modify.setObjectName("secondary")
        self.btn_modify.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_modify)
        btn_row.addWidget(self.btn_confirm)
        layout.addLayout(btn_row)


class TemplateBrowserDialog(QDialog):
    """Browse the 144-piece template library and pick one as a base."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Template Browser"))
        self.resize(680, 520)
        self.selected = None
        try:
            self._all = template_db.all_templates()
        except Exception:
            self._all = []
        v = QVBoxLayout(self)
        self.ed_filter = QLineEdit()
        self.ed_filter.setPlaceholderText(_("Filter templates by keyword\u2026"))
        self.ed_filter.textChanged.connect(self._refresh)
        v.addWidget(self.ed_filter)
        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self._pick)
        v.addWidget(self.list, 1)
        btns = QDialogButtonBox()
        ok = btns.addButton(_("Generate from this template"), QDialogButtonBox.ButtonRole.AcceptRole)
        ok.clicked.connect(self._pick_current)
        cancel = btns.addButton(_("Cancel"), QDialogButtonBox.ButtonRole.RejectRole)
        cancel.clicked.connect(self.reject)
        v.addWidget(btns)
        self._refresh()

    def _refresh(self):
        self.list.clear()
        f = self.ed_filter.text().strip().lower()
        for r in self._all:
            hay = " ".join([r.get("name", ""), r.get("title", ""), r.get("mood", ""),
                            r.get("instrument", "") or "", r.get("category", ""),
                            str(r.get("tempo_bpm", ""))]).lower()
            if f and f not in hay:
                continue
            item = QListWidgetItem(
                f"{r.get('name','')} ｜ {r.get('mood','?')} ｜ {r.get('tempo_bpm','?')}BPM ｜ "
                f"{r.get('key_signature','?')} ｜ {r.get('category','')} ｜ {r.get('track_count',0)} {_('tracks')}")
            item.setData(Qt.ItemDataRole.UserRole, r.get("name"))
            self.list.addItem(item)

    def _pick_current(self):
        cur = self.list.currentItem()
        if cur:
            self._pick(cur)

    def _pick(self, item):
        self.selected = item.data(Qt.ItemDataRole.UserRole)
        self.accept()


class MixDialog(QDialog):
    """Per-track velocity scaling + mute, re-rendered on accept."""

    def __init__(self, score, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Mix Adjustment"))
        self.setMinimumWidth(460)
        self._score = score
        self._sliders = []
        self._mutes = []
        v = QVBoxLayout(self)
        tracks = (score or {}).get("tracks") or []
        if not tracks:
            v.addWidget(QLabel(_("No score loaded yet.")))
        for i, tr in enumerate(tracks):
            name = str(tr.get("instrument", "?") or "?")
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{i + 1}. {name}"))
            s = QSlider(Qt.Orientation.Horizontal)
            s.setRange(0, 200)
            s.setValue(100)
            s.setFixedWidth(220)
            m = QCheckBox(_("Mute"))
            row.addWidget(s, 1)
            row.addWidget(m)
            v.addLayout(row)
            self._sliders.append(s)
            self._mutes.append(m)
        btns = QDialogButtonBox()
        apply = btns.addButton(_("Apply & Re-render"), QDialogButtonBox.ButtonRole.AcceptRole)
        apply.clicked.connect(self.accept)
        cancel = btns.addButton(_("Cancel"), QDialogButtonBox.ButtonRole.RejectRole)
        cancel.clicked.connect(self.reject)
        v.addWidget(btns)

    def result_score(self):
        import copy
        score = copy.deepcopy(self._score or {})
        tracks = score.get("tracks") or []
        for i, tr in enumerate(tracks):
            if i >= len(self._sliders):
                break
            pct = self._sliders[i].value() / 100.0
            muted = self._mutes[i].isChecked()
            if muted:
                # Mute: clear all notes (more reliable than velocity=0)
                tr["notes"] = []
            else:
                for n in tr.get("notes", []):
                    if not isinstance(n, dict):
                        continue
                    old_v = n.get("velocity", 80)
                    if isinstance(old_v, int):
                        n["velocity"] = max(1, min(127, int(old_v * pct)))
        return score


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
        self._setup_player()

        self._build_ui()
        self._apply_theme(self.theme)
        self._refresh_stats()

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

        left_v.addWidget(QLabel(_("Natural Language Description")))
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
        self._set_busy(True)
        self.log_view.clear()
        self.log_view.appendPlainText("Stage 1: Analyzing your request (LLM considers spec sections, templates)...")
        self._analyze_worker = AnalyzeWorker(text)
        self._analyze_worker.finished.connect(self._on_analyze_finished)
        self._analyze_worker.error.connect(self._on_worker_error)
        self._analyze_worker.start()

    def _on_analyze_finished(self, analysis_text):
        self._set_busy(False)
        self.log_view.appendPlainText("LLM understanding received. Showing confirmation dialog...")
        dialog = UnderstandingDialog(analysis_text, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # User confirmed - proceed to Stage 2 generation
            self._set_busy(True)
            self._worker = GenWorker(
                self.nl_input.toPlainText().strip(),
                mode="llm_v2",
                analysis=analysis_text
            )
            self._worker.log.connect(self.log_view.appendPlainText)
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
        self._worker = GenWorker(text, seed=seed, mode=mode, use_template=use_template, n=n)
        self._worker.log.connect(self.log_view.appendPlainText)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.error.connect(self._on_worker_error)
        self._worker.start()

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
        self.seed_label.setText(f"Seed: {self._last_seed}")
        self.btn_same_seed.setEnabled(self._last_seed is not None)
        gp = res.get("generated", {})
        self._cache_artifacts = gp
        self._wav_bytes = _read_bytes(gp.get("wav_path"))
        self._midi_bytes = _read_bytes(gp.get("midi_path"))
        self._json_text = _read_text(gp.get("json_path"))
        self.btn_export.setEnabled(True)
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
        self.log_view.appendPlainText("✔ 混音后重新渲染完成")
        self._load_result(res)

    def _on_worker_error(self, msg):
        self._set_busy(False)
        self.play_status.setText("生成失败")
        self.log_view.appendPlainText("✘ 错误：" + msg)
        QMessageBox.critical(self, "生成失败", msg)

    # ---------- export ----------
    _EXPORT_FILTERS = (
        "MusicXML (*.mxl);;MIDI (*.mid);;WAV (*.wav);;MP3 (*.mp3);;FLAC (*.flac);;"
        "OGG (*.ogg);;LilyPond (*.ly);;JSON (*.json)"
    )

    def _on_export(self):
        if not self._last_generated or not self._cache_artifacts:
            QMessageBox.warning(self, _("Export\u2026"), _("Please generate a song first before exporting."))
            return
        base = os.path.splitext(self._cache_artifacts.get("json_file", "piece"))[0]
        default_path = os.path.join(os.path.expanduser("~"), base + ".mxl")
        path, selected = QFileDialog.getSaveFileName(
            self, "Export Song (choose location and format)", default_path, self._EXPORT_FILTERS
        )
        if not path:
            return
        m = re.search(r"\*\.(\w+)", selected or "")
        fmt = m.group(1).lower() if m else "mxl"
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
        QMessageBox.information(self, "Export Complete", "Exported to:\n" + path)

    def _on_export_error(self, msg):
        self.btn_export.setEnabled(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.log_view.appendPlainText("Export failed: " + msg)
        self.status_bar.showMessage("Export failed")
        QMessageBox.critical(self, "Export Error", msg)

    # ---------- playback ----------
    def _set_play_ui(self, playing):
        self.btn_play.setEnabled(bool(self._current_wav) and os.path.exists(self._current_wav or ""))
        self.play_slider.setEnabled(playing)
        if not playing:
            self.btn_stop.setEnabled(False)
            self.play_slider.setValue(0)
            self.time_label.setText("0:00 / 0:00")
            if self._current_wav:
                self.play_status.setText(f"Ready: {os.path.basename(self._current_wav)}")
        else:
            self.btn_stop.setEnabled(True)
            self.play_status.setText("Playing...")

    def _play(self):
        if not self._player or not self._current_wav or not os.path.exists(self._current_wav):
            QMessageBox.warning(self, "Playback", "No audio available. Please generate a song first.")
            return
        self._player.setSource(QUrl.fromLocalFile(self._current_wav))
        self._player.play()
        self._set_play_ui(True)

    def _stop(self):
        if self._player:
            self._player.stop()
        self._set_play_ui(False)
        self.play_status.setText(f"已停止：{os.path.basename(self._current_wav or '')}")


def main():
    app = QApplication(sys.argv)
    win = VibeDoMuse()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
