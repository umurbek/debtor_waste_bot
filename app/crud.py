from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from app.models import User, Customer, Debt, Payment, Product, Waste

# --- users ---
async def get_or_create_user(session: AsyncSession, tg_id: int, name: str, role: str = "seller") -> User:
    res = await session.execute(select(User).where(User.tg_id == tg_id))
    u = res.scalar_one_or_none()
    if u:
        if name and u.name != name:
            u.name = name
            await session.commit()
        return u
    u = User(tg_id=tg_id, name=name or "", role=role)
    session.add(u)
    await session.commit()
    return u

async def set_role(session: AsyncSession, tg_id: int, role: str) -> None:
    res = await session.execute(select(User).where(User.tg_id == tg_id))
    u = res.scalar_one_or_none()
    if not u:
        u = User(tg_id=tg_id, role=role, name="")
        session.add(u)
    else:
        u.role = role
    await session.commit()

async def get_user(session: AsyncSession, tg_id: int) -> User | None:
    res = await session.execute(select(User).where(User.tg_id == tg_id))
    return res.scalar_one_or_none()

# --- customers ---
async def create_customer(session: AsyncSession, name: str, phone: str, note: str = "") -> Customer:
    c = Customer(name=name, phone=phone, note=note)
    session.add(c)
    await session.commit()
    return c

async def find_customer_by_phone(session: AsyncSession, phone: str) -> Customer | None:
    res = await session.execute(select(Customer).where(Customer.phone == phone))
    return res.scalar_one_or_none()

# --- debts/payments ---
async def add_debt(session: AsyncSession, customer_id: int, amount: Decimal, note: str, created_by: int):
    d = Debt(customer_id=customer_id, amount=amount, note=note, created_by=created_by)
    session.add(d)
    await session.commit()

async def add_payment(session: AsyncSession, customer_id: int, amount: Decimal, note: str, created_by: int):
    p = Payment(customer_id=customer_id, amount=amount, note=note, created_by=created_by)
    session.add(p)
    await session.commit()

async def customer_balance(session: AsyncSession, customer_id: int) -> Decimal:
    dsum = await session.execute(select(func.coalesce(func.sum(Debt.amount), 0)).where(Debt.customer_id == customer_id))
    psum = await session.execute(select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.customer_id == customer_id))
    return Decimal(dsum.scalar_one()) - Decimal(psum.scalar_one())

# --- products/waste ---
async def create_product(session: AsyncSession, name: str, unit: str) -> Product:
    p = Product(name=name, unit=unit)
    session.add(p)
    await session.commit()
    return p

async def list_products(session: AsyncSession) -> list[Product]:
    res = await session.execute(select(Product).order_by(Product.name.asc()))
    return list(res.scalars().all())

async def add_waste(session: AsyncSession, product_id: int, qty: Decimal, reason: str, note: str, created_by: int):
    w = Waste(product_id=product_id, qty=qty, reason=reason, note=note, created_by=created_by)
    session.add(w)
    await session.commit()
