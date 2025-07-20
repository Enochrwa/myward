import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging
from fastapi import HTTPException

import mysql.connector
from mysql.connector import Error

from ..model import  (User,
ClothingCategory,
ClothingAttribute,
ColorAnalysis,
UserProfile,
WardrobeItem,WeatherData,
WeatherPreference,WeeklyPlan,
Occasion,Outfit,OutfitRecommendation,StyleHistory,UserStyleProfile,ItemClassification,
Feedback,

WeeklyPlanDayOutfit)
from .base import Base
# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Declare the Base

# MySQL Configuration
MYSQL_CONFIG = {
    'host': 'localhost',
    'database': 'image_processing',
    'user': 'enoch',
    'password': 'enoch',  # Change this to your MySQL password
    'port': 3306
}

def get_database_connection():
    """Get MySQL database connection"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        return connection
    except Error as e:
        logger.error(f"Error connecting to database: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection failed")
    


# Database functions
def init_clothes_database():
    """Initialize MySQL database and create tables"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
        cursor.execute(f"USE {MYSQL_CONFIG['database']}")
        
        # Create images table
        create_images_table = """
        CREATE TABLE IF NOT EXISTS images (
            id VARCHAR(36) PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            image_url VARCHAR(255),
            original_name VARCHAR(255) NOT NULL,
            category VARCHAR(255),
            category_confirmed BOOLEAN DEFAULT FALSE,
            clothing_part VARCHAR(255),
            color_palette JSON,
            dominant_color VARCHAR(7),
            style VARCHAR(255),
            occasion JSON,
            season JSON,
            temperature_range JSON,
            gender VARCHAR(255),
            material VARCHAR(255),
            pattern VARCHAR(255),
            upload_date DATETIME NOT NULL,
            background_removed BOOLEAN DEFAULT FALSE,
            foreground_pixel_count INT DEFAULT 0,
            resnet_features JSON,
            file_size INT,
            image_width INT,
            image_height INT,
            opencv_features JSON,
            batch_id VARCHAR(36),
            user_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_batch_id (batch_id),
            INDEX idx_upload_date (upload_date),
            INDEX idx_background_removed (background_removed),
            INDEX idx_category (category)
        )
        """
        cursor.execute(create_images_table)

        # Add category_confirmed column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE images ADD COLUMN category_confirmed BOOLEAN DEFAULT FALSE")
            connection.commit()
            logger.info("Added 'category_confirmed' column to 'images' table.")
        except Error as e:
            if "Duplicate column name" in str(e):
                pass  # Column already exists
            else:
                raise
        
        # Create batch_uploads table for tracking batch operations
        create_batch_table = """
        CREATE TABLE IF NOT EXISTS batch_uploads (
            batch_id VARCHAR(36) PRIMARY KEY,
            total_images INT NOT NULL,
            successful_images INT NOT NULL,
            failed_images INT NOT NULL,
            upload_date DATETIME NOT NULL,
            processing_time FLOAT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_batch_table)

        # Create outfits table
        create_outfits_table = """
        CREATE TABLE IF NOT EXISTS outfits (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36),
            name VARCHAR(255),
            gender VARCHAR(50),
            clothing_parts JSON,
            clothing_items JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            preview_image BLOB
        )
        """
        cursor.execute(create_outfits_table)
        
        
        connection.commit()
        logger.info("Database initialized successfully")
        
    except Error as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise HTTPException(status_code=500, detail="Database initialization failed")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()




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
        from app import model  # make sure models.User, etc., are defined here
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
