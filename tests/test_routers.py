"""Проверки обработки сообщений без подключения к Telegram."""

import asyncio
from unittest.mock import AsyncMock

from aiogram.types import Message, MessageEntity, ReplyKeyboardMarkup, ReplyKeyboardRemove

from src.bot.routers.echo import echo_handler, hide_menu_handler
from src.bot.routers.menu import MENU_KEYBOARD, MENU_TEXT, menu_handler


def test_text_echo_preserves_formatting_entities() -> None:
    """Текст и Telegram-сущности форматирования передаются без изменений."""
    message = AsyncMock(spec=Message)
    message.answer = AsyncMock()
    message.send_copy = AsyncMock()
    message.text = "Жирный текст"
    message.entities = [MessageEntity(type="bold", offset=0, length=7)]

    asyncio.run(echo_handler(message))

    message.answer.assert_awaited_once_with(
        "Жирный текст",
        entities=[MessageEntity(type="bold", offset=0, length=7)],
    )
    message.send_copy.assert_not_awaited()


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

    message.answer.assert_awaited_once_with(MENU_TEXT, reply_markup=MENU_KEYBOARD)


def test_hide_menu_removes_keyboard() -> None:
    """Кнопка скрытия меню убирает клавиатуру."""
    message = AsyncMock(spec=Message)
    message.answer = AsyncMock()
    asyncio.run(hide_menu_handler(message))

    reply_markup = message.answer.await_args.kwargs["reply_markup"]
    assert isinstance(reply_markup, ReplyKeyboardRemove)
    assert reply_markup.remove_keyboard is True
