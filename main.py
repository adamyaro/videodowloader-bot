import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

BOT_TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Бот работает ✅")

@dp.message()
async def echo(message: Message):
    await message.answer("Я получил сообщение!")

async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не найден")

    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
