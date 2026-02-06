from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from app.db import SessionLocal
from app.config import ADMIN_TG_ID
from app import crud
from app.keyboards import kb_admin, kb_staff

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    tg_id = message.from_user.id
    name = message.from_user.full_name

    async with SessionLocal() as session:
        # admin bo‘lsa role=admin, bo‘lmasa seller qilib ochamiz
        role = "admin" if tg_id == ADMIN_TG_ID else "seller"
        user = await crud.get_or_create_user(session, tg_id=tg_id, name=name, role=role)

    if user.role == "admin":
        await message.answer(
            f"Salom! Admin panel ✅\nSizning TG ID: {tg_id}",
            reply_markup=kb_admin()
        )
    else:
        can_waste = user.role in ("warehouse",)
        await message.answer(
            f"Salom! Xodim menyu ✅\nSizning TG ID: {tg_id}",
            reply_markup=kb_staff(can_waste=can_waste)
        )
