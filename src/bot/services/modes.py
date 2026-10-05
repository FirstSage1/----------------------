"""Выбор режима работы отдельно от Telegram-интерфейса."""

from enum import StrEnum


class Mode(StrEnum):
    NORMAL = "normal"
    ART = "art"
    TRANSLATE = "translate"


class ModeService:
    """Хранить режим отдельно для каждого чата до перезапуска."""

    def __init__(self) -> None:
        self._modes: dict[int, Mode] = {}

    def get(self, chat_id: int) -> Mode:
        return self._modes.get(chat_id, Mode.NORMAL)

    def set(self, chat_id: int, mode: Mode) -> None:
        self._modes[chat_id] = mode
