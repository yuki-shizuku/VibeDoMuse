# -*- coding: utf-8 -*-
"""
VibeDoMuse · bgm/generate_bgm.py
BGM 数据库生成脚本（galgame_bgm 类别）。

职责：
- PIECES：全量曲目元数据（44 首存量 + 12 首现代新增），供 vibedomuse/template_db.py
  加载，激活情绪 / 织体 / 和弦进行检索（模块级纯字面量，无任何 import 依赖）；
- build_new_pieces()：生成 12 首现代风格 BGM（City Pop / Lo-fi / Synthwave /
  Future Bass / EDM / K-pop Ballad / J-pop / R&B / Funk），严禁古典风格；
  生成逻辑仅在显式调用时执行（build_modern_db.py），不影响 PIECES 加载。
"""
PIECES = [
    {"name_en": name, "mood": mood, "pattern": "", "chords": []}
    for name, mood in [
        # ---- 存量 44 首（情绪按 nl_parser 词汇表映射）----
        ("morning_awakening", "bright"), ("school_road_scenery", "cheerful"),
        ("classroom_daily", "gentle"), ("lunch_break_moment", "cheerful"),
        ("youth_footsteps", "bright"), ("library_silence", "calm"),
        ("gymnasium_echo", "lively"), ("school_festival_prep", "cheerful"),
        ("first_love_melody", "warm"), ("starry_sky_promise", "warm"),
        ("under_cherry_tree", "warm"), ("rain_then_confession", "warm"),
        ("holding_hands", "warm"), ("reason_for_tears", "sad"),
        ("farewell_station", "sad"), ("endless_rain", "melancholic"),
        ("into_dream_world", "thoughtful"), ("moonlight_waltz", "thoughtful"),
        ("fairy_mischief", "lively"), ("starfall_fantasy", "thoughtful"),
        ("mystery_room", "dramatic"), ("chase_theme", "dramatic"),
        ("footsteps_in_dark", "dramatic"), ("battle_determination", "uplifting"),
        ("rising_courage", "uplifting"), ("power_of_bonds", "uplifting"),
        ("comeback_moment", "uplifting"), ("distant_promise", "warm"),
        ("old_album", "warm"), ("childhood_dream", "warm"),
        ("seasons_passed", "warm"), ("night_breeze_whisper", "calm"),
        ("moonlight_beach", "calm"), ("lullaby", "calm"),
        ("midnight_piano", "calm"), ("star_twinkle", "calm"),
        ("new_beginning", "uplifting"), ("light_shining_future", "uplifting"),
        ("flower_of_hope", "uplifting"), ("sunbeam_cat", "warm"),
        ("tea_time", "warm"), ("family_dinner_table", "warm"),
        ("friends_smile", "cheerful"), ("warm_memories", "warm"),
        # ---- 现代新增 12 首 ----
        ("citypop_sunset_drive", "cheerful"), ("citypop_neon_signs", "cheerful"),
        ("lofi_rainy_window", "thoughtful"), ("lofi_late_study", "calm"),
        ("synthwave_midnight_highway", "dramatic"),
        ("synthwave_retro_skyline", "melancholic"),
        ("future_bass_cherry_steps", "cheerful"),
        ("edm_summer_festival", "uplifting"),
        ("kpop_ballad_first_snow", "melancholic"),
        ("jpop_anime_sprint", "cheerful"), ("rnb_velvet_groove", "warm"),
        ("funk_street_parade", "lively"),
    ]
]

