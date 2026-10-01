"""Проверки скриптов именно в Windows PowerShell 5.1."""

import os
from pathlib import Path
import subprocess
import sys

import pytest

PROJECT_DIR = Path(__file__).resolve().parents[1]
SCRIPT_NAMES = ("run_bot.ps1", "install_autostart.ps1", "uninstall_autostart.ps1")


@pytest.mark.skipif(sys.platform != "win32", reason="Требуется Windows PowerShell")
@pytest.mark.parametrize("script_name", SCRIPT_NAMES)
def test_startup_script_parses_in_windows_powershell(script_name: str) -> None:
    """Кириллица не должна нарушать разбор скриптов автозапуска."""
    powershell = Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"
    command = (
        "$tokens=$null; $errors=$null; "
        "[System.Management.Automation.Language.Parser]::ParseFile("
        f"(Join-Path (Get-Location) '{script_name}'), [ref]$tokens, [ref]$errors) | Out-Null; "
        "if ($errors.Count) { exit 1 }"
    )
    result = subprocess.run(
        [str(powershell), "-NoProfile", "-NonInteractive", "-Command", command],
        cwd=PROJECT_DIR, capture_output=True, timeout=20, check=False,
    )
    assert result.returncode == 0, f"Не удалось разобрать {script_name}"
