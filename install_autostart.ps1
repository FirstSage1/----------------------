$ErrorActionPreference = "Stop"

$TASK_NAME = "TelegramBotAdvancedVibecoding"
$RUNNER_PATH = Join-Path $PSScriptRoot "run_bot.ps1"
$POWERSHELL_PATH = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"
$START_CHECK_SECONDS = 3

if (-not (Test-Path -LiteralPath $RUNNER_PATH)) {
    Write-Error "Не найден скрипт запуска: $RUNNER_PATH"
}

# Путь передаётся одним аргументом, а файл читается как UTF-8 с BOM.
$taskArguments = "-NoProfile -NonInteractive -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$RUNNER_PATH`""

# Задача запускается для текущего пользователя при каждом входе в Windows.
$identity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$action = New-ScheduledTaskAction -Execute $POWERSHELL_PATH -Argument $taskArguments -WorkingDirectory $PSScriptRoot
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $identity
$principal = New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $TASK_NAME -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Автоматический запуск Telegram-бота" -Force | Out-Null
Start-ScheduledTask -TaskName $TASK_NAME
Start-Sleep -Seconds $START_CHECK_SECONDS
if ((Get-ScheduledTask -TaskName $TASK_NAME).State -ne "Running") {
    $result = (Get-ScheduledTaskInfo -TaskName $TASK_NAME).LastTaskResult
    throw "Задание не работает. Код Планировщика: $result"
}
Write-Output "Задание запущено. Подключение бота проверьте в logs\bot.log."
