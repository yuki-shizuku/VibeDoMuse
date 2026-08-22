# -*- coding: utf-8 -*-
"""
VibeDoMuse 简化打包脚本
使用系统Python + PyInstaller 进行打包
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
    build_dir = Path("windows")
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
    
    # 复制前端文件
    frontend_src = Path("frontend_pyqt6")
    if frontend_src.exists():
        frontend_dst = build_dir / "frontend_pyqt6"
        shutil.copytree(frontend_src, frontend_dst)
    
    # 复制知识库
    if Path("knowledge_base").exists():
        shutil.copytree("knowledge_base", build_dir / "knowledge_base")
    
    # 复制文档
    for doc in ["README.md", "DATABASE_OVERVIEW.md", "JSON_Format_Specification.md"]:
        if Path(doc).exists():
            shutil.copy(doc, build_dir)
    
    # 复制配置文件
    for config in ["config.ini.example", "requirements.txt"]:
        if Path(config).exists():
            shutil.copy(config, build_dir)

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
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'scipy', 'pandas'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
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
"""
    spec_path = build_dir / "domuse.spec"
    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    return spec_path

def build_executable(build_dir, spec_file):
    """使用PyInstaller构建可执行文件"""
    print("🔨 构建可执行文件...")
    
    cmd = [sys.executable, "-m", "PyInstaller", str(spec_file)]
    
    try:
        subprocess.run(cmd, check=True, cwd=build_dir)
        print("✅ 构建完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False

def create_launchers(build_dir):
    """创建启动脚本"""
    # 创建启动脚本
    launcher_content = """@echo off
chcp 65001 >nul
echo 启动 VibeDoMuse...
echo.

if exist "python.exe" (
    echo 使用本地Python...
    python "main.py"
) else (
    echo 请确保Python已安装...
    pause
    exit /b 1
)
"""
    
    launcher_path = build_dir / "run.bat"
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_content)

def main():
    """主函数"""
    print("🚀 开始构建 VibeDoMuse Windows 版本...")
    
    # 检查PyInstaller是否安装
    try:
        import PyInstaller
        print("✅ PyInstaller 已安装")
    except ImportError:
        print("❌ PyInstaller 未安装，请先安装: pip install PyInstaller")
        return 1
    
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
    
    # 构建可执行文件
    if build_executable(build_dir, build_dir / "domuse.spec"):
        # 创建启动脚本
        create_launchers(build_dir)
        
        print("\n🎉 构建完成！")
        print(f"📂 输出目录: {build_dir}")
        print("📦 包含文件:")
        print("  - DoMuse.exe (主程序)")
        print("  - run.bat (启动脚本)")
        print("  - domuse.ico (图标)")
        print("  - 所有数据库文件和资源")
        
        # 显示目录大小
        total_size = sum(f.stat().st_size for f in build_dir.rglob('*') if f.is_file())
        print(f"💾 总大小: {total_size / 1024 / 1024:.1f} MB")
        
        print("\n📋 使用说明:")
        print("1. 双击 run.bat 启动程序")
        print("2. 或直接双击 DoMuse.exe")
        print("3. 首次运行会创建配置文件")
    else:
        print("❌ 构建失败")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())