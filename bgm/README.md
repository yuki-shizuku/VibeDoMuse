# BGM 数据库文档

> VibeDoMuse BGM 数据库：背景音乐库，适合场景氛围营造。

## 目录结构

```
bgm/
├── README.md              ← 本文档
├── generate_bgm.py        ← 生成脚本（12首现代 + 44首存量）
├── json/                 ← V2 格式 JSON 文件（56首）
│   ├── morning_awakening.json
│   ├── school_road_scenery.json
│   ├── ...（存量44首）
│   ├── citypop_sunset_drive.json
│   ├── lofi_rainy_window.json
│   ...（现代12首）
└── old/                  ← V1 格式备份（可选）
```

## 数据规模

| 类别 | 数量 | 说明 |
|------|------|------|
| 存量曲目 | 44 | 原有校园/青春/恋爱/战斗主题 |
| 现代曲目 | 12 | City Pop、Lo-fi、Synthwave、Future Bass、EDM、K-pop Ballad、J-pop、R&B、Funk |
| **总计** | **56** | **全部 V2 格式** |

## 现代曲目详情

### City Pop 风格（2首）
- **citypop_sunset_drive**  
  - 标题：サンセット・ドライブ  
  - BPM：104 | 调性：F | 情绪：cheerful  
  - 织体：citypop_walk | 和弦：Fmaj7 → Gm7 → C7 → Fmaj7  
  - 乐器：Electric Piano 1 + Electric Bass (finger)

- **citypop_neon_signs**  
  - 标题：ネオンの街並み  
  - BPM：108 | 调性：C | 情绪：cheerful  
  - 织体：citypop_walk | 和弦：Cmaj7 → Bm7 → Em7 → Am7  
  - 乐器：Electric Piano 1 + Electric Bass (finger)

### Lo-fi 风格（2首）
- **lofi_rainy_window**  
  - 标题：雨の日の窓辺で  
  - BPM：72 | 调性：Am | 情绪：thoughtful  
  - 织体：halves | 和弦：Am7 → Dm7 → G7 → Cmaj7  
  - 乐器：Electric Piano 1 + Acoustic Bass

- **lofi_late_study**  
  - 标题：深夜のローファイ  
  - BPM：78 | 调性：Dm | 情绪：calm  
  - 织体：halves | 和弦：Dm7 → G7 → Cmaj7 → Am7  
  - 乐器：Electric Piano 1 + Acoustic Bass

### Synthwave 风格（2首）
- **synthwave_midnight_highway**  
  - 标题：ミッドナイト・ハイウェイ  
  - BPM：100 | 调性：Em | 情绪：dramatic  
  - 织体：straight8 | 和弦：Em → C → G → D  
  - 乐器：Lead 2 (sawtooth) + Synth Bass 1

- **synthwave_retro_skyline**  
  - 标题：レトロなスカイライン  
  - BPM：104 | 调性：Cm | 情绪：melancholic  
  - 织体：straight8 | 和弦：Cm → Ab → Eb → Bb  
  - 乐器：Lead 2 (sawtooth) + Synth Bass 1

### 其他现代风格（6首）
- **future_bass_cherry_steps**（Future Bass）  
  - BPM：120 | 调性：G | 情绪：cheerful | 织体：straight8

- **edm_summer_festival**（EDM）  
  - BPM：128 | 调性：D | 情绪：uplifting | 织体：straight8

- **kpop_ballad_first_snow**（K-pop Ballad）  
  - BPM：72 | 调性：Eb | 情绪：melancholic | 织体：ballad_arp

- **jpop_anime_sprint**（J-pop）  
  - BPM：138 | 调性：A | 情绪：cheerful | 织体：straight8

- **rnb_velvet_groove**（R&B）  
  - BPM：92 | 调性：Bb | 情绪：warm | 织体：citypop_walk

- **funk_street_parade**（Funk）  
  - BPM：110 | 调性：E | 情绪：lively | 织体：funk

## 情绪分布

| 情绪 | 曲目数 | 代表曲目 |
|------|--------|----------|
| cheerful | 8 | citypop_neon_signs, future_bass_cherry_steps, jpop_anime_sprint |
| calm | 4 | lofi_late_study, midnight_piano, star_twinkle |
| uplifting | 4 | edm_summer_festival, power_of_bonds, comeback_moment |
| warm | 6 | rnb_velvet_groove, first_love_melody, holding_hands |
| melancholic | 4 | synthwave_retro_skyline, kpop_ballad_first_snow, endless_rain |
| thoughtful | 3 | lofi_rainy_window, into_dream_world, moonlight_waltz |
| dramatic | 3 | synthwave_midnight_highway, mystery_room, chase_theme |
| lively | 4 | funk_street_parade, fairy_mischief, gymnasium_echo |
| bright | 5 | morning_awakening, youth_footsteps, school_road_scenery |
| sad | 4 | reason_for_tears, farewell_station, rain_then_confession |

## 使用方法

### 1. 通过 template_db 检索
```python
from vibedomuse import template_db

# 检索明亮的 citypop BGM
params = template_db.parse("明るいcitypopのBGM")
results = template_db.search(params, category="galgame_bgm")
```

### 2. 直接调用生成脚本
```python
import bgm.generate_bgm as g

# 生成所有现代 BGM
scores = g.build_new_pieces()
for name, score in scores.items():
    print(f"生成: {name}")
```

### 3. 文件格式说明
所有文件均为 V2 格式，包含：
- `format: "v2"`
- `title`: 曲目标题
- `metadata`: tempo_bpm, time_signature, key_signature
- `tracks`: 乐器轨道 + 音符列表（含 offset 绝对定位）

## Modern Expansion

本次更新新增 12 首现代风格 BGM，特点：
- **五声音阶骨架**：避免古典音阶跑动
- **切分节奏**：现代律动核心，重音错位
- **现代色彩和弦**：maj7、m7、9th、sus4、借用小iv、♭VII
- **结构统一**：A A' B A'' 四句式，BPM 68-138

生成脚本：`bgm/generate_bgm.py`  
数据目录：`bgm/json/`  
总曲目数：56 首（44 存量 + 12 现代）