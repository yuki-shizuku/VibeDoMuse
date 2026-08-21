# -*- coding: utf-8 -*-
"""
VibeDoMuse · frontend_pyqt6/dialogs.py
Modal dialogs extracted from main.py:
  - LlmSettingsDialog   : edit LLM base_url / model / key / timeout / temperature
  - UnderstandingDialog : show the LLM's intent analysis, ask to confirm
  - TemplateBrowserDialog : browse the 144-piece template library
  - MixDialog           : per-track velocity scaling + mute
"""
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, QDialogButtonBox,
    QMessageBox, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QListWidget, QListWidgetItem, QSlider, QCheckBox,
)
from PyQt6.QtCore import Qt

from vibedomuse import config, template_db

from .i18n import _


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

        # Disable the button during test
        self.btn_test.setEnabled(False)
        self.btn_test.setText(_("Testing..."))

        try:
            result = llm_client.test_connection(
                base_url=v["base_url"] or None,
                model=v["model"] or None,
                api_key=v["api_key"] or None,
                timeout=int(v["timeout"]) if v["timeout"] else 10,
            )

            if result["ok"]:
                QMessageBox.information(
                    self, _("Test Result"),
                    _("Connection successful!") + "\n\n" +
                    _("Model responded:") + f" {result['details'].get('response', 'N/A')}",
                )
            else:
                QMessageBox.warning(
                    self, _("Test Result"),
                    _("Connection failed!") + "\n\n" +
                    f"{result['message']}\n\n" +
                    _("Details:") + f" {result['details']}",
                )
        finally:
            self.btn_test.setEnabled(True)
            self.btn_test.setText(_("Test Connection"))

    def _save(self):
        cfg = config.load_config()
        cfg["llm"].update(self._values())
        config.save_config(cfg)
        QMessageBox.information(self, _("Saved"), _("Configuration saved to:") + f"\n{config.CONFIG_PATH}")
        self.accept()


class UnderstandingDialog(QDialog):
    """Shows the LLM's understanding of the user's request and asks for confirmation.

    User can modify the understanding before confirming.
    """

    def __init__(self, analysis, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Confirm AI Understanding"))
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

        # Title with both languages
        title = QLabel(_("The AI understands your request as follows. Confirm to proceed, or modify the description."))
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)

        # Editable analysis text
        self.analysis_view = QTextEdit()
        self.analysis_view.setPlainText(analysis)
        self.analysis_view.setReadOnly(False)  # Allow user to edit
        self.analysis_view.setMinimumHeight(200)
        layout.addWidget(self.analysis_view, 1)

        # Hint text with both languages
        hint = QLabel(_("You can modify the understanding above before confirming.") + "\n" +
                      _("If correct, click") + " \"" + _("Confirm & Generate") + "\" " +
                      _("to proceed, or click") + " \"" + _("Modify Description") + "\" " +
                      _("to go back."))
        hint.setStyleSheet("color: #666666; font-size: 12px;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        btn_row = QHBoxLayout()
        self.btn_confirm = QPushButton(_("Confirm & Generate"))
        self.btn_confirm.clicked.connect(self.accept)
        self.btn_modify = QPushButton(_("Modify Description"))
        self.btn_modify.setObjectName("secondary")
        self.btn_modify.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_modify)
        btn_row.addWidget(self.btn_confirm)
        layout.addLayout(btn_row)

    def get_analysis(self):
        """Return the user's modified understanding text."""
        return self.analysis_view.toPlainText()


