"""Проверки режима ChatGPT без обращения к сети."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, call

import pytest
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message

from src.bot.routers import chatgpt


@pytest.fixture(autouse=True)
def isolate_chat_state(monkeypatch: pytest.MonkeyPatch) -> None:
    """Не переносить состояние сервиса и чатов между тестами."""
    monkeypatch.setattr(chatgpt, "_service", None)
    monkeypatch.setattr(chatgpt, "_active_chats", set())


def _message(chat_id: int = 1, text: str = "Вопрос") -> Message:
    message = AsyncMock(spec=Message)
    message.answer = AsyncMock()
    status = AsyncMock()
    status.delete = AsyncMock()
    message.answer.return_value = status
    message.bot = AsyncMock()
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
    assert message.answer.await_args_list == [call("Бот печатает…"), call("Ответ модели")]
    message.answer.return_value.delete.assert_awaited_once()


def test_chatgpt_message_continues_after_typing_status_error() -> None:
    """Ошибка индикатора не должна отменять запрос к сервису."""
    service = AsyncMock()
    service.ask.return_value = "Ответ модели"
    chatgpt._service = service
    chatgpt._active_chats.clear()
    chatgpt._active_chats.add(1)
    message = _message()
    message.bot.send_chat_action.side_effect = TelegramAPIError(
        method=MagicMock(), message="Сбой статуса"
    )

    asyncio.run(chatgpt.chatgpt_message_handler(message))

    service.ask.assert_awaited_once_with(1, "Вопрос")
    assert message.answer.await_args_list == [call("Бот печатает…"), call("Ответ модели")]


def test_waiting_message_visible_until_answer_is_delivered() -> None:
    """Во время ожидания статус существует, удаление выполняется после ответа."""
    message = _message()
    service = AsyncMock()
    chatgpt._service = service

    async def run() -> None:
        started = asyncio.Event()
        release = asyncio.Event()

        async def ask(chat_id: int, question: str) -> str:
            started.set()
            await release.wait()
            return "Ответ модели"

        service.ask.side_effect = ask
        task = asyncio.create_task(chatgpt.chatgpt_message_handler(message))
        try:
            await asyncio.wait_for(started.wait(), timeout=1)
            message.answer.assert_awaited_once_with("Бот печатает…")
            message.answer.return_value.delete.assert_not_awaited()
        finally:
            release.set()
            await task

        assert message.answer.await_args_list[-1] == call("Ответ модели")
        message.answer.return_value.delete.assert_awaited_once()

    asyncio.run(run())


def test_service_error_replaces_waiting_message() -> None:
    """Ошибка ИИ заменяет статус, чтобы не оставлять ложное ожидание."""
    message = _message()
    service = AsyncMock()
    service.ask.side_effect = chatgpt.AnyModelError("Сервис недоступен")
    chatgpt._service = service

    asyncio.run(chatgpt.chatgpt_message_handler(message))

    message.answer.assert_awaited_once_with("Бот печатает…")
    message.answer.return_value.edit_text.assert_awaited_once_with(
        "Не удалось получить ответ: Сервис недоступен"
    )


def test_status_deletion_failure_does_not_lose_answer() -> None:
    """Недоступное удаление статуса не мешает получить ответ."""
    message = _message()
    service = AsyncMock()
    service.ask.return_value = "Ответ модели"
    chatgpt._service = service
    message.answer.return_value.delete.side_effect = TelegramAPIError(
        method=MagicMock(), message="Удаление недоступно"
    )

    asyncio.run(chatgpt.chatgpt_message_handler(message))

    assert message.answer.await_args_list[-1] == call("Ответ модели")
