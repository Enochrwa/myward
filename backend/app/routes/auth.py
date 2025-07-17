from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import List, Optional
import json
import os
import uuid

from .. import tables as schemas
from .. import security
from ..security import get_current_user
from sqlalchemy.orm import Session
from ..db.database import get_db
from .. import model as models
from sqlalchemy import or_
from ..tables import UserCreate
from ..utils.user_photo_analysis import PhotoProcessingService
router = APIRouter(
    tags=["auth"],
)

UPLOAD_DIR = "uploads"


@router.post("/register", response_model=schemas.Token)
async def register(
    db: Session = Depends(get_db),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    fullName: Optional[str] = Form(None),
    age: Optional[int] = Form(None),
    gender: Optional[str] = Form(None),
    height: Optional[str] = Form(None),
    weight: Optional[str] = Form(None),
    bmi: Optional[str] = Form(None),
    bodyType: Optional[str] = Form(None),
    skinTone: Optional[str] = Form(None),
    location: Optional[str] = Form(None), # Keep as string from form
    timezone: Optional[str] = Form(None),
    lifestyle: Optional[str] = Form(None),
    budgetRange: Optional[str] = Form(None),
    stylePreferences: Optional[str] = Form(None),
    colorPreferences: Optional[str] = Form(None),
    favoriteColors: Optional[str] = Form(None),
    avoidColors: Optional[str] = Form(None),
    allergies: Optional[str] = Form(None),
    disabilities: Optional[str] = Form(None),
    weatherPreferences: Optional[str] = Form(None), # Keep as string from form
    temperatureRange: Optional[str] = Form(None), # Keep as string from form
    occasionPreferences: Optional[str] = Form(None), # Keep as string from form
    profilePhoto: Optional[UploadFile] = File(None),
    bodyPhotos: List[UploadFile] = File([]),
    autoExtractFeatures: bool = Form(False),
):
    db_user_by_username = db.query(models.User).filter(models.User.username == username).first()
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user_by_email = db.query(models.User).filter(models.User.email == email).first()
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = security.get_password_hash(password)

    profile_photo_path = None
    full_profile_photo_path = None
    if profilePhoto:
        file_extension = os.path.splitext(profilePhoto.filename)[1]
        profile_photo_filename = f"profile_{uuid.uuid4().hex}{file_extension}"
        full_profile_photo_path = os.path.join(UPLOAD_DIR, profile_photo_filename)
        with open(full_profile_photo_path, "wb") as f:
            f.write(await profilePhoto.read())
        profile_photo_path = f"/uploads/{profile_photo_filename}"

    body_photos_paths = []
    full_body_photos_paths = []
    for photo in bodyPhotos:
        file_extension = os.path.splitext(photo.filename)[1]
        body_photo_filename = f"body_{uuid.uuid4().hex}{file_extension}"
        full_body_photo_path = os.path.join(UPLOAD_DIR, body_photo_filename)
        with open(full_body_photo_path, "wb") as f:
            f.write(await photo.read())
        body_photos_paths.append(f"/uploads/{body_photo_filename}")
        full_body_photos_paths.append(full_body_photo_path)
    
    extracted_features = {}
    if autoExtractFeatures and (full_profile_photo_path or full_body_photos_paths):
        photo_service = PhotoProcessingService()
        extraction_results = photo_service.process_user_photos(
            full_profile_photo_path, 
            full_body_photos_paths
        )
        
        if extraction_results.get("success"):
            extracted_features = extraction_results
            if not skinTone and extraction_results.get("skin_tone"):
                skinTone = extraction_results["skin_tone"]
            if not bodyType and extraction_results.get("body_type"):
                bodyType = extraction_results["body_type"]
        
    db_user = models.User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name=fullName,
        age=age,
        gender=gender,
        height=height,
        weight=weight,
        bmi=bmi,
        body_type=bodyType,
        skin_tone=skinTone,
        location=json.loads(location) if location else None,
        timezone=timezone,
        lifestyle=lifestyle,
        budget_range=budgetRange,
        style_preferences=stylePreferences,
        color_preferences=colorPreferences,
        favorite_colors=favoriteColors,
        avoid_colors=avoidColors,
        allergies=allergies,
        disabilities=disabilities,
        weather_preferences=json.loads(weatherPreferences) if weatherPreferences else None,
        temperature_range=json.loads(temperatureRange) if temperatureRange else None,
        occasion_preferences=json.loads(occasionPreferences) if occasionPreferences else None,
        profile_photo=profile_photo_path,
        body_photos=body_photos_paths,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        extraction_metadata=json.dumps(extracted_features) if extracted_features else None
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "extracted_features": extracted_features if autoExtractFeatures else None
    }

@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_in_db = db.query(models.User).filter(
        or_(
            models.User.username == form_data.username,
            models.User.email == form_data.username
        )
    ).first()

    if not user_in_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username, email, or password")

    if not security.verify_password(form_data.password, user_in_db.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username, email, or password")

    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user_in_db.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=schemas.User)
async def read_users_me(user_update: UserCreate,current_user: schemas.User = Depends(get_current_user),db: Session = Depends(get_db)):
    current_user.body_type = user_update.body_type
    current_user.height = user_update.height
    current_user.weight = user_update.weight
    current_user.skin_tone = user_update.skin_tone
    current_user.timezone = user_update.timezone
    db.commit()
    db.refresh(current_user)
    return current_user
