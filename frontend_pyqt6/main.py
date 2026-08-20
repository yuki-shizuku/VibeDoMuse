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
    QDialog, QFormLayout, QSpinBox, QDialogButtonBox, QListWidget, QCheckBox,
    QListWidgetItem, QInputDialog,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QAction, QFont, QColor, QSyntaxHighlighter, QTextCharFormat, QPainter

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


# ======================================================================
# Piano roll visualization
# ======================================================================
_DUR_Q = {
    "whole": 4.0, "half": 2.0, "quarter": 1.0, "eighth": 0.5, "16th": 0.25,
    "32nd": 0.125, "64th": 0.0625, "half.": 3.0, "quarter.": 1.5, "eighth.": 0.75,
    "16th.": 0.375, "32nd.": 0.1875,
}
_TUP_F = {3: 2 / 3, 5: 4 / 5, 6: 4 / 6, 7: 4 / 7, 9: 8 / 9}
_TRACK_COLORS = [(25, 118, 210), (214, 83, 126), (29, 158, 117), (186, 117, 23), (90, 92, 255)]


class PianoRoll(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._notes = []      # (start_beat, dur_beats, pitch, track_idx)
        self._tracks = []
        self._total_beats = 1.0
        self._min_pitch, self._max_pitch = 24, 96
        self.setMinimumHeight(280)

    def set_score(self, score):
        self._notes = []
        self._tracks = []
        self._total_beats = 1.0
        if not score:
            self.update()
            return
        tracks = score.get("tracks") or []
        total = 0.0
        for ti, tr in enumerate(tracks):
            off = 0.0
            for n in (tr.get("notes") or []):
                if not isinstance(n, dict):
                    continue
                if n.get("ref") is not None:
                    off += 1.0
                    continue
                d = _DUR_Q.get(n.get("duration"), 1.0)
                if n.get("tuplet") in _TUP_F:
                    d *= _TUP_F[n["tuplet"]]
                if isinstance(n.get("chord"), list):
                    for p in n["chord"]:
                        if isinstance(p, int) and p > 0:
                            self._notes.append((off, d, p, ti))
                elif isinstance(n.get("pitch"), int) and n["pitch"] > 0:
                    self._notes.append((off, d, n["pitch"], ti))
                off += d
            total = max(total, off)
        self._tracks = [str(t.get("instrument", "")) for t in tracks]
        self._total_beats = max(1.0, total)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        w, h = self.width(), self.height()
        pad_l, pad_r, pad_t, pad_b = 44, 12, 14, 18
        pw = w - pad_l - pad_r
        ph = h - pad_t - pad_b
        pmin, pmax = self._min_pitch, self._max_pitch
        span = max(1, pmax - pmin)
        beats = max(1.0, self._total_beats)
        bg = QColor("#ffffff") if self.palette().window().color().lightness() > 128 else QColor("#1a1a1a")
        p.fillRect(0, 0, w, h, bg)
        grid_c = QColor("#e0e0e0" if bg.lightness() > 128 else "#383838")
        text_c = QColor("#000000" if bg.lightness() > 128 else "#b0bec5")

        def x(b):
            return pad_l + b / beats * pw

        def y(pitch):
            return pad_t + (pmax - pitch) / span * ph

        # measure/beat grid
        p.setPen(grid_c)
        step = 0.5
        b = 0.0
        while b <= beats + 1e-9:
            p.drawLine(int(x(b)), pad_t, int(x(b)), h - pad_b)
            b += step
        # pitch lines at C octaves
        pc = pmin + (4 - (pmin % 12)) % 12
        p.setPen(grid_c)
        while pc <= pmax:
            p.drawLine(pad_l, int(y(pc)), w - pad_r, int(y(pc)))
            pc += 12
        # note rects
        p.setPen(Qt.PenStyle.NoPen)
        for (sb, dur, pitch, ti) in self._notes:
            if not (pmin <= pitch <= pmax):
                continue
            c = _TRACK_COLORS[ti % len(_TRACK_COLORS)]
            col = QColor(*c)
            p.setBrush(col)
            p.drawRect(int(x(sb)), int(y(pitch)), max(2, int(x(sb + dur) - x(sb))), max(3, int(ph / span) - 1))
        # pitch labels (C octaves)
        p.setPen(text_c)
        p.setFont(QFont("Consolas", 9))
        pc = pmin + (4 - (pmin % 12)) % 12
        while pc <= pmax:
            octave = pc // 12 - 1
            p.drawText(2, int(y(pc)) + 4, f"C{octave}")
            pc += 12
        # legend
        leg_y = 4
        p.setFont(QFont("Microsoft YaHei", 9))
        for ti, name in enumerate(self._tracks):
            col = QColor(*_TRACK_COLORS[ti % len(_TRACK_COLORS)])
            p.setBrush(col)
            p.drawRect(8, leg_y, 10, 10)
            p.setPen(text_c)
            p.drawText(22, leg_y + 9, name[:18])
            leg_y += 16
            if leg_y > pad_t - 6:
                break
        p.end()


# ======================================================================
# Worker threads
# ======================================================================
class GenWorker(QThread):
    """Runs the Agent in the background; emits {kind, ...} results."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, text, seed=None, mode="llm", use_template=None, n=4):
        super().__init__()
        self.text = text
        self.seed = seed
        self.mode = mode
        self.use_template = use_template
        self.n = n

    def run(self):
        try:
            if self.mode == "variants":
                self.log.emit(f"▶ 批量生成 {self.n} 个变体（规则引擎，不同种子）…")
                items = agent.run_variants(self.text, n=self.n, seed=self.seed)
                self.finished.emit({"kind": "variants", "items": items})
                return
            if self.mode == "layers":
                self.log.emit("▶ 生成同主题「平静层 / 紧张层」…")
                data = agent.run_layers(self.text, seed=self.seed)
                self.finished.emit({"kind": "layers", "data": data})
                return
            if self.mode == "rule":
                self.log.emit("▶ 规则引擎直接合成…")
                res = agent.run(self.text, seed=self.seed, use_template=self.use_template)
                self.finished.emit({"kind": "single", "data": res})
                return
            self.log.emit("▶ ① 检索本地知识库（JSON 规范小节 + 真实模板示例）…")
            res = agent.run_llm(self.text, seed=self.seed)
            self.log.emit("✔ ② LLM 借助知识库撰写 Do-muse JSON，本地校验…")
            self.log.emit("✔ ③ 渲染 MIDI / WAV…")
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
        self.setWindowTitle("LLM 设置（明文存于根目录 config.ini）")
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
        form.addRow("API Base URL", self.ed_base)
        form.addRow("模型名称", self.ed_model)
        form.addRow("API Key", self.ed_key)
        form.addRow("超时(秒)", self.sp_timeout)

        btns = QDialogButtonBox()
        self.btn_test = btns.addButton("测试连接", QDialogButtonBox.ButtonRole.ActionRole)
        self.btn_test.clicked.connect(self._test)
        self.btn_save = btns.addButton("保存", QDialogButtonBox.ButtonRole.AcceptRole)
        self.btn_save.clicked.connect(self._save)
        self.btn_cancel = btns.addButton("取消", QDialogButtonBox.ButtonRole.RejectRole)
        self.btn_cancel.clicked.connect(self.reject)
        form.addRow(btns)

    def _values(self):
        return {
            "base_url": self.ed_base.text().strip(),
            "model": self.ed_model.text().strip(),
            "api_key": self.ed_key.text().strip(),
            "timeout": str(self.sp_timeout.value()),
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


class TemplateBrowserDialog(QDialog):
    """Browse the 144-piece template library and pick one as a base."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("模板库浏览器（144 首）")
        self.resize(680, 520)
        self.selected = None
        try:
            self._all = template_db.all_templates()
        except Exception:
            self._all = []
        v = QVBoxLayout(self)
        self.ed_filter = QLineEdit()
        self.ed_filter.setPlaceholderText("按名称 / 情绪 / 乐器 / 类别 / 速度过滤…")
        self.ed_filter.textChanged.connect(self._refresh)
        v.addWidget(self.ed_filter)
        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self._pick)
        v.addWidget(self.list, 1)
        btns = QDialogButtonBox()
        ok = btns.addButton("以该模板为基础生成", QDialogButtonBox.ButtonRole.AcceptRole)
        ok.clicked.connect(self._pick_current)
        cancel = btns.addButton("取消", QDialogButtonBox.ButtonRole.RejectRole)
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
                f"{r.get('key_signature','?')} ｜ {r.get('category','')} ｜ {r.get('track_count',0)}轨")
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
        self.setWindowTitle("混音调整（按轨力度/静音，接受后重新渲染）")
        self.setMinimumWidth(460)
        self._score = score
        self._sliders = []
        self._mutes = []
        v = QVBoxLayout(self)
        tracks = (score or {}).get("tracks") or []
        if not tracks:
            v.addWidget(QLabel("当前没有可混音的乐谱。"))
        for i, tr in enumerate(tracks):
            name = str(tr.get("instrument", "?") or "?")
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{i + 1}. {name}"))
            s = QSlider(Qt.Orientation.Horizontal)
            s.setRange(0, 200)
            s.setValue(100)
            s.setFixedWidth(220)
            m = QCheckBox("静音")
            row.addWidget(s, 1)
            row.addWidget(m)
            v.addLayout(row)
            self._sliders.append(s)
            self._mutes.append(m)
        btns = QDialogButtonBox()
        apply = btns.addButton("应用并重新渲染", QDialogButtonBox.ButtonRole.AcceptRole)
        apply.clicked.connect(self.accept)
        cancel = btns.addButton("取消", QDialogButtonBox.ButtonRole.RejectRole)
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
            for n in tr.get("notes", []):
                if not isinstance(n, dict):
                    continue
                if muted:
                    n["velocity"] = 0
                elif "velocity" in n and isinstance(n["velocity"], int):
                    n["velocity"] = max(1, min(127, int(n["velocity"] * pct)))
        return score


