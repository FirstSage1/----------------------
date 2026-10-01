$ErrorActionPreference = "Stop"

$TASK_NAME = "TelegramBotAdvancedVibecoding"

if (Get-ScheduledTask -TaskName $TASK_NAME -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TASK_NAME -Confirm:$false
    Write-Output "Автозапуск бота отключён."
}
else {
    Write-Output "Задача автозапуска не найдена."
}
