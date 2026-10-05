"""Общие клавиатуры приложения."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

HELP_COMMAND = "/help"
CHATGPT_COMMAND = "/chatgpt"


def mode_keyboard() -> ReplyKeyboardMarkup:
    """Показать режимы работы и команды меню."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Обычный режим"), KeyboardButton(text="Арт")],
            [KeyboardButton(text="Перевод RU → EN")],
            [KeyboardButton(text="/start"), KeyboardButton(text="/help")],
            [KeyboardButton(text="/chatgpt")],
            [KeyboardButton(text="Скрыть меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите команду или отправьте сообщение",
    )


def help_keyboard() -> ReplyKeyboardMarkup:
    """Создать клавиатуру с командой справки."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=HELP_COMMAND)]], resize_keyboard=True,
        one_time_keyboard=True,
    )
