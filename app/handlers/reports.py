from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select, func
from app.db import SessionLocal
from app.models import Debt, Payment, Waste

router = Router()

@router.message(F.text == "📊 Hisobot")
async def report(message: Message):
    async with SessionLocal() as session:
        debts_sum = await session.execute(select(func.coalesce(func.sum(Debt.amount), 0)))
        pay_sum = await session.execute(select(func.coalesce(func.sum(Payment.amount), 0)))
        waste_count = await session.execute(select(func.count(Waste.id)))

    ds = debts_sum.scalar_one()
    ps = pay_sum.scalar_one()
    balance_total = ds - ps

    await message.answer(
        "📊 Umumiy hisobot:\n"
        f"🧾 Jami qarz: {ds}\n"
        f"💸 Jami to‘lov: {ps}\n"
        f"💰 Umumiy balans: {balance_total}\n"
        f"🗑 Otxod yozuvlari: {waste_count.scalar_one()}"
    )
