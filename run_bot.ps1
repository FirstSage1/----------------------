$ErrorActionPreference = "Stop"

$RESTART_DELAY_SECONDS = 15
$PYTHON_PATH = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

# Переходим в папку проекта, чтобы .env всегда находился рядом с ботом.
Set-Location -LiteralPath $PSScriptRoot

if (-not (Test-Path -LiteralPath $PYTHON_PATH)) {
    Write-Error "Не найдено виртуальное окружение .venv. Создайте его командой: python -m venv .venv"
}

while ($true) {
    & $PYTHON_PATH "-m" "src.bot"
    $exitCode = $LASTEXITCODE

    # Неверный токен не исправится повторным запуском и требует ручной проверки.
    if ($exitCode -eq 1) {
        Write-Error "Бот остановлен из-за ошибки конфигурации. Проверьте .env и запустите скрипт заново."
        exit $exitCode
    }

    Write-Warning "Бот завершился с кодом $exitCode. Повторный запуск через $RESTART_DELAY_SECONDS секунд."
    Start-Sleep -Seconds $RESTART_DELAY_SECONDS
}
