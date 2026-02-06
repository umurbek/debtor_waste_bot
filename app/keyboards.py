from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def kb_admin():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Mijoz qo‘shish"), KeyboardButton(text="🧾 Qarz qo‘shish")],
            [KeyboardButton(text="💸 To‘lov qabul qilish"), KeyboardButton(text="👁 Mijoz balans")],
            [KeyboardButton(text="🧱 Mahsulotlar"), KeyboardButton(text="🗑 Otxod kiritish")],
            [KeyboardButton(text="📊 Hisobot"), KeyboardButton(text="👤 Xodimlar")],
        ],
        resize_keyboard=True
    )

def kb_staff(can_waste: bool = False):
    rows = [
        [KeyboardButton(text="🧾 Qarz qo‘shish"), KeyboardButton(text="💸 To‘lov")],
        [KeyboardButton(text="👁 Mijoz balans")],
    ]
    if can_waste:
        rows.append([KeyboardButton(text="🗑 Otxod kiritish")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

def kb_products_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Mahsulot qo‘shish"), KeyboardButton(text="📃 Mahsulotlar ro‘yxati")],
            [KeyboardButton(text="⬅️ Orqaga")],
        ],
        resize_keyboard=True
    )

def kb_back():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="⬅️ Orqaga")]], resize_keyboard=True)


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def ikb_units():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📦 dona", callback_data="unit:dona"),
            InlineKeyboardButton(text="📏 metr", callback_data="unit:metr"),
            InlineKeyboardButton(text="⚖️ kg", callback_data="unit:kg"),
        ]
    ])

def ikb_waste_reasons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💥 singan", callback_data="wreason:singan")],
        [InlineKeyboardButton(text="✂️ kesimdan ortdi", callback_data="wreason:kesimdan_ortdi")],
        [InlineKeyboardButton(text="🚫 yaroqsiz", callback_data="wreason:yaroqsiz")],
        [InlineKeyboardButton(text="↩️ qaytgan", callback_data="wreason:qaytgan")],
    ])