# 现代曲目元数据（包含 pattern 和 chords）
_NEW_PIECES = {
    "citypop_sunset_drive": {"mood": "cheerful", "pattern": "citypop_walk", "chords": ["Fmaj7", "Gm7", "C7", "Fmaj7"]},
    "citypop_neon_signs": {"mood": "cheerful", "pattern": "citypop_walk", "chords": ["Cmaj7", "Bm7", "Em7", "Am7"]},
    "lofi_rainy_window": {"mood": "thoughtful", "pattern": "halves", "chords": ["Am7", "Dm7", "G7", "Cmaj7"]},
    "lofi_late_study": {"mood": "calm", "pattern": "halves", "chords": ["Dm7", "G7", "Cmaj7", "Am7"]},
    "synthwave_midnight_highway": {"mood": "dramatic", "pattern": "straight8", "chords": ["Em", "C", "G", "D"]},
    "synthwave_retro_skyline": {"mood": "melancholic", "pattern": "straight8", "chords": ["Cm", "Ab", "Eb", "Bb"]},
    "future_bass_cherry_steps": {"mood": "cheerful", "pattern": "straight8", "chords": ["G", "D", "Em", "C"]},
    "edm_summer_festival": {"mood": "uplifting", "pattern": "straight8", "chords": ["D", "Bm", "G", "A"]},
    "kpop_ballad_first_snow": {"mood": "melancholic", "pattern": "ballad_arp", "chords": ["Eb", "Cm", "Ab", "Bb"]},
    "jpop_anime_sprint": {"mood": "cheerful", "pattern": "straight8", "chords": ["A", "E", "F#m", "D"]},
    "rnb_velvet_groove": {"mood": "warm", "pattern": "citypop_walk", "chords": ["Bbmaj7", "Gm7", "Cm7", "F7"]},
    "funk_street_parade": {"mood": "lively", "pattern": "funk", "chords": ["E7", "D", "A", "E7"]},
}
for _p in PIECES:
    if _p["name_en"] in _NEW_PIECES:
        meta = _NEW_PIECES[_p["name_en"]]
        _p["mood"] = meta["mood"]
        _p["pattern"] = meta["pattern"]
        _p["chords"] = meta["chords"]

# ----------------------------------------------------------------------------
# 现代曲目生成定义（name, title, bpm, key, key_root, scale, chords,
#                    旋律乐器, 副轨乐器, 副轨风格, 旋律音域）
# ----------------------------------------------------------------------------
MODERN_DEFS = [
    ("citypop_sunset_drive", "サンセット・ドライブ", 104, "F", 5, "maj",
     ["Fmaj7", "Gm7", "C7", "Fmaj7"],
     "Electric Piano 1", "Electric Bass (finger)", "citypop_walk", (64, 84)),
    ("citypop_neon_signs", "ネオンの街並み", 108, "C", 0, "maj",
     ["Cmaj7", "Bm7", "Em7", "Am7"],
     "Electric Piano 1", "Electric Bass (finger)", "citypop_walk", (64, 84)),
    ("lofi_rainy_window", "雨の日の窓辺で", 72, "Am", 9, "min",
     ["Am7", "Dm7", "G7", "Cmaj7"],
     "Electric Piano 1", "Acoustic Bass", "halves", (60, 79)),
    ("lofi_late_study", "深夜のローファイ", 78, "Dm", 2, "min",
     ["Dm7", "G7", "Cmaj7", "Am7"],
     "Electric Piano 1", "Acoustic Bass", "halves", (60, 79)),
    ("synthwave_midnight_highway", "ミッドナイト・ハイウェイ", 100, "Em", 4, "min",
     ["Em", "C", "G", "D"],
     "Lead 2 (sawtooth)", "Synth Bass 1", "straight8", (64, 86)),
    ("synthwave_retro_skyline", "レトロなスカイライン", 104, "Cm", 0, "min",
     ["Cm", "Ab", "Eb", "Bb"],
     "Lead 2 (sawtooth)", "Synth Bass 1", "straight8", (64, 86)),
    ("future_bass_cherry_steps", "チェリーステップス", 128, "G", 7, "maj",
     ["G", "D", "Em", "C"],
     "Lead 1 (square)", "Synth Bass 1", "edm", (67, 88)),
    ("edm_summer_festival", "夏祭りの夜", 126, "D", 2, "maj",
     ["D", "Bm", "G", "A"],
     "Lead 1 (square)", "Synth Bass 1", "edm", (67, 88)),
    ("kpop_ballad_first_snow", "初雪のバラード", 68, "Eb", 3, "maj",
     ["Eb", "Cm", "Ab", "Bb"],
     "Acoustic Grand Piano", "Acoustic Grand Piano", "bed", (62, 84)),
    ("jpop_anime_sprint", "アニメの疾走", 138, "A", 9, "maj",
     ["A", "E", "F#m", "D"],
     "Acoustic Grand Piano", "Electric Bass (finger)", "straight8", (64, 86)),
    ("rnb_velvet_groove", "ベルベット・グルーヴ", 92, "Bb", 10, "maj",
     ["Bbmaj7", "Gm7", "Cm7", "F7"],
     "Electric Piano 1", "Electric Bass (finger)", "citypop_walk", (62, 83)),
    ("funk_street_parade", "ストリート・パレード", 110, "E", 4, "min",
     ["E7", "D", "A", "E7"],
     "Clav", "Electric Bass (finger)", "funk", (62, 84)),
]

