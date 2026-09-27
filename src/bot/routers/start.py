"""Обработчики команды /start."""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message


router = Router(name="start")


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    """Поздороваться с пользователем и объяснить назначение бота."""
    await message.answer(
        "Привет! Я эхобот. Отправь мне сообщение, и я повторю его."
    )
