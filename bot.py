import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from handlers import setup_handlers
from middlewares import LoggingMiddleware

from db_handler import db
from config import bot_token

bot = Bot(token=bot_token)
dp = Dispatcher()

dp.message.middleware(LoggingMiddleware())
setup_handlers(dp)

async def main():
    print("Launching database")
    await db.start_session()
    print("Launching bot")
    await dp.start_polling(bot)
    await db.close_session()

if __name__ == "__main__":
    asyncio.run(main())
