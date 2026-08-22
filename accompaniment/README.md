# Accompaniment 数据库文档

> VibeDoMuse Accompaniment 数据库：和声伴奏库，适合对话/过场/情绪铺垫。

## 目录结构

```
accompaniment/
├── README.md              ← 本文档
├── generate_accompaniment.py ← 生成脚本（30首现代 + 50首存量）
├── json/                 ← V2 格式 JSON 文件（80首）
│   ├── gentle_カノン.json
│   ├── gentle_4516.json
│   ├── ...（存量50首）
│   ├── bright_citypop.json
│   ├── warm_rnb.json
│   ...（现代30首）
└── old/                  ← V1 格式备份（可选）
```

## 数据规模

| 类别 | 数量 | 说明 |
|------|------|------|
| 存量曲目 | 50 | 原有温柔/优雅/轻快/清爽等情绪伴奏 |
| 现代曲目 | 30 | 5现代情绪 × 6现代和声进行 × 现代织体 |
| **总计** | **80** | **全部 V2 格式** |

## 现代曲目架构

### 情绪分类（5种）
| 情绪 | 中文 | 特点 |
|------|------|------|
| bright | 明亮 | 活力四射，积极向上 |
| warm | 温暖 | 柔和舒适，治愈系 |
| smart | 潇洒 | 爵士感，都市风 |
| uplifting | 高昂 | 激励人心，希望感 |
| cheerful | 欢快 | 轻松愉快，元气满满 |

### 和声进行（6种）
| 进行 | 特点 | 代表和弦 |
|------|------|----------|
| citypop | City Pop 风格 | Cmaj7 → Bm7 → Em7 → Am7 |
| rnb | R&B 风格 | Bbmaj7 → Gm7 → Cm7 → F7 |
| lofi | Lo-fi 风格 | Am7 → Dm7 → G7 → Cmaj7 |
| mixo | Mixolydian 调式 | G → D → Em → C |
| borrowed | 借用和弦 | C → F → Gm → C |
| minorpop | 小流行风格 | Am → G → C → F |

### 现代织体（6种）
| 织体 | 特点 | 适用场景 |
|------|------|----------|
| sixteen_beat | 16分音符律动 | 现代 Pop、电子音乐 |
| lofi_swing | Lo-fi 摇摆 | 深夜学习、放松时光 |
| citypop_groove | City Pop 节奏 | 都市夜景、浪漫场景 |
| funk_riff | Funk 连复段 | 派对、活力场景 |
| edm_pulse | EDM 脉冲 | 电音、未来感 |
| pop_arp | 流行琶音 | 温馨、治愈场景 |

## 现代曲目示例

### bright_citypop（明亮 City Pop）
- **情绪**：bright | **和声**：citypop | **织体**：sixteen_beat
- **调性**：C | **BPM**：120
- **和弦**：Cmaj7 → Bm7 → Em7 → Am7
- **乐器**：双轨钢琴（旋律 + 织体）

### warm_rnb（温暖 R&B）
- **情绪**：warm | **和声**：rnb | **织体**：citypop_groove
- **调性**：Bb | **BPM**：90
- **和弦**：Bbmaj7 → Gm7 → Cm7 → F7
- **乐器**：双轨钢琴（旋律 + 织体）

### smart_funk（潇洒 Funk）
- **情绪**：smart | **和声**：funk_riff | **织体**：funk_riff
- **调性**：G | **BPM**：110
- **和弦**：G → D → Em → C
- **乐器**：双轨钢琴（旋律 + 织体）

### uplifting_edm（高昂 EDM）
- **情绪**：uplifting | **和声**：edm_pulse | **织体**：edm_pulse
- **调性**：D | **BPM**：128
- **和弦**：D → Bm → G → A
- **乐器**：双轨钢琴（旋律 + 织体）

### cheerful_lofi（欢快 Lo-fi）
- **情绪**：cheerful | **和声**：lofi | **织体**：lofi_swing
- **调性**：F | **BPM**：100
- **和弦**：F → Gm → Am → Dm
- **乐器**：双轨钢琴（旋律 + 织体）

## 情绪-织体映射表

| 情绪 | sixteen_beat | lofi_swing | citypop_groove | funk_riff | edm_pulse | pop_arp |
|------|--------------|------------|----------------|-----------|-----------|---------|
| bright | ✓ | | ✓ | | | |
| warm | | | ✓ | | | ✓ |
| smart | | | | ✓ | | |
| uplifting | | | | | ✓ | |
| cheerful | ✓ | ✓ | | | | |

## 使用方法

### 1. 通过 template_db 检索
```python
from vibedomuse import template_db

# 检索温暖的 R&B 伴奏
params = template_db.parse("warm rnb accompaniment")
results = template_db.search(params, category="galgame_accompaniment")
```

### 2. 直接调用生成脚本
```python
import accompaniment.generate_accompaniment as a

# 生成所有现代伴奏
scores = a.build_new_pieces()
for name, score in scores.items():
    print(f"生成: {name}")
```

### 3. 文件格式说明
所有文件均为 V2 格式，双轨钢琴配置：
- `format: "v2"`
- `tracks[0]`: 钢琴旋律轨道
- `tracks[1]`: 钢琴织体轨道
- 每个音符包含 offset 绝对定位

## Modern Expansion

本次更新新增 30 首现代风格伴奏，特点：
- **情绪驱动**：5种现代情绪分类，覆盖多元场景
- **和声进行**：6种现代和声进行，包括 City Pop、R&B、Lo-fi、Mixolydian 等
- **织体创新**：6种现代织体，16分音符、Funk 连复段、EDM 脉冲等
- **双轨设计**：钢琴旋律 + 钢琴织体，层次丰富

生成脚本：`accompaniment/generate_accompaniment.py`  
数据目录：`accompaniment/json/`  
总曲目数：80 首（50 存量 + 30 现代）