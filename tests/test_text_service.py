"""Unit-тесты сервиса обработки текста."""

from src.bot.services.text import echo_text
import pytest


@pytest.mark.parametrize("text", ["", "Привет, бот!", "  текст\n", "<b>текст</b>", "😀", "я" * 4096])
def test_echo_text_returns_input_unchanged(text: str) -> None:
    """Эхосервис должен возвращать исходный текст без изменений."""
    assert echo_text(text) == text
