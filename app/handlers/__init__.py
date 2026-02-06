from .start import router as start_router
from .customers import router as customers_router
from .debts import router as debts_router
from .payments import router as payments_router
from .products import router as products_router
from .waste import router as waste_router
from .reports import router as reports_router
from .balance import router as balance_router

all_routers = [
    start_router,
    customers_router,
    debts_router,
    payments_router,
    products_router,
    waste_router,
    reports_router,
    balance_router,
]
