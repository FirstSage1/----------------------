"""Обработчики режима диалога с AnyModel."""

from aiogram import Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.services.chatgpt import AnyModelError, ChatService
from src.bot.utils.typing import typing_status

WAITING_TEXT = "Бот печатает…"

router = Router(name="chatgpt")
_service: ChatService | None = None
_active_chats: set[int] = set()


def configure(api_key: str, model: str, base_url: str, proxy: str | None = None) -> None:
    """Настроить общий сервис диалогов."""
    global _service
    _service = ChatService(api_key, model, base_url, proxy)


@router.message(Command("chatgpt"))
async def chatgpt_command_handler(message: Message) -> None:
    """Включить режим ChatGPT для текущего чата."""
    _active_chats.add(message.chat.id)
    if _service is not None:
        _service.reset(message.chat.id)
    await message.answer("Режим ChatGPT включён. Отправьте вопрос или /stopchatgpt для выхода.")


@router.message(Command("stopchatgpt"))
async def stop_chatgpt_handler(message: Message) -> None:
    """Выключить режим ChatGPT и очистить контекст."""
    _active_chats.discard(message.chat.id)
    if _service is not None:
        _service.reset(message.chat.id)
    await message.answer("Режим ChatGPT выключен.")


@router.message(lambda message: message.chat.id in _active_chats and message.text is not None)
async def chatgpt_message_handler(message: Message) -> None:
    """Передать вопрос пользователя в AnyModel."""
    if _service is None:
        await message.answer("Сервис ChatGPT ещё не настроен.")
        return
    status_message = await message.answer(WAITING_TEXT)
    async with typing_status(message.bot, message.chat.id):
        try:
            answer = await _service.ask(message.chat.id, message.text or "")
        except AnyModelError as exc:
            answer = f"Не удалось получить ответ: {exc}"
            try:
                await status_message.edit_text(answer)
                return
            except TelegramAPIError:
                # Если статус уже удалён, отправим ошибку отдельным сообщением.
                pass
    await message.answer(answer)
    try:
        await status_message.delete()
    except TelegramAPIError:
        # Ответ уже доставлен; удаление статуса не должно прерывать обработчик.
        pass
