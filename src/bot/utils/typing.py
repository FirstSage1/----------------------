"""Безопасное отображение статуса набора текста в Telegram."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import suppress
from contextlib import asynccontextmanager

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

TYPING_INTERVAL_SECONDS = 4


async def _send_typing(bot: Bot, chat_id: int) -> None:
    """Отправить статус набора текста, не прерывая основную операцию при сбое."""
    try:
        await bot.send_chat_action(chat_id=chat_id, action="typing")
    except TelegramAPIError:
        # Статус необязателен, поэтому ошибка Telegram не влияет на ответ бота.
        return


async def _keep_typing(bot: Bot, chat_id: int, stop_event: asyncio.Event) -> None:
    """Обновлять статус, пока не завершится длительная операция."""
    while not stop_event.is_set():
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=TYPING_INTERVAL_SECONDS)
        except TimeoutError:
            await _send_typing(bot, chat_id)


@asynccontextmanager
async def typing_status(bot: Bot, chat_id: int) -> AsyncIterator[None]:
    """Показывать «бот печатает» в течение выполнения операции."""
    await _send_typing(bot, chat_id)
    stop_event = asyncio.Event()
    typing_task = asyncio.create_task(_keep_typing(bot, chat_id, stop_event))
    try:
        yield
    finally:
        stop_event.set()
        typing_task.cancel()
        with suppress(asyncio.CancelledError):
            await typing_task
