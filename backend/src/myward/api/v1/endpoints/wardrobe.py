"""Wardrobe item CRUD endpoints."""
from __future__ import annotations

import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from myward.core.settings import settings
from myward.db.session import get_db
from myward.models.orm import ClothingCategory, User, WardrobeItem
from myward.services.security import get_current_user

router = APIRouter()


def _save_upload(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename or "img.jpg")[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = os.path.join(settings.UPLOAD_DIR, filename)
    with open(dest, "wb") as f:
        f.write(file.file.read())
    return f"/uploads/{filename}"


@router.post("/", status_code=201)
async def create_item(
    name: str = Form(...),
    category_id: int = Form(...),
    season: Optional[str] = Form(None),
    color: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    formality_level: int = Form(3),
    notes: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    # Validate category
    cat = db.query(ClothingCategory).filter(ClothingCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    image_url: Optional[str] = None
    if file:
        image_url = _save_upload(file)

    item = WardrobeItem(
        user_id=current_user.id,
        name=name,
        category_id=category_id,
        season=season,
        color=color,
        brand=brand,
        formality_level=formality_level,
        notes=notes,
        image_url=image_url,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "name": item.name, "image_url": item.image_url}


@router.get("/")
def list_items(
    category_id: Optional[int] = None,
    season: Optional[str] = None,
    favorite: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, object]]:
    q = db.query(WardrobeItem).filter(WardrobeItem.user_id == current_user.id)
    if category_id:
        q = q.filter(WardrobeItem.category_id == category_id)
    if season:
        q = q.filter(WardrobeItem.season == season)
    if favorite is not None:
        q = q.filter(WardrobeItem.favorite == favorite)
    items = q.all()
    return [
        {
            "id": i.id,
            "name": i.name,
            "brand": i.brand,
            "season": i.season,
            "color": i.color,
            "image_url": i.image_url,
            "favorite": i.favorite,
            "times_worn": i.times_worn,
        }
        for i in items
    ]


@router.get("/{item_id}")
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    item = (
        db.query(WardrobeItem)
        .filter(WardrobeItem.id == item_id, WardrobeItem.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {
        "id": item.id,
        "name": item.name,
        "brand": item.brand,
        "season": item.season,
        "color": item.color,
        "image_url": item.image_url,
        "favorite": item.favorite,
        "times_worn": item.times_worn,
        "notes": item.notes,
        "condition": item.condition,
        "formality_level": item.formality_level,
    }


@router.patch("/{item_id}/favorite")
def toggle_favorite(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, bool]:
    item = (
        db.query(WardrobeItem)
        .filter(WardrobeItem.id == item_id, WardrobeItem.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.favorite = not item.favorite
    db.commit()
    return {"favorite": item.favorite}


@router.delete("/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    item = (
        db.query(WardrobeItem)
        .filter(WardrobeItem.id == item_id, WardrobeItem.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
