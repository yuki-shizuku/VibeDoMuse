# -*- coding: utf-8 -*-
"""
VibeDoMuse · nl_parser.py
Natural language -> MusicParams parser (the Agent's understanding layer).
Supports Chinese / Japanese / English keywords covering mood, key, tempo,
time signature, texture, instrument, track count, duration, style category,
percussion (drums) and seamless loop. All local rule-based mapping; no external
LLM required, fully offline.
"""
import re
from dataclasses import dataclass, field
from . import music_theory as mt


@dataclass
class MusicParams:
    text: str = ""
    mood: str = "gentle"
    mood_cn: str = "温柔"
    key: str = "C"
    is_minor: bool = False
    tempo_bpm: int = 90
    time_sig: str = "4/4"
    pattern: str = "arpeggio_1353"
    instrument: str = "Acoustic Grand Piano"
    tracks: int = 2
    category: str = "galgame_accompaniment"
    progressions: list = field(default_factory=list)
    duration_sec: int = 30
    drums: bool = False
    loop: bool = False
    seed: int = None

    def summary(self):
        extra = []
        if self.drums:
            extra.append("鼓点")
        if self.loop:
            extra.append("无缝循环")
        extra_s = (" · " + "/".join(extra)) if extra else ""
        return (
            f"情绪={self.mood_cn}({self.mood}) | 调性={self.key} | "
            f"速度={self.tempo_bpm}BPM | 拍号={self.time_sig} | 织体={self.pattern} | "
            f"乐器={self.instrument} | 声部={self.tracks}轨 | 类别={self.category} | "
            f"时长={self.duration_sec}s{extra_s}"
        )


def _detect_mood(text):
    for kw, mood in mt.MOOD_KEYWORDS:
        if kw in text:
            return mood
    return None


def _detect_tempo(text, base):
    mm = re.search(r"(\d{2,3})\s*bpm", text, re.IGNORECASE)
    explicit = None
    if mm:
        explicit = int(mm.group(1))
    else:
        mm = re.search(r"(?:速度|tempo|速率)\s*[:：]?\s*(\d{2,3})", text, re.IGNORECASE)
        if mm:
            explicit = int(mm.group(1))
        else:
            mm = re.search(r"(\d{2,3})\s*(?:拍|速)", text, re.IGNORECASE)
            if mm:
                explicit = int(mm.group(1))
    if explicit:
        return max(40, min(220, explicit))
    t = text.lower()
    if any(k in text for k in ("快", "急", "fast", "upbeat", "quick", "活泼", "活力", "激昂", "激烈", "energetic")):
        return max(40, min(220, base + 20))
    if any(k in text for k in ("慢", "缓", "slow", "舒缓", "安静", "宁静", "静")):
        return max(40, min(220, base - 20))
    return base


def _detect_time_sig(text):
    if "3/4" in text or "三拍" in text or "华尔兹" in text or "waltz" in text.lower():
        return "3/4"
    if "4/4" in text or "四拍" in text:
        return "4/4"
    if "6/8" in text or "六八拍" in text:
        return "6/8"
    if "2/4" in text or "二拍" in text:
        return "2/4"
    return None


def _detect_pattern(text):
    for kw, pat in mt.PATTERN_ALIASES.items():
        if kw in text:
            return pat
    return None


def _detect_instrument(text):
    # longest alias first so "小提琴" wins over the single char "琴"
    for kw in sorted(mt.INSTRUMENT_ALIASES, key=len, reverse=True):
        if kw in text:
            return mt.INSTRUMENT_ALIASES[kw]
    return None


def _detect_tracks(text):
    if any(k in text for k in ("三轨", "3轨", "弦乐铺垫", "弦乐垫", "三层", "三層", "pad", "弦乐")):
        return 3
    if any(k in text for k in ("二重奏", "duet", "两轨", "2轨", "双轨", "钢琴伴奏", "伴奏")):
        return 2
    if any(k in text for k in ("单轨", "独奏", "旋律", "solo", "单声部")):
        return 1
    return None


