from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.states import AddDebt
from app.keyboards import kb_back, kb_admin, kb_staff
from app.db import SessionLocal
from app import crud
from app.utils import parse_money
from app.utils import normalize_phone
from app.utils import format_money



router = Router()

@router.message(F.text.in_(["🧾 Qarz qo‘shish"]))
async def debt_start(message: Message, state: FSMContext):
    await state.set_state(AddDebt.phone)
    await message.answer("Mijoz telefonini kiriting:", reply_markup=kb_back())

@router.message(AddDebt.phone)
async def debt_phone(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        return await message.answer("Menyu", reply_markup=kb_admin())

    try:
        phone = normalize_phone(message.text)
    except ValueError as e:
        return await message.answer(f"❌ {e}")

    await state.update_data(phone=phone)
    await state.set_state(AddDebt.amount)

    await message.answer("Qarz summasi (masalan: 150000 yoki 150000.50):")

@router.message(AddDebt.amount)
async def debt_amount(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        return await message.answer("Menyu", reply_markup=kb_admin())

    try:
        amount = parse_money(message.text)
    except ValueError:
        return await message.answer("❌ Summa xato. Qayta kiriting:")

    await state.update_data(amount=str(amount))
    await state.set_state(AddDebt.note)
    await message.answer("Izoh (nima oldi?) (masalan: '10kg un'):")

@router.message(AddDebt.note)
async def debt_note(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        return await message.answer("Menyu", reply_markup=kb_admin())

    data = await state.get_data()
    phone = data["phone"]
    note = message.text.strip()
    tg_id = message.from_user.id

    async with SessionLocal() as session:
        user = await crud.get_user(session, tg_id)
        if not user:
            user = await crud.get_or_create_user(session, tg_id, message.from_user.full_name, role="seller")

        customer = await crud.find_customer_by_phone(session, phone)
        if not customer:
            await state.clear()
            return await message.answer("❌ Bu telefon bilan mijoz topilmadi. Avval mijoz qo‘shing.")

        from decimal import Decimal
        await crud.add_debt(session, customer_id=customer.id, amount=Decimal(data["amount"]), note=note, created_by=user.id)
        bal = await crud.customer_balance(session, customer.id)

    await state.clear()
    await message.answer(f"✅ Qarz yozildi.\n📞 {phone}\n💰 Balans: {format_money(bal)}",reply_markup=kb_admin())