class TemplateBrowserDialog(QDialog):
    """Browse the 144-piece template library and pick one as a base."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Template Browser"))
        self.resize(680, 520)
        self.selected = None
        try:
            self._all = template_db.all_templates()
        except Exception:  # noqa: BLE001
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


class HistoryDetailDialog(QDialog):
    """Shows detailed information about a history item."""

    def __init__(self, history_item, parent=None):
        super().__init__(parent)
        self.history_item = history_item
        self.setWindowTitle(_("History Details"))
        self.setMinimumSize(800, 600)

        # Build dialog content
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header section
        title = QLabel(_("History Details"))
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # Tabs for different aspects
        from PyQt6.QtWidgets import QTabWidget
        tabs = QTabWidget()

        # Tab 1: Overview
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)

        # Show basic info
        info_text = (
            f"{'='*50}\n"
            f"{_('Timestamp')}: {self._format_timestamp(history_item.timestamp)}\n"
            f"{_('Method')}: {history_item.method}\n"
            f"{_('Seed')}: {history_item.seed or 'N/A'}\n"
            f"{_('Summary')}: {history_item.summary}\n"
            f"{'='*50}"
        )
        if history_item.parent_id:
            info_text += f"\n{_('Parent ID')}: {history_item.parent_id}"
        if history_item.feedback:
            info_text += f"\n{_('Feedback')}: {history_item.feedback}"

        info_label = QLabel(info_text)
        info_label.setStyleSheet("font-family: monospace; white-space: pre-wrap;")
        overview_layout.addWidget(info_label)

        # Load this result button
        btn_load = QPushButton(_("Load this result"))
        btn_load.clicked.connect(self._load_result)
        overview_layout.addWidget(btn_load)

        # Copy JSON button
        btn_copy = QPushButton(_("Copy JSON"))
        btn_copy.clicked.connect(self._copy_json)
        overview_layout.addWidget(btn_copy)

        tabs.addTab(overview_tab, _("Overview"))

        # Tab 2: User Request & AI Understanding
        req_tab = QWidget()
        req_layout = QVBoxLayout(req_tab)

        req_layout.addWidget(QLabel(f"<b>{_('User Request')}:</b>"))
        req_text = QTextEdit()
        req_text.setPlainText(history_item.user_text)
        req_text.setReadOnly(True)
        req_layout.addWidget(req_text, 1)

        if history_item.analysis:
            req_layout.addWidget(QLabel(f"<b>{_('AI Understanding')}:</b>"))
            analysis_text = QTextEdit()
            analysis_text.setPlainText(history_item.analysis)
            analysis_text.setReadOnly(True)
            req_layout.addWidget(analysis_text, 1)

        tabs.addTab(req_tab, _("User Request"))

        # Tab 3: Generated JSON
        json_tab = QWidget()
        json_layout = QVBoxLayout(json_tab)

        if history_item.score:
            from json import dumps
            json_text = QTextEdit()
            json_content = dumps(history_item.score, ensure_ascii=False, indent=2)
            json_text.setPlainText(json_content)
            json_text.setReadOnly(True)
            json_layout.addWidget(json_text, 1)
        else:
            json_layout.addWidget(QLabel(_("No JSON score available.")))

        tabs.addTab(json_tab, _("Generated JSON"))

        # Conversation Thread tab (if this is a follow-up)
        if history_item.parent_id:
            from vibedomuse.history_manager import history_manager
            thread = history_manager.get_conversation_thread(history_item.id)
            if thread and len(thread) > 1:
                thread_tab = QWidget()
                thread_layout = QVBoxLayout(thread_tab)

                thread_layout.addWidget(QLabel(f"<b>{_('Conversation Thread')}:</b>"))
                thread_text = QTextEdit()
                thread_content = self._format_thread(thread)
                thread_text.setPlainText(thread_content)
                thread_text.setReadOnly(True)
                thread_layout.addWidget(thread_text, 1)

                tabs.addTab(thread_tab, _("Conversation Thread"))

        layout.addWidget(tabs, 1)

        # Close button
        btn_close = QPushButton(_("Close"))
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

        # Apply theme styling
        self._apply_theme()

    def _format_timestamp(self, timestamp):
        """Format Unix timestamp to readable string."""
        from datetime import datetime
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def _format_thread(self, thread):
        """Format the conversation thread for display."""
        lines = []
        for i, item in enumerate(thread):
            timestamp_str = self._format_timestamp(item.timestamp)
            lines.append(f"[{i+1}] {timestamp_str} - {item.method}")
            lines.append(f"    {_('User Request')}: {item.user_text[:60]}...")
            if item.analysis:
                lines.append(f"    {_('AI Understanding')}: {item.analysis[:60]}...")
            if item.feedback:
                lines.append(f"    {_('Feedback')}: {item.feedback[:60]}...")
            lines.append("")
        return "\n".join(lines)

    def _load_result(self):
        """Load the history item's result into the main window."""
        if self.history_item.score:
            # Emit a signal or call a method to load this result
            # For now, just close and let the caller handle it
            self.accept()
            # Note: The parent window should connect to this dialog's accepted signal
            # and handle loading the result
        else:
            QMessageBox.warning(self, _("Error"), _("No score data available in this history item."))

    def _copy_json(self):
        """Copy the JSON to clipboard."""
        if self.history_item.score:
            from json import dumps
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(dumps(self.history_item.score, ensure_ascii=False, indent=2))
            QMessageBox.information(self, _("Copied"), _("JSON copied to clipboard."))
        else:
            QMessageBox.warning(self, _("Error"), _("No JSON available to copy."))

    def _apply_theme(self):
        """Apply the current theme to the dialog."""
        from .i18n import _lang
        theme = "dark" if _lang() == "dark" else "light"

        if theme == "dark":
            self.setStyleSheet("""
                QDialog { background-color: #1e1e1e; }
                QLabel { color: #e0e0e0; }
                QTextEdit { background-color: #2d2d2d; color: #e0e0e0; border: 1px solid #383838; }
                QPushButton { background-color: #0d47a1; color: #e0e0e0; border: none; padding: 6px 12px; border-radius: 4px; }
                QPushButton:hover { background-color: #1565c0; }
                QTabWidget::pane { border: 1px solid #383838; background-color: #2d2d2d; }
                QTabBar::tab { background-color: #3a3a3a; color: #e0e0e0; border: 1px solid #383838; padding: 6px 12px; }
                QTabBar::tab:selected { background-color: #2d2d2d; color: #e0e0e0; border-bottom: 2px solid #0d47a1; }
            """)
        else:
            self.setStyleSheet("""
                QDialog { background-color: #ffffff; }
                QLabel { color: #000000; }
                QTextEdit { background-color: #f5f5f5; color: #000000; border: 1px solid #e0e0e0; }
                QPushButton { background-color: #1976d2; color: white; border: none; padding: 6px 12px; border-radius: 4px; }
                QPushButton:hover { background-color: #1565c0; }
                QTabWidget::pane { border: 1px solid #e0e0e0; background-color: #ffffff; }
                QTabBar::tab { background-color: #f5f5f5; color: #000000; border: 1px solid #e0e0e0; padding: 6px 12px; }
                QTabBar::tab:selected { background-color: #ffffff; color: #000000; border-bottom: 2px solid #1976d2; }
            """)
