# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all


datas = [("client/sounds", "sounds"), ("client/locales", "locales")]
binaries = []
hiddenimports = [
    "wx",
    "cosmos",
    "requests",
    "psutil",
    "websockets",
    "pyperclip",
    "fluent.runtime",
    "fluent.syntax",
]

# collect_all("cosmos") carries cosmos.pyd and the Steam Audio runtime
# (phonon.dll) that sits beside it in the package directory.
for package_name in (
    "accessible_output2",
    "cosmos",
    "requests",
    "fluent",
    "livekit",
    "sounddevice",
    "keyring",
):
    tmp_ret = collect_all(package_name)
    datas += tmp_ret[0]
    binaries += tmp_ret[1]
    hiddenimports += tmp_ret[2]

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
