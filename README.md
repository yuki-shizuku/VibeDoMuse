# VibeDoMuse

把灵感 / 自然语言转化为音乐作品的 AI 工具：通过 LLM 将文本描述解析为结构化乐谱 JSON，
再经 FluidSynth 渲染为音频，并提供 PyQt6 桌面界面与可选 REST 后端。

## 功能

- 基于 LLM 的文本 → 结构化乐谱（JSON）解析与生成
- 内置知识库检索（`knowledge_base/`）
- 144 个 Do-muse 模板（bgm / accompaniment / other）的自然语言检索与匹配
- FluidSynth 渲染 MIDI → 音频
- PyQt6 桌面前端 + 可选 REST 后端（`vibedomuse/server.py`）

## 目录结构

| 路径 | 说明 |
| --- | --- |
| `vibedomuse/` | 核心库：解析、生成、渲染、LLM 客户端、配置 |
| `frontend_pyqt6/` | PyQt6 桌面界面（`run.bat` 入口） |
| `accompaniment/`、`bgm/`、`other/` | 乐谱 / 模板数据（JSON + 文档） |
| `knowledge_base/` | 知识库文档（检索与示例） |
| `main.py` | 项目根入口，启动桌面 GUI |
| `build_windows.ps1` | Windows 便携版打包脚本（uv + PyInstaller） |
| `config.ini.example` | 配置模板（复制为 `config.ini` 使用） |
| `windows/` | ⚠️ 打包产物，**不纳入版本库**（见下方说明） |

## 快速开始

1. 安装依赖：`pip install -r requirements.txt`（当前仅需 `PyQt6>=6.6`）
2. 复制配置模板：`cp config.ini.example config.ini`，按需填写 LLM 的 `base_url` / `model` / `api_key`
   （首次运行若不存在 `config.ini` 也会自动创建默认配置）
3. 准备运行时资源（见下方「资源」）
4. 运行：

   ```bash
   python main.py
   # 或直接：frontend_pyqt6/run.bat
   ```

## 配置

LLM 参数与服务器参数位于项目根目录 `config.ini`（已被 `.gitignore` 忽略，不会提交，
请勿将含 API Key 的配置推送到仓库）。也可在桌面端 **设置 → LLM 设置** 中图形化修改。

## 资源（二进制，未纳入版本库）

以下文件体积较大或为平台相关的运行时，未纳入 Git 版本库，请按本地环境自行准备，
或改用 Git LFS / GitHub Releases 管理：

- `bin/DoMuse.exe` —— 约 64MB
- `fluidsynth/` —— FluidSynth 运行时（Windows 预编译版，约 6MB）
- `32MbGMStereo.sf2` —— 音色文件（约 32MB）

> 运行时代码（`vibedomuse/_paths.py`）会自动在仓库根目录 / exe 目录 / `_internal`
> 等候选位置查找上述资源；缺失时仅相关渲染功能不可用，程序可正常启动。

## Windows 便携版打包

仓库内的 `build_windows.ps1` 使用 `uv` + PyInstaller 将项目打包为可直接分发的
`windows/` 文件夹（`--onedir --windowed`，图标 `domuse.ico`）：

```powershell
# 在项目根目录执行
powershell -ExecutionPolicy Bypass -File build_windows.ps1
```

- 产物为 `windows/` 整目录，可复制到任意 Windows 环境直接运行（无需安装 Python）
- 首次运行自动在 `windows/` 内生成 `config.ini`
- `windows/` 已被 `.gitignore` 忽略，建议通过 GitHub Releases 发布便携版

## 上传至 GitHub 的说明

本仓库只包含源码、数据与文档，以下内容一律**不纳入版本库**（已由 `.gitignore` 忽略）：

- 构建产物：`windows/`、`build_pyinstaller/`、`*.spec`、`build_windows.log`
- 二进制 / 大型资源：`bin/`、`fluidsynth/`、`*.sf2`、`*.dll`、`*.exe`、`*.pyd`
- 虚拟环境与缓存：`.venv/`、`.venv_build/`、`venv/`、`__pycache__/`
- 运行配置与输出：`config.ini`（含 API Key）、`generated/`
- 本地工作数据：`.workbuddy/`
