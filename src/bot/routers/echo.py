"""Обработчики сообщений для режима эхо."""

from aiogram import Router
from aiogram.types import Message

from src.bot.services.text import echo_text


router = Router(name="echo")


@router.message()
async def echo_handler(message: Message) -> None:
    """Повторить поддерживаемое сообщение в том же чате."""
    if message.text is not None:
        await message.answer(echo_text(message.text), entities=message.entities)
        return

    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # Некоторые типы сообщений Telegram нельзя скопировать.
        await message.answer("Я пока не умею повторять этот тип сообщения.")
