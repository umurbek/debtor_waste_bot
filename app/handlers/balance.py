from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.states import Balance
from app.keyboards import kb_back, kb_admin
from app.db import SessionLocal
from app import crud
from app.utils import normalize_phone
from app.utils import format_money


router = Router()

@router.message(F.text == "👁 Mijoz balans")
async def balance_start(message: Message, state: FSMContext):
    await state.set_state(Balance.phone)
    await message.answer("Mijoz telefonini kiriting:", reply_markup=kb_back())

@router.message(Balance.phone)
async def balance_show(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        return await message.answer("Menyu", reply_markup=kb_admin())

    try:
        phone = normalize_phone(message.text)
    except ValueError as e:
        await state.clear()
        return await message.answer(f"❌ {e}", reply_markup=kb_admin())
    
    async with SessionLocal() as session:
        c = await crud.find_customer_by_phone(session, phone)
        if not c:
            await state.clear()
            return await message.answer("❌ Mijoz topilmadi.")
        bal = await crud.customer_balance(session, c.id)

    await state.clear()
    await message.answer(f"👤 {c.name}\n📞 {c.phone}\n💰 Balans: {format_money(bal)}", reply_markup=kb_admin())
