"""Обработчик меню команд бота."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup


MENU_TEXT = (
    "Меню команд\n\n"
    "/start — приветствие и краткое описание.\n"
    "/help — справка по возможностям бота.\n"
    "/chatgpt — включить режим диалога с LLM.\n"
    "/stopchatgpt — выключить режим диалога.\n"
    "Любое другое сообщение бот повторит без изменений."
)
MENU_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/start"), KeyboardButton(text="/help")],
        [KeyboardButton(text="/chatgpt")],
        [KeyboardButton(text="Скрыть меню")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите команду или отправьте сообщение",
)
router = Router(name="menu")


@router.message(Command("menu"))
async def menu_handler(message: Message) -> None:
    """Показать пользователю основные команды и кнопки меню."""
    await message.answer(MENU_TEXT, reply_markup=MENU_KEYBOARD)
