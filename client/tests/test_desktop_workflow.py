from pathlib import Path
import tomllib


CLIENT_DIR = Path(__file__).resolve().parents[1]


def test_client_dev_extra_installs_test_tools():
    pyproject = tomllib.loads((CLIENT_DIR / "pyproject.toml").read_text())

    dev_deps = pyproject["project"]["optional-dependencies"]["dev"]

    assert any(dep.startswith("pytest") for dep in dev_deps)
    assert any(dep.startswith("pytest-asyncio") for dep in dev_deps)
    assert any(dep.startswith("pytest-xdist") for dep in dev_deps)


def test_run_client_syncs_development_dependencies():
    script = (CLIENT_DIR / "run_client.bat").read_text(encoding="utf-8").lower()

    assert "uv sync --extra dev" in script
    assert "uv pip install" not in script


def test_main_window_applies_server_locale_without_restart_prompt():
    source = (CLIENT_DIR / "ui" / "main_window.py").read_text(encoding="utf-8")

    assert 'self._apply_locale_change(packet.get("locale", "en"))' in source
    assert "Localization.set_locale(locale)" in source
    assert "options-restart-required-message" not in source


def test_welcome_sound_has_one_server_ordering_authority():
    repo_root = CLIENT_DIR.parent
    client_handlers = [
        CLIENT_DIR / "ui" / "main_window.py",
        repo_root / "web_client" / "app.js",
        repo_root / "mobile_client" / "src" / "app" / "PlayAuralApp.tsx",
    ]

    for handler in client_handlers:
        source = handler.read_text(encoding="utf-8")
        assert "playSound(\"welcome.ogg\"" not in source
        assert 'playSound({ name: "welcome.ogg"' not in source
        assert 'sound_manager.play("welcome.ogg"' not in source

    for pack in ("client", "web_client", "mobile_client"):
        assert (repo_root / pack / "sounds" / "welcome.ogg").is_file()


def test_all_clients_adopt_server_canonical_username_after_authorization():
    repo_root = CLIENT_DIR.parent
    network_source = (CLIENT_DIR / "network_manager.py").read_text(encoding="utf-8")
    window_source = (CLIENT_DIR / "ui" / "main_window.py").read_text(
        encoding="utf-8"
    )
    web_source = (repo_root / "web_client" / "app.js").read_text(encoding="utf-8")
    mobile_source = (
        repo_root / "mobile_client" / "src" / "app" / "PlayAuralApp.tsx"
    ).read_text(encoding="utf-8")

    assert 'canonical_username = packet.get("username")' in network_source
    assert 'self.credentials["username"] = canonical_username' in window_source
    assert "username: packet.username || this.lastUser" in web_source
    assert "this.elements.username.value = packet.username" in web_source
    assert "credentialsRef.current.username = authPacket.username" in mobile_source
    assert "setUsername(authPacket.username);" in mobile_source
