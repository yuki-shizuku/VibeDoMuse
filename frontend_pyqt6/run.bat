@echo off
setlocal
REM VibeDoMuse 启动器（Windows）— 自动探测可用的 Python（已装 PyQt6），不再硬编码用户路径
set "PROJECT_DIR=%~dp0.."
cd /d "%PROJECT_DIR%"

set "PY="

REM 1) 项目同级的本地 venv（推荐）
if exist "%PROJECT_DIR%\.venv\Scripts\python.exe" set "PY=%PROJECT_DIR%\.venv\Scripts\python.exe"
if not defined PY if exist "%PROJECT_DIR%\venv\Scripts\python.exe" set "PY=%PROJECT_DIR%\venv\Scripts\python.exe"

REM 2) 常见用户级隔离 venv（WorkBuddy 托管环境）
if not defined PY if exist "%USERPROFILE%\.workbuddy\binaries\python\envs\default\Scripts\python.exe" set "PY=%USERPROFILE%\.workbuddy\binaries\python\envs\default\Scripts\python.exe"

REM 3) 系统 Python（py launcher 优先，其次 PATH 中的 python）
if not defined PY (
  where py >nul 2>nul
  if not errorlevel 1 set "PY=py -3"
)
if not defined PY (
  where python >nul 2>nul
  if not errorlevel 1 set "PY=python"
)

if not defined PY (
  echo [错误] 未找到 Python。请安装 Python 3.10+ 并确保 python 在 PATH 中。
  pause
  exit /b 1
)

echo 使用 Python: %PY%
%PY% main.py
endlocal
