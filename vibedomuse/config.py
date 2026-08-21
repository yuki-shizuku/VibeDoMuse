# -*- coding: utf-8 -*-
"""
VibeDoMuse · config.py
Config file I/O: LLM API parameters are stored in plaintext in config.ini
at the project root.
- Auto-created (with defaults) if the file is missing.
- Edits made in the GUI (Settings -> LLM Settings) take effect immediately.
"""
import configparser
import os

from ._paths import RUNTIME_DIR

CONFIG_PATH = os.path.join(RUNTIME_DIR, "config.ini")

DEFAULTS = {
    "base_url": "http://127.0.0.1:1234/v1",
    "model": "model",   # placeholder; the user fills in the real model name on first run
    "api_key": "",      # leave empty on first run; the user fills in the real key
    "timeout": "15",
    "temperature": "0.3",
}

APP_DEFAULTS = {
    "theme": "light",
    "language": "en",
}

SERVER_DEFAULTS = {
    "port": "8000",
    "bind": "127.0.0.1",
    "token": "",
}


def load_config():
    """Read config.ini; missing keys fall back to defaults."""
    cfg = configparser.ConfigParser(interpolation=None)
    cfg["llm"] = dict(DEFAULTS)
    cfg["app"] = dict(APP_DEFAULTS)
    cfg["server"] = dict(SERVER_DEFAULTS)
    if os.path.exists(CONFIG_PATH):
        try:
            cfg.read(CONFIG_PATH, encoding="utf-8")
        except Exception:
            pass
    return cfg


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        cfg.write(f)


def ensure_config_file():
    """Create config.ini (with defaults) at the project root if missing."""
    if not os.path.exists(CONFIG_PATH):
        save_config(load_config())


def get_llm_settings():
    """Return the [llm] section as a dict (used by llm_client and the GUI dialog)."""
    ensure_config_file()
    cfg = load_config()
    llm = cfg["llm"]
    try:
        timeout = int(llm.get("timeout", "15"))
    except Exception:
        timeout = 15
    try:
        temperature = float(llm.get("temperature", "0.3"))
    except Exception:
        temperature = 0.3
    temperature = max(0.0, min(2.0, temperature))
    return {
        "base_url": (llm.get("base_url", "") or "").strip() or DEFAULTS["base_url"],
        "model": (llm.get("model", "") or "").strip() or DEFAULTS["model"],
        "api_key": (llm.get("api_key", "") or "").strip(),
        "timeout": max(3, min(120, timeout)),
        "temperature": temperature,
    }


def get_theme():
    """Return the app theme ("light" or "dark")."""
    ensure_config_file()
    cfg = load_config()
    t = cfg["app"].get("theme", "light")
    return t if t in ("light", "dark") else "light"


def get_language():
    """Return the app UI language ("en" or "zh")."""
    ensure_config_file()
    cfg = load_config()
    lang = cfg["app"].get("language", "en")
    return lang if lang in ("en", "zh") else "en"


def set_language(lang):
    """Persist the UI language to config.ini."""
    lang = lang if lang in ("en", "zh") else "en"
    cfg = load_config()
    cfg["app"]["language"] = lang
    save_config(cfg)


def get_server_settings():
    """Return the [server] section (port / bind / token) for the REST backend."""
    ensure_config_file()
    cfg = load_config()
    srv = cfg["server"]
    try:
        port = int(srv.get("port", "8000"))
    except Exception:
        port = 8000
    port = max(1, min(65535, port))
    bind = (srv.get("bind", "") or "").strip() or SERVER_DEFAULTS["bind"]
    return {
        "port": port,
        "bind": bind,
        "token": (srv.get("token", "") or "").strip(),
    }


def set_theme(theme):
    """Persist the app theme to config.ini."""
    theme = theme if theme in ("light", "dark") else "light"
    cfg = load_config()
    if "app" not in cfg:
        cfg["app"] = {}
    cfg["app"]["theme"] = theme
    save_config(cfg)
