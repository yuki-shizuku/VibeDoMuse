# -*- coding: utf-8 -*-
"""
VibeDoMuse · other/generate_galgame_v3.py
多调性数据库生成脚本（galgame_v3 类别）。

职责：
- PIECES：全量曲目元数据（50 首存量 + 25 首现代新增），供 template_db.py
  激活情绪 / 织体 / 和弦进行检索（模块级纯字面量，无 import 依赖）；
- build_new_pieces()：生成 25 首现代三轨乐曲（5 新调 × 5 现代织体），
  轨制为钢琴旋律 + 钢琴织体 + 弦乐垫，严禁古典风格。
"""

# ---- 存量 10 个调（key -> (情绪, 和弦进行)；tender 映射为 gentle）----
_V3_KEYS = {
    "c": ("cheerful", ["C", "Em", "F", "G"]),
    "g": ("warm", ["G", "C", "Am", "D"]),
    "d": ("uplifting", ["D", "Bm", "G", "A"]),
    "f": ("gentle", ["F", "C", "Dm", "Bb"]),
    "bb": ("smart", ["Bb", "Gm", "Eb", "F"]),
    "a": ("bright", ["A", "D", "F#m", "E"]),
    "eb": ("rich", ["Eb", "Cm", "Ab", "Bb"]),
    "am": ("melancholic", ["Am", "Dm", "E7", "Am"]),
    "em": ("thoughtful", ["Em", "C", "G", "D"]),
    "dm": ("dramatic", ["Dm", "Gm", "C7", "F"]),
}
# 存量文件名织体 -> nl_parser 织体词汇
_V3_OLD_PAT = {
    "flowing": "broad_arpeggio", "gentle": "ballad_arp",
    "pulsing": "pulse_chord", "rhythmic": "syncopated",
    "steady": "block_chord",
}

# ---- 现代新增：5 新调（key -> (情绪, 主音, 音阶, 和弦进行, 旋律池)）----
_V3_NEW_KEYS = {
    "e": ("uplifting", 4, "maj", ["E", "C#m", "A", "B"], "POP"),
    "b": ("bright", 11, "maj", ["B", "G#m", "E", "F#"], "POP"),
    "ab": ("warm", 8, "maj", ["Ab", "Fm", "Db", "Eb"], "LOFI"),
    "db": ("rich", 1, "maj", ["Db", "Bbm", "Gb", "Ab"], "POP"),
    "bm": ("melancholic", 11, "min", ["Bm", "G", "D", "A"], "LOFI"),
}
# 现代织体（pattern -> (BPM, 日文名)）
_V3_NEW_PATS = {
    "sixteen_beat": (108, "16ビート"),
    "lofi_swing": (80, "ローファイスウィング"),
    "citypop_groove": (100, "シティポップ"),
    "funk_riff": (106, "ファンク"),
    "edm_pulse": (124, "EDMパルス"),
}
_MOOD_JP = {
    "uplifting": "高揚の", "bright": "明るい", "warm": "温かい",
    "rich": "豊か", "melancholic": "物憂げ",
}
_KEY_SIG = {"e": "E", "b": "B", "ab": "Ab", "db": "Db", "bm": "Bm"}

PIECES = (
    # 存量 50 首：{key}_{mood}_{pattern}
    [
        {"name_en": "%s_%s_%s" % (key, mood, pat), "mood": mood,
         "pattern": _V3_OLD_PAT[pat], "chords": list(chords)}
        for key, (mood, chords) in _V3_KEYS.items()
        for pat in _V3_OLD_PAT
    ]
    + [
        # 现代新增 25 首：{key}_{mood}_{modern_pattern}
        {"name_en": "%s_%s_%s" % (key, mood, pat), "mood": mood,
         "pattern": pat, "chords": list(chords)}
        for key, (mood, _root, _mode, chords, _pool) in _V3_NEW_KEYS.items()
        for pat in _V3_NEW_PATS
    ]
)

BARS = 32  # 32 小节（A A' B A'' × 2 轮）


def build_new_pieces():
    """生成 25 首现代三轨乐曲（钢琴旋律 + 钢琴织体 + 弦乐垫）。

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
    }
    resolve = (m.R_RESOLVE_A, m.R_RESOLVE_B)

    scores = {}
    for key, (mood, key_root, mode, chords, pool_name) in _V3_NEW_KEYS.items():
        scale = m.PENT_MAJ if mode == "maj" else m.PENT_MIN
        for pat, (bpm, pat_jp) in _V3_NEW_PATS.items():
            name = "%s_%s_%s" % (key, mood, pat)
            rng = m.rng_for(name)
            mel = m.gen_melody(rng, chords, key_root, scale, pools[pool_name],
                               resolve, 64, 84, cycles=2)
            texture = m.gen_texture(rng, chords, pat, BARS)
            pad = m.gen_pad(chords, BARS)
            scores[name] = m.build_v2_score(
                "%s%s (%s)" % (_MOOD_JP[mood], pat_jp, _KEY_SIG[key]),
                bpm, _KEY_SIG[key], "galgame_v3",
                [{"instrument": "Acoustic Grand Piano", "events": mel},
                 {"instrument": "Acoustic Grand Piano", "events": texture},
                 {"instrument": "String Ensemble 1", "events": pad}])
    return scores


if __name__ == "__main__":
    _scores = build_new_pieces()
    print("generated %d modern v3 pieces: %s"
          % (len(_scores), ", ".join(sorted(_scores))))
