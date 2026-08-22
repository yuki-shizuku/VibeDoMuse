# VibeDoMuse

把灵感 / 自然语言转化为音乐作品的 AI 工具。通过本地 LLM 将文本描述解析为
结构化乐谱（Do-muse JSON），再经 FluidSynth 渲染为 MIDI / WAV 音频，并提供
PyQt6 桌面界面与可选 REST 后端。

An AI tool that turns ideas and natural language into music. It parses text
descriptions into structured scores (Do-muse JSON) via a local LLM, renders
them to MIDI / WAV audio with FluidSynth, and ships with a PyQt6 desktop UI
plus an optional REST backend.

## 功能 Features

- **自然语言 → 乐谱**：输入"一首温柔的钢琴曲"等描述，AI 生成完整乐谱 JSON（V2 绝对定位格式）
- **知识库增强**：自动检索格式规范与 400+ 真实曲库模板作为生成参考
- **两阶段生成**：先意图分析、再生成乐谱，可确认/修改理解后再生成
- **多轨编曲**：支持 BGM、伴奏、三轨交响等类别与任意乐器组合
- **音频渲染**：内置 FluidSynth + 音色库，一键导出 MIDI / WAV
- **批量变体**：一键生成多个种子变体、情绪层（平静/紧张）版本
- **追问修改**：基于已生成曲目，用自然语言反馈继续修改

- **Natural language → score**: describe music in plain words (e.g. "a gentle
  piano piece") and the AI composes a complete score JSON (V2 absolute positioning)
- **Knowledge base**: automatically retrieves the format spec and 400+ real
  template pieces to guide generation
- **Two-stage generation**: intent analysis first, then score generation; you
  can review or edit the understanding before the score is written
- **Multi-track arrangement**: BGM, accompaniment, 3-track ensemble and any
  instrument combination
- **Audio rendering**: bundled FluidSynth + SoundFont, one-click MIDI / WAV export
- **Variants & layers**: generate multiple seed variants or calm/tense layer
  versions of the same theme
- **Follow-up editing**: refine an existing piece through natural-language feedback

## 启动方式 Getting Started

### 方式一：Windows 便携版（无需安装 Python）

Method 1: Windows portable build (no Python required)

1. 获取 `windows/` 发布目录（或解压发布包），保持文件夹结构完整
2. 双击 `DoMuse.exe`，或运行 `run.bat`
3. 首次启动会自动生成 `config.ini`，在 **设置 → LLM 设置** 中填入 LLM 的
   `base_url` / `model` / `api_key` 后即可使用

1. Obtain the `windows/` folder (or unzip the release package) and keep its
   structure intact
2. Double-click `DoMuse.exe`, or run `run.bat`
3. On first launch a `config.ini` is created automatically; fill in the LLM
   `base_url` / `model` / `api_key` under **Settings → LLM Settings**

### 方式二：源码运行（开发模式）

Method 2: Run from source (development)

```bash
# 安装依赖 / install dependencies
pip install -r requirements.txt

# 复制配置模板（首次运行也会自动创建）/ copy config template (auto-created on first run)
cp config.ini.example config.ini

# 启动桌面界面 / launch the desktop UI
python main.py
```
