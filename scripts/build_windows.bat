@echo off
REM Builds YT Downloader.exe. Run this ON WINDOWS from the project root
REM (PyInstaller does not cross-compile from Linux/macOS to Windows):
REM
REM   scripts\build_windows.bat
REM
REM Requires a venv with requirements.txt + requirements-build.txt installed:
REM   python -m venv .venv
REM   .venv\Scripts\activate
REM   pip install -r requirements.txt -r requirements-build.txt

setlocal

set VENV_PYTHON=.venv\Scripts\python.exe
if not exist "%VENV_PYTHON%" (
    echo Virtual environment not found at %VENV_PYTHON%.
    echo Create it first: python -m venv .venv ^&^& .venv\Scripts\activate ^&^& pip install -r requirements.txt -r requirements-build.txt
    exit /b 1
)

"%VENV_PYTHON%" -m PyInstaller packaging\windows.spec --noconfirm
if errorlevel 1 exit /b 1

echo.
echo Build complete: dist\YT Downloader.exe
echo Make sure ffmpeg.exe is on the target machine's PATH (see README) --
echo it is not bundled into the .exe.
