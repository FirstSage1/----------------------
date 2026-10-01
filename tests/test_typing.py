"""Проверки индикатора набора текста."""

import asyncio
from unittest.mock import AsyncMock

from aiogram.exceptions import TelegramNetworkError

from src.bot.utils.typing import typing_status


def test_typing_status_starts_before_operation() -> None:
    """Статус набора текста отправляется при начале ожидания."""
    bot = AsyncMock()

    async def run() -> None:
        async with typing_status(bot, 1):
            pass

    asyncio.run(run())

    bot.send_chat_action.assert_awaited_once_with(chat_id=1, action="typing")


def test_typing_status_does_not_block_operation_on_telegram_error() -> None:
    """Ошибка статуса не отменяет длительную операцию."""
    bot = AsyncMock()
    bot.send_chat_action.side_effect = TelegramNetworkError(method=AsyncMock(), message="Сеть недоступна")
    completed = False

    async def run() -> None:
        nonlocal completed
        async with typing_status(bot, 1):
            completed = True

    asyncio.run(run())

    assert completed is True
