@echo off
chcp 65001 >nul
title OmniCapture for Obsidian
cd /d "%~dp0"

echo ========================================================
echo   正在启动 OmniCapture for Obsidian...
echo   快捷键:
echo     Alt + J : 闪念速记
echo     Alt + X : 截图标注 / 截图翻译
echo ========================================================

if exist "C:\Users\gaore\AppData\Local\Programs\Python\Python312\python.exe" (
    "C:\Users\gaore\AppData\Local\Programs\Python\Python312\python.exe" desktop\app.py
) else (
    python desktop\app.py
)

if errorlevel 1 (
    echo.
    echo 启动出错，请查看上方报错信息。
    pause
)
