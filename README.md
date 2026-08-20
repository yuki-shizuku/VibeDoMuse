# VibeDoMuse

把灵感/自然语言转化为音乐作品的 AI 工具：通过 LLM 将文本描述解析为结构化乐谱 JSON，
再经 FluidSynth 渲染为音频，并提供 PyQt6 桌面界面与可选 REST 后端。

## 功能

- 基于 LLM 的文本 → 结构化乐谱（JSON）解析与生成
- 内置知识库检索（`knowledge_base/`）
- FluidSynth 渲染 MIDI → 音频
- PyQt6 桌面前端 + 可选 REST 后端（`vibedomuse/server.py`）

## 目录结构

| 路径 | 说明 |
| --- | --- |
| `vibedomuse/` | 核心库：解析、生成、渲染、LLM 客户端、配置 |
| `frontend_pyqt6/` | PyQt6 桌面界面（`run.bat` 入口） |
| `accompaniment/`、`bgm/`、`other/` | 乐谱 / 模板数据 |
| `knowledge_base/` | 知识库文档 |
| `main.py` | 项目根入口，启动桌面 GUI |

## 快速开始

1. 安装依赖：`pip install -r requirements.txt`
2. 复制配置模板：`cp config.ini.example config.ini`，按需填写 LLM 的 `base_url` / `model` / `api_key`
3. 准备运行时资源（见下方「资源」）
4. 运行：

   ```bash
   python main.py
   # 或直接：frontend_pyqt6/run.bat
   ```

## 配置

LLM 参数与服务器参数位于项目根目录 `config.ini`（首次运行由 `main.py` 自动创建，
已被 `.gitignore` 忽略，不会提交）。也可在桌面端 **设置 → LLM 设置** 中图形化修改。

## 资源（二进制，未纳入版本库）

以下文件体积较大或为平台相关的运行时，未纳入 Git 版本库，请按本地环境自行准备，
或改用 Git LFS / GitHub Releases 管理：

- `bin/DoMuse.exe` —— 约 64MB
- `fluidsynth/` —— FluidSynth 运行时（约 6MB）
- `32MbGMStereo.sf2` —— 音色文件（约 32MB）

## 说明

本仓库只包含源码、数据与文档，不含大型二进制与用户配置。如需在团队 / CI 中复现运行环境，
请单独管理上述资源，并基于 `config.ini.example` 生成本地 `config.ini`。
