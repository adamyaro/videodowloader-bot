import asyncio
import os
import re

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile

from downloader import download_video

BOT_TOKEN = os.getenv("BOT_TOKEN")
dp = Dispatcher()

URL_RE = re.compile(r"https?://\S+", re.I)


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Отправь ссылку на TikTok, YouTube или Instagram — я попробую скачать видео."
    )


@dp.message(F.text)
async def handle_link(message: Message):
    text = message.text.strip()
    match = URL_RE.search(text)

    if not match:
        await message.answer("Пришли именно ссылку на видео.")
        return

    url = match.group(0)
    status = await message.answer("⏳ Скачиваю...")
    file_path = None

    try:
        file_path = await asyncio.to_thread(download_video, url)

        try:
            await message.answer_video(FSInputFile(file_path), caption="✅ Готово")
        except Exception:
            await message.answer_document(FSInputFile(file_path), caption="✅ Готово")

        await status.edit_text("✅ Готово")
    except Exception as e:
        await message.answer(f"Не получилось скачать видео.\nОшибка: {e}")
    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass


@dp.message()
async def other(message: Message):
    await message.answer("Отправь ссылку текстом. Я пока понимаю только ссылки.")


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не найден")

    bot = Bot(token=BOT_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())