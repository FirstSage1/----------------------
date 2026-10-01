$ErrorActionPreference = "Stop"

$RESTART_DELAY_SECONDS = 15
$PYTHON_PATH = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$MUTEX_NAME = "Local\TelegramBotAdvancedVibecodingRunner"

# Переходим в папку проекта, чтобы .env всегда находился рядом с ботом.
Set-Location -LiteralPath $PSScriptRoot

if (-not (Test-Path -LiteralPath $PYTHON_PATH)) {
    Write-Error "Не найдено виртуальное окружение .venv. Создайте его командой: python -m venv .venv"
}

$mutex = [System.Threading.Mutex]::new($false, $MUTEX_NAME)
$ownsMutex = $false
try {
    try {
        $ownsMutex = $mutex.WaitOne(0)
    }
    catch [System.Threading.AbandonedMutexException] {
        $ownsMutex = $true
    }
    if (-not $ownsMutex) {
        Write-Output "Скрипт запуска бота уже работает."
        exit 0
    }

    while ($true) {
        # Отдельный процесс не превращает сообщения Python в ошибки PowerShell 5.1.
        $process = Start-Process -FilePath $PYTHON_PATH -ArgumentList @("-u", "-m", "src.bot") -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru
        $process.WaitForExit()
        Write-Warning "Бот завершился с кодом $($process.ExitCode). Повторный запуск через $RESTART_DELAY_SECONDS секунд."
        Start-Sleep -Seconds $RESTART_DELAY_SECONDS
    }
}
finally {
    if ($ownsMutex) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
