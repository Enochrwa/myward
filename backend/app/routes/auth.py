from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # OAuth2PasswordBearer removed
from datetime import datetime, timedelta
# from pydantic import BaseModel # No longer needed here

from .. import tables as schemas
from .. import security
from ..security import get_current_user # Import get_current_user
from sqlalchemy.orm import Session
from ..db.database import get_db
from .. import model as models # Import your SQLAlchemy models
from sqlalchemy import or_ # Add this import
from ..tables import UserCreate
# oauth2_scheme moved to security.py

router = APIRouter(
    tags=["auth"],
)

# Token model is now in schemas.py
# get_current_user moved to security.py


@router.post("/register", response_model=schemas.Token)  # Changed response_model
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user_by_username = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user_by_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        body_type=user.body_type,
        height=user.height,
        weight=user.weight,
        skin_tone=user.skin_tone,
        timezone=user.timezone,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Generate token for the new user
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=schemas.Token)
async def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)): # Changed signature
    user_in_db = db.query(models.User).filter(
        or_(
            models.User.username == user_credentials.emailOrUsername,
            models.User.email == user_credentials.emailOrUsername
        )
    ).first()

    if not user_in_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username, email, or password")

    if not security.verify_password(user_credentials.password, user_in_db.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username, email, or password")

    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user_in_db.username}, expires_delta=access_token_expires # Use username for token subject
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
