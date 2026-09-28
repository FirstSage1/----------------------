"""Проверки экранных клавиатур бота."""

from aiogram.types import ReplyKeyboardMarkup

from src.bot.keyboards.common import HELP_COMMAND, help_keyboard
from src.bot.routers.menu import MENU_KEYBOARD


def test_help_keyboard_contains_help_command() -> None:
    """Клавиатура справки содержит единственную кнопку /help."""
    keyboard = help_keyboard()

    assert isinstance(keyboard, ReplyKeyboardMarkup)
    assert keyboard.resize_keyboard is True
    assert keyboard.one_time_keyboard is True
    assert [[button.text for button in row] for row in keyboard.keyboard] == [
        [HELP_COMMAND]
    ]


def test_menu_keyboard_contains_commands_and_hide_button() -> None:
    """Меню показывает команды и кнопку для скрытия клавиатуры."""
    assert MENU_KEYBOARD.resize_keyboard is True
    assert MENU_KEYBOARD.input_field_placeholder == (
        "Выберите команду или отправьте сообщение"
    )
    assert [[button.text for button in row] for row in MENU_KEYBOARD.keyboard] == [
        ["/start", "/help"],
        ["Скрыть меню"],
    ]