def _detect_duration(text):
    m = re.search(r"(\d+)\s*分钟", text)
    if m:
        return max(5, min(180, int(m.group(1)) * 60))
    m = re.search(r"(\d+)\s*秒", text)
    if m:
        return max(5, min(180, int(m.group(1))))
    if "半分钟" in text:
        return 30
    if "一分钟" in text:
        return 60
    return 30


def _detect_category(text):
    t = text.lower()
    if "伴奏" in text or "accompaniment" in t:
        return "galgame_accompaniment"
    if any(k in text for k in ("多调", "v3", "三轨弦乐", "多key", "多调性")):
        return "galgame_v3"
    if any(k in text for k in ("背景音乐", "bgm", "普通", "旋律驱动", "galgame")):
        return "galgame_bgm"
    return None


def _detect_drums(text):
    return any(k in text for k in ("鼓", "打击乐", "鼓点", "节奏打击", "drums", "drum", "percussion", "beat"))


def _detect_loop(text):
    t = text.lower()
    return any(k in text for k in ("循环", "无缝", "无限循环", "seamless", "loop")) or "loop" in t


def _pick_progression(mood, key):
    cands = mt.MOOD_PROFILES[mood].progressions
    if key:
        key_root = key[0].upper()
        for prog in cands:
            if mt.parse_chord(prog[0])[0].upper() == key_root:
                return list(prog)
    return list(cands[0]) if cands else [["C", "G", "Am", "F"]][0]


def parse(text, seed=None):
    """Parse natural-language text into MusicParams."""
    text = (text or "").strip()
    if not text:
        text = "温柔的钢琴伴奏"
    mood = _detect_mood(text) or "gentle"
    prof = mt.MOOD_PROFILES[mood]

    # key
    nk = mt.normalize_key(text)
    if nk:
        key, is_minor = nk
    else:
        is_minor = prof.mode == "minor"
        key = "Am" if is_minor else "C"

    tempo = _detect_tempo(text, prof.tempo)
    time_sig = _detect_time_sig(text) or prof.time_sig
    pattern = _detect_pattern(text) or prof.pattern
    instrument = _detect_instrument(text) or prof.instrument
    explicit_tracks = _detect_tracks(text)
    tracks = explicit_tracks if explicit_tracks is not None else prof.tracks
    if any(k in text for k in ("弦乐", "pad", "三轨", "3轨")):
        tracks = 3
    duration = _detect_duration(text)
    category = _detect_category(text) or prof.category
    # 3-track + strings requests belong to the multi-key v3 category
    if tracks >= 3 and any(k in text for k in ("弦乐", "pad", "三轨", "3轨", "三层")) \
            and category != "galgame_v3":
        category = "galgame_v3"
    # category defaults only apply when the user did not pick the track count
    if category == "galgame_v3" and tracks < 3 and explicit_tracks is None:
        tracks = 3
        instrument = "Acoustic Grand Piano"
    if category == "galgame_accompaniment" and tracks < 2 and explicit_tracks is None:
        tracks = 2
        instrument = "Acoustic Grand Piano"
    # an explicit solo stays solo (do not overwrite the instrument) and is BGM-like
    if explicit_tracks == 1 and category == "galgame_accompaniment":
        category = "galgame_bgm"

    progressions = _pick_progression(mood, key)
    drums = _detect_drums(text)
    loop = _detect_loop(text)

    return MusicParams(
        text=text, mood=mood, mood_cn=prof.cn, key=key, is_minor=is_minor,
        tempo_bpm=int(tempo), time_sig=time_sig, pattern=pattern,
        instrument=instrument, tracks=int(tracks), category=category,
        progressions=progressions, duration_sec=int(duration),
        drums=drums, loop=loop, seed=seed,
    )
