# -*- coding: utf-8 -*-
"""
VibeDoMuse · frontend_pyqt6/widgets.py
Reusable view widgets extracted from main.py:
  - JsonHighlighter : JSON syntax highlighter for the preview pane
  - PianoRoll       : piano-roll style visualization of a generated score
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import (
    QColor, QFont, QPainter, QPen, QSyntaxHighlighter, QTextCharFormat,
)


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
