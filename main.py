import asyncio
import os
import re

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    FSInputFile,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from downloader import download_video
from database import connect_db, add_user, get_stats
BOT_TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📥 Скачать видео")],
        [KeyboardButton(text="ℹ️ Помощь")],
    ],
    resize_keyboard=True,
)

URL_RE = re.compile(r"https?://\S+", re.I)


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в Save Media!\n\n"
        "📥 Отправьте ссылку на видео с:\n\n"
        "• TikTok\n"
        "• YouTube\n"
        "• Instagram\n\n"
        "Я автоматически скачаю видео и отправлю его вам.",
        reply_markup=keyboard,
    )


@dp.message(F.text == "ℹ️ Помощь")
async def help_button(message: Message):
    await message.answer(
        "📌 Просто отправьте ссылку на видео.\n\n"
        "Поддерживаются:\n"
        "• TikTok\n"
        "• YouTube\n"
        "• Instagram\n\n"
        "Например:\n"
        "https://www.tiktok.com/..."
    )


@dp.message(F.text)
async def handle_link(message: Message):
    text = message.text.strip()

    if text == "📥 Скачать видео":
        await message.answer("📎 Просто отправьте ссылку на видео.")
        return

    match = URL_RE.search(text)

    if not match:
        await message.answer("❌ Пришлите ссылку на видео.")
        return

    url = match.group(0)

    status = await message.answer("⏳ Скачиваю видео...")

    file_path = None

    try:
        file_path = await asyncio.to_thread(download_video, url)

        try:
            await message.answer_video(
                FSInputFile(file_path),
                caption="✅ Готово!"
            )
        except Exception:
            await message.answer_document(
                FSInputFile(file_path),
                caption="✅ Готово!"
            )

        await status.edit_text("✅ Видео успешно скачано!")

    except Exception:
        await status.edit_text(
            "❌ Не удалось скачать видео.\n\n"
            "Проверьте ссылку и попробуйте ещё раз."
        )

    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не найден")

    bot = Bot(token=BOT_TOKEN)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())