"""Обработчик справки."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.keyboards.common import help_keyboard

HELP_TEXT = (
    "/mode_normal — повторение сообщений, числа увеличиваются на 1.\n"
    "/mode_art — отправьте описание, и бот нарисует изображение.\n"
    "/mode_translate — отправьте текст на русском, бот переведёт его на английский.\n"
    "/mode_summarize — краткое изложение длинного текста по пунктам.\n"
    "/chatgpt — диалог с ИИ; /stopchatgpt — возврат в обычный режим.\n"
    "/menu — кнопки выбора режима. Режим сохраняется до перезапуска бота."
)
router = Router(name="help")


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    """Показать справку и доступную команду."""
    await message.answer(HELP_TEXT, reply_markup=help_keyboard())
