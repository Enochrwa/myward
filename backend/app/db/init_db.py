import os
from sqlalchemy.orm import Session
from app.model import User, UserRole
from app.security import get_password_hash

def create_superadmin(db: Session):
    enoch_exists = db.query(User).filter(User.username == "promesse").first()
    if not enoch_exists:
        hashed_password = get_password_hash("promesse")
        superadmin = User(
            username="promesse",
            email="promesse@gmail.com",
            hashed_password=hashed_password,
            full_name="Promesse",
            gender="female",
            role=UserRole.superadmin.value,
        )
        db.add(superadmin)
        db.commit()
        db.refresh(superadmin)
        print("Superadmin 'promesse' created.")
    else:
        print("Superadmin 'promesse' already exists.")

def init_db(db: Session):
    # This function can be expanded to initialize other data
    create_superadmin(db)
