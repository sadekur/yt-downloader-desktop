@echo off
REM Builds a full Windows installer: dist\installer\YT-Downloader-Setup.exe.
REM Run this ON WINDOWS from the project root (PyInstaller does not
REM cross-compile from Linux/macOS to Windows):
REM
REM   scripts\build_windows.bat
REM
REM Requires:
REM   - A venv with requirements.txt + requirements-build.txt installed:
REM       python -m venv .venv
REM       .venv\Scripts\activate
REM       pip install -r requirements.txt -r requirements-build.txt
REM   - Inno Setup 6 installed (https://jrsoftware.org/isdl.php), so ISCC.exe
REM     is either on PATH or at its default install location.
REM
REM ffmpeg.exe/ffprobe.exe are fetched automatically (not checked into git)
REM and bundled into the .exe, so the installed app needs no separate
REM ffmpeg install on the target machine.

setlocal

set VENV_PYTHON=.venv\Scripts\python.exe
if not exist "%VENV_PYTHON%" (
    echo Virtual environment not found at %VENV_PYTHON%.
    echo Create it first: python -m venv .venv ^&^& .venv\Scripts\activate ^&^& pip install -r requirements.txt -r requirements-build.txt
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File scripts\fetch_ffmpeg_windows.ps1
if errorlevel 1 exit /b 1

"%VENV_PYTHON%" -m PyInstaller packaging\windows.spec --noconfirm
if errorlevel 1 exit /b 1

set ISCC="%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC=ISCC.exe

%ISCC% packaging\installer.iss
if errorlevel 1 (
    echo.
    echo ISCC.exe not found. Install Inno Setup 6 from https://jrsoftware.org/isdl.php
    echo then re-run this script.
    exit /b 1
)

echo.
echo Build complete: dist\installer\YT-Downloader-Setup.exe
echo This is a self-contained installer -- ffmpeg is bundled, nothing else
echo needs to be installed on the target machine.
