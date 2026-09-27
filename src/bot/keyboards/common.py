"""Общие клавиатуры приложения."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

HELP_COMMAND = "/help"


def help_keyboard() -> ReplyKeyboardMarkup:
    """Создать клавиатуру с командой справки."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=HELP_COMMAND)]], resize_keyboard=True,
        one_time_keyboard=True,
    )
