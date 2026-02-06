from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.states import AddCustomer
from app.keyboards import kb_back, kb_admin
from app.db import SessionLocal
from app import crud
from app.utils import normalize_phone


router = Router()

@router.message(F.text == "➕ Mijoz qo‘shish")
async def add_customer_start(message: Message, state: FSMContext):
    await state.set_state(AddCustomer.name)
    await message.answer("Mijoz ismini kiriting:", reply_markup=kb_back())

@router.message(AddCustomer.name)
async def add_customer_name(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        return await message.answer("Admin menyu", reply_markup=kb_admin())

    await state.update_data(name=message.text.strip())
    await state.set_state(AddCustomer.phone)
    await message.answer("Telefon raqam (masalan: +998901234567):")

@router.message(AddCustomer.phone)
async def add_customer_phone(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        return await message.answer("Admin menyu", reply_markup=kb_admin())

    try:
        phone = normalize_phone(message.text)
    except ValueError as e:
        return await message.answer(f"❌ {e}")

    await state.update_data(phone=phone)
    
    await state.set_state(AddCustomer.note)
    await message.answer("Manzil/izoh (ixtiyoriy). Bo‘sh qoldirish uchun - yozing: -")

@router.message(AddCustomer.note)
async def add_customer_note(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        return await message.answer("Admin menyu", reply_markup=kb_admin())

    data = await state.get_data()
    note = "" if message.text.strip() == "-" else message.text.strip()

    async with SessionLocal() as session:
        existing = await crud.find_customer_by_phone(session, data["phone"])
        if existing:
            await state.clear()
            return await message.answer("Bu telefon bilan mijoz bor. (Telefon unique bo‘lib turadi)")

        c = await crud.create_customer(session, name=data["name"], phone=data["phone"], note=note)

    await state.clear()
    await message.answer(f"✅ Mijoz qo‘shildi: #{c.id} {c.name} ({c.phone})", reply_markup=kb_admin())
