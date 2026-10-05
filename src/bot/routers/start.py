"""Обработчики команды /start."""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.bot.keyboards.common import mode_keyboard


router = Router(name="start")


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    """Поздороваться с пользователем и объяснить назначение бота."""
    await message.answer(
        "Привет! Выбери режим кнопками: обычный, арт или перевод с русского на английский. "
        "В обычном режиме я повторяю сообщения. /chatgpt включает диалог с ИИ. "
        "Кнопки можно открыть командой /menu.",
        reply_markup=mode_keyboard(),
    )
