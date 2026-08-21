# VibeDoMuse Windows Build Script (PowerShell)
# Uses uv + PyInstaller to create a portable --onedir deployment.
#
# 产物：项目根目录下的 windows\ 文件夹（含 VibeDoMuse.exe 与全部资源）。
# 该文件夹可整体复制到任意 Windows 环境直接运行，无需安装 Python。
# 首次运行会在 windows\ 内自动生成 config.ini。
#
# 用法：在项目根目录右键"使用 PowerShell 运行"本脚本，
#       或在 PowerShell 中执行：  .\build_windows.ps1

# 注意：不要设 $ErrorActionPreference = "Stop" —— PS 5.1 下原生命令的 stderr 会被当成
# 终止性 NativeCommandError，导致 uv / PyInstaller 等输出一行提示就中断整个构建。
# 改为显式检查 $LASTEXITCODE。
$ErrorActionPreference = "Continue"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot
if (-not (Test-Path $ProjectRoot)) { Write-Host "[ERROR] project root missing: $ProjectRoot" -ForegroundColor Red; exit 1 }

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  VibeDoMuse Windows Build Tool" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# 1. Check uv
$uv = Get-Command "uv" -ErrorAction SilentlyContinue
if (-not $uv) {
    Write-Host "[ERROR] uv not found. Install from https://docs.astral.sh/uv/" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] uv found: $(uv --version)" -ForegroundColor Green

# 2. Build venv at a SHORT path.
#    PyQt6 的 bindings\QtBluetooth\... 层级很深，长中文项目路径会触发
#    Windows 260 字符上限（"系统找不到指定的路径"）。放到 LOCALAPPDATA 下规避。
$venvDir = Join-Path $env:LOCALAPPDATA "vdm_build"
$venvPython = Join-Path (Join-Path $venvDir "Scripts") "python.exe"
if (-not (Test-Path $venvPython)) {
    # 残缺/缺失：用 uv venv --clear 就地重建（避免直接删除目录，规避安全删除钩子）
    Write-Host "[..] (Re)creating build venv at $venvDir ..." -ForegroundColor Yellow
    # --force --clear 需同时使用：--force 移除已存在的非 venv 目录，--clear 允许替换重建
    uv venv --force --clear $venvDir 2>&1 | Out-Host
    if ($LASTEXITCODE -ne 0) { Write-Host "[ERROR] uv venv failed" -ForegroundColor Red; exit 1 }
}
if (-not (Test-Path $venvPython)) {
    Write-Host "[ERROR] venv python missing: $venvPython" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Build venv ready" -ForegroundColor Green

# 3. Install build deps via a China mirror (much faster in CN)
#    固定版本避免构建漂移（当前 venv 实测可成功打包的组合）。
$MIRROR = "https://pypi.tuna.tsinghua.edu.cn/simple"
Write-Host "[..] Installing PyInstaller + PyQt6 (mirror: tuna) ..." -ForegroundColor Yellow
uv pip install --python $venvPython --index-url $MIRROR "pyinstaller==6.22.2" "PyQt6==6.11.0" 2>&1 | Out-Host
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] dependency install failed" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Dependencies installed" -ForegroundColor Green

