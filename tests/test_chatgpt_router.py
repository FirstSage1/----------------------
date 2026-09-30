"""Проверки режима ChatGPT без обращения к сети."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from aiogram.types import Message

from src.bot.routers import chatgpt


def _message(chat_id: int = 1, text: str = "Вопрос") -> Message:
    message = AsyncMock(spec=Message)
    message.answer = AsyncMock()
    message.chat = type("ChatStub", (), {"id": chat_id})()
    message.text = text
    return message


def test_chatgpt_command_enables_mode_and_clears_history() -> None:
    """Команда включает режим и сбрасывает предыдущий диалог."""
    service = MagicMock()
    service.reset = MagicMock()
    chatgpt._service = service
    chatgpt._active_chats.clear()
    message = _message()

    asyncio.run(chatgpt.chatgpt_command_handler(message))

    assert 1 in chatgpt._active_chats
    service.reset.assert_called_once_with(1)


def test_chatgpt_message_returns_service_answer() -> None:
    """В активном режиме ответ сервиса отправляется пользователю."""
    service = AsyncMock()
    service.ask.return_value = "Ответ модели"
    chatgpt._service = service
    chatgpt._active_chats.clear()
    chatgpt._active_chats.add(1)
    message = _message()

    asyncio.run(chatgpt.chatgpt_message_handler(message))

    service.ask.assert_awaited_once_with(1, "Вопрос")
    assert message.answer.await_count == 2
    assert message.answer.await_args_list[0].args == ("⏳ Обрабатываю вопрос…",)
    assert message.answer.await_args_list[1].args == ("Ответ модели",)
