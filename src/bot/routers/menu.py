"""Обработчик меню команд бота."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.keyboards.common import mode_keyboard


MENU_TEXT = (
    "Меню команд\n\n"
    "/start — приветствие и краткое описание.\n"
    "/help — справка по возможностям бота.\n"
    "/chatgpt — включить режим диалога с LLM.\n"
    "/stopchatgpt — выключить режим диалога.\n"
    "/mode_normal — обычный режим (эхо).\n"
    "/mode_art — нарисовать изображение по описанию.\n"
    "/mode_translate — перевод с русского на английский."
)
router = Router(name="menu")
MENU_KEYBOARD = mode_keyboard()


@router.message(Command("menu"))
async def menu_handler(message: Message) -> None:
    """Показать пользователю основные команды и кнопки меню."""
    await message.answer(MENU_TEXT, reply_markup=MENU_KEYBOARD)
