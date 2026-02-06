from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.states import AddPayment
from app.keyboards import kb_back, kb_admin
from app.db import SessionLocal
from app import crud
from app.utils import parse_money
from app.utils import format_money

router = Router()

@router.message(F.text.in_(["💸 To‘lov qabul qilish", "💸 To‘lov"]))
async def pay_start(message: Message, state: FSMContext):
    await state.set_state(AddPayment.phone)
    await message.answer("Mijoz telefonini kiriting:", reply_markup=kb_back())

@router.message(AddPayment.phone)
async def pay_phone(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        return await message.answer("Menyu", reply_markup=kb_admin())

    await state.update_data(phone=message.text.strip())
    await state.set_state(AddPayment.amount)
    await message.answer("To‘lov summasi:")

@router.message(AddPayment.amount)
async def pay_amount(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        return await message.answer("Menyu", reply_markup=kb_admin())

    try:
        amount = parse_money(message.text)
    except ValueError:
        return await message.answer("❌ Summa xato. Qayta kiriting:")

    await state.update_data(amount=str(amount))
    await state.set_state(AddPayment.note)
    await message.answer("Izoh (ixtiyoriy). Bo‘sh bo‘lsa '-' yozing:")

@router.message(AddPayment.note)
async def pay_note(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        return await message.answer("Menyu", reply_markup=kb_admin())

    data = await state.get_data()
    phone = data["phone"]
    note = "" if message.text.strip() == "-" else message.text.strip()
    tg_id = message.from_user.id

    async with SessionLocal() as session:
        user = await crud.get_user(session, tg_id)
        if not user:
            user = await crud.get_or_create_user(session, tg_id, message.from_user.full_name, role="seller")

        customer = await crud.find_customer_by_phone(session, phone)
        if not customer:
            await state.clear()
            return await message.answer("❌ Bu telefon bilan mijoz topilmadi.")

        from decimal import Decimal
        await crud.add_payment(session, customer_id=customer.id, amount=Decimal(data["amount"]), note=note, created_by=user.id)
        bal = await crud.customer_balance(session, customer.id)

    await state.clear() 
    await message.answer(
    f"✅ To‘lov kiritildi.\n📞 {phone}\n💰 Yangi balans: {format_money(bal)}",
    reply_markup=kb_admin()
)