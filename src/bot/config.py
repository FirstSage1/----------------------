"""Загрузка и проверка конфигурации приложения."""

from dataclasses import dataclass, field
import os
from pathlib import Path
from urllib.request import getproxies

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


@dataclass(frozen=True, slots=True)
class Settings:
    """Настройки, необходимые для запуска Telegram-бота."""

    bot_token: str = field(repr=False)
    bot_proxy: str | None = field(repr=False)


def load_settings() -> Settings:
    """Загрузить настройки из .env и системного прокси."""
    load_dotenv(ENV_FILE)

    bot_token = (os.getenv("BOT_TOKEN") or "").strip()
    if not bot_token:
        raise RuntimeError(
            "Не задан BOT_TOKEN. Добавьте токен от @BotFather в файл .env"
        )

    bot_proxy = (os.getenv("BOT_PROXY") or "").strip() or getproxies().get("https")
    return Settings(bot_token=bot_token, bot_proxy=bot_proxy)
