"""API v1 — aggregates all endpoint routers."""
from __future__ import annotations

from fastapi import APIRouter

from myward.api.v1.endpoints import (
    admin,
    auth,
    outfits,
    recommendations,
    uploads,
    users,
    wardrobe,
    weekly_plans,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(wardrobe.router, prefix="/wardrobe", tags=["wardrobe"])
api_router.include_router(outfits.router, prefix="/outfits", tags=["outfits"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(weekly_plans.router, prefix="/weekly-plans", tags=["weekly-plans"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
