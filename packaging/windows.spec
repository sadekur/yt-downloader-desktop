# PyInstaller spec for the Windows build. Run with:
#   pyinstaller packaging/windows.spec
# from the project root (see scripts/build_windows.bat). Must be run on
# Windows — PyInstaller does not cross-compile.
import os

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(SPEC)), ".."))

block_cipher = None

a = Analysis(
    [os.path.join(PROJECT_ROOT, "main.py")],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=[
        (os.path.join(PROJECT_ROOT, "app", "resources"), os.path.join("app", "resources")),
        *collect_data_files("qt_material"),
    ],
    hiddenimports=collect_submodules("yt_dlp"),
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
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
    # Passing binaries/zipfiles/datas here (rather than to a COLLECT step)
    # produces a single-file .exe.
    name="YT Downloader",
    icon=os.path.join(PROJECT_ROOT, "app", "resources", "icon.ico"),
    console=False,
)
