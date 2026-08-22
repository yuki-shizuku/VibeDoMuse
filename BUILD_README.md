# VibeDoMuse Windows 打包说明

## 📦 打包方式

### 方式一：使用 uv + PyInstaller（推荐）

```bash
# 1. 安装 uv
pip install uv

# 2. 运行打包脚本
python build_windows.py
```

### 方式二：使用系统Python + PyInstaller

```bash
# 1. 安装 PyInstaller
pip install PyInstaller

# 2. 运行简化打包脚本
python build_simple.py
```

## 📁 输出结构

打包完成后会创建 `windows/` 目录，包含：

```
windows/
├── DoMuse.exe              # 主程序（轻量启动器）
├── _internal/              # 多文件打包的依赖目录（Python 运行时、PyQt6、DLL 等）
├── run.bat                 # 启动脚本
├── domuse.ico              # 程序图标
├── bgm/                    # BGM数据库
├── accompaniment/          # 伴奏数据库
├── other/                  # 三轨曲数据库
├── knowledge_base/         # 知识库
├── README.md               # 说明文档
├── DATABASE_OVERVIEW.md    # 数据库总览
└── JSON_Format_Specification.md # 格式规范
```

> 发布版为自包含运行：Python 代码已编译进 `_internal/`（PyInstaller 归档），
> 不再携带 `vibedomuse/`、`frontend_pyqt6/`、`main.py` 源码副本，
> 目标电脑无需安装 Python。

## 🔧 打包特性

- ✅ **多文件打包（onedir）**：轻量 exe + `_internal/` 依赖目录，启动快、便于排查问题
- ✅ **图标集成**：使用 domuse.ico 作为程序图标
- ✅ **无控制台窗口**：GUI模式运行
- ✅ **资源外置**：数据库文件与 exe 同目录，便于更新维护
- ✅ **依赖管理**：自动处理PyQt6等依赖

## 🚀 运行方式

### 方法1：直接运行
```bash
windows/DoMuse.exe
```

### 方法2：使用启动脚本
```bash
cd windows
run.bat
```

## 📋 系统要求

- Windows 10/11
- Python 3.8+（如果使用简化打包）
- 至少 100MB 可用空间

## 🔍 故障排除

### 问题1：PyInstaller未安装
```bash
pip install PyInstaller
```

### 问题2：缺少依赖
```bash
pip install PyQt6>=6.6
```

### 问题3：打包失败
- 检查Python版本是否兼容
- 确保有足够的磁盘空间
- 关杀毒软件重试

### 问题4：运行时错误
- 确保 config.ini 文件存在
- 检查数据库文件完整性
- 查看控制台输出错误信息

## 📊 打包信息

- **程序名称**：DoMuse
- **图标**：domuse.ico
- **输出格式**：Windows 可执行文件 (.exe)
- **运行模式**：GUI 无控制台
- **UPX压缩**：启用

## 🎯 后续优化

- 可以添加数字签名
- 可以创建安装程序 (Inno Setup)
- 可以添加更新机制
- 可以优化启动速度