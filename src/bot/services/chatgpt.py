"""Клиент AnyModel и управление историей диалогов."""

from collections import defaultdict
from typing import Final
import asyncio
import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener

MAX_HISTORY_MESSAGES: Final = 20
REQUEST_TIMEOUT: Final = 20
FALLBACK_MODELS: Final = ("ag/gemini-3.6-flash-medium", "am/kimi-k3", "am/gpt-oss-20b")
RETRYABLE_STATUSES: Final = (502, 503, 504)
NETWORK_RETRIES: Final = 2


def _extract_answer(data: object) -> str:
    """Проверить структуру Chat Completions и вернуть только текст ответа."""
    if not isinstance(data, dict):
        raise AnyModelError("AnyModel вернул неожиданный ответ.")
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise AnyModelError("AnyModel вернул неожиданный ответ.")
    message = choices[0].get("message")
    if not isinstance(message, dict):
        raise AnyModelError("AnyModel вернул неожиданный ответ.")
    answer = message.get("content")
    if not isinstance(answer, str) or not answer.strip():
        raise AnyModelError("AnyModel вернул пустой ответ.")
    return answer


class AnyModelError(RuntimeError):
    """Ошибка запроса к AnyModel."""


class ChatService:
    """Отправляет сообщения в AnyModel и хранит контекст по чатам."""

    def __init__(self, api_key: str, model: str, base_url: str, proxy: str | None = None) -> None:
        self._headers = {"Authorization": f"Bearer {api_key}"}
        self._models = tuple(dict.fromkeys((model, *FALLBACK_MODELS)))
        self._url = f"{base_url}/chat/completions"
        self._proxy = proxy
        self._histories: dict[int, list[dict[str, str]]] = defaultdict(list)

    def reset(self, chat_id: int) -> None:
        self._histories.pop(chat_id, None)

    async def ask(self, chat_id: int, question: str) -> str:
        # Не сохраняем незавершённый вопрос при ошибке любого маршрута.
        history = [*self._histories[chat_id], {"role": "user", "content": question}]
        data: object = None
        last_error = "Не удалось получить ответ от AnyModel."
        for model_index, model in enumerate(self._models):
            for attempt in range(NETWORK_RETRIES):
                try:
                    data, status = await asyncio.to_thread(self._request, model, history)
                    break
                except OSError:
                    if attempt + 1 == NETWORK_RETRIES:
                        last_error = "AnyModel временно недоступен. Повторите запрос через несколько секунд."
                        continue
            else:
                continue
            if status < 400:
                try:
                    answer = _extract_answer(data)
                except AnyModelError as exc:
                    last_error = str(exc)
                    logging.warning(
                        "Маршрут AnyModel %d вернул ответ без пригодного текста; проверяем резервный.",
                        model_index + 1,
                    )
                    continue
                history.append({"role": "assistant", "content": answer})
                self._histories[chat_id] = history[-MAX_HISTORY_MESSAGES:]
                return answer
            error = data.get("error", {}) if isinstance(data, dict) else {}
            last_error = str(error.get("message") or f"HTTP {status}") if isinstance(error, dict) else f"HTTP {status}"
            if status not in RETRYABLE_STATUSES:
                raise AnyModelError(last_error)
        raise AnyModelError(last_error)

    def _request(self, model: str, history: list[dict[str, str]]) -> tuple[object, int]:
        """Выполнить запрос AnyModel с явным прокси."""
        request = Request(
            self._url,
            data=json.dumps({"model": model, "messages": history}).encode(),
            headers={**self._headers, "Content-Type": "application/json", "User-Agent": "AnyModelBot/1.0"},
            method="POST",
        )
        opener = build_opener(ProxyHandler({"http": self._proxy, "https": self._proxy})) if self._proxy else build_opener()
        try:
            with opener.open(request, timeout=REQUEST_TIMEOUT) as response:
                return json.loads(response.read()), response.status
        except HTTPError as error:
            raw = error.read().decode("utf-8", errors="replace")
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = {"error": {"message": raw or str(error)}}
            return payload, error.code
        except URLError as error:
            raise OSError(str(error)) from error
