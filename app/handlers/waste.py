from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.states import AddWaste
from app.keyboards import kb_back, kb_admin
from app.db import SessionLocal
from app import crud
from app.utils import parse_money
from aiogram.types import CallbackQuery
from app.keyboards import ikb_waste_reasons


router = Router()

@router.message(F.text == "🗑 Otxod kiritish")
async def waste_start(message: Message, state: FSMContext):
    async with SessionLocal() as session:
        products = await crud.list_products(session)
    if not products:
        return await message.answer("❌ Avval mahsulot qo‘shing: 🧱 Mahsulotlar")

    await state.set_state(AddWaste.product)
    text = "Mahsulot ID sini tanlang:\n" + "\n".join([f"#{p.id} — {p.name} ({p.unit})" for p in products])
    await message.answer(text, reply_markup=kb_back())

@router.message(AddWaste.product)
async def waste_product(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        return await message.answer("Menyu", reply_markup=kb_admin())

    try:
        product_id = int(message.text.strip().replace("#", ""))
    except ValueError:
        return await message.answer("❌ Product ID raqam bo‘lsin (masalan: 3)")

    await state.update_data(product_id=product_id)
    await state.set_state(AddWaste.qty)
    await message.answer("Miqdor (masalan: 2 yoki 1.5):")

@router.message(AddWaste.qty)
async def waste_qty(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        return await message.answer("Menyu", reply_markup=kb_admin())

    try:
        qty = parse_money(message.text)  # Decimal qaytaradi
    except ValueError:
        return await message.answer("❌ Miqdor xato. Qayta kiriting:")

    await state.update_data(qty=str(qty))
    await state.set_state(AddWaste.reason)
    await message.answer("Sabab: singan / kesimdan_ortdi / yaroqsiz / qaytgan")

@router.message(AddWaste.reason)
async def waste_reason(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        return await message.answer("Menyu", reply_markup=kb_admin())

    reason = message.text.strip().lower()
    allowed = {"singan", "kesimdan_ortdi", "yaroqsiz", "qaytgan"}
    if reason not in allowed:
        return await message.answer("❌ Sabab xato. Tanlang: singan/kesimdan_ortdi/yaroqsiz/qaytgan")

    await state.update_data(reason=reason)
    await state.set_state(AddWaste.note)
    await message.answer("Izoh (ixtiyoriy). Bo‘sh bo‘lsa '-' yozing:")

@router.message(AddWaste.note)
async def waste_note(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        return await message.answer("Menyu", reply_markup=kb_admin())

    data = await state.get_data()
    note = "" if message.text.strip() == "-" else message.text.strip()
    tg_id = message.from_user.id

    async with SessionLocal() as session:
        user = await crud.get_user(session, tg_id)
        if not user:
            user = await crud.get_or_create_user(session, tg_id, message.from_user.full_name, role="warehouse")

        from decimal import Decimal
        await crud.add_waste(
            session,
            product_id=int(data["product_id"]),
            qty=Decimal(data["qty"]),
            reason=data["reason"],
            note=note,
            created_by=user.id
        )

    await state.clear()
    await message.answer("✅ Otxod kiritildi.", reply_markup=kb_admin())


@router.callback_query(AddWaste.reason, F.data.startswith("wreason:"))
async def waste_reason_cb(call: CallbackQuery, state: FSMContext):
    reason = call.data.split(":", 1)[1]
    await state.update_data(reason=reason)
    await state.set_state(AddWaste.note)

    await call.answer("✅ Tanlandi")
    await call.message.edit_text(f"Sabab: {reason}\nIzoh (ixtiyoriy). Bo‘sh bo‘lsa '-' yozing:")
