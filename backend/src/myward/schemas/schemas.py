"""Pydantic v2 schemas for API request/response models."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ── Auth ──────────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserLogin(BaseModel):
    username: str
    password: str


# ── Users ─────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, alias="fullName")
    gender: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    username: str
    email: str
    full_name: Optional[str] = Field(None, alias="fullName")
    gender: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    gender: Optional[str] = None


# ── Wardrobe ──────────────────────────────────────────────────────────────────

class WardrobeItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category_id: int
    brand: Optional[str] = None
    season: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    currency: str = "USD"
    material: Optional[str] = None
    formality_level: int = Field(3, ge=1, le=5)
    notes: Optional[str] = None
    tags: list[str] = Field(default_factory=list)


class WardrobeItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    brand: Optional[str]
    season: Optional[str]
    color: Optional[str]
    image_url: Optional[str]
    favorite: bool
    times_worn: int
    condition: str
    formality_level: int
    date_added: datetime


class WardrobeItemUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    season: Optional[str] = None
    color: Optional[str] = None
    notes: Optional[str] = None
    condition: Optional[str] = None
    formality_level: Optional[int] = Field(None, ge=1, le=5)
    tags: Optional[list[str]] = None


# ── Outfits ───────────────────────────────────────────────────────────────────

class OutfitCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    season: Optional[str] = None
    formality_level: int = Field(3, ge=1, le=5)
    occasion_type: Optional[str] = None
    item_ids: list[int] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class OutfitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    season: Optional[str]
    formality_level: int
    occasion_type: Optional[str]
    style_score: Optional[float]
    color_harmony_score: Optional[float]
    image_url: Optional[str]
    times_worn: int
    avg_rating: Optional[float]
    created_at: datetime


# ── Pagination ────────────────────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[object]
