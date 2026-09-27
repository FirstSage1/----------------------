$ErrorActionPreference = "Stop"

# Переходим в папку проекта, чтобы .env всегда находился рядом с ботом.
Set-Location -LiteralPath $PSScriptRoot

if (-not (Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
    Write-Error "Не найдено виртуальное окружение .venv. Создайте его командой: python -m venv .venv"
}

& ".venv\Scripts\python.exe" "-m" "src.bot"
exit $LASTEXITCODE
