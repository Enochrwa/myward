from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

from . import tables as schemas  # Pydantic schemas
from . import model as models    # SQLAlchemy models
from .db.database import get_db

# ──────🔐 Load Environment Variables ──────
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY") or "development-secret-key-change-in-production-12345678901234567890"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if not os.getenv("SECRET_KEY"):
    print("⚠️ Warning: Using default SECRET_KEY for development. Set SECRET_KEY in .env for production!")

# ──────🔒 Password Hashing ──────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# ──────🔐 Token & Auth Schemas ──────
class TokenData(BaseModel):
    username: Optional[str] = None

# ──────🔑 OAuth2 Bearer Token Setup ──────
# tokenUrl must match your login route
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# ──────🔐 Create JWT ──────
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ──────🔐 Decode JWT ──────
def decode_access_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except JWTError:
        return None

# ──────🔐 Get Current User ──────
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> schemas.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="❌ Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = decode_access_token(token)
    if token_data is None or token_data.username is None:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        raise credentials_exception

    return schemas.User.model_validate(user)

# ──────🔐 Role-based Access Example ──────
def superadmin_required(user: schemas.User = Depends(get_current_user)) -> schemas.User:
    if user.role != "superadmin":
        raise HTTPException(status_code=403, detail="⛔ Superadmin access required")
    return user
