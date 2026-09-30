"""Загрузка и проверка конфигурации приложения."""

from dataclasses import dataclass, field
import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


@dataclass(frozen=True, slots=True)
class Settings:
    """Настройки, необходимые для запуска Telegram-бота."""

    bot_token: str = field(repr=False)
    bot_proxy: str | None = field(repr=False)
    anymodel_api_key: str = field(repr=False)
    anymodel_model: str
    anymodel_base_url: str


def load_settings() -> Settings:
    """Загрузить настройки из .env и явный прокси."""
    load_dotenv(ENV_FILE)

    bot_token = (os.getenv("BOT_TOKEN") or "").strip()
    if not bot_token:
        raise RuntimeError(
            "Не задан BOT_TOKEN. Добавьте токен от @BotFather в файл .env"
        )

    # Прокси включается только явной настройкой, чтобы недоступный системный
    # прокси не блокировал запуск бота.
    bot_proxy = (os.getenv("BOT_PROXY") or "").strip() or None
    anymodel_api_key = (os.getenv("ANYMODEL_API_KEY") or "").strip()
    if not anymodel_api_key:
        raise RuntimeError("Не задан ANYMODEL_API_KEY. Добавьте ключ AnyModel в файл .env")
    anymodel_model = (os.getenv("ANYMODEL_MODEL") or "cc/claude-opus-5").strip()
    anymodel_base_url = (os.getenv("ANYMODEL_BASE_URL") or "https://anymodel.org/v1").strip().rstrip("/")
    return Settings(
        bot_token=bot_token,
        bot_proxy=bot_proxy,
        anymodel_api_key=anymodel_api_key,
        anymodel_model=anymodel_model,
        anymodel_base_url=anymodel_base_url,
    )
