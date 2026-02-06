import re
from decimal import Decimal, InvalidOperation

UZ_PHONE_RE = re.compile(r"^\+998\d{9}$")

def normalize_phone(text: str) -> str:
    """
    Qabul qiladi: 99890..., +99890..., 90..., 90 123 45 67, (90)1234567
    Qaytaradi: +998XXXXXXXXX
    """
    t = re.sub(r"\D", "", text)  # faqat raqamlar
    # 998 bilan boshlansa:
    if t.startswith("998") and len(t) == 12:
        return "+" + t
    # 9 raqam bo'lsa (90xxxxxxx):
    if len(t) == 9:
        return "+998" + t
    # 12 raqam +998siz bo'lsa (998XXXXXXXXX)
    if len(t) == 12 and t.startswith("998"):
        return "+" + t
    # 13 raqam +998... bo'lsa (lekin + olib tashlangan bo'ladi)
    if len(t) == 12 and not t.startswith("998"):
        # nomalum
        pass
    raise ValueError("Telefon formati xato. Masalan: +998901234567 yoki 901234567")

def validate_phone(phone: str) -> None:
    if not UZ_PHONE_RE.match(phone):
        raise ValueError("Telefon formati xato. Masalan: +998901234567")

def parse_money(text: str, min_amount: Decimal = Decimal("1"), max_amount: Decimal = Decimal("1000000000")) -> Decimal:
    """
    Qabul qiladi: 20000, 20 000, 20,000, 20.000 (ehtiyot), 20000.50, 20 000,50
    """
    t = text.strip()

    # Raqam emas belgilarni tozalaymiz (space, so'm, uzs, va h.k.)
    t = t.lower().replace("so'm", "").replace("som", "").replace("uzs", "").strip()

    # bo'shliqlarni olib tashlaymiz
    t = t.replace(" ", "")

    # agar vergul bor va nuqta yo'q bo'lsa -> decimal separator sifatida qabul qilamiz
    if "," in t and "." not in t:
        t = t.replace(",", ".")
    # agar ikkala bo'lsa: 20,000.50 -> , ni thousand deb hisoblaymiz
    elif "," in t and "." in t:
        t = t.replace(",", "")

    # faqat raqam va bitta nuqta ruxsat
    if not re.fullmatch(r"\d+(\.\d{1,2})?", t):
        raise ValueError("Summa faqat raqam bo‘lsin. Masalan: 20000 yoki 20000.50")

    try:
        val = Decimal(t)
    except InvalidOperation:
        raise ValueError("Summa xato")

    if val < min_amount:
        raise ValueError(f"Summa kamida {min_amount}")
    if val > max_amount:
        raise ValueError(f"Summa juda katta (max {max_amount})")

    return val.quantize(Decimal("0.01"))

def format_money(val: Decimal | int | float) -> str:
    d = Decimal(str(val)).quantize(Decimal("0.01"))
    s = f"{d:,.2f}"          # 20,000.00
    s = s.replace(",", " ")  # 20 000.00
    # agar .00 bo'lsa olib tashlaymiz:
    if s.endswith(".00"):
        s = s[:-3]
    return s + " so‘m"
