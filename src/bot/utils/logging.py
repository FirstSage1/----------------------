"""Настройка безопасного журналирования."""

import logging

LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"


class SafeFormatter(logging.Formatter):
    """Скрывать секреты и детали исключений сторонних библиотек."""

    def __init__(self, secrets: tuple[str, ...]) -> None:
        super().__init__(LOG_FORMAT)
        self.secrets = tuple(value for value in secrets if value)

    def format(self, record: logging.LogRecord) -> str:
        if record.exc_info:
            return "Ошибка обработчика; подробности скрыты для защиты данных."
        result = super().format(record)
        for secret in self.secrets:
            result = result.replace(secret, "<скрыто>")
        return result


def configure_logging(secrets: tuple[str, ...] = ()) -> None:
    """Настроить консольный журнал без содержимого сообщений."""
    handler = logging.StreamHandler()
    handler.setFormatter(SafeFormatter(secrets))
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
    logging.getLogger("aiogram").setLevel(logging.WARNING)
