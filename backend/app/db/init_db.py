import os
from sqlalchemy.orm import Session
from app.model import User, UserRole
from app.security import get_password_hash

def create_superadmin(db: Session):
    enoch_exists = db.query(User).filter(User.username == "enoch").first()
    if not enoch_exists:
        hashed_password = get_password_hash("enoch")
        superadmin = User(
            username="enoch",
            email="enoch@gmail.com",
            hashed_password=hashed_password,
            full_name="Enoch",
            gender="male",
            role=UserRole.superadmin.value,
        )
        db.add(superadmin)
        db.commit()
        db.refresh(superadmin)
        print("Superadmin 'enoch' created.")
    else:
        print("Superadmin 'enoch' already exists.")

def init_db(db: Session):
    # This function can be expanded to initialize other data
    create_superadmin(db)
