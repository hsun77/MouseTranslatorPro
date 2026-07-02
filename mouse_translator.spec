# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules
from pathlib import Path


hiddenimports = []
hiddenimports += collect_submodules("pynput")
hiddenimports += collect_submodules("pyautogui")
icon_path = "assets/icon.ico" if Path("assets/icon.ico").exists() else None


a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("config.example.json", "."),
        ("logs/.gitkeep", "logs"),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="MouseTranslatorPro",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="MouseTranslatorPro",
)
