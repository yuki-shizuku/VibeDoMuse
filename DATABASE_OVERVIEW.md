# VibeDoMuse 数据库总览

> 完整的 V2 格式音乐数据库，包含 211 首现代风格乐曲，支持多语言检索。

## 数据库架构

### 三大类别

| 类别 | 说明 | 数量 | 特点 |
|------|------|------|------|
| **galgame_bgm** | 背景音乐库 | 56 | 场景氛围营造，单/双轨配置 |
| **galgame_accompaniment** | 和声伴奏库 | 80 | 对话/过场/情绪铺垫，双轨钢琴 |
| **galgame_v3** | 三轨完整曲库 | 75 | 主题曲/重要场景，三轨配置 |

### 数据构成

| 类型 | 数量 | 说明 |
|------|------|------|
| 存量曲目 | 144 | 原有校园/青春/恋爱/战斗主题 |
| 现代曲目 | 67 | City Pop、Lo-fi、Synthwave、Future Bass、EDM、K-pop Ballad、J-pop、R&B、Funk |
| **总计** | **211** | **全部 V2 格式** |

## 现代曲目分布

### BGM 类别（12首）
| 风格 | 数量 | 代表曲目 |
|------|------|----------|
| City Pop | 2 | citypop_sunset_drive, citypop_neon_signs |
| Lo-fi | 2 | lofi_rainy_window, lofi_late_study |
| Synthwave | 2 | synthwave_midnight_highway, synthwave_retro_skyline |
| Future Bass | 1 | future_bass_cherry_steps |
| EDM | 1 | edm_summer_festival |
| K-pop Ballad | 1 | kpop_ballad_first_snow |
| J-pop | 1 | jpop_anime_sprint |
| R&B | 1 | rnb_velvet_groove |
| Funk | 1 | funk_street_parade |

### Accompaniment 类别（30首）
| 情绪 | 数量 | 和声进行 | 织体 |
|------|------|----------|------|
| bright | 6 | citypop, rnb, lofi, mixo, borrowed, minorpop | sixteen_beat |
| warm | 6 | citypop, rnb, lofi, mixo, borrowed, minorpop | citypop_groove, pop_arp |
| smart | 6 | citypop, rnb, lofi, mixo, borrowed, minorpop | funk_riff |
| uplifting | 6 | citypop, rnb, lofi, mixo, borrowed, minorpop | edm_pulse |
| cheerful | 6 | citypop, rnb, lofi, mixo, borrowed, minorpop | lofi_swing, sixteen_beat |

### Other 类别（25首）
| 调性 | 数量 | 织体 | 情绪 |
|------|------|------|------|
| E | 5 | sixteen_beat, lofi_swing, citypop_groove, funk_riff, edm_pulse | bright, warm, calm |
| B | 5 | sixteen_beat, lofi_swing, citypop_groove, funk_riff, edm_pulse | warm, calm, melancholic |
| Ab | 5 | sixteen_beat, lofi_swing, citypop_groove, funk_riff, edm_pulse | calm, melancholic, lively |
| Db | 5 | sixteen_beat, lofi_swing, citypop_groove, funk_riff, edm_pulse | lively, dramatic |
| Bm | 5 | sixteen_beat, lofi_swing, citypop_groove, funk_riff, edm_pulse | melancholic, dramatic |

## 技术规格

### V2 格式特性
- **绝对定位**：音符携带 offset 字段，精确位置控制
- **自动补休止**：空隙自动填充休止符
- **元数据完整**：pitch_name、measure、beat、end_offset
- **兼容性**：支持 V1 渐进升级

### 现代音乐特征
- **五声音阶骨架**：避免古典音阶跑动
- **切分节奏**：现代律动核心，重音错位
- **现代色彩和弦**：maj7、m7、9th、sus4、借用小iv、♭VII
- **结构统一**：A A' B A'' 四句式，BPM 68-138

### 多语言支持
- **中文**：温柔、明亮、欢快、温暖、潇洒、高昂
- **日文**：優しい、明るい、陽気、温かい、洒落、高揚
- **英文**：gentle、bright、cheerful、warm、smart、uplifting

## 使用指南

### 1. 快速检索
```python
from vibedomuse import template_db

# 多语言检索示例
queries = [
    "明るいcitypopのBGM",           # 日文
    "温暖的R&B伴奏",                # 中文
    "cheerful lofi background",    # 英文
    "dramatic synthwave music"     # 英文
]

for q in queries:
    params = template_db.parse(q)
    results = template_db.search(params, limit=5)
    print(f"{q}: {len(results)} 个结果")
```

### 2. 类别筛选
```python
# 按类别检索
bgm_results = template_db.search(params, category="galgame_bgm")
acc_results = template_db.search(params, category="galgame_accompaniment")
v3_results = template_db.search(params, category="galgame_v3")
```

### 3. 生成新曲目
```python
# 生成现代曲目
import bgm.generate_bgm as g
import accompaniment.generate_accompaniment as a
import other.generate_galgame_v3 as o

# 生成所有现代曲目
modern_bgm = g.build_new_pieces()
modern_acc = a.build_new_pieces()
modern_v3 = o.build_new_pieces()
```

## 文件组织

```
VibeDoMuse/
├── DATABASE_OVERVIEW.md      ← 本文档
├── bgm/                      ← BGM 数据库
│   ├── README.md            ← BGM 专用文档
│   ├── generate_bgm.py      ← BGM 生成脚本
│   └── json/               ← BGM V2 文件（56首）
├── accompaniment/           ← 伴奏数据库
│   ├── README.md            ← 伴奏专用文档
│   ├── generate_accompaniment.py ← 伴奏生成脚本
│   └── json/               ← 伴奏 V2 文件（80首）
├── other/                   ← 三轨曲数据库
│   ├── README.md            ← 三轨曲专用文档
│   ├── generate_galgame_v3.py ← 三轨曲生成脚本
│   └── json/               ← 三轨曲 V2 文件（75首）
└── vibedomuse/              ← 核心模块
    ├── template_db.py      ← 检索引擎
    ├── json_validator.py   ← 格式校验
    └── nl_parser.py        ← 自然语言解析
```

## 版本信息

- **当前版本**：V2 全面升级版
- **总曲目数**：211 首（144 存量 + 67 现代）
- **格式**：全部 V2 格式，支持绝对定位
- **更新时间**：2026-08-22
- **现代风格**：City Pop、Lo-fi、Synthwave、Future Bass、EDM、K-pop Ballad、J-pop、R&B、Funk

## 检索性能

- **响应时间**：< 100ms
- **命中率**：现代曲目前5名命中率 > 80%
- **支持语言**：中文、日文、英文
- **情绪覆盖**：10种主要情绪分类
- **风格覆盖**：9种现代音乐风格