import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import pymysql
from ..model import *
from .base import Base
# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Declare the Base


def create_mysql_database_if_not_exists():
    """Create MySQL database if it doesn't exist"""
    if DATABASE_URL and "mysql" in DATABASE_URL:
        try:
            db_name = DATABASE_URL.split("/")[-1]
            base_url = DATABASE_URL.rsplit("/", 1)[0]
            
            temp_engine = create_engine(base_url)
            with temp_engine.connect() as connection:
                result = connection.execute(text(f"SHOW DATABASES LIKE '{db_name}'"))
                if not result.fetchone():
                    connection.execute(text(f"CREATE DATABASE {db_name}"))
                    print(f"✅ Created database: {db_name}")
                else:
                    print(f"✅ Database {db_name} already exists")
            temp_engine.dispose()
        except Exception as e:
            print(f"❌ Error creating database: {e}")

def create_database_engine():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in .env")
    
    create_mysql_database_if_not_exists()

    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False
    )

    # Import all models before creating tables
    try:
        from app import models  # make sure models.User, etc., are defined here
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created (if not already present)")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

    return engine

# Create engine and session
engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_database_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
print(Base.metadata.tables.keys())
