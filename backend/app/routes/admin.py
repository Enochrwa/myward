from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import tables as schemas
from .. import model as models
from ..security import get_current_user, superadmin_required
from ..db.database import get_db
from ..model import UserRole

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(get_current_user)]
)

@router.get("/users", response_model=List[schemas.User])
async def admin_get_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.admin.value, UserRole.superadmin.value]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this resource")
    
    # Exclude superadmins from the list
    users = db.query(models.User).filter(models.User.role != UserRole.superadmin.value).all()
    return users

@router.put("/users/{user_id}", response_model=schemas.User)
async def admin_update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.admin.value, UserRole.superadmin.value]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this resource")

    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if db_user.role == UserRole.superadmin.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Superadmin users cannot be modified.")

    update_data = user_update.model_dump(exclude_unset=True)
    
    # Ensure that a user cannot be promoted to superadmin via this endpoint
    if "role" in update_data and update_data["role"] == UserRole.superadmin.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot promote to superadmin.")

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.admin.value, UserRole.superadmin.value]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this resource")

    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if db_user.role == UserRole.superadmin.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Superadmin users cannot be deleted.")

    db.delete(db_user)
    db.commit()
    return

@router.post("/superadmin/promote-admin/{user_id}")
def promote_to_admin(user_id: int, current_user: dict = Depends(superadmin_required), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = "admin"
    db.commit()
    return {"message": f"{user.username} is now an admin"}
