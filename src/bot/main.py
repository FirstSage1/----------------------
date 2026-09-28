"""Точка инициализации и запуска Telegram-бота."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError, TelegramUnauthorizedError
from aiogram.types import BotCommand

from src.bot.config import load_settings
from src.bot.routers.echo import router as echo_router
from src.bot.routers.help import router as help_router
from src.bot.routers.menu import router as menu_router
from src.bot.routers.start import router as start_router
from src.bot.utils.logging import configure_logging

SESSION_TIMEOUT = 30
STARTUP_TIMEOUT = 20
BOT_COMMANDS = [
    BotCommand(command="start", description="Начать работу с ботом"),
    BotCommand(command="menu", description="Открыть меню"),
    BotCommand(command="help", description="Показать справку"),
]


def create_dispatcher() -> Dispatcher:
    """Создать диспетчер и подключить все роутеры."""
    dispatcher = Dispatcher()
    dispatcher.include_routers(start_router, menu_router, help_router, echo_router)
    return dispatcher


async def run_bot() -> None:
    """Проверить соединение и запустить long polling."""
    settings = load_settings()
    configure_logging((settings.bot_token, settings.bot_proxy or ""))
    session = AiohttpSession(proxy=settings.bot_proxy, timeout=SESSION_TIMEOUT)
    bot = Bot(token=settings.bot_token, session=session)
    dispatcher = create_dispatcher()

    try:
        logging.info(
            "Подключение к Telegram%s...",
            " через прокси" if settings.bot_proxy else "",
        )
        await bot.get_me(request_timeout=STARTUP_TIMEOUT)
        await bot.delete_webhook(drop_pending_updates=False, request_timeout=STARTUP_TIMEOUT)
        await bot.set_my_commands(BOT_COMMANDS, request_timeout=STARTUP_TIMEOUT)
        logging.info("Бот запущен. Ожидание сообщений.")
        await dispatcher.start_polling(bot, close_bot_session=False)
    except TelegramUnauthorizedError:
        logging.error("Telegram отклонил токен. Проверьте BOT_TOKEN в .env")
        raise SystemExit(1) from None
    except TelegramNetworkError:
        logging.error(
            "Нет соединения с Telegram API. Проверьте интернет, VPN или прокси."
        )
        raise SystemExit(1) from None
    finally:
        await bot.session.close()


def main() -> None:
    """Настроить журналирование и запустить асинхронное приложение."""
    configure_logging()
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logging.info("Бот остановлен.")


if __name__ == "__main__":
    main()
