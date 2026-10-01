"""Проверки защиты секретов в сохраняемом журнале."""

import logging

from src.bot.utils.logging import SafeFormatter


def test_formatter_hides_secrets_and_exception_details() -> None:
    """Токены и содержимое исключений не попадают в журнал."""
    formatter = SafeFormatter(("test-secret",))
    record = logging.LogRecord("test", logging.ERROR, "", 0, "Ошибка test-secret", (), None)
    assert "test-secret" not in formatter.format(record)
    try:
        raise ValueError("private-content")
    except ValueError as error:
        record.exc_info = (type(error), error, error.__traceback__)
    assert "private-content" not in formatter.format(record)
