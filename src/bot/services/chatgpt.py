"""Клиент AnyModel и управление историей диалогов."""

from collections import defaultdict
from typing import Final
import asyncio
import json
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener

MAX_HISTORY_MESSAGES: Final = 20
REQUEST_TIMEOUT: Final = 20
FALLBACK_MODELS: Final = ("ag/gemini-3.6-flash-medium", "am/kimi-k3", "am/gpt-oss-20b")
RETRYABLE_STATUSES: Final = (502, 503, 504)


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
        history = self._histories[chat_id]
        history.append({"role": "user", "content": question})
        # Общий тайм-аут учитывает последовательные попытки резервных моделей.
        data: object = None
        last_error = "Не удалось получить ответ от AnyModel."
        for model in self._models:
            try:
                data, status = await asyncio.to_thread(self._request, model, history)
            except (OSError, TimeoutError) as exc:
                raise AnyModelError("Не удалось связаться с AnyModel.") from exc
            if status < 400:
                break
            error = data.get("error", {}) if isinstance(data, dict) else {}
            last_error = str(error.get("message") or f"HTTP {status}")
            if status not in RETRYABLE_STATUSES:
                raise AnyModelError(last_error)
        else:
            raise AnyModelError(last_error)

        try:
            answer = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AnyModelError("AnyModel вернул неожиданный ответ.") from exc
        if not isinstance(answer, str) or not answer.strip():
            raise AnyModelError("AnyModel вернул пустой ответ.")
        history.append({"role": "assistant", "content": answer})
        if len(history) > MAX_HISTORY_MESSAGES:
            del history[:-MAX_HISTORY_MESSAGES]
        return answer

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
