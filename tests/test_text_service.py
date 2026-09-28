"""Unit-тесты сервиса обработки текста."""

from src.bot.services.text import echo_text, increment_number
import pytest


@pytest.mark.parametrize("text", ["", "Привет, бот!", "  текст\n", "<b>текст</b>", "😀", "я" * 4096])
def test_echo_text_returns_input_unchanged(text: str) -> None:
    """Эхосервис должен возвращать исходный текст без изменений."""
    assert echo_text(text) == text


@pytest.mark.parametrize(
    ("text", "expected"),
    [("41", "42"), ("-1", "0"), ("3.5", "4.5"), (" 10 ", "11")],
)
def test_increment_number_adds_one(text: str, expected: str) -> None:
    """Числовой текст увеличивается ровно на единицу."""
    assert increment_number(text) == expected


@pytest.mark.parametrize("text", ["", "Привет", "1.2.3", "NaN", "Infinity"])
def test_increment_number_rejects_non_numbers(text: str) -> None:
    """Обычный или специальный текст не считается числом."""
    assert increment_number(text) is None