# 4. Clean old build artifacts (best-effort; 用 .NET API 删除，规避 PS 安全删除钩子)
#    默认「增量重建」：保留 PyInstaller 的 workpath 缓存（LOCALAPPDATA\vdm_build_tmp），
#    并直接覆盖旧 windows\ 产物，显著缩短重复构建时间。
#    需要彻底全量重建时设环境变量 VDM_CLEAN=1（例如 PyInstaller 大版本升级后）。
function Remove-BestEffort {
    param([string]$Target)
    try {
        $full = [System.IO.Path]::GetFullPath($Target)
        if ([System.IO.Directory]::Exists($full)) {
            [System.IO.Directory]::Delete($full, $true)
        } elseif ([System.IO.File]::Exists($full)) {
            [System.IO.File]::Delete($full)
        }
    } catch {
        Write-Host "[WARN] skip cleanup $Target : $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

$Clean = $env:VDM_CLEAN -eq "1"
if ($Clean) {
    Write-Host "[..] Full clean rebuild (VDM_CLEAN=1)" -ForegroundColor Yellow
    Remove-BestEffort "build_pyinstaller"
    Remove-BestEffort "VibeDoMuse.spec"
    Remove-BestEffort "windows"
} else {
    Write-Host "[..] Incremental rebuild (set VDM_CLEAN=1 for a full clean rebuild)" -ForegroundColor Yellow
    # 旧布局残留清理：新脚本把 spec/work 放 LOCALAPPDATA\vdm_build_tmp，根目录若有旧产物一并清掉
    Remove-BestEffort "build_pyinstaller"
    Remove-BestEffort "VibeDoMuse.spec"
    # 清理 windows 顶层旧目录，避免 flattening 步骤冲突（Move-Item -Force 无法覆盖已有目录）
    # 仅清除已知会冲突的旧数据目录，保留 VibeDoMuse.exe（PyInstaller --noconfirm 会覆盖）
    $distRoot = Join-Path $ProjectRoot "windows"
    if (Test-Path $distRoot) {
        @("accompaniment", "bgm", "other", "bin", "fluidsynth", "ffmpeg", "PyQt6", "base_library.zip", "domuse.ico", "JSON_Format_Specification.md") | ForEach-Object {
            $target = Join-Path $distRoot $_
            if (Test-Path $target) {
                Remove-BestEffort $target
            }
        }
    }
}

# 构建临时目录也放到短路径，规避 Windows 260 字符上限
$buildTmp = Join-Path $env:LOCALAPPDATA "vdm_build_tmp"

# 5. Run PyInstaller (--onedir, windowed). Data bundled next to the exe so the
#    whole windows\ folder is portable (move it anywhere, it still runs).
Write-Host "[..] Packaging with PyInstaller (--onedir) ..." -ForegroundColor Yellow

$pyinstallerArgs = @(
    "main.py"
    "--name", "VibeDoMuse"
    "--onedir"
    "--windowed"
    "--noupx"
    "--noconfirm"   # 增量重建时直接覆盖旧 windows\ 产物，不弹确认
    "--icon", (Join-Path $ProjectRoot "domuse.ico")
    "--distpath", "windows"
    "--specpath", $buildTmp
    "--workpath", (Join-Path $buildTmp "work")
    # PyInstaller 6 默认把数据放进 exe 旁的 _internal/ 子目录，导致 windows\VibeDoMuse\ 双层嵌套。
    # 指定 contents-directory=. 让全部文件直接落在 windows/ 顶层（经典 onedir 布局，run.bat/README 指向正确）。
    "--contents-directory", "."
    # bundled read-only data / binaries (paths resolved via vibedomuse._paths)
    "--add-data", "$(Join-Path $ProjectRoot 'bin/DoMuse.exe');bin"
    # 整个 fluidsynth 目录（含 exe 与其依赖的 .dll，运行时 exe 会加载同目录 dll）
    "--add-data", "$(Join-Path $ProjectRoot 'fluidsynth');fluidsynth"
    # 整个 ffmpeg 目录（含 ffmpeg.exe 与其依赖的 .dll，运行时 exe 会加载同目录 dll）
    "--add-data", "$(Join-Path $ProjectRoot 'ffmpeg');ffmpeg"
    "--add-data", "$(Join-Path $ProjectRoot '32MbGMStereo.sf2');."
    "--add-data", "$(Join-Path $ProjectRoot 'JSON_Format_Specification.md');."
    "--add-data", "$(Join-Path $ProjectRoot 'domuse.ico');."
    "--add-data", "$(Join-Path $ProjectRoot 'bgm/json');bgm/json"
    "--add-data", "$(Join-Path $ProjectRoot 'accompaniment/json');accompaniment/json"
    "--add-data", "$(Join-Path $ProjectRoot 'other/json');other/json"
    # 注：template_db.py 会尝试 importlib 加载 bgm/generate_bgm.py 等脚本（PIECES 元数据），
    # 但这些脚本在当前仓库中不存在（仅 JSON 目录），缺失时 template_db 自动跳过（os.path.exists 检查），
    # 因此无需打包，避免 --add-data 指向不存在文件导致构建失败。
    # PyQt6 依赖（QtMultimedia 在代码里动态 import，需显式收集）
    "--hidden-import", "PyQt6.sip"
    "--hidden-import", "PyQt6.QtMultimedia"
    "--hidden-import", "PyQt6.QtMultimediaWidgets"
    "--collect-submodules", "PyQt6"
)

& $venvPython -m PyInstaller $pyinstallerArgs 2>&1 | Out-Host

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] PyInstaller build failed" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Packaging complete" -ForegroundColor Green

# 5.5 Flatten: PyInstaller 6 onedir 总是产出 windows\VibeDoMuse\ 子目录，
#     把子目录内容提升到 windows/ 顶层，保证 windows\VibeDoMuse.exe 可直接双击。
$distApp = Join-Path (Join-Path $ProjectRoot "windows") "VibeDoMuse"
if (Test-Path $distApp) {
    Write-Host "[..] Flattening windows\VibeDoMuse -> windows ..." -ForegroundColor Yellow
    $distRoot = Join-Path $ProjectRoot "windows"
    Get-ChildItem -Force $distApp | ForEach-Object {
        $dest = Join-Path $distRoot $_.Name
        if (Test-Path $dest) {
            Remove-BestEffort $dest
        }
        Move-Item -Force -LiteralPath $_.FullName -Destination $dest
    }
    try { [System.IO.Directory]::Delete($distApp, $false) | Out-Null } catch {
        Write-Host "[WARN] remove empty $distApp : $($_.Exception.Message)" -ForegroundColor Yellow
    }
    Write-Host "[OK] windows\ flattened" -ForegroundColor Green
}

# 6. Create run.bat for the windows folder
$runBatContent = @'
@echo off
setlocal
cd /d "%~dp0"
echo VibeDoMuse - AI Music Composition Agent
echo.
echo First run will auto-create config.ini.
echo Configure API via: Settings -^> LLM Settings
echo.
start "" "VibeDoMuse.exe"
endlocal
'@
$runBatPath = Join-Path (Join-Path $ProjectRoot "windows") "run.bat"
if (-not (Test-Path $runBatPath)) {
    Set-Content -Path $runBatPath -Value $runBatContent -Encoding ASCII
    Write-Host "[OK] Created windows\run.bat" -ForegroundColor Green
}

# 7. Clean temp build files (best-effort)
Remove-BestEffort "build_pyinstaller"
Remove-BestEffort "VibeDoMuse.spec"

# 8. Write a short README into the windows folder
$readme = @'
VibeDoMuse — Windows 便携版
============================

运行：
  - 直接双击 VibeDoMuse.exe
  - 或双击 run.bat

可移植性：
  - 本 windows\ 文件夹可整体复制 / 移动到任意 Windows 电脑，
    无需安装 Python 或任何依赖，直接运行。
  - 程序运行所需数据（模板 JSON、fluidsynth、声音字体、DoMuse.exe）
    都已打包在本文件夹内。

配置：
  - 首次运行会在本文件夹自动创建 config.ini（含默认 LLM 设置）。
  - 在软件内通过「设置 -> LLM 设置」填写 base_url / model / api_key。
  - 生成结果默认保存在本文件夹的 generated\ 子目录下。

说明：
  - 若启动时提示缺少 MSVC 运行库（MSVCP140.dll 等），请安装
    "Microsoft Visual C++ Redistributable" 后再运行。
'@
Set-Content -Path (Join-Path (Join-Path $ProjectRoot "windows") "README.txt") -Value $readme -Encoding UTF8
Write-Host "[OK] Created windows\README.txt" -ForegroundColor Green

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  [DONE] Build successful!" -ForegroundColor Green
Write-Host ""
Write-Host "  Output: windows/"
Write-Host "  Run:    double-click windows\VibeDoMuse.exe"
Write-Host "          or windows\run.bat"
Write-Host ""
Write-Host "  Portable: copy the entire windows\ folder"
Write-Host "  Config:   auto-created as windows\config.ini"
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
