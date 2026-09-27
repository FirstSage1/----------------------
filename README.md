# Простой эхобот

Бот повторяет сообщения пользователя в Telegram. Он написан на Python с использованием `aiogram` и загружает токен из файла `.env`.

## Подготовка

1. Создайте бота у [@BotFather](https://t.me/BotFather) и получите токен.
2. Установите Python 3.10 или новее. В папке проекта создайте виртуальное окружение и установите зависимости:

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### macOS и Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

3. Если `.env` ещё нет, скопируйте `.env.example` в `.env` и укажите токен:

```dotenv
BOT_TOKEN=123456:your-token-from-BotFather
```

## Запуск

В PowerShell из папки проекта (активация окружения не требуется):

```powershell
.\.venv\Scripts\python.exe bot.py
```

Либо запустите готовый скрипт из PowerShell:

```powershell
.\run_bot.ps1
```

Если PowerShell запрещает выполнение скриптов, используйте команду с `python.exe` выше.

На macOS и Linux:

```bash
.venv/bin/python bot.py
```

Дождитесь строки «Бот запущен», затем отправьте боту `/start` и любое сообщение в Telegram. Оставьте терминал открытым: бот отвечает, пока работает программа. Для остановки нажмите `Ctrl+C`. Запускайте только один экземпляр бота с этим токеном. Файл `main.py` содержит отдельный учебный пример; для бота используйте `bot.py`.

## Соединение с Telegram

Бот автоматически использует HTTPS-прокси из настроек системы. Если доступ к Telegram обеспечивается программой VPN/прокси, она должна оставаться включённой. При необходимости задайте свой адрес в `.env`:

```dotenv
BOT_PROXY=http://127.0.0.1:10809
```

Адрес выше — пример; порт должен совпадать с настройками вашей программы. Пустой или отсутствующий `BOT_PROXY` означает автоматический выбор системного прокси.

Если появляется сообщение о соединении с Telegram API, проверьте интернет и VPN: бот работает через Telegram Bot API и не сможет получать сообщения при блокировке доступа к `api.telegram.org`.

Настройка прокси соответствует [документации aiogram](https://docs.aiogram.dev/en/latest/api/session/aiohttp.html).
