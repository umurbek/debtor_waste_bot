import re
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.keyboards import kb_products_menu, kb_admin, kb_back
from app.states import AddProduct
from app.db import SessionLocal
from app import crud
from aiogram.types import CallbackQuery
from app.keyboards import ikb_units



router = Router()

def normalize_unit(text: str) -> str:
    t = text.strip().lower()

    # "78 m" / "54 kg" kabi yozuvlardan faqat harflarni ajratib olamiz
    parts = re.findall(r"[a-zA-Z]+", t)
    unit_raw = parts[-1] if parts else t

    mapping = {
        "dona": "dona",
        "ta": "dona",
        "pcs": "dona",
        "pc": "dona",

        "metr": "metr",
        "m": "metr",
        "meter": "metr",

        "kg": "kg",
        "kilo": "kg",
    }

    if unit_raw in mapping:
        return mapping[unit_raw]

    raise ValueError("Faqat: dona / metr / kg (masalan: '78 m' yoki '54 kg')")

@router.message(F.text == "🧱 Mahsulotlar")
async def products_menu(message: Message):
    await message.answer("Mahsulotlar bo‘limi:", reply_markup=kb_products_menu())

@router.message(F.text == "⬅️ Orqaga")
async def go_back(message: Message):
    await message.answer("Admin menyu:", reply_markup=kb_admin())

@router.message(F.text == "➕ Mahsulot qo‘shish")
async def product_add_start(message: Message, state: FSMContext):
    await state.set_state(AddProduct.name)
    await message.answer("Mahsulot nomi:", reply_markup=kb_back())

@router.message(AddProduct.name)
async def product_add_name(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        return await message.answer("Mahsulotlar bo‘limi:", reply_markup=kb_products_menu())

    name = message.text.strip()
    if len(name) < 2:
        return await message.answer("❌ Mahsulot nomi juda qisqa. Qayta kiriting:")

    await state.update_data(name=name)
    await state.set_state(AddProduct.unit)

    await message.answer(
        "Birlikni tanlang (button):",
        reply_markup=ikb_units()
    )


@router.message(F.text == "📃 Mahsulotlar ro‘yxati")
async def product_list(message: Message):
    async with SessionLocal() as session:
        products = await crud.list_products(session)
    if not products:
        return await message.answer("Hali mahsulot yo‘q.")
    text = "📃 Mahsulotlar:\n" + "\n".join([f"#{p.id} — {p.name} ({p.unit})" for p in products])
    await message.answer(text)


@router.callback_query(AddProduct.unit, F.data.startswith("unit:"))
async def product_unit_cb(call: CallbackQuery, state: FSMContext):
    unit = call.data.split(":", 1)[1]  # dona/metr/kg
    data = await state.get_data()

    async with SessionLocal() as session:
        try:
            p = await crud.create_product(session, name=data["name"], unit=unit)
        except Exception:
            await state.clear()
            await call.answer("Bunday mahsulot bor!", show_alert=True)
            return await call.message.answer("❌ Bunday mahsulot bor (nomi unique). Boshqa nom kiriting.", reply_markup=kb_products_menu())

    await state.clear()
    await call.answer("✅ Saqlandi")
    # inline button turgan xabarni yangilab qo‘yamiz
    await call.message.edit_text(f"✅ Mahsulot qo‘shildi: {p.name} ({p.unit})")
    await call.message.answer("Mahsulotlar bo‘limi:", reply_markup=kb_products_menu())
