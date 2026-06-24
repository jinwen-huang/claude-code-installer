@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo   Claude Code 一键安装工具 - 打包脚本
echo ========================================
echo.

echo [1/3] 安装依赖...
pip install -r requirements.txt
pip install pyinstaller
echo.

echo [2/3] 清理旧构建产物...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist ClaudeInstaller.spec del /q ClaudeInstaller.spec
echo.

echo [3/3] 打包为 exe...
pyinstaller --onefile --windowed ^
    --name "ClaudeCode安装工具" ^
    --add-data "core;core" ^
    --add-data "installers;installers" ^
    --icon NONE ^
    main.py
echo.

echo ========================================
echo   打包完成！exe 在 dist/ 目录
echo ========================================
pause
