import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_TG_ID = int(os.getenv("ADMIN_TG_ID", "0"))
DB_URL = os.getenv("DB_URL", "sqlite+aiosqlite:///./bot.db")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN .env da yo‘q!")
if ADMIN_TG_ID == 0:
    raise RuntimeError("ADMIN_TG_ID .env da yo‘q!")
