"""User profile endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from myward.db.session import get_db
from myward.models.orm import User, UserProfile
from myward.services.security import get_current_user, require_admin

router = APIRouter()


@router.get("/")
async def list_users(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[dict[str, object]]:
    users = db.query(User).all()
    return [
        {"id": u.id, "username": u.username, "email": u.email, "role": u.role, "is_active": u.is_active}
        for u in users
    ]


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    if current_user.id != user_id and current_user.role not in ("admin", "superadmin"):
        raise HTTPException(status_code=403, detail="Forbidden")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "gender": user.gender,
        "role": user.role,
        "created_at": user.created_at,
    }


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