# 曲风 -> 旋律节奏单元池 / 收束池（modern_lib 中定义的单元名）
_GENRE_POOL = {
    "citypop": ("POP", "RESOLVE_AB"),
    "lofi": ("LOFI", "RESOLVE_B"),
    "synthwave": ("SYNTH", "RESOLVE_A"),
    "futurebass": ("FB", "RESOLVE_A"),
    "edm": ("EDM", "RESOLVE_A"),
    "kpop_ballad": ("BALLAD", "RESOLVE_BC"),
    "jpop": ("JPOP", "RESOLVE_A"),
    "rnb": ("RNB", "RESOLVE_B"),
    "funk": ("FUNK", "RESOLVE_A"),
}
_GENRE_OF = {
    "citypop_sunset_drive": "citypop", "citypop_neon_signs": "citypop",
    "lofi_rainy_window": "lofi", "lofi_late_study": "lofi",
    "synthwave_midnight_highway": "synthwave",
    "synthwave_retro_skyline": "synthwave",
    "future_bass_cherry_steps": "futurebass", "edm_summer_festival": "edm",
    "kpop_ballad_first_snow": "kpop_ballad", "jpop_anime_sprint": "jpop",
    "rnb_velvet_groove": "rnb", "funk_street_parade": "funk",
}

BARS = 16  # 16 小节（A A' B A'' 结构，每句 4 小节）


def build_new_pieces():
    """生成 12 首现代风格 BGM 乐谱。

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
        "SYNTH": (m.R_POP_C, m.R_POP_A),
        "FB": (m.R_GROOVE, m.R_EDM, m.R_POP_A),
        "EDM": (m.R_EDM, m.R_GROOVE),
        "BALLAD": (m.R_BALLAD, m.R_LOFI, m.R_POP_A),
        "JPOP": (m.R_POP_A, m.R_POP_C, m.R_GROOVE),
        "RNB": (m.R_POP_B, m.R_LOFI, m.R_POP_C),
        "FUNK": (m.R_FUNK, m.R_GROOVE),
    }
    resolves = {
        "RESOLVE_A": (m.R_RESOLVE_A,),
        "RESOLVE_B": (m.R_RESOLVE_B,),
        "RESOLVE_AB": (m.R_RESOLVE_A, m.R_RESOLVE_B),
        "RESOLVE_BC": (m.R_RESOLVE_B, m.R_RESOLVE_C),
    }

    scores = {}
    for (name, title, bpm, key, key_root, mode, chords,
         mel_inst, sub_inst, sub_style, mel_range) in MODERN_DEFS:
        rng = m.rng_for(name)
        genre = _GENRE_OF[name]
        pool, res = _GENRE_POOL[genre]
        scale = m.PENT_MAJ if mode == "maj" else m.PENT_MIN
        mel = m.gen_melody(rng, chords, key_root, scale, pools[pool],
                           resolves[res], mel_range[0], mel_range[1])
        if sub_style == "bed":
            sub = m.gen_bed(rng, chords, BARS)
        else:
            sub = m.gen_bass(rng, chords, sub_style, BARS)
        scores[name] = m.build_v2_score(
            title, bpm, key, "galgame_bgm",
            [{"instrument": mel_inst, "events": mel},
             {"instrument": sub_inst, "events": sub}])
    return scores


if __name__ == "__main__":
    _scores = build_new_pieces()
    print("generated %d modern bgm pieces: %s"
          % (len(_scores), ", ".join(sorted(_scores))))
