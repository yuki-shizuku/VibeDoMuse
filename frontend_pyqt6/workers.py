# -*- coding: utf-8 -*-
"""
VibeDoMuse · frontend_pyqt6/workers.py
Background QThread workers extracted from main.py.

Workers run the agent / renderer in a non-UI thread and report progress via
signals. AnalyzeWorker and GenWorker additionally emit a ``token`` signal for
every streamed LLM text chunk so the UI can render generation live.
"""
from PyQt6.QtCore import QThread, pyqtSignal

from vibedomuse import agent


class AnalyzeWorker(QThread):
    """First-stage: sends user prompt to LLM for intent analysis."""
    finished = pyqtSignal(str)  # analysis text
    error = pyqtSignal(str)
    token = pyqtSignal(str)     # streamed LLM text chunks

    def __init__(self, text):
        super().__init__()
        self.text = text

    def run(self):
        try:
            analysis = agent.analyze(self.text, on_token=lambda c: self.token.emit(c))
            if analysis:
                self.finished.emit(analysis)
            else:
                self.error.emit("LLM analysis returned no result. Check your LLM configuration.")
        except Exception as e:  # noqa: BLE001
            self.error.emit(str(e))


class GenWorker(QThread):
    """Runs the Agent in the background; emits {kind, ...} results."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    log = pyqtSignal(str)
    token = pyqtSignal(str)     # streamed LLM JSON text chunks (llm / llm_v2 only)

    def __init__(self, text, seed=None, mode="llm", use_template=None, n=4, analysis=None):
        super().__init__()
        self.text = text
        self.seed = seed
        self.mode = mode
        self.use_template = use_template
        self.n = n
        self.analysis = analysis

    def run(self):
        cb = lambda c: self.token.emit(c)  # noqa: E731
        try:
            if self.mode == "llm_v2":
                self.log.emit("Stage 2: Generating score with original prompt + understanding...")
                res = agent.run_llm_v2(self.text, self.analysis, seed=self.seed, on_token=cb)
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
            res = agent.run_llm(self.text, seed=self.seed, on_token=cb)
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


class FollowupWorker(QThread):
    """Generates a follow-up based on user feedback."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    log = pyqtSignal(str)
    token = pyqtSignal(str)     # streamed LLM JSON text chunks

    def __init__(self, original_text, original_analysis, current_score, user_feedback, seed=None):
        super().__init__()
        self.original_text = original_text
        self.original_analysis = original_analysis
        self.current_score = current_score
        self.user_feedback = user_feedback
        self.seed = seed

    def run(self):
        cb = lambda c: self.token.emit(c)  # noqa: E731
        try:
            self.log.emit("Follow-up: analyzing feedback and generating improved score...")
            res = agent.run_followup(
                self.original_text,
                self.original_analysis,
                self.current_score,
                self.user_feedback,
                seed=self.seed,
                on_token=cb
            )
            self.log.emit("Follow-up: validation and rendering complete.")
            self.finished.emit({"kind": "single", "data": res})
        except Exception as e:  # noqa: BLE001
            self.error.emit(str(e))
