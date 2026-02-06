import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import BOT_TOKEN
from app.db import engine
from app.models import Base
from app.handlers import all_routers

async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main():
    await on_startup()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    for r in all_routers:
        dp.include_router(r)    

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
