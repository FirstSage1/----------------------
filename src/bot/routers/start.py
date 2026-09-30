"""Обработчики команды /start."""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove


router = Router(name="start")


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    """Поздороваться с пользователем и объяснить назначение бота."""
    await message.answer(
        "Привет! Я бот с режимом эхо и ChatGPT. Отправь мне сообщение, и я повторю его. "
        "Команда /chatgpt включает ответы LLM. "
        "Команды доступны в меню рядом со строкой ввода.",
        reply_markup=ReplyKeyboardRemove(),
    )
