from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from . import tables as schemas
from .db.database import SessionLocal, get_db # Import SessionLocal and get_db
from . import model as models # Import your SQLAlchemy models
from sqlalchemy.orm import Session # Import Session for type hinting
from dotenv import load_dotenv # For SECRET_KEY
import os # For SECRET_KEY

load_dotenv()

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# JWT Token
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    # Use a default secret key for development
    SECRET_KEY = "development-secret-key-change-in-production-12345678901234567890"
    print("Warning: Using default SECRET_KEY for development. Change this in production!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class TokenData(BaseModel):
    username: Optional[str] = None


# Imports needed for get_current_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login") # tokenUrl is relative to the app root

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)): # Add db session
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = decode_access_token(token)
    if token_data is None or token_data.username is None:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.username == token_data.username).first()

    if user is None:
        raise credentials_exception
    # User is now a SQLAlchemy model instance. Convert to User schema.
    # Ensure your schemas.User can be created from the SQLAlchemy model instance.
    # This might require adding `from_orm = True` in your Pydantic schema's Config class.
    return schemas.User.model_validate(user) # Use model_validate for Pydantic v2

def superadmin_required(user: schemas.User = Depends(get_current_user)):
    if user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Superadmin access required")
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None # Or raise exception
        return TokenData(username=username)
    except JWTError:
        return None # Or raise exception
