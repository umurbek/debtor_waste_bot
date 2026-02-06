from aiogram.fsm.state import State, StatesGroup

class AddCustomer(StatesGroup):
    name = State()
    phone = State()
    note = State()

class AddDebt(StatesGroup):
    phone = State()
    amount = State()
    note = State()

class AddPayment(StatesGroup):
    phone = State()
    amount = State()
    note = State()

class AddProduct(StatesGroup):
    name = State()
    unit = State()

class AddWaste(StatesGroup):
    product = State()
    qty = State()
    reason = State()
    note = State()

class Balance(StatesGroup):
    phone = State()
