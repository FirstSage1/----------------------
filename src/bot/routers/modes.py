"""Переключение режимов и обработка перевода и арт-запросов."""

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, Message

from src.bot.keyboards.common import mode_keyboard
from src.bot.routers import chatgpt
from src.bot.services.chatgpt import AnyModelError, ChatService
from src.bot.services.modes import Mode, ModeService

TELEGRAM_TEXT_LIMIT = 4096
MODE_TEXTS = {
    Mode.NORMAL: "Обычный режим включён. Бот повторяет сообщения; /chatgpt включает диалог.",
    Mode.ART: "Арт-режим включён. Отправьте описание изображения.",
    Mode.TRANSLATE: "Режим перевода включён. Отправьте текст на русском языке.",
}
MODE_BUTTONS = {
    "Обычный режим": Mode.NORMAL,
    "Арт": Mode.ART,
    "Перевод RU → EN": Mode.TRANSLATE,
}
router = Router(name="modes")
mode_service = ModeService()
_service: ChatService | None = None


def configure(service: ChatService) -> None:
    """Подключить сервис AnyModel, созданный при запуске."""
    global _service
    _service = service


async def select_mode(message: Message, mode: Mode) -> None:
    """Переключить режим и очистить прежний диалог."""
    mode_service.set(message.chat.id, mode)
    chatgpt.deactivate(message.chat.id)
    await message.answer(MODE_TEXTS[mode], reply_markup=mode_keyboard())


@router.message(Command("mode_normal"))
async def normal_handler(message: Message) -> None:
    await select_mode(message, Mode.NORMAL)


@router.message(Command("mode_art"))
async def art_handler(message: Message) -> None:
    await select_mode(message, Mode.ART)


@router.message(Command("mode_translate"))
async def translate_handler(message: Message) -> None:
    await select_mode(message, Mode.TRANSLATE)


@router.message(F.text.in_(MODE_BUTTONS))
async def mode_button_handler(message: Message) -> None:
    await select_mode(message, MODE_BUTTONS[message.text or ""])


@router.message(lambda message: mode_service.get(message.chat.id) != Mode.NORMAL
                and not (message.text or "").startswith("/")
                and message.text != "Скрыть меню")
async def mode_message_handler(message: Message) -> None:
    """Отправить запрос и доставить результат выбранного режима."""
    if not message.text or not message.text.strip():
        await message.answer("В этом режиме нужен текст. Отправьте описание или текст для перевода.")
        return
    if _service is None:
        await message.answer("Сервис AnyModel ещё не настроен.")
        return
    mode = mode_service.get(message.chat.id)
    status = await message.answer("Рисую изображение…" if mode == Mode.ART else "Перевожу…")
    try:
        if mode == Mode.ART:
            image = await _service.generate_image(message.text)
            await message.answer_photo(BufferedInputFile(image, filename="art.jpg"))
        else:
            answer = await _service.translate(message.text)
            for offset in range(0, len(answer), TELEGRAM_TEXT_LIMIT):
                await message.answer(answer[offset:offset + TELEGRAM_TEXT_LIMIT])
    except (AnyModelError, OSError):
        await message.answer("Не удалось выполнить запрос. Попробуйте ещё раз позже.")
    except TelegramAPIError:
        await message.answer("Telegram не смог доставить результат. Попробуйте ещё раз.")
    finally:
        try:
            await status.delete()
        except TelegramAPIError:
            pass
