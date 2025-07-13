from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging # Added logging

from .. import tables as schemas
from .. import model as models
from ..security import get_current_user
from ..db.database import get_db


from ..services import user_style_profile_service # Import the new service

logger = logging.getLogger(__name__) # Added logger

router = APIRouter(
    prefix="/profile",
    tags=["User Profile"],
    responses={404: {"description": "Not found"}},
)

@router.get("/me", response_model=schemas.UserProfile)
async def read_user_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # This endpoint refers to models.UserProfile (the explicit user settings)
    profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == current_user.id).first()
    if profile is None:
        # Before raising, create a default UserProfile and UserStyleProfile if they don't exist
        # This ensures that a user always has a profile, even if empty
        try:
            profile = models.UserProfile(user_id=current_user.id, updated_at=datetime.utcnow())
            db.add(profile)
            user_style_profile_service.get_or_create_user_style_profile(db, current_user.id) # Ensure UserStyleProfile also exists
            db.commit()
            db.refresh(profile)
            logger.info(f"Created default UserProfile and UserStyleProfile for user_id: {current_user.id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating default profile for user {current_user.id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create default profile.")
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found for current user, created a default one.")
    return profile

@router.post("/me", response_model=schemas.UserProfile, status_code=status.HTTP_201_CREATED)
async def create_user_profile(
    profile_data: schemas.UserProfileCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # This endpoint manages models.UserProfile
    existing_profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile already exists for this user. Use PUT to update.")

    new_profile = models.UserProfile(
        **profile_data.model_dump(),
        user_id=current_user.id,
        updated_at=datetime.utcnow()
    )
    db.add(new_profile)
    
    try:
        # Also ensure UserStyleProfile is created and synced
        user_style_profile_service.sync_user_profile_to_style_profile(db, current_user.id)
        db.commit()
        db.refresh(new_profile)
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating profile or syncing UserStyleProfile for user {current_user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error saving profile information.")
        
    return new_profile

@router.put("/me", response_model=schemas.UserProfile)
async def update_user_profile(
    profile_update_data: schemas.UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # This endpoint manages models.UserProfile
    db_profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == current_user.id).first()

    if db_profile is None:
        # If profile doesn't exist, create it (idempotent PUT)
        db_profile = models.UserProfile( # Assign to db_profile to be used later
            **profile_update_data.model_dump(exclude_unset=True),
            user_id=current_user.id,
            updated_at=datetime.utcnow()
        )
        db.add(db_profile)
    else:
        # Profile exists, update it
        update_data = profile_update_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_profile, key, value)
        db_profile.updated_at = datetime.utcnow()
        
    try:
        # Sync with UserStyleProfile (ML profile) after UserProfile changes
        user_style_profile_service.sync_user_profile_to_style_profile(db, current_user.id)
        db.commit()
        db.refresh(db_profile)
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating profile or syncing UserStyleProfile for user {current_user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error saving profile information.")
        
    return db_profile
