import asyncio
import os
import re

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    FSInputFile,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from downloader import download_video
from database import (
    connect_db,
    add_user,
    add_download,
    get_stats,
)

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
    await add_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )

    await message.answer(
        "👋 Добро пожаловать в Save Media!\n\n"
        "📥 Отправьте ссылку на видео:\n\n"
        "• TikTok\n"
        "• YouTube\n"
        "• Instagram",
        reply_markup=keyboard,
    )


@dp.message(Command("stats"))
async def stats(message: Message):
    stats = await get_stats()

    await message.answer(
        f"📊 Статистика\n\n"
        f"👥 Пользователей: {stats['users']}\n"
        f"📥 Всего скачиваний: {stats['total']}\n\n"
        f"🎬 TikTok: {stats['tiktok']}\n"
        f"▶️ YouTube: {stats['youtube']}\n"
        f"📸 Instagram: {stats['instagram']}"
    )


@dp.message(F.text == "ℹ️ Помощь")
async def help_button(message: Message):
    await message.answer(
        "📌 Просто отправьте ссылку на видео.\n\n"
        "Поддерживаются:\n"
        "• TikTok\n"
        "• YouTube\n"
        "• Instagram"
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

    platform = "Другое"

    if "tiktok" in url.lower():
        platform = "TikTok"
    elif "youtu" in url.lower():
        platform = "YouTube"
    elif "instagram" in url.lower():
        platform = "Instagram"

    status = await message.answer(
        "🔗 Ссылка получена\n\n"
        "🔍 Анализирую видео..."
    )

    file_path = None

    try:
        file_path = await asyncio.to_thread(download_video, url)
await add_download(platform)
        await status.edit_text(
            "🔗 Ссылка получена\n\n"
            "📥 Видео скачано\n"
            "🎬 Подготавливаю отправку..."
        )

        await asyncio.sleep(0.5)

        await status.edit_text(
            "🔗 Ссылка получена\n\n"
            "📥 Видео скачано\n"
            "📤 Отправляю в Telegram..."
        )

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

        await status.edit_text(
            "🎉 Готово!\n\n"
            "✅ Видео успешно отправлено.\n\n"
            "❤️ Спасибо, что пользуетесь Save Media!"
        )

    except Exception:
        await status.edit_text(
            "❌ Не удалось скачать видео.\n\n"
            "Проверьте ссылку и попробуйте ещё раз."
        )

    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не найден")

    await connect_db()

    bot = Bot(token=BOT_TOKEN)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())