import json
import subprocess
import sys


def test_installed_cli_demo_and_config_error(tmp_path):
    config = tmp_path / "demo.toml"
    config.write_text(
        f"state_dir = {json.dumps(str(tmp_path / 'state'))}\n"
        '[[accounts]]\nname = "demo"\nprovider = "demo"\n'
    )
    command = [sys.executable, "-m", "cap_runtime.cli", "--config", str(config)]
    probe = subprocess.run([*command, "doctor", "--probe"], capture_output=True, text=True)
    assert probe.returncode == 0
    assert json.loads(probe.stdout)["accounts"][0]["connection"] == "connected"
    briefing = subprocess.run([*command, "briefing"], capture_output=True, text=True)
    assert briefing.returncode == 0
    assert json.loads(briefing.stdout)["complete"]
    config.write_text('SECRET_CONTENT = "should-not-be-echoed"\n')
    invalid = subprocess.run([*command, "doctor"], capture_output=True, text=True)
    assert invalid.returncode == 2
    assert "SECRET_CONTENT" not in invalid.stderr
