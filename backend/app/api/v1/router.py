"""
Main API router.
Aggregates all API endpoints following Single Responsibility.
"""
from fastapi import APIRouter

from .endpoints import auth, users, products, sales, qr_codes

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    products.router,
    prefix="/products",
    tags=["Products"]
)

api_router.include_router(
    sales.router,
    prefix="/sales",
    tags=["Sales"]
)

api_router.include_router(
    qr_codes.router,
    prefix="/qr",
    tags=["QR Codes"]
)