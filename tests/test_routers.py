"""Проверки обработки сообщений без подключения к Telegram."""

import asyncio
from unittest.mock import AsyncMock

from aiogram.types import Message

from src.bot.routers.echo import echo_handler, hide_menu_handler
from src.bot.routers.menu import MENU_TEXT, menu_handler


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


def test_menu_shows_commands() -> None:
    """Команда меню выводит подсказки и клавиатуру."""
    message = AsyncMock(spec=Message)
    message.answer = AsyncMock()
    asyncio.run(menu_handler(message))
    message.answer.assert_awaited_once()
    assert message.answer.await_args.args[0] == MENU_TEXT


def test_hide_menu_removes_keyboard() -> None:
    """Кнопка скрытия меню убирает клавиатуру."""
    message = AsyncMock(spec=Message)
    message.answer = AsyncMock()
    asyncio.run(hide_menu_handler(message))
    message.answer.assert_awaited_once()
