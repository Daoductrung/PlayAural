# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs


datas = [
    ("client/sounds", "sounds"),
    ("client/locales", "locales"),
    ("cosmos/LICENSE", "cosmos"),
]
binaries = collect_dynamic_libs("cosmos")
hiddenimports = [
    "wx",
    "cosmos",
    "cosmos.cosmos",
    "requests",
    "psutil",
    "websockets",
    "fluent.runtime",
    "fluent.syntax",
    "livekit.rtc",
    "livekit.rtc.resources",
]

# Keep only the package resources used at runtime. Broad collect_all() calls
# also copy source modules and *.dist-info metadata as loose files. PyInstaller
# already analyzes the Python modules, and its standard hooks collect the
# accessible_output2 DLLs, sounddevice's PortAudio DLL, and keyring's backends.
# Keyring's hook intentionally retains its distribution metadata because its
# runtime backend discovery reads the entry points declared there.
datas += collect_data_files(
    "cosmos",
    includes=["third_party/steam_audio/*"],
)
datas += collect_data_files(
    "livekit.rtc",
    includes=["resources/livekit_ffi.dll", "resources/LICENSE.md"],
)

hiddenimports += [
    "keyring.backends",
    "keyring.backends.Windows",
    "keyring.backends.fail",
    "win32ctypes.core",
    "win32ctypes.pywin32",
]


a = Analysis(
    ["client\\client.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PlayAural",
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="PlayAural",
)
