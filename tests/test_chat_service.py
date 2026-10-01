"""Проверки резервных маршрутов AnyModel без сетевых запросов."""

import asyncio
from unittest.mock import Mock

import pytest

from src.bot.services.chatgpt import AnyModelError, ChatService


def _reply(content: object) -> dict[str, object]:
    return {"choices": [{"message": {"content": content}}]}


@pytest.mark.parametrize("content", ["", "   ", None])
def test_empty_answer_uses_fallback(content: object) -> None:
    """HTTP 200 без текста не прекращает поиск рабочего маршрута."""
    service = ChatService("test-key", "primary", "https://example.test/v1")
    request = Mock(side_effect=[(_reply(content), 200), (_reply("Ответ"), 200)])
    service._request = request

    assert asyncio.run(service.ask(1, "Вопрос")) == "Ответ"
    assert request.call_count == 2
    assert [entry["role"] for entry in service._histories[1]] == ["user", "assistant"]


@pytest.mark.parametrize("payload", [{}, {"choices": []}, {"choices": [None]}])
def test_malformed_answer_uses_fallback(payload: object) -> None:
    """Неполная структура ответа не блокирует резервную модель."""
    service = ChatService("test-key", "primary", "https://example.test/v1")
    service._request = Mock(side_effect=[(payload, 200), (_reply("Ответ"), 200)])

    assert asyncio.run(service.ask(1, "Вопрос")) == "Ответ"


def test_all_empty_answers_preserve_previous_history() -> None:
    """После отказа всех моделей история успешного диалога не меняется."""
    service = ChatService("test-key", "primary", "https://example.test/v1")
    service._request = Mock(return_value=(_reply("Первый ответ"), 200))
    asyncio.run(service.ask(1, "Первый вопрос"))
    previous = list(service._histories[1])
    request = Mock(return_value=(_reply(""), 200))
    service._request = request

    with pytest.raises(AnyModelError, match="пустой ответ"):
        asyncio.run(service.ask(1, "Второй вопрос"))

    assert service._histories[1] == previous
    assert request.call_count == len(service._models)


def test_unauthorized_response_is_not_retried_and_preserves_history() -> None:
    """Ошибку авторизации нельзя исправить сменой модели."""
    service = ChatService("test-key", "primary", "https://example.test/v1")
    request = Mock(return_value=({"error": {"message": "Unauthorized"}}, 401))
    service._request = request

    with pytest.raises(AnyModelError, match="Unauthorized"):
        asyncio.run(service.ask(1, "Вопрос"))

    assert service._histories[1] == []
    assert request.call_count == 1
