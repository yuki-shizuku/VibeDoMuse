# -*- coding: utf-8 -*-
"""
VibeDoMuse Windows 打包脚本
使用 uv + PyInstaller 将项目打包为可执行文件
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def setup_environment():
    """设置打包环境"""
    project_root = Path(__file__).parent
    os.chdir(project_root)
    return project_root

def create_build_dir():
    """创建构建目录"""
    build_dir = Path("windows_build")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir()
    return build_dir

def copy_resources(build_dir):
    """复制资源文件"""
    print("📁 复制资源文件...")
    
    # 复制主要文件
    shutil.copy("main.py", build_dir)
    shutil.copy("domuse.ico", build_dir)
    
    # 复制vibedomuse模块
    shutil.copytree("vibedomuse", build_dir / "vibedomuse")
    
    # 复制数据库文件
    for category in ["bgm", "accompaniment", "other"]:
        src = Path(category)
        dst = build_dir / category
        if src.exists():
            shutil.copytree(src, dst)
            print(f"  ✓ 复制 {category}/ 数据库 ({len(list(src.rglob('*.json')))} 个文件)")
    
    # 复制ffmpeg
    if Path("ffmpeg").exists():
        shutil.copytree("ffmpeg", build_dir / "ffmpeg")
        print(f"  ✓ 复制 ffmpeg/ 库")
    
    # 复制前端文件
    frontend_src = Path("frontend_pyqt6")
    if frontend_src.exists():
        frontend_dst = build_dir / "frontend_pyqt6"
        shutil.copytree(frontend_src, frontend_dst)
        print(f"  ✓ 复制 frontend_pyqt6/ 界面模块")
    
    # 复制知识库
    if Path("knowledge_base").exists():
        shutil.copytree("knowledge_base", build_dir / "knowledge_base")
        print(f"  ✓ 复制 knowledge_base/ 文档")
    
    # 复制文档
    for doc in ["README.md", "DATABASE_OVERVIEW.md", "JSON_Format_Specification.md"]:
        if Path(doc).exists():
            shutil.copy(doc, build_dir)
            print(f"  ✓ 复制 {doc}")
    
    # 复制配置文件
    for config in ["config.ini.example", "requirements.txt"]:
        if Path(config).exists():
            shutil.copy(config, build_dir)
            print(f"  ✓ 复制 {config}")
    
    # 检查外部二进制文件（这些需要用户单独提供）
    binary_files = [
        "bin/DoMuse.exe",
        "32MbGMStereo.sf2",
        "fluidsynth/fluidsynth-v2.5.7-win10-x64-cpp11/bin/fluidsynth.exe"
    ]
    
    missing_binaries = []
    for binary in binary_files:
        src = Path(binary)
        if src.exists():
            dst = build_dir / binary
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  ✓ 复制 {binary}")
        else:
            missing_binaries.append(binary)
    
    if missing_binaries:
        print(f"  ⚠️ 缺少外部二进制文件（需要手动添加）:")
        for binary in missing_binaries:
            print(f"    - {binary}")
    
    print("📁 资源复制完成")

def create_spec_file(build_dir):
    """创建PyInstaller规范文件"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[r'.'],
    binaries=[],
    datas=[
        ('domuse.ico', '.'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtMultimedia',
        'PyQt6.QtMultimediaWidgets',
        'vibedomuse',
        'vibedomuse.agent',
        'vibedomuse.config',
        'vibedomuse.generator',
        'vibedomuse.history_manager',
        'vibedomuse.json_validator',
        'vibedomuse.json_writer',
        'vibedomuse.knowledge',
        'vibedomuse.llm_client',
        'vibedomuse.music_theory',
        'vibedomuse.nl_parser',
        'vibedomuse.renderer',
        'vibedomuse.server',
        'vibedomuse.template_db',
        'vibedomuse._paths',
        'json',
        'json.encoder',
        'json.decoder',
        'urllib',
        'urllib.request',
        'urllib.error',
        'http',
        'http.client',
        'socket',
        'ssl',
        'hashlib',
        'struct',
        'wave',
        'tempfile',
        'configparser',
        'logging',
        'os',
        'sys',
        'time',
        'random',
        'shutil',
        'subprocess',
        're',
        'io',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tkinter',
        'test',
        'tests',
        'pytest',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# onedir（多文件）模式：exe 只含 bootloader 与清单，Python 代码与依赖
# 经 COLLECT 输出到 exe 旁的 _internal/ 目录。启动更快、便于排查，
# 也符合本项目"exe + 资源目录同层"的发布布局。
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DoMuse',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='domuse.ico',
    uac_admin=False,
    version='version.txt' if os.path.exists('version.txt') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DoMuse',
)
"""
    spec_path = build_dir / "domuse.spec"
    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    return spec_path

def install_dependencies(build_dir):
    """使用uv安装依赖"""
    print("📦 安装依赖...")
    os.chdir(build_dir)
    
    # 使用uv创建虚拟环境并安装依赖
    try:
        print("  创建虚拟环境...")
        subprocess.run([sys.executable, "-m", "uv", "venv"], check=True, capture_output=True)
        
        # 确定虚拟环境Python路径
        if os.name == 'nt':
            venv_python = build_dir / ".venv" / "Scripts" / "python.exe"
        else:
            venv_python = build_dir / ".venv" / "bin" / "python"
        
        # 检查虚拟环境Python是否存在
        if not venv_python.exists():
            print(f"❌ 虚拟环境Python不存在: {venv_python}")
            return None
            
        print(f"  虚拟环境创建成功: {venv_python}")
        
        # 安装PyQt6
        print("  安装PyQt6...")
        subprocess.run([str(venv_python), "-m", "pip", "install", "PyQt6>=6.6"], check=True, capture_output=True)
        print("✅ 依赖安装完成")
        return str(venv_python)
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        if e.stdout:
            print(f"输出: {e.stdout}")
        if e.stderr:
            print(f"错误: {e.stderr}")
        return None

def build_executable(build_dir, spec_file, venv_python):
    """使用PyInstaller构建可执行文件"""
    print("🔨 构建可执行文件...")
    
    # 切换到构建目录（spec 用绝对路径，且必须在 chdir 之前基于项目根解析，
    # 否则相对路径会基于构建目录再次拼接）
    original_cwd = os.getcwd()
    spec_abs = str(Path(spec_file).resolve())
    os.chdir(build_dir)
    
    try:
        if venv_python:
            # 使用虚拟环境中的Python
            cmd = [venv_python, "-m", "PyInstaller", spec_abs]
        else:
            # 使用系统Python
            cmd = [sys.executable, "-m", "PyInstaller", spec_abs]
        
        # 添加详细输出参数以便调试
        cmd.extend(["--log-level", "INFO"])
        print(f"  执行命令: {' '.join(cmd)}")
        
        subprocess.run(cmd, check=True, capture_output=False, text=True)
        print("✅ 构建完成")
        
        # onedir 产物（dist/DoMuse/ 下的 DoMuse.exe + _internal/ 等）并入
        # 构建目录根，与资源目录同层（_paths.py 从 exe 目录解析资源）。
        build_root_abs = Path(spec_abs).parent
        onedir_out = build_root_abs / "dist" / "DoMuse"
        if onedir_out.is_dir():
            for item in onedir_out.iterdir():
                dst = build_root_abs / item.name
                if dst.exists():
                    if dst.is_dir():
                        shutil.rmtree(dst)
                    else:
                        dst.unlink()
                shutil.move(str(item), str(dst))
            shutil.rmtree(build_root_abs / "dist", ignore_errors=True)
            print(f"✅ onedir 产物已并入构建目录根 ({onedir_out} -> {build_root_abs})")
        
        # 检查生成的文件（用 spec 的绝对路径定位，避免 chdir 后相对路径失效）
        exe_path = build_root_abs / "DoMuse.exe"
        if exe_path.exists():
            exe_size = exe_path.stat().st_size / 1024 / 1024  # MB
            print(f"✅ 可执行文件生成: {exe_path} ({exe_size:.1f} MB)")
        else:
            print("⚠️ 警告: 未找到生成的可执行文件")
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        if e.stdout:
            print(f"标准输出: {e.stdout}")
        if e.stderr:
            print(f"错误输出: {e.stderr}")
        return False
    finally:
        # 恢复原始工作目录
        os.chdir(original_cwd)

def create_installer(build_dir):
    """创建安装器脚本"""
    installer_content = """@echo off
chcp 65001 >nul
cls
echo ================================================================
echo                   VibeDoMuse 安装程序
echo ================================================================
echo.

echo 正在检查安装文件...
echo.

if not exist "DoMuse.exe" (
    echo [错误] 找不到主程序 DoMuse.exe
    echo.
    echo 请确保以下文件存在：
    echo   - DoMuse.exe (主程序)
    echo   - domuse.ico (图标文件)
    echo   - vibedomuse/ (核心模块)
    echo   - frontend_pyqt6/ (界面模块)
    echo   - bgm/, accompaniment/, other/ (数据库)
    echo   - ffmpeg/ (可选，用于音频导出)
    echo.
    echo 缺少文件，请检查安装包完整性。
    pause
    exit /b 1
)

echo [√] 主程序文件检查通过

if not exist "vibedomuse" (
    echo [错误] 找不到核心模块目录
    pause
    exit /b 1
)

echo [√] 核心模块检查通过

REM 检查可选的外部二进制文件
set MISSING_EXTERNAL=0

if not exist "bin/DoMuse.exe" (
    echo [警告] 找不到外部工具 bin/DoMuse.exe
    echo   音乐生成功能将不可用
    set MISSING_EXTERNAL=1
)

if not exist "fluidsynth/32MbGMStereo.sf2" (
    echo [警告] 找不到音色文件 fluidsynth/32MbGMStereo.sf2
    echo   音频渲染功能将不可用
    set MISSING_EXTERNAL=1
)

if not exist "fluidsynth/fluidsynth-v2.5.7-win10-x64-cpp11/bin/fluidsynth.exe" (
    echo [警告] 找不到 FluidSynth 播放器
    echo   音频渲染功能将不可用
    set MISSING_EXTERNAL=1
)

if %MISSING_EXTERNAL%==1 (
    echo.
    echo [提示] 可以从以下地址获取缺失的外部文件：
    echo   - GitHub Releases: https://github.com/your-repo/vibedomuse/releases
    echo   - 本地开发环境: 从 bin/ 和 fluidsynth/ 目录复制
    echo.
)

echo.
echo 正在创建配置文件...
if not exist "config.ini" (
    echo [√] 自动创建默认配置文件 config.ini
) else (
    echo [√] 配置文件已存在
)

echo.
echo 正在创建桌面快捷方式...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\\DoMuse.lnk'); $s.TargetPath = '%~dp0DoMuse.exe'; $s.WorkingDirectory = '%~dp0'; $s.Save()" >nul 2>&1

if exist "%USERPROFILE%\Desktop\DoMuse.lnk" (
    echo [√] 桌面快捷方式创建成功
) else (
    echo [警告] 桌面快捷方式创建失败
)

echo.
echo ================================================================
echo                      安装完成！
echo ================================================================
echo.
echo 🎵  VibeDoMuse 已成功安装到当前目录
echo.
echo 📝  使用说明：
echo    • 双击 DoMuse.exe 启动程序
echo    • 首次运行请配置 LLM 设置（设置 → LLM 设置）
echo    • 详细文档请参考 README.md
echo.
echo ⚠️  重要提醒：
echo    • 如果缺少外部二进制文件，部分功能可能不可用
echo    • 生成的音乐文件保存在 generated/ 目录中
echo    • 配置文件 config.ini 包含 API 密钥，请勿泄露
echo.
echo 🌐  官方网站：https://github.com/your-repo/vibedomuse
echo.
pause
"""
    
    installer_path = build_dir / "install.bat"
    with open(installer_path, 'w', encoding='utf-8') as f:
        f.write(installer_content)
    
    # 创建启动脚本
    launcher_content = """@echo off
chcp 65001 >nul
echo 启动 VibeDoMuse...
echo.

if exist ".venv\\Scripts\\python.exe" (
    echo 使用虚拟环境...
    ".venv\\Scripts\\python.exe" "main.py"
) else (
    echo 使用系统Python...
    python "main.py"
)
"""
    
    launcher_path = build_dir / "run.bat"
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_content)

def main():
    """主函数"""
    print("🚀 开始构建 VibeDoMuse Windows 版本...")
    
    # 设置环境
    project_root = setup_environment()
    print(f"📍 项目根目录: {project_root}")
    
    # 创建构建目录
    build_dir = create_build_dir()
    print(f"📁 构建目录: {build_dir}")
    
    # 复制资源
    copy_resources(build_dir)
    print("✅ 资源复制完成")
    
    # 创建规范文件
    spec_file = create_spec_file(build_dir)
    print("✅ 规范文件创建完成")
    
    # 跳过虚拟环境创建，直接使用系统Python进行构建
    print("🔨 使用系统Python进行构建...")
    venv_python = None  # 不使用虚拟环境
    
    # 构建可执行文件
    if build_executable(build_dir, spec_file, venv_python):
        # 创建安装器
        create_installer(build_dir)
        
        print("\n🎉 构建完成！")
        print(f"📂 输出目录: {build_dir}")
        print("📦 包含文件:")
        print("  - DoMuse.exe (主程序)")
        print("  - install.bat (安装程序)")
        print("  - run.bat (启动脚本)")
        print("  - domuse.ico (图标)")
        print("  - 所有数据库文件和资源")
        print("  - 可选：外部二进制文件（如果存在）")
        
        # 显示目录大小
        total_size = sum(f.stat().st_size for f in build_dir.rglob('*') if f.is_file())
        print(f"💾 总大小: {total_size / 1024 / 1024:.1f} MB")
        
        # 显示使用说明
        print("\n📋 使用说明:")
        print("  1. 运行 install.bat 进行安装")
        print("  2. 或直接双击 DoMuse.exe 启动")
        print("  3. 首次运行请配置 LLM 设置")
        
        # 检查关键文件
        critical_files = [
            "DoMuse.exe",
            "vibedomuse/__init__.py",
            "frontend_pyqt6/main.py",
            "config.ini.example"
        ]
        
        missing_critical = []
        build_root = Path(build_dir).resolve()
        for file in critical_files:
            if not (build_root / file).exists():
                missing_critical.append(file)
        
        if missing_critical:
            print(f"\n⚠️ 缺少关键文件: {', '.join(missing_critical)}")
        
    else:
        print("❌ 构建失败")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())