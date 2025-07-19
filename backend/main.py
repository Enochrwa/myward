# main.py
from fastapi import FastAPI
from sklearn.cluster import KMeans
import tempfile
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles

import os

import uvicorn
import logging
from app.db import database 
from app.db.database import Base, get_database_connection, init_clothes_database
from app import models # Assuming models.py is in backend/app/


from app.routes import (
    auth,
    other_routes,
    outfit_routes,
    search_router,
    wardrobe,
    user_profile,
    admin,
    recommendation_routes,
    classifier,
    upload_routes
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


MYSQL_CONFIG = {
    'host': 'localhost',
    'database': 'image_processing',
    'user': 'enoch',
    'password': 'enoch',  # Change this to your MySQL password
    'port': 3306
}

Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Image Processing API",
    description="AI-powered image processing with ResNet50 features and MySQL storage - Multiple upload support",
    version="2.0.0"
)



# Configuration
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB per file
MAX_FILES_PER_REQUEST = 20
MIN_FILES_PER_REQUEST = 1

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
os.makedirs("static", exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(auth.router, prefix="/api")
app.include_router(user_profile.router, prefix="/api") 
app.include_router(outfit_routes.router, prefix="/api")
app.include_router(wardrobe.router, prefix="/api")
app.include_router(search_router.router, prefix="/api")
app.include_router(other_routes.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(classifier.router, prefix="/api")
app.include_router(recommendation_routes.router, prefix="/api")
app.include_router(upload_routes.router, prefix="/api")

init_clothes_database()

@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "Image Processing API is running",
        "version": "2.0.0",
        "status": "healthy",
        "max_files_per_request": MAX_FILES_PER_REQUEST,
        "max_file_size_mb": MAX_FILE_SIZE / (1024 * 1024)
    }


@app.get("/health/")
async def health_check():
    """Comprehensive health check"""
    try:
        # Check database connection
        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        db_status = "healthy"
        cursor.close()
        connection.close()
    except:
        db_status = "unhealthy"
    
    # Check upload directory
    upload_dir_exists = os.path.exists(UPLOAD_DIR)
    upload_dir_writable = os.access(UPLOAD_DIR, os.W_OK) if upload_dir_exists else False
    
    
    return {
        "api_status": "healthy",
        "database_status": db_status,
        "upload_directory": {
            "exists": upload_dir_exists,
            "writable": upload_dir_writable
        },
        "version": "2.0.0",
        "max_files_per_request": MAX_FILES_PER_REQUEST,
        "max_file_size_mb": MAX_FILE_SIZE / (1024 * 1024)
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)