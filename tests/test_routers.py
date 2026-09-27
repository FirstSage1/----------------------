"""Проверки обработки сообщений без подключения к Telegram."""

import asyncio
from unittest.mock import AsyncMock

from aiogram.types import Message

from src.bot.routers.echo import echo_handler


def test_text_keeps_entities() -> None:
    """Форматирование передаётся вместе с текстом."""
    message = AsyncMock(spec=Message)
    message.answer = AsyncMock()
    message.send_copy = AsyncMock()
    message.text = "Привет"
    message.entities = []
    asyncio.run(echo_handler(message))
    message.answer.assert_awaited_once_with("Привет", entities=[])


def test_unsupported_message_has_reply() -> None:
    """Неподдерживаемое сообщение не прерывает обработчик."""
    message = AsyncMock(spec=Message)
    message.answer = AsyncMock()
    message.send_copy = AsyncMock()
    message.text = None
    message.chat = type("ChatStub", (), {"id": 1})()
    message.send_copy.side_effect = TypeError("unsupported")
    asyncio.run(echo_handler(message))
    message.answer.assert_awaited_once()
