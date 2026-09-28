"""Операции над текстом, не зависящие от Telegram и aiogram."""

from decimal import Decimal, InvalidOperation


def echo_text(text: str) -> str:
    """Вернуть текст без изменений для ответа эхобота."""
    return text


def increment_number(text: str) -> str | None:
    """Вернуть число, увеличенное на единицу, или None для обычного текста."""
    normalized_text = text.strip()
    if not normalized_text:
        return None

    try:
        number = Decimal(normalized_text)
    except InvalidOperation:
        return None

    if not number.is_finite():
        return None
    return format(number + Decimal("1"), "f")
