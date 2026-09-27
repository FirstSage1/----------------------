"""Обработчик справки."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.keyboards.common import help_keyboard

HELP_TEXT = "Отправьте текст, фотографию или стикер, и я повторю сообщение."
router = Router(name="help")


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    """Показать справку и доступную команду."""
    await message.answer(HELP_TEXT, reply_markup=help_keyboard())