# ======================================================================
# Main window
# ======================================================================
class VibeDoMuse(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VibeDoMuse · AI 音乐创作 Agent")
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
        self._history = []               # list of dicts
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
        file_menu = mb.addMenu("文件")
        act_exit = QAction("退出", self)
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        theme_menu = mb.addMenu("主题")
        act_light = QAction("浅色", self)
        act_light.triggered.connect(lambda: self._apply_theme("light"))
        act_dark = QAction("暗色", self)
        act_dark.triggered.connect(lambda: self._apply_theme("dark"))
        theme_menu.addAction(act_light)
        theme_menu.addAction(act_dark)

        settings_menu = mb.addMenu("设置")
        act_llm = QAction("LLM 设置", self)
        act_llm.triggered.connect(self._llm_settings)
        settings_menu.addAction(act_llm)

        tools_menu = mb.addMenu("工具")
        act_tpl = QAction("模板库浏览器（144 首）", self)
        act_tpl.triggered.connect(self._open_template_browser)
        tools_menu.addAction(act_tpl)
        act_mix = QAction("混音调整…", self)
        act_mix.triggered.connect(self._open_mix)
        tools_menu.addAction(act_mix)

        central = QWidget()
        self.setCentralWidget(central)
        root_v = QVBoxLayout(central)

        title = QLabel("VibeDoMuse · AI 音乐创作 Agent（自然语言 → 知识库 → 乐谱生成）")
        title.setStyleSheet("font-size:16px; font-weight:bold; padding:4px 2px;")
        root_v.addWidget(title)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        root_v.addWidget(splitter, 1)

        # ---- left panel ----
        left = QWidget()
        left_v = QVBoxLayout(left)
        left_v.setContentsMargins(4, 4, 4, 4)

        left_v.addWidget(QLabel("自然语言描述"))
        self.nl_input = QTextEdit()
        self.nl_input.setPlaceholderText(
            "例如：来一首忧伤的 a 小调慢速钢琴曲\n"
            "例如：我想要一首温柔的 C 大调钢琴伴奏，琶音风格，90 速度\n"
            "例如：生成一段忧伤的 Dm 小调戏剧性三轨弦乐铺垫，脉冲织体\n"
            "提示：加「循环」生成无缝循环 BGM；加「鼓」添加打击乐轨"
        )
        self.nl_input.setMinimumHeight(110)
        left_v.addWidget(self.nl_input, 1)

        row1 = QHBoxLayout()
        self.btn_generate = QPushButton("生成歌曲")
        self.btn_generate.clicked.connect(self._on_generate)
        row1.addWidget(self.btn_generate, 1)
        self.btn_same_seed = QPushButton("同种子再生成")
        self.btn_same_seed.setObjectName("secondary")
        self.btn_same_seed.setEnabled(False)
        self.btn_same_seed.clicked.connect(self._on_same_seed)
        row1.addWidget(self.btn_same_seed, 1)
        left_v.addLayout(row1)

        row2 = QHBoxLayout()
        self.btn_variant = QPushButton("换种子变体")
        self.btn_variant.setObjectName("secondary")
        self.btn_variant.clicked.connect(self._on_variant)
        row2.addWidget(self.btn_variant, 1)
        self.btn_layers = QPushButton("分层变奏")
        self.btn_layers.setObjectName("secondary")
        self.btn_layers.clicked.connect(self._on_layers)
        row2.addWidget(self.btn_layers, 1)
        left_v.addLayout(row2)

        row3 = QHBoxLayout()
        self.btn_batch = QPushButton("批量变体…")
        self.btn_batch.setObjectName("secondary")
        self.btn_batch.clicked.connect(self._on_batch)
        row3.addWidget(self.btn_batch, 1)
        self.btn_export = QPushButton("导出…")
        self.btn_export.setEnabled(False)
        self.btn_export.clicked.connect(self._on_export)
        row3.addWidget(self.btn_export, 1)
        left_v.addLayout(row3)

        self.progress = QProgressBar()
        self.progress.setTextVisible(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        left_v.addWidget(self.progress)

        self.seed_label = QLabel("种子：-")
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
        self.history_list = QListWidget()
        self.history_list.currentRowChanged.connect(self._on_history_row)
        self.log_view = QPlainTextEdit()
        self.log_view.setObjectName("logConsole")
        self.log_view.setReadOnly(True)
        self.tabs.addTab(self.json_view, "JSON 预览")
        self.tabs.addTab(self.roll_view, "钢琴卷帘")
        self.tabs.addTab(self.history_list, "历史")
        self.tabs.addTab(self.log_view, "日志")
        right_v.addWidget(self.tabs, 1)

        play_row = QHBoxLayout()
        self.btn_play = QPushButton("▶ 试听")
        self.btn_play.clicked.connect(self._play)
        self.btn_play.setEnabled(False)
        self.btn_stop = QPushButton("■ 停止")
        self.btn_stop.setObjectName("stopButton")
        self.btn_stop.clicked.connect(self._stop)
        self.btn_stop.setEnabled(False)
        self.chk_loop = QCheckBox("循环")
        self.chk_loop.setToolTip("无缝循环播放（生成结果含 loop 标记时自动开启）")
        self.play_status = QLabel("尚未生成")
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
                f"知识库：{st['total']} 首模板 + JSON 规范 37 节 ｜ LLM 配置见 设置 → LLM 设置"
            )
        except Exception as e:  # noqa: BLE001
            self.status_bar.showMessage(f"知识库加载失败：{e}")

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
            self.status_bar.showMessage("Agent 正在检索知识库并创作中…")
        else:
            self.progress.setRange(0, 100)
            self.progress.setValue(100)
            self._refresh_stats()

    def _llm_settings(self):
        dlg = LlmSettingsDialog(self)
        dlg.exec()

    def _open_template_browser(self):
        dlg = TemplateBrowserDialog(self)
        if dlg.exec() and dlg.selected:
            self._set_busy(True)
            text = self.nl_input.toPlainText().strip()
            if not text:
                text = "以此模板为基础创作一首同风格的曲子"
            self._run_agent(text, mode="rule", use_template=dlg.selected)

    def _open_mix(self):
        if not self._last_generated or not self._last_generated.get("score"):
            QMessageBox.warning(self, "提示", "请先生成歌曲，再调整混音。")
            return
        dlg = MixDialog(self._last_generated.get("score"), self)
        if dlg.exec():
            score = dlg.result_score()
            self._set_busy(True)
            self.log_view.appendPlainText("▶ 重新渲染混音后的乐谱…")
            self._render_worker = RenderWorker(score, "mixed_" + str(self._last_generated.get("seed", 0)))
            self._render_worker.finished.connect(self._on_render_done)
            self._render_worker.error.connect(self._on_worker_error)
            self._render_worker.start()

    def _on_generate(self):
        text = self.nl_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "提示", "请先输入自然语言描述。")
            return
        self._run_agent(text, mode="llm")

    def _on_same_seed(self):
        text = self.nl_input.toPlainText().strip() or (self._last_generated or {}).get("text", "")
        if not text:
            QMessageBox.warning(self, "提示", "请先输入自然语言描述。")
            return
        self._run_agent(text, mode="llm", seed=self._last_seed)

    def _on_variant(self):
        text = self.nl_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "提示", "请先输入自然语言描述。")
            return
        self._run_agent(text, mode="rule")

    def _on_layers(self):
        text = self.nl_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "提示", "请先输入自然语言描述。")
            return
        self._run_agent(text, mode="layers")

    def _on_batch(self):
        text = self.nl_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "提示", "请先输入自然语言描述。")
            return
        n, ok = QInputDialog.getInt(self, "批量变体", "生成几个变体（2-8）？", 4, 2, 8, 1)
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
            self.log_view.appendPlainText(f"✔ 批量完成：{len(items)} 个变体")
            for it in items:
                self._push_history(it)
                self.log_view.appendPlainText(
                    f"  · #{it.get('variant')} 种子 {it.get('seed')} ｜ {it.get('summary', '')} ｜ "
                    f"{it.get('elapsed_sec', '?')}s")
            if items:
                self._load_result(items[0])
                self.status_bar.showMessage(f"批量生成完成（{len(items)} 个变体，见「历史」）")
            return
        if kind == "layers":
            data = payload.get("data") or {}
            layers = data.get("layers") or []
            self.log_view.appendPlainText("✔ 分层变奏完成：")
            for lr in layers:
                self._push_history(lr)
                self.log_view.appendPlainText(
                    f"  · {lr.get('layer_label')}（{lr.get('layer')}）种子 {lr.get('seed')} ｜ {lr.get('summary', '')}")
            if layers:
                self._load_result(layers[0])
                self.status_bar.showMessage("分层变奏完成（平静层/紧张层，见「历史」）")
            return
        res = payload.get("data") or {}
        self._load_result(res)

    def _load_result(self, res):
        self._last_generated = res
        self._last_seed = res.get("seed")
        self.seed_label.setText(f"种子：{self._last_seed}")
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
        if wav_rel:
            abs_wav = wav_rel if os.path.isabs(wav_rel) else os.path.join(ROOT, wav_rel)
            self._current_wav = abs_wav
            self.btn_play.setEnabled(os.path.exists(abs_wav))
        else:
            self._current_wav = None
            self.btn_play.setEnabled(False)
        self._set_play_ui(False)
        cached = "（缓存命中）" if gp.get("cached") else ""
        loop_s = "｜循环" if isinstance(res.get("score"), dict) and res["score"].get("loop") else ""
        self.play_status.setText(
            f"已生成{cached}：{gp.get('wav_file','')}（{res.get('elapsed_sec','?')}s{loop_s}）")
        method = res.get("method", "llm")
        if method == "llm":
            self.log_view.appendPlainText("✔ 创作方式：LLM + 本地知识库")
            if res.get("llm_warnings"):
                self.log_view.appendPlainText("  ⚠ 校验提示：" + "；".join(res["llm_warnings"][:3]))
        elif method == "fallback":
            self.log_view.appendPlainText("⚠ 已回退规则引擎：" + (res.get("llm_error") or "未知原因"))
        elif method == "layers":
            self.log_view.appendPlainText("✔ 创作方式：分层变奏（规则引擎）")
        else:
            self.log_view.appendPlainText("✔ 创作方式：规则引擎")
        ks = res.get("knowledge_sections")
        if ks:
            self.log_view.appendPlainText("  参考规范小节：" + " | ".join(ks[:4]))
        ke = res.get("knowledge_examples")
        if ke:
            self.log_view.appendPlainText("  参考模板示例：" + " | ".join(ke[:2]))
        self.log_view.appendPlainText(
            f"\n✔ 完成｜类别：{res.get('category_cn','')}｜种子：{res.get('seed','')}｜"
            f"耗时：{res.get('elapsed_sec','?')}s")
        self.status_bar.showMessage(f"生成成功：{gp.get('wav_file','')}")
        self._push_history(res)

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

    # ---------- history ----------
    def _push_history(self, res):
        self._history.append(res)
        gp = res.get("generated", {}) or {}
        label = (res.get("layer_label") or "") or ("#" + str(res.get("variant", "")) if res.get("variant") else "")
        tag = f"【{label}】" if label else ""
        item = QListWidgetItem(
            f"{tag}{res.get('summary','')} ｜ {res.get('method','')} ｜ {res.get('elapsed_sec','?')}s")
        item.setData(Qt.ItemDataRole.UserRole, len(self._history) - 1)
        self.history_list.addItem(item)
        if self.history_list.count() > 100:
            self.history_list.takeItem(0)

    def _on_history_row(self, row):
        if row < 0 or row >= self.history_list.count():
            return
        idx = self.history_list.item(row).data(Qt.ItemDataRole.UserRole)
        if 0 <= idx < len(self._history):
            self._load_result(self._history[idx])

    # ---------- export ----------
    _EXPORT_FILTERS = (
        "MusicXML (*.mxl);;MIDI (*.mid);;WAV (*.wav);;MP3 (*.mp3);;FLAC (*.flac);;"
        "OGG (*.ogg);;LilyPond (*.ly);;JSON (*.json)"
    )

    def _on_export(self):
        if not self._last_generated or not self._cache_artifacts:
            QMessageBox.warning(self, "提示", "请先生成歌曲，再导出。")
            return
        base = os.path.splitext(self._cache_artifacts.get("json_file", "piece"))[0]
        default_path = os.path.join(os.path.expanduser("~"), base + ".mxl")
        path, selected = QFileDialog.getSaveFileName(
            self, "导出歌曲（选择保存位置与格式）", default_path, self._EXPORT_FILTERS
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
        self.status_bar.showMessage(f"正在导出 {fmt.upper()}…")
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
        self.log_view.appendPlainText(f"✔ 已导出：{path}")
        self.status_bar.showMessage("已导出：" + path)
        QMessageBox.information(self, "导出完成", "已导出到：\n" + path)

    def _on_export_error(self, msg):
        self.btn_export.setEnabled(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.log_view.appendPlainText("✘ 导出失败：" + msg)
        self.status_bar.showMessage("导出失败")
        QMessageBox.critical(self, "导出失败", msg)

    # ---------- playback ----------
    def _set_play_ui(self, playing):
        self.btn_play.setEnabled(bool(self._current_wav) and os.path.exists(self._current_wav or ""))
        self.play_slider.setEnabled(playing)
        if not playing:
            self.btn_stop.setEnabled(False)
            self.play_slider.setValue(0)
            self.time_label.setText("0:00 / 0:00")
            if self._current_wav:
                self.play_status.setText(f"就绪：{os.path.basename(self._current_wav)}")
        else:
            self.btn_stop.setEnabled(True)
            self.play_status.setText("播放中…")

    def _play(self):
        if not self._player or not self._current_wav or not os.path.exists(self._current_wav):
            QMessageBox.warning(self, "提示", "当前没有可播放的音频（请先生成）。")
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
