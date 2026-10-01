$ErrorActionPreference = "Stop"

$TASK_NAME = "TelegramBotAdvancedVibecoding"
$RUNNER_PATH = Join-Path $PSScriptRoot "run_bot.ps1"

if (-not (Test-Path -LiteralPath $RUNNER_PATH)) {
    Write-Error "Не найден скрипт запуска: $RUNNER_PATH"
}

# Кодировка Base64 исключает искажение кириллического пути Планировщиком заданий.
$command = "& '$($RUNNER_PATH.Replace("'", "''"))'"
$encodedCommand = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))
$taskArguments = "-NoProfile -NonInteractive -ExecutionPolicy Bypass -WindowStyle Hidden -EncodedCommand $encodedCommand"

# Задача запускается для текущего пользователя при каждом входе в Windows.
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $taskArguments
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:UserName
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TASK_NAME -Action $action -Trigger $trigger -Settings $settings -Description "Автоматический запуск Telegram-бота" -Force | Out-Null
Start-ScheduledTask -TaskName $TASK_NAME
Write-Output "Автозапуск настроен. Бот запущен в фоне."
