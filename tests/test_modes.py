"""Проверки режимов, перевода и генерации без реальных API-запросов."""

import asyncio
import base64
from unittest.mock import AsyncMock, Mock

import pytest
from aiogram.types import BufferedInputFile, Message

from src.bot.routers import chatgpt, modes
from src.bot.services.chatgpt import AnyModelError, ChatService
from src.bot.services.modes import Mode, ModeService


@pytest.fixture(autouse=True)
def isolate_modes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(modes, "mode_service", ModeService())
    monkeypatch.setattr(modes, "_service", None)
    monkeypatch.setattr(chatgpt, "_service", None)
    monkeypatch.setattr(chatgpt, "_active_chats", set())
    monkeypatch.setattr(chatgpt, "_modes", modes.mode_service)


def make_message(text: str | None = "Привет") -> Message:
    message = AsyncMock(spec=Message)
    message.answer = AsyncMock(return_value=AsyncMock())
    message.answer_photo = AsyncMock()
    message.chat = type("ChatStub", (), {"id": 1})()
    message.text = text
    return message


def test_modes_are_isolated() -> None:
    state = ModeService()
    state.set(1, Mode.ART)
    assert state.get(1) == Mode.ART
    assert state.get(2) == Mode.NORMAL


def test_switch_disables_chatgpt() -> None:
    chatgpt._active_chats.add(1)
    chatgpt._service = Mock()
    asyncio.run(modes.select_mode(make_message(), Mode.ART))
    assert 1 not in chatgpt._active_chats
    chatgpt._service.reset.assert_called_once_with(1)
    assert modes.mode_service.get(1) == Mode.ART


def test_chatgpt_exits_art() -> None:
    modes.mode_service.set(1, Mode.ART)
    asyncio.run(chatgpt.chatgpt_command_handler(make_message()))
    assert modes.mode_service.get(1) == Mode.NORMAL
    assert 1 in chatgpt._active_chats


def test_translation_has_system_prompt_and_no_history() -> None:
    service = ChatService("test", "primary", "https://example.test/v1")
    service._request = Mock(return_value=({"choices": [{"message": {"content": "Hello"}}]}, 200))
    assert asyncio.run(service.translate("Привет")) == "Hello"
    history = service._request.call_args.args[1]
    assert history[0]["role"] == "system"
    assert history[1] == {"role": "user", "content": "Привет"}
    assert not service._histories


def test_image_decoding_and_payload() -> None:
    service = ChatService("test", "primary", "https://example.test/v1")
    service._request_json = Mock(return_value=({"data": [{"b64_json": base64.b64encode(b"image").decode()}]}, 200))
    assert asyncio.run(service.generate_image("Кот")) == b"image"
    path, payload = service._request_json.call_args.args
    assert path == "/images/generations"
    assert payload["prompt"] == "Кот"
    assert payload["response_format"] == "b64_json"


@pytest.mark.parametrize("payload", [None, {}, {"data": []}, {"data": [None]}, {"data": [{"b64_json": "%%%"}]}])
def test_invalid_images_fail_safely(payload: object) -> None:
    service = ChatService("test", "primary", "https://example.test/v1")
    service._request_json = Mock(return_value=(payload, 200))
    with pytest.raises(AnyModelError):
        asyncio.run(service.generate_image("Кот"))


def test_art_sends_photo() -> None:
    modes.mode_service.set(1, Mode.ART)
    modes._service = AsyncMock()
    modes._service.generate_image.return_value = b"image"
    message = make_message("Кот")
    asyncio.run(modes.mode_message_handler(message))
    modes._service.generate_image.assert_awaited_once_with("Кот")
    photo = message.answer_photo.await_args.args[0]
    assert isinstance(photo, BufferedInputFile)
    assert photo.data == b"image"
    message.answer.return_value.delete.assert_awaited_once()


def test_translation_splits_long_answer() -> None:
    modes.mode_service.set(1, Mode.TRANSLATE)
    modes._service = AsyncMock()
    modes._service.translate.return_value = "x" * 5000
    message = make_message()
    asyncio.run(modes.mode_message_handler(message))
    assert [len(c.args[0]) for c in message.answer.await_args_list[1:]] == [4096, 904]


def test_service_error_cleans_status() -> None:
    modes.mode_service.set(1, Mode.ART)
    modes._service = AsyncMock()
    modes._service.generate_image.side_effect = AnyModelError("Ошибка")
    message = make_message()
    asyncio.run(modes.mode_message_handler(message))
    message.answer_photo.assert_not_awaited()
    message.answer.return_value.delete.assert_awaited_once()


def test_nontext_does_not_call_service() -> None:
    modes.mode_service.set(1, Mode.ART)
    modes._service = AsyncMock()
    asyncio.run(modes.mode_message_handler(make_message(None)))
    modes._service.generate_image.assert_not_awaited()
