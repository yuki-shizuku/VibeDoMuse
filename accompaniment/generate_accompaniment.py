# -*- coding: utf-8 -*-
"""
VibeDoMuse · accompaniment/generate_accompaniment.py
伴奏数据库生成脚本（galgame_accompaniment 类别）。

职责：
- PIECES：全量曲目元数据（50 首存量 + 30 首现代新增），供 template_db.py
  激活情绪 / 织体 / 和弦进行检索（模块级纯字面量，无 import 依赖）；
- build_new_pieces()：生成 30 首现代和声驱动伴奏（5 现代情绪 × 6 现代进行），
  双轨钢琴（旋律 + 现代织体），严禁古典风格。
"""

# ---- 存量 10 个和弦进行（C 大调系统）----
_PROGS = {
    "王道pop": ["C", "G", "Am", "F"],
    "小室": ["Am", "F", "G", "C"],
    "4516": ["F", "G", "Em", "Am"],
    "副歌": ["C", "Am", "F", "G"],
    "II-V-I": ["Dm7", "G7", "Cmaj7", "Cmaj7"],
    "カノン": ["C", "G", "Am", "Em", "F", "C", "F", "G"],
    "小調循環": ["Am", "Dm", "G", "C"],
    "基本": ["C", "F", "G", "C"],
    "extended": ["Em", "Am", "Dm7", "G7"],
    "混合": ["Cmaj7", "Am7", "Fmaj7", "G7"],
}
# 存量情绪 -> 织体（与 nl_parser PATTERN_ALIASES 对齐）
_PATTERNS = {
    "gentle": "arpeggio_1353", "calm": "block_chord", "elegant": "waltz",
    "lively": "alternating_bass", "refreshing": "syncopated",
}

# ---- 现代新增：6 个现代进行 × 5 现代情绪（情绪即织体）----
_NEW_PROGS = {
    "citypop": ["Cmaj7", "Bm7", "Em7", "Am7"],       # I-vii-iii-vi 都会系下行
    "rnb": ["Cmaj7", "Am7", "Dm7", "G7"],            # I7-vi7-ii7-V7 R&B回转
    "lofi": ["Am7", "Dm7", "G7", "Cmaj7"],           # vi-ii-V-I 慢速爵士链
    "mixo": ["C", "Bb", "F", "C"],                   # I-bVII-IV 混合利底亚
    "borrowed": ["C", "G", "Am", "Fm"],              # I-V-vi-iv 借用小iv
    "minorpop": ["Am", "F", "C", "G"],               # vi-IV-I-V 轴心小调流行
}
_NEW_MOODS = {
    "bright": ("sixteen_beat", 108, "明るい"),
    "warm": ("lofi_swing", 76, "温かい"),
    "smart": ("funk_riff", 104, "洒落た"),
    "uplifting": ("citypop_groove", 100, "高揚の"),
    "cheerful": ("edm_pulse", 124, "元気の"),
}
_NEW_PROG_JP = {
    "citypop": "シティポップ", "rnb": "R&B", "lofi": "ローファイ",
    "mixo": "フラットセブン", "borrowed": "借用コード",
    "minorpop": "マイナーポップ",
}

PIECES = (
    # 存量 50 首：{mood}_{progression}
    [
        {"name_en": "%s_%s" % (mood, prog), "mood": mood,
         "pattern": _PATTERNS[mood], "chords": list(chords)}
        for mood in _PATTERNS for prog, chords in _PROGS.items()
    ]
    + [
        # 现代新增 30 首：{mood}_{modern_prog}
        {"name_en": "%s_%s" % (mood, prog), "mood": mood,
         "pattern": _NEW_MOODS[mood][0], "chords": list(chords)}
        for mood in _NEW_MOODS for prog, chords in _NEW_PROGS.items()
    ]
)

BARS = 16  # 16 小节 = 4 轮和弦循环

# 现代情绪 -> 旋律配置（节奏池名, 音阶, 主音, 旋律音域）
_MELODY_CFG = {
    "bright": ("POP", "maj", 0, (67, 86)),
    "warm": ("LOFI", "maj", 0, (64, 83)),
    "smart": ("FUNK", "min", 9, (62, 84)),
    "uplifting": ("POP", "maj", 0, (67, 86)),
    "cheerful": ("EDM", "maj", 0, (67, 88)),
}


def build_new_pieces():
    """生成 30 首现代和声驱动伴奏乐谱（双轨钢琴）。

    参数：无。
    返回：
        dict[str, dict]: {曲名: V2 乐谱 JSON 文档}。
    """
    import os
    import sys
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _root not in sys.path:
        sys.path.insert(0, _root)
    import modern_lib as m

    pools = {
        "POP": (m.R_POP_A, m.R_POP_B, m.R_POP_C),
        "LOFI": (m.R_LOFI, m.R_POP_B, m.R_BALLAD),
        "EDM": (m.R_EDM, m.R_GROOVE, m.R_POP_A),
        "FUNK": (m.R_FUNK, m.R_GROOVE),
    }
    resolves = {
        "A": (m.R_RESOLVE_A,),
        "B": (m.R_RESOLVE_B,),
        "AB": (m.R_RESOLVE_A, m.R_RESOLVE_B),
    }

    scores = {}
    for mood, (pattern, bpm, mood_jp) in _NEW_MOODS.items():
        pool_name, mode, key_root, mel_range = _MELODY_CFG[mood]
        scale = m.PENT_MAJ if mode == "maj" else m.PENT_MIN
        for prog, chords in _NEW_PROGS.items():
            name = "%s_%s" % (mood, prog)
            rng = m.rng_for(name)
            mel = m.gen_melody(rng, chords, key_root, scale, pools[pool_name],
                               resolves["AB"], mel_range[0], mel_range[1])
            texture = m.gen_texture(rng, chords, pattern, BARS)
            scores[name] = m.build_v2_score(
                "%s%s" % (mood_jp, _NEW_PROG_JP[prog]), bpm, "C",
                "galgame_accompaniment",
                [{"instrument": "Acoustic Grand Piano", "events": mel},
                 {"instrument": "Acoustic Grand Piano", "events": texture}])
    return scores


if __name__ == "__main__":
    _scores = build_new_pieces()
    print("generated %d modern accompaniment pieces: %s"
          % (len(_scores), ", ".join(sorted(_scores))))
