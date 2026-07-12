# PyInstaller spec for the Windows build. Run with:
#   pyinstaller packaging/windows.spec
# from the project root (see scripts/build_windows.bat). Must be run on
# Windows — PyInstaller does not cross-compile.
import glob
import os

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(SPEC)), ".."))

block_cipher = None


def _pyside6_plugin_binaries() -> list[tuple[str, str]]:
    # PyInstaller's own PySide6 hooks normally locate Qt's plugin DLLs (most
    # importantly platforms/qwindows.dll, without which the app can't start
    # at all — "no Qt platform plugin could be initialized") by importing
    # PySide6.QtCore during analysis. When cross-building under Wine, that
    # import reliably fails (Wine's PE loader chokes on Qt6Core.dll's
    # icuuc.dll delay-load import, which real Windows loads lazily and never
    # actually needs), so the hook silently collects zero plugins. `import
    # PySide6` alone (without `.QtCore`) doesn't trigger that failure, so we
    # locate the plugins directory that way and copy the DLLs in ourselves.
    # Destination mirrors what PyInstaller's runtime hook expects at launch:
    # QT_PLUGIN_PATH = <bundle>/PySide6/plugins.
    import PySide6

    plugins_dir = os.path.join(os.path.dirname(PySide6.__file__), "plugins")
    categories = [
        "platforms",  # required — qwindows.dll; app can't start without it
        "styles",
        "imageformats",
        "iconengines",
        "generic",
        "platforminputcontexts",
    ]
    entries = []
    for category in categories:
        for dll in glob.glob(os.path.join(plugins_dir, category, "*.dll")):
            entries.append((dll, os.path.join("PySide6", "plugins", category)))
    return entries


a = Analysis(
    [os.path.join(PROJECT_ROOT, "main.py")],
    pathex=[PROJECT_ROOT],
    binaries=_pyside6_plugin_binaries(),
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
