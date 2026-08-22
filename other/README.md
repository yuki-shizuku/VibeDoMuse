# Other 数据库文档

> VibeDoMuse Other 数据库：三轨完整乐曲库，适合主题曲/重要场景/完整曲目。

## 目录结构

```
other/
├── README.md              ← 本文档
├── generate_galgame_v3.py ← 生成脚本（25首现代 + 50首存量）
├── json/                 ← V2 格式 JSON 文件（75首）
│   ├── c_gentle_flowing.json
│   ├── c_gentle_steady.json
│   ├── ...（存量50首）
│   ├── e_bright_sixteen_beat.json
│   ├── b_warm_citypop_groove.json
│   ...（现代25首）
└── old/                  ← V1 格式备份（可选）
```

## 数据规模

| 类别 | 数量 | 说明 |
|------|------|------|
| 存量曲目 | 50 | 原有温柔/流动/脉冲/节奏/稳定等三轨曲 |
| 现代曲目 | 25 | 5新调 × 5现代织体，三轨配置 |
| **总计** | **75** | **全部 V2 格式** |

## 现代曲目架构

### 新增调式（5个）
| 调性 | 特点 | 适用风格 |
|------|------|----------|
| E（E大调） | 明亮温暖 | City Pop、J-pop |
| B（B大调） | 深沉优雅 | R&B、Ballad |
| Ab（降A大调） | 浪漫梦幻 | Synthwave、K-pop |
| Db（降D大调） | 现代感强 | EDM、Future Bass |
| Bm（B小调） | 戏剧张力 | Funk、Dramatic |

### 现代织体（5种）
| 织体 | 特点 | 适用场景 |
|------|------|----------|
| sixteen_beat | 16分音符律动 | 现代 Pop、电子音乐 |
| lofi_swing | Lo-fi 摇摆 | 深夜、放松场景 |
| citypop_groove | City Pop 节奏 | 都市、浪漫场景 |
| funk_riff | Funk 连复段 | 派对、活力场景 |
| edm_pulse | EDM 脉冲 | 电音、未来感 |

### 三轨配置
- **轨道1**：钢琴旋律（主旋律）
- **轨道2**：钢琴织体（节奏/和声）
- **轨道3**：弦乐垫（氛围铺垫）

## 现代曲目示例

### e_bright_sixteen_beat（E大调 明亮16分）
- **调性**：E | **情绪**：bright | **织体**：sixteen_beat
- **BPM**：120 | **配置**：钢琴旋律 + 钢琴织体 + 弦乐垫
- **和弦**：Emaj7 → C#m7 → F#m7 → B7
- **适用**：开场主题曲、活力场景

### b_warm_citypop_groove（B大调 温暖City Pop）
- **调性**：B | **情绪**：warm | **织体**：citypop_groove
- **BPM**：100 | **配置**：钢琴旋律 + 钢琴织体 + 弦乐垫
- **和弦**：Bmaj7 → G#m7 → C#m7 → F#7
- **适用**：浪漫场景、温馨时刻

### ab_lofi_swing（降A大调 Lo-fi摇摆）
- **调性**：Ab | **情绪**：calm | **织体**：lofi_swing
- **BPM**：80 | **配置**：钢琴旋律 + 钢琴织体 + 弦乐垫
- **和弦**：Abmaj7 → Fm7 → Bbm7 → Eb7
- **适用**：深夜场景、放松时刻

### db_funk_riff（降D大调 Funk连复段）
- **调性**：Db | **情绪**：lively | **织体**：funk_riff
- **BPM**：110 | **配置**：钢琴旋律 + 钢琴织体 + 弦乐垫
- **和弦**：Dbmaj7 → Bbm7 → Ebm7 → Ab7
- **适用**：派对场景、活力时刻

### b_melancholic_edm_pulse（B小调 忧郁EDM脉冲）
- **调性**：Bm | **情绪**：melancholic | **织体**：edm_pulse
- **BPM**：100 | **配置**：钢琴旋律 + 钢琴织体 + 弦乐垫
- **和弦**：Bm → D → A → E
- **适用**：悲伤场景、戏剧张力

## 调式-情绪映射表

| 调性 | bright | warm | calm | melancholic | lively | dramatic |
|------|--------|------|------|-------------|--------|----------|
| E | ✓ | | | | | |
| B | | ✓ | | | | |
| Ab | | | ✓ | | | |
| Db | | | | | ✓ | |
| Bm | | | | ✓ | | ✓ |

## 使用方法

### 1. 通过 template_db 检索
```python
from vibedomuse import template_db

# 检索E大调的明亮三轨曲
params = template_db.parse("E大调 明亮三轨曲")
params.category = "galgame_v3"
results = template_db.search(params)
```

### 2. 直接调用生成脚本
```python
import other.generate_galgame_v3 as o

# 生成所有现代三轨曲
scores = o.build_new_pieces()
for name, score in scores.items():
    print(f"生成: {name}")
```

### 3. 文件格式说明
所有文件均为 V2 格式，三轨配置：
- `format: "v2"`
- `tracks[0]`: 钢琴旋律（主旋律）
- `tracks[1]`: 钢琴织体（节奏/和声）
- `tracks[2]`: String Ensemble 1（弦乐垫）
- 每个音符包含 offset 绝对定位

## Modern Expansion

本次更新新增 25 首现代风格三轨曲，特点：
- **新调式探索**：E/B/Ab/Db/Bm 五个现代调式，丰富色彩选择
- **织体创新**：sixteen_beat、citypop_groove、funk_riff、edm_pulse 等现代织体
- **三轨层次**：钢琴旋律 + 钢琴织体 + 弦乐垫，层次丰富
- **五声音阶**：避免古典音阶跑动，现代旋律骨架

生成脚本：`other/generate_galgame_v3.py`  
数据目录：`other/json/`  
总曲目数：75 首（50 存量 + 25 现代）

## 技术特点

- **V2 格式**：绝对定位 offset，空隙自动补休止
- **现代和声**：maj7、m7、9th、sus4、借用小iv、♭VII
- **节奏设计**：切分起拍、附点、16分 groove，重音错位
- **结构统一**：A A' B A'' 四句式，BPM 68-138