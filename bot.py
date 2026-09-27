"""Простой Telegram-эхобот на aiogram."""

import asyncio
import logging
import os
from pathlib import Path
from urllib.request import getproxies

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError, TelegramUnauthorizedError
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv


# Загружаем переменные из .env рядом с этим файлом, независимо от текущей папки.
load_dotenv(Path(__file__).with_name(".env"))

TOKEN = (os.getenv("BOT_TOKEN") or "").strip()
if not TOKEN:
    raise RuntimeError(
        "Не задан BOT_TOKEN. Добавьте токен от @BotFather в файл .env"
    )

dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    """Приветствуем пользователя после команды /start."""
    await message.answer(
        "Привет! Я эхобот. Отправь мне сообщение, и я повторю его."
    )


@dp.message()
async def echo_handler(message: Message) -> None:
    """Повторяем полученное сообщение в том же чате."""
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # Некоторые типы сообщений нельзя скопировать через send_copy.
        await message.answer("Я пока не умею повторять этот тип сообщения.")


async def main() -> None:
    """Запускаем бота в режиме long polling."""
    # Используем заданный прокси или настройки системы (включая Windows).
    proxy = os.getenv("BOT_PROXY") or getproxies().get("https")
    session = AiohttpSession(proxy=proxy, timeout=30)
    bot = Bot(token=TOKEN, session=session)
    try:
        logging.info("Подключение к Telegram%s...", " через прокси" if proxy else "")
        me = await bot.get_me(request_timeout=20)
        # Переключаемся на polling, сохраняя необработанные сообщения.
        await bot.delete_webhook(drop_pending_updates=False, request_timeout=20)
        logging.info("Бот запущен: @%s", me.username)
        await dp.start_polling(bot)
    except TelegramUnauthorizedError:
        logging.error("Telegram отклонил токен. Проверьте BOT_TOKEN в файле .env")
        raise SystemExit(1) from None
    except TelegramNetworkError:
        logging.error(
            "Нет соединения с Telegram API. Проверьте интернет, VPN или настройки прокси."
        )
        raise SystemExit(1) from None
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен.")
