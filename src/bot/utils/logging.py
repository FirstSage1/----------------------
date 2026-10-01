"""Настройка безопасного журналирования."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
LOG_PATH = Path(__file__).resolve().parents[3] / "logs" / "bot.log"
LOG_MAX_BYTES = 2_000_000
LOG_BACKUP_COUNT = 3


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
    """Настроить консольный и ограниченный по размеру файловый журнал."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.StreamHandler()
    handler.setFormatter(SafeFormatter(secrets))
    file_handler = RotatingFileHandler(
        LOG_PATH, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding="utf-8"
    )
    file_handler.setFormatter(SafeFormatter(secrets))
    logging.basicConfig(level=logging.INFO, handlers=[handler, file_handler], force=True)
    logging.getLogger("aiogram").setLevel(logging.WARNING)
