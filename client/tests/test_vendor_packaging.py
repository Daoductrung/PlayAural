"""Release-packaging checks for vendored desktop dependencies."""

from pathlib import Path
from zipfile import ZipFile


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def test_cosmos_wheel_retains_runtime_license_notices():
    wheels = list((REPOSITORY_ROOT / "client" / "vendor").glob("cosmos-*.whl"))

    assert len(wheels) == 1
    with ZipFile(wheels[0]) as wheel:
        entries = set(wheel.namelist())
        metadata_name = next(
            name for name in entries if name.endswith(".dist-info/METADATA")
        )
        metadata = wheel.read(metadata_name).decode("utf-8")

        assert "License-Expression: MIT" in metadata
        assert any(name.endswith(".dist-info/licenses/LICENSE") for name in entries)
        assert "cosmos/phonon.dll" in entries
        for name in (
            "LICENSE.md",
            "THIRDPARTY.md",
            "TRADEMARK_RIGHTS.md",
            "UPSTREAM.json",
        ):
            path = f"cosmos/third_party/steam_audio/{name}"
            assert path in entries
            assert wheel.getinfo(path).file_size > 0


def test_cosmos_source_and_python_package_use_the_same_license():
    source_license = REPOSITORY_ROOT / "cosmos" / "LICENSE"
    package_license = REPOSITORY_ROOT / "cosmos" / "cosmos-python" / "LICENSE"

    assert source_license.read_bytes() == package_license.read_bytes()
