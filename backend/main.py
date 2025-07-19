# main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from rembg import remove, new_session
from sklearn.cluster import KMeans
import tempfile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
import os
import json
from sklearn.neighbors import NearestNeighbors
import uvicorn
import logging
from datetime import datetime
import numpy as np
import cv2
from PIL import Image
import mysql.connector
from mysql.connector import Error
import base64
import io
from colorthief import ColorThief
import webcolors

from io import BytesIO
from PIL import Image


from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing import image
import tensorflow as tf
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.db import database
from app.db.database import Base
from app import models # Assuming models.py is in backend/app/

from utils.color_utils import (
    rgb_to_hex, 
    get_color_name, 
    get_tone, 
    get_temperature, 
    get_saturation, 
    get_color_palette
)
from app.routes import (
    auth,
    other_routes,
    outfit_routes,
    search_router,
    wardrobe,
    user_profile,
    admin,
    recommendation_routes,
    classifier
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# MySQL Configuration
MYSQL_CONFIG = {
    'host': 'localhost',
    'database': 'image_processing',
    'user': 'enoch',
    'password': 'enoch',  # Change this to your MySQL password
    'port': 3306
}

# Create directories
os.makedirs(UPLOAD_DIR, exist_ok=True)


## EDIT




##EDIT

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
os.makedirs("static", exist_ok=True) # Ensure the base static directory exists
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

# Load ResNet50 model
try:
    resnet_model = ResNet50(weights='imagenet', include_top=False, pooling='avg')
    logger.info("ResNet50 model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load ResNet50 model: {str(e)}")
    resnet_model = None

# Thread pool for parallel processing
executor = ThreadPoolExecutor(max_workers=4)

# Pydantic models
class ImageMetadata(BaseModel):
    id: str
    filename: str
    original_name: str
    file_size: int
    image_width: int
    image_height: int
    dominant_color: str
    color_palette: List[str]
    resnet_features: List[float]
    opencv_features: Dict[str, Any]
    upload_date: str

class ImageResponse(BaseModel):
    message: str
    image_id: str
    image_url: str
    metadata: ImageMetadata

class BatchUploadResponse(BaseModel):
    message: str
    total_images: int
    successful_uploads: int
    failed_uploads: int
    batch_id: str
    results: List[Dict[str, Any]]
    processing_time: float

class BatchImageMetadata(BaseModel):
    batch_id: str
    total_images: int
    successful_images: int
    failed_images: int
    upload_date: str
    processing_time: float

# Database functions
def init_database():
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
            original_name VARCHAR(255) NOT NULL,
            file_size INT NOT NULL,
            image_width INT NOT NULL,
            image_height INT NOT NULL,
            dominant_color VARCHAR(7) NOT NULL,
            color_palette JSON NOT NULL,
            resnet_features JSON NOT NULL,
            opencv_features JSON NOT NULL,
            upload_date DATETIME NOT NULL,
            batch_id VARCHAR(36),
            category VARCHAR(255),
            background_removed BOOLEAN DEFAULT FALSE,
            foreground_pixel_count INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_batch_id (batch_id),
            INDEX idx_upload_date (upload_date),
            INDEX idx_background_removed (background_removed),
            INDEX idx_category (category)
        )
        """
        cursor.execute(create_images_table)
        
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
        
        connection.commit()
        logger.info("Database initialized successfully")
        
    except Error as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise HTTPException(status_code=500, detail="Database initialization failed")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()




def remove_background_rembg(image_path, model_name='u2net'):
    """
    Remove background using rembg library (most accurate)
    """
    try:
        # Create session for specific model
        session = new_session(model_name)
        
        # Read image
        with open(image_path, 'rb') as input_file:
            input_data = input_file.read()
        
        # Remove background
        output_data = remove(input_data, session=session)
        
        # Convert to PIL Image
        output_image = Image.open(BytesIO(output_data)).convert("RGBA")
        
        return output_image
    except Exception as e:
        print(f"Error with rembg background removal: {str(e)}")
        return None
    


def remove_background_grabcut(image_path):
    """
    Remove background using OpenCV GrabCut algorithm (fallback method)
    """
    try:
        # Read image
        img = cv2.imread(image_path)
        height, width = img.shape[:2]
        
        # Create mask
        mask = np.zeros((height, width), np.uint8)
        
        # Define rectangle around the object (assuming centered object)
        # You can make this more sophisticated by detecting the main subject
        rect_margin = min(width, height) // 8
        rect = (rect_margin, rect_margin, width - 2*rect_margin, height - 2*rect_margin)
        
        # Initialize background and foreground models
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        
        # Apply GrabCut
        cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
        
        # Create binary mask
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        
        # Apply mask to image
        img_no_bg = img * mask2[:, :, np.newaxis]
        
        # Convert to PIL Image with transparency
        img_rgba = cv2.cvtColor(img_no_bg, cv2.COLOR_BGR2RGBA)
        
        # Set transparent pixels where mask is 0
        img_rgba[mask2 == 0] = [0, 0, 0, 0]
        
        pil_image = Image.fromarray(img_rgba, 'RGBA')
        
        return pil_image
    except Exception as e:
        print(f"Error with GrabCut background removal: {str(e)}")
        return None

def remove_background_edge_detection(image_path):
    """
    Simple background removal using edge detection and flood fill
    """
    try:
        # Read image
        img = cv2.imread(image_path)
        height, width = img.shape[:2]
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Dilate edges to close gaps
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create mask from largest contour (assuming it's the main object)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            mask = np.zeros((height, width), np.uint8)
            cv2.fillPoly(mask, [largest_contour], 255)
            
            # Apply morphological operations to smooth mask
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Apply mask
            img_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
            img_rgba[mask == 0] = [0, 0, 0, 0]
            
            pil_image = Image.fromarray(img_rgba, 'RGBA')
            return pil_image
    except Exception as e:
        print(f"Error with edge detection background removal: {str(e)}")
        return None

def extract_foreground_pixels(image_rgba):
    """
    Extract only non-transparent pixels from RGBA image
    """
    try:
        # Convert to numpy array
        img_array = np.array(image_rgba)
        
        # Get alpha channel
        alpha = img_array[:, :, 3]
        
        # Find non-transparent pixels
        non_transparent_mask = alpha > 0
        
        # Extract RGB values of non-transparent pixels
        foreground_pixels = img_array[non_transparent_mask][:, :3]  # Only RGB, not alpha
        
        return foreground_pixels
    except Exception as e:
        print(f"Error extracting foreground pixels: {str(e)}")
        return None

def get_dominant_color_from_pixels(pixels, num_colors=1):
    """
    Get dominant color from pixel array using K-means clustering
    """
    try:
        from sklearn.cluster import KMeans
        
        if len(pixels) == 0:
            return None
        
        # Reshape pixels for clustering
        pixels_reshaped = pixels.reshape(-1, 3)
        
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
        kmeans.fit(pixels_reshaped)
        
        # Get dominant color
        dominant_color = kmeans.cluster_centers_[0].astype(int)
        
        return tuple(dominant_color)
    except Exception as e:
        print(f"Error getting dominant color: {str(e)}")
        return None

def extract_color_features_no_background(image_path):
    """
    Enhanced color feature extraction with background removal
    """
    try:
        # Method 1: Try rembg first (most accurate)
        image_no_bg = remove_background_rembg(image_path, model_name='u2net')
        
        # Method 2: Fallback to GrabCut if rembg fails
        if image_no_bg is None:
            print("Falling back to GrabCut method...")
            image_no_bg = remove_background_grabcut(image_path)
        
        # Method 3: Final fallback to edge detection
        if image_no_bg is None:
            print("Falling back to edge detection method...")
            image_no_bg = remove_background_edge_detection(image_path)
        
        # If all background removal methods fail, use original image
        if image_no_bg is None:
            print("All background removal methods failed, using original image...")
            return extract_color_features_original(image_path)
        
        # Extract foreground pixels
        foreground_pixels = extract_foreground_pixels(image_no_bg)
        
        if foreground_pixels is None or len(foreground_pixels) == 0:
            print("No foreground pixels found, using original image...")
            return extract_color_features_original(image_path)
        
        # Get dominant color from foreground pixels
        dominant_color = get_dominant_color_from_pixels(foreground_pixels, num_colors=1)
        
        # Get color palette (multiple dominant colors)
        palette_colors = []
        try:
            for i in range(2, 6):  # Try to get 2-5 colors
                colors = get_dominant_color_from_pixels(foreground_pixels, num_colors=i)
                if colors is not None:
                    palette_colors = colors
                    break
        except:
            palette_colors = [dominant_color] if dominant_color else []
        
        # Save processed image temporarily for ColorThief (as backup)
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            # Convert RGBA to RGB with white background for ColorThief
            image_rgb = Image.new("RGB", image_no_bg.size, (255, 255, 255))
            image_rgb.paste(image_no_bg, mask=image_no_bg.split()[-1])
            image_rgb.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            # Use ColorThief as backup/validation
            color_thief = ColorThief(tmp_path)
            ct_dominant = color_thief.get_color(quality=1)
            ct_palette = color_thief.get_palette(color_count=5, quality=1)
        except:
            ct_dominant = dominant_color
            ct_palette = palette_colors if isinstance(palette_colors, list) else [palette_colors]
        
        # Clean up temporary file
        try:
            os.unlink(tmp_path)
        except:
            pass
        
        # Use our custom method result, fallback to ColorThief if needed
        final_dominant = dominant_color if dominant_color else ct_dominant
        final_palette = palette_colors if palette_colors else ct_palette
        
        # Convert to hex and get color properties
        if final_dominant:
            dominant_hex = rgb_to_hex(*final_dominant)
            dominant_color_name = get_color_name(list(final_dominant))
            tone = get_tone(list(final_dominant))
            temperature = get_temperature(list(final_dominant))
            saturation = get_saturation(list(final_dominant))
            color_palette = get_color_palette(list(final_dominant))
        else:
            # Fallback values
            dominant_hex = "#000000"
            dominant_color_name = "black"
            tone = "Dark"
            temperature = "Neutral"
            saturation = "Low"
            color_palette = {
                "original": "#000000",
                "complementary": "#000000",
                "analogous1": "#000000",
                "analogous2": "#000000"
            }
        
        # Convert palette to hex
        if isinstance(final_palette, list) and len(final_palette) > 0:
            palette_hex = [rgb_to_hex(*color) if isinstance(color, (tuple, list)) and len(color) >= 3 else "#000000" for color in final_palette]
            palette_names = [get_color_name(list(color)) if isinstance(color, (tuple, list)) else "unknown" for color in final_palette]
        else:
            palette_hex = [dominant_hex]
            palette_names = [dominant_color_name]
        
        return {
            "dominant_color": dominant_hex,
            "dominant_color_name": dominant_color_name,
            "dominant_color_tone": tone,
            "dominant_color_temperature": temperature,
            "dominant_color_saturation": saturation,
            "palette": palette_hex[:5],  # Limit to 5 colors
            "palette_names": palette_names[:5],
            "suggested_palette": color_palette,
            "background_removed": True,
            "foreground_pixel_count": len(foreground_pixels) if foreground_pixels is not None else 0
        }
        
    except Exception as e:
        print(f"Error in extract_color_features_no_background: {str(e)}")
        # Fallback to original method
        return extract_color_features_original(image_path)

def extract_color_features_original(image_path):
    """
    Original color feature extraction (fallback method)
    """
    try:
        # Get dominant color
        color_thief = ColorThief(image_path)
        dominant_color = color_thief.get_color(quality=1)
       
        # Get color palette
        palette = color_thief.get_palette(color_count=5, quality=1)
       
        # Convert dominant color to list format for color_utils functions
        dominant_color_list = list(dominant_color)
        
        # Use color_utils functions
        dominant_hex = rgb_to_hex(*dominant_color)
        palette_hex = [rgb_to_hex(*color) for color in palette]
       
        # Get color names using color_utils
        dominant_color_name = get_color_name(dominant_color_list)
        color_names = [get_color_name(list(color)) for color in palette]
        
        # Get additional color properties for dominant color
        tone = get_tone(dominant_color_list)
        temperature = get_temperature(dominant_color_list)
        saturation = get_saturation(dominant_color_list)
        
        # Get color palette suggestions
        color_palette = get_color_palette(dominant_color_list)
       
        return {
            "dominant_color": dominant_hex,
            "dominant_color_name": dominant_color_name,
            "dominant_color_tone": tone,
            "dominant_color_temperature": temperature,
            "dominant_color_saturation": saturation,
            "palette": palette_hex,
            "palette_names": color_names,
            "suggested_palette": color_palette,
            "background_removed": False,
            "foreground_pixel_count": 0
        }
   
    except Exception as e:
        print(f"Error extracting color features: {str(e)}")
        return {
            "dominant_color": "#000000",
            "dominant_color_name": "black",
            "dominant_color_tone": "Dark",
            "dominant_color_temperature": "Neutral",
            "dominant_color_saturation": "Low",
            "palette": ["#000000"],
            "palette_names": ["black"],
            "suggested_palette": {
                "original": "#000000",
                "complementary": "#000000",
                "analogous1": "#000000",
                "analogous2": "#000000"
            },
            "background_removed": False,
            "foreground_pixel_count": 0
        }

def get_database_connection():
    """Get MySQL database connection"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        return connection
    except Error as e:
        logger.error(f"Error connecting to database: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# Image processing functions
def extract_resnet_features(image_path):
    """Extract features using ResNet50"""
    try:
        if resnet_model is None:
            raise Exception("ResNet50 model not available")
        
        # Load and preprocess image
        img = image.load_img(image_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        # Extract features
        features = resnet_model.predict(img_array)
        return features.flatten().tolist()
    
    except Exception as e:
        logger.error(f"Error extracting ResNet features: {str(e)}")
        return []

def extract_opencv_features(image_path):
    """Extract features using OpenCV"""
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise Exception("Could not read image")
        
        # Convert to different color spaces
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Calculate basic statistics
        mean_bgr = np.mean(img, axis=(0, 1)).tolist()
        std_bgr = np.std(img, axis=(0, 1)).tolist()
        
        # Calculate histogram
        hist_b = cv2.calcHist([img], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([img], [1], None, [256], [0, 256])
        hist_r = cv2.calcHist([img], [2], None, [256], [0, 256])
        
        # Calculate texture features using Laplacian
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Calculate edges
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        features = {
            "mean_bgr": mean_bgr,
            "std_bgr": std_bgr,
            "brightness": float(np.mean(gray)),
            "contrast": float(np.std(gray)),
            "laplacian_variance": float(laplacian_var),
            "edge_density": float(edge_density),
            "histogram_peaks": {
                "blue": int(np.argmax(hist_b)),
                "green": int(np.argmax(hist_g)),
                "red": int(np.argmax(hist_r))
            }
        }
        
        return features
    
    except Exception as e:
        logger.error(f"Error extracting OpenCV features: {str(e)}")
        return {}

# def extract_color_features(image_path):
#     """Extract color features using ColorThief and color_utils"""
#     try:
#         # Get dominant color
#         color_thief = ColorThief(image_path)
#         dominant_color = color_thief.get_color(quality=1)
       
#         # Get color palette
#         palette = color_thief.get_palette(color_count=5, quality=1)
       
#         # Convert dominant color to list format for color_utils functions
#         dominant_color_list = list(dominant_color)
        
#         # Use color_utils functions
#         dominant_hex = rgb_to_hex(*dominant_color)
#         palette_hex = [rgb_to_hex(*color) for color in palette]
       
#         # Get color names using color_utils
#         dominant_color_name = get_color_name(dominant_color_list)
#         color_names = [get_color_name(list(color)) for color in palette]
        
#         # Get additional color properties for dominant color
#         tone = get_tone(dominant_color_list)
#         temperature = get_temperature(dominant_color_list)
#         saturation = get_saturation(dominant_color_list)
        
#         # Get color palette suggestions
#         color_palette = get_color_palette(dominant_color_list)
       
#         return {
#             "dominant_color": dominant_hex,
#             "dominant_color_name": dominant_color_name,
#             "dominant_color_tone": tone,
#             "dominant_color_temperature": temperature,
#             "dominant_color_saturation": saturation,
#             "palette": palette_hex,
#             "palette_names": color_names,
#             "suggested_palette": color_palette
#         }
   
#     except Exception as e:
#         logger.error(f"Error extracting color features: {str(e)}")
#         return {
#             "dominant_color": "#000000",
#             "dominant_color_name": "black",
#             "dominant_color_tone": "Dark",
#             "dominant_color_temperature": "Neutral",
#             "dominant_color_saturation": "Low",
#             "palette": ["#000000"],
#             "palette_names": ["black"],
#             "suggested_palette": {
#                 "original": "#000000",
#                 "complementary": "#000000",
#                 "analogous1": "#000000",
#                 "analogous2": "#000000"
#             }
#         }
    

def extract_color_features(image_path):
    """Extract color features using ColorThief and color_utils with background removal"""
    return extract_color_features_no_background(image_path)


def get_image_dimensions(image_path):
    """Get image dimensions"""
    try:
        with Image.open(image_path) as img:
            return img.size  # Returns (width, height)
    except Exception as e:
        logger.error(f"Error getting image dimensions: {str(e)}")
        return (0, 0)

# def process_single_image(file_data, batch_id=None):
#     """Process a single image - used for parallel processing"""
#     try:
#         file_content, filename, original_name = file_data
        
#         # Generate unique filename
#         file_extension = os.path.splitext(original_name)[1]
#         unique_filename = f"{uuid.uuid4().hex}{file_extension}"
#         filepath = os.path.join(UPLOAD_DIR, unique_filename)
        
#         # Save file
#         with open(filepath, "wb") as f:
#             f.write(file_content)
        
#         # Get image dimensions
#         width, height = get_image_dimensions(filepath)
        
#         # Classify image
#         img = Image.open(filepath).convert("RGB")
#         category = classifier.predict_class_from_pil(img)
        
#         # Extract features
#         resnet_features = extract_resnet_features(filepath)
#         opencv_features = extract_opencv_features(filepath)
#         color_features = extract_color_features(filepath)
        
#         # Create metadata
#         image_id = str(uuid.uuid4())
#         metadata = {
#             "id": image_id,
#             "filename": unique_filename,
#             "original_name": original_name,
#             "file_size": len(file_content),
#             "image_width": width,
#             "image_height": height,
#             "dominant_color": color_features["dominant_color"],
#             "color_palette": color_features["palette"],
#             "resnet_features": resnet_features,
#             "opencv_features": opencv_features,
#             "upload_date": datetime.now().isoformat(),
#             "batch_id": batch_id,
#             "category": category
#         }
        
#         return {
#             "success": True,
#             "metadata": metadata,
#             "filepath": filepath,
#             "color_features": color_features
#         }
        
#     except Exception as e:
#         logger.error(f"Error processing image {original_name}: {str(e)}")
#         return {
#             "success": False,
#             "error": str(e),
#             "original_name": original_name
#         }


def process_single_image(file_data, batch_id=None):
    """Process a single image - used for parallel processing"""
    try:
        file_content, filename, original_name = file_data
        
        # Generate unique filename
        file_extension = os.path.splitext(original_name)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        filepath = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(filepath, "wb") as f:
            f.write(file_content)
        
        # Get image dimensions
        width, height = get_image_dimensions(filepath)
        
        # Classify image
        img = Image.open(filepath).convert("RGB")
        category = classifier.predict_class_from_pil(img)
        
        # Extract features
        resnet_features = extract_resnet_features(filepath)
        opencv_features = extract_opencv_features(filepath)
        
        # Extract color features with background removal
        color_features = extract_color_features_no_background(filepath)  # Updated line
        
        # Create metadata
        image_id = str(uuid.uuid4())
        metadata = {
            "id": image_id,
            "filename": unique_filename,
            "original_name": original_name,
            "file_size": len(file_content),
            "image_width": width,
            "image_height": height,
            "dominant_color": color_features["dominant_color"],
            "color_palette": color_features["palette"],
            "resnet_features": resnet_features,
            "opencv_features": opencv_features,
            "upload_date": datetime.now().isoformat(),
            "batch_id": batch_id,
            "category": category,
            "background_removed": color_features.get("background_removed", False),  # New field
            "foreground_pixel_count": color_features.get("foreground_pixel_count", 0)  # New field
        }
        
        return {
            "success": True,
            "metadata": metadata,
            "filepath": filepath,
            "color_features": color_features
        }
        
    except Exception as e:
        logger.error(f"Error processing image {original_name}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "original_name": original_name
        }

# Initialize database on startup
init_database()

@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "Image Processing API is running",
        "version": "2.0.0",
        "status": "healthy",
        "resnet_available": resnet_model is not None,
        "max_files_per_request": MAX_FILES_PER_REQUEST,
        "max_file_size_mb": MAX_FILE_SIZE / (1024 * 1024)
    }

@app.post("/api/upload-image/", response_model=ImageResponse)
async def upload_single_image(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None)
):
    """Upload and process a single image (legacy endpoint)"""
    try:
        # Validate file
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Check file size
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        
        # Process the image
        file_data = (contents, file.filename, file.filename)
        result = process_single_image(file_data)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        metadata = result["metadata"]
        
        # Store in database
        try:
            connection = get_database_connection()
            cursor = connection.cursor()
            
            insert_query = """
                INSERT INTO images (
                    id, filename, original_name, file_size, image_width, image_height,
                    dominant_color, color_palette, resnet_features, opencv_features, 
                    upload_date, batch_id, category, background_removed, foreground_pixel_count
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
            
            values = (
            metadata["id"],
            metadata["filename"],
            metadata["original_name"],
            metadata["file_size"],
            metadata["image_width"],
            metadata["image_height"],
            metadata["dominant_color"],
            json.dumps(metadata["color_palette"]),
            json.dumps(metadata["resnet_features"]),
            json.dumps(metadata["opencv_features"]),
            datetime.now(),
            metadata["batch_id"],
            metadata["category"],
            metadata.get("background_removed", False),
            metadata.get("foreground_pixel_count", 0)
        )
                    
            cursor.execute(insert_query, values)
            connection.commit()
            
            logger.info(f"Successfully stored image metadata in database: {metadata['id']}")
            
        except Error as e:
            logger.error(f"Error storing in database: {str(e)}")
            # Clean up file
            if os.path.exists(result["filepath"]):
                os.remove(result["filepath"])
            raise HTTPException(status_code=500, detail="Error storing image metadata")
        
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
        
        return ImageResponse(
            message="Image uploaded and processed successfully",
            image_id=metadata["id"],
            image_url=f"http://127.0.0.1:8000/uploads/{metadata['filename']}",
            metadata=ImageMetadata(**metadata)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_single_image: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")



@app.get("/api/recommend/similar/{image_id}")
def recommend_similar(image_id: str, top_k: int = 5):
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    # 1️⃣ Fetch the query image feature and category
    cursor.execute("SELECT category, resnet_features FROM images WHERE id = %s", (image_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Image not found.")

    category = row['category']
    query_vec = np.array(json.loads(row['resnet_features']), dtype=np.float32)

    # 2️⃣ Fetch all metadata and features for this category
    cursor.execute("SELECT * FROM images WHERE category = %s", (category,))
    metadata_rows = cursor.fetchall()

    exclude_keys = {"resnet_features", "opencv_features"}
    BASE_URL = "http://127.0.0.1:8000/uploads/"

    metadata_map = {}
    for r in metadata_rows:
        meta = {k: v for k, v in r.items() if k not in exclude_keys}
        if 'filename' in meta and meta['filename']:
            meta['image_url'] = BASE_URL + meta['filename']
        metadata_map[r['id']] = meta


    # 3️⃣ Fetch their resnet_features separately
    cursor.execute("SELECT id, resnet_features FROM images WHERE category = %s", (category,))
    rows = cursor.fetchall()

    ids = []
    features = []

    for r in rows:
        ids.append(r['id'])
        vec = np.array(json.loads(r['resnet_features']), dtype=np.float32)
        features.append(vec)

    if len(features) < top_k:
        raise HTTPException(status_code=400, detail="Not enough images in this category to recommend.")

    features = np.vstack(features)

    # 4️⃣ Build KNN on-the-fly
    knn = NearestNeighbors(n_neighbors=min(top_k + 1, len(features)), metric='euclidean')
    knn.fit(features)

    # 5️⃣ Find neighbors
    dists, idxs = knn.kneighbors([query_vec])

    # 6️⃣ Prepare response (exclude self, exclude resnet_features)
    recommendations = []
    for i in idxs[0]:
        if ids[i] != image_id:
            meta = metadata_map.get(ids[i])
            if meta:
                recommendations.append(meta)
        if len(recommendations) >= top_k:
            break

    return {
        "query_image_id": image_id,
        "category": category,
        "recommendations": recommendations
    }


@app.post("/api/upload-images/", response_model=BatchUploadResponse)
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    description: Optional[str] = Form(None)
):
    """Upload and process multiple images (1-20 images)"""
    start_time = datetime.now()
    
    try:
        # Validate number of files
        if len(files) < MIN_FILES_PER_REQUEST:
            raise HTTPException(status_code=400, detail=f"Must upload at least {MIN_FILES_PER_REQUEST} file")
        
        if len(files) > MAX_FILES_PER_REQUEST:
            raise HTTPException(status_code=400, detail=f"Cannot upload more than {MAX_FILES_PER_REQUEST} files at once")
        
        # Generate batch ID
        batch_id = str(uuid.uuid4())
        
        # Prepare file data for processing
        file_data_list = []
        for file in files:
            # Validate file type
            if not file.content_type or not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} must be an image")
            
            # Check file size
            contents = await file.read()
            if len(contents) > MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail=f"File {file.filename} is too large")
            
            file_data_list.append((contents, file.filename, file.filename))
        
        # Process images in parallel
        logger.info(f"Processing {len(file_data_list)} images in batch {batch_id}")
        
        # Use ThreadPoolExecutor for parallel processing
        loop = asyncio.get_event_loop()
        processing_tasks = []
        
        for file_data in file_data_list:
            task = loop.run_in_executor(executor, process_single_image, file_data, batch_id)
            processing_tasks.append(task)
        
        # Wait for all processing to complete
        processing_results = await asyncio.gather(*processing_tasks)
        
        # Separate successful and failed results
        successful_results = [r for r in processing_results if r["success"]]
        failed_results = [r for r in processing_results if not r["success"]]
        
        # Store successful results in database
        stored_results = []
        if successful_results:
            try:
                connection = get_database_connection()
                cursor = connection.cursor()
                
                # Prepare batch insert
                insert_query = """
                INSERT INTO images (
                    id, filename, original_name, file_size, image_width, image_height,
                    dominant_color, color_palette, resnet_features, opencv_features, upload_date, batch_id, category
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values_list = []
                for result in successful_results:
                    metadata = result["metadata"]
                    values = (
                        metadata["id"],
                        metadata["filename"],
                        metadata["original_name"],
                        metadata["file_size"],
                        metadata["image_width"],
                        metadata["image_height"],
                        metadata["dominant_color"],
                        json.dumps(metadata["color_palette"]),
                        json.dumps(metadata["resnet_features"]),
                        json.dumps(metadata["opencv_features"]),
                        datetime.now(),
                        batch_id,
                        metadata["category"]
                    )
                    values_list.append(values)
                
                # Execute batch insert
                cursor.executemany(insert_query, values_list)
                
                # Store batch metadata
                processing_time = (datetime.now() - start_time).total_seconds()
                batch_insert_query = """
                INSERT INTO batch_uploads (
                    batch_id, total_images, successful_images, failed_images, upload_date, processing_time
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """
                batch_values = (
                    batch_id,
                    len(files),
                    len(successful_results),
                    len(failed_results),
                    datetime.now(),
                    processing_time
                )
                cursor.execute(batch_insert_query, batch_values)
                
                connection.commit()
                
                # Prepare successful results for response
                for result in successful_results:
                    metadata = result["metadata"]
                    stored_results.append({
                        "success": True,
                        "image_id": metadata["id"],
                        "filename": metadata["original_name"],
                        "image_url": f"http://127.0.0.1:8000/uploads/{metadata['filename']}",
                        "file_size": metadata["file_size"],
                        "dimensions": f"{metadata['image_width']}x{metadata['image_height']}",
                        "dominant_color": metadata["dominant_color"]
                    })
                
                logger.info(f"Successfully stored {len(successful_results)} images in batch {batch_id}")
                
            except Error as e:
                logger.error(f"Error storing batch in database: {str(e)}")
                # Clean up files on database error
                for result in successful_results:
                    if os.path.exists(result["filepath"]):
                        os.remove(result["filepath"])
                raise HTTPException(status_code=500, detail="Error storing image metadata")
            
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        
        # Add failed results to response
        for result in failed_results:
            stored_results.append({
                "success": False,
                "filename": result["original_name"],
                "error": result["error"]
            })
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return BatchUploadResponse(
            message=f"Batch upload completed. {len(successful_results)} successful, {len(failed_results)} failed.",
            total_images=len(files),
            successful_uploads=len(successful_results),
            failed_uploads=len(failed_results),
            batch_id=batch_id,
            results=stored_results,
            processing_time=processing_time
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_multiple_images: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/batches/")
async def get_batches(
    limit: Optional[int] = Query(10, description="Number of batches to return"),
    offset: Optional[int] = Query(0, description="Offset for pagination")
):
    """Get list of batch uploads"""
    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT * FROM batch_uploads
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """
        
        cursor.execute(query, (limit, offset))
        batches = cursor.fetchall()
        
        return {
            "count": len(batches),
            "batches": batches
        }
    
    except Error as e:
        logger.error(f"Error retrieving batches: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving batches")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.get("/api/batches/{batch_id}")
async def get_batch_images(batch_id: str):
    """Get all images from a specific batch"""
    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get batch info
        batch_query = "SELECT * FROM batch_uploads WHERE batch_id = %s"
        cursor.execute(batch_query, (batch_id,))
        batch_info = cursor.fetchone()
        
        if not batch_info:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        # Get images in batch
        images_query = """
        SELECT id, filename, original_name, file_size, image_width, image_height,
               dominant_color, color_palette, upload_date
        FROM images 
        WHERE batch_id = %s
        ORDER BY created_at
        """
        
        cursor.execute(images_query, (batch_id,))
        images = cursor.fetchall()
        
        # Add image URLs and parse JSON
        for image in images:
            image["image_url"] = f"http://127.0.0.1:8000/uploads/{image['filename']}"
            image["color_palette"] = json.loads(image["color_palette"])
        
        return {
            "batch_info": batch_info,
            "images": images
        }
    
    except Error as e:
        logger.error(f"Error retrieving batch images: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving batch images")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.get("/api/images/")
async def get_images(
    limit: Optional[int] = Query(10, description="Number of images to return"),
    offset: Optional[int] = Query(0, description="Offset for pagination"),
    batch_id: Optional[str] = Query(None, description="Filter by batch ID")
):
    """Get list of uploaded images"""
    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        if batch_id:
            query = """
            SELECT id, filename, original_name, file_size, image_width, image_height,
                   dominant_color, color_palette, upload_date, batch_id, category, created_at
            FROM images
            WHERE batch_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """
            cursor.execute(query, (batch_id, limit, offset))
        else:
            query = """
            SELECT id, filename, original_name, file_size, image_width, image_height,
                   dominant_color, color_palette, upload_date, batch_id, category, created_at
            FROM images
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """
            cursor.execute(query, (limit, offset))
        
        images = cursor.fetchall()
        
        # Add image URLs
        for image in images:
            image["image_url"] = f"http://127.0.0.1:8000/uploads/{image['filename']}"
            image["color_palette"] = json.loads(image["color_palette"])
        
        return {
            "count": len(images),
            "images": images
        }
    
    except Error as e:
        logger.error(f"Error retrieving images: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving images")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.get("/api/images/{image_id}")
async def get_image(image_id: str):
    """Get specific image by ID"""
    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT * FROM images WHERE id = %s
        """
        
        cursor.execute(query, (image_id,))
        image = cursor.fetchone()
        
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Parse JSON fields
        image["color_palette"] = json.loads(image["color_palette"])
        image["resnet_features"] = json.loads(image["resnet_features"])
        image["opencv_features"] = json.loads(image["opencv_features"])
        image["image_url"] = f"http://127.0.0.1:8000/uploads/{image['filename']}"
        
        return image
    
    except Error as e:
        logger.error(f"Error retrieving image: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving image")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.delete("/api/images/{image_id}")
async def delete_image(image_id: str):
    """Delete an image"""
    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get image info first
        cursor.execute("SELECT filename FROM images WHERE id = %s", (image_id,))
        image = cursor.fetchone()
        
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Delete from database
        cursor.execute("DELETE FROM images WHERE id = %s", (image_id,))
        connection.commit()
        
        # Delete file
        filepath = os.path.join(UPLOAD_DIR, image["filename"])
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return {"message": "Image deleted successfully", "image_id": image_id}
    
    except Error as e:
        logger.error(f"Error deleting image: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting image")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.delete("/api/batches/{batch_id}")
async def delete_batch(batch_id: str):
    """Delete an entire batch of images"""
    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get all images in the batch
        cursor.execute("SELECT filename FROM images WHERE batch_id = %s", (batch_id,))
        images = cursor.fetchall()
        
        if not images:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        # Delete images from database
        cursor.execute("DELETE FROM images WHERE batch_id = %s", (batch_id,))
        
        # Delete batch record
        cursor.execute("DELETE FROM batch_uploads WHERE batch_id = %s", (batch_id,))
        
        connection.commit()
        
        # Delete files from disk
        deleted_files = 0
        for image in images:
            filepath = os.path.join(UPLOAD_DIR, image["filename"])
            if os.path.exists(filepath):
                os.remove(filepath)
                deleted_files += 1
        
        return {
            "message": f"Batch deleted successfully. Removed {len(images)} images from database and {deleted_files} files from disk.",
            "batch_id": batch_id,
            "deleted_images": len(images)
        }
    
    except Error as e:
        logger.error(f"Error deleting batch: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting batch")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.get("/api/analytics/")
async def get_analytics():
    """Get analytics about uploaded images"""
    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get basic statistics
        cursor.execute("SELECT COUNT(*) as total_images FROM images")
        total_images = cursor.fetchone()["total_images"]
        
        cursor.execute("SELECT SUM(file_size) as total_size FROM images")
        total_size = cursor.fetchone()["total_size"] or 0
        
        cursor.execute("SELECT AVG(image_width) as avg_width, AVG(image_height) as avg_height FROM images")
        avg_dimensions = cursor.fetchone()
        
        # Get batch statistics
        cursor.execute("SELECT COUNT(*) as total_batches FROM batch_uploads")
        total_batches = cursor.fetchone()["total_batches"]
        
        cursor.execute("SELECT AVG(processing_time) as avg_processing_time FROM batch_uploads")
        avg_processing_time = cursor.fetchone()["avg_processing_time"] or 0
        
        cursor.execute("SELECT AVG(total_images) as avg_batch_size FROM batch_uploads")
        avg_batch_size = cursor.fetchone()["avg_batch_size"] or 0
        
        # Get color distribution
        cursor.execute("SELECT dominant_color, COUNT(*) as count FROM images GROUP BY dominant_color ORDER BY count DESC LIMIT 10")
        color_distribution = cursor.fetchall()
        
        # Get recent batch activity
        cursor.execute("""
            SELECT batch_id, total_images, successful_images, failed_images, upload_date, processing_time
            FROM batch_uploads 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_batches = cursor.fetchall()
        
        # Get upload trends (last 30 days)
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM images 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)
        upload_trends = cursor.fetchall()
        
        return {
            "total_images": total_images,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "average_dimensions": {
                "width": round(avg_dimensions["avg_width"] or 0, 2),
                "height": round(avg_dimensions["avg_height"] or 0, 2)
            },
            "batch_statistics": {
                "total_batches": total_batches,
                "average_processing_time": round(avg_processing_time, 2),
                "average_batch_size": round(avg_batch_size, 2)
            },
            "color_distribution": color_distribution,
            "recent_batches": recent_batches,
            "upload_trends": upload_trends
        }
    
    except Error as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving analytics")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.get("/api/search/")
async def search_images(
    color: Optional[str] = Query(None, description="Search by dominant color (hex format)"),
    min_width: Optional[int] = Query(None, description="Minimum image width"),
    max_width: Optional[int] = Query(None, description="Maximum image width"),
    min_height: Optional[int] = Query(None, description="Minimum image height"),
    max_height: Optional[int] = Query(None, description="Maximum image height"),
    batch_id: Optional[str] = Query(None, description="Filter by batch ID"),
    limit: Optional[int] = Query(10, description="Number of results to return"),
    offset: Optional[int] = Query(0, description="Offset for pagination")
):
    """Search images with various filters"""
    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Build dynamic query
        where_conditions = []
        params = []
        
        if color:
            where_conditions.append("dominant_color = %s")
            params.append(color)
        
        if min_width:
            where_conditions.append("image_width >= %s")
            params.append(min_width)
        
        if max_width:
            where_conditions.append("image_width <= %s")
            params.append(max_width)
        
        if min_height:
            where_conditions.append("image_height >= %s")
            params.append(min_height)
        
        if max_height:
            where_conditions.append("image_height <= %s")
            params.append(max_height)
        
        if batch_id:
            where_conditions.append("batch_id = %s")
            params.append(batch_id)
        
        # Construct query
        base_query = """
        SELECT id, filename, original_name, file_size, image_width, image_height,
               dominant_color, color_palette, upload_date, batch_id, created_at
        FROM images
        """
        
        if where_conditions:
            query = base_query + " WHERE " + " AND ".join(where_conditions)
        else:
            query = base_query
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        images = cursor.fetchall()
        
        # Add image URLs and parse JSON
        for image in images:
            image["image_url"] = f"http://0.0.0.0:8000/uploads/{image['filename']}"
            image["color_palette"] = json.loads(image["color_palette"])
        
        return {
            "count": len(images),
            "images": images,
            "filters_applied": {
                "color": color,
                "min_width": min_width,
                "max_width": max_width,
                "min_height": min_height,
                "max_height": max_height,
                "batch_id": batch_id
            }
        }
    
    except Error as e:
        logger.error(f"Error searching images: {str(e)}")
        raise HTTPException(status_code=500, detail="Error searching images")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

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
    
    # Check model availability
    model_status = "loaded" if resnet_model is not None else "not_loaded"
    
    return {
        "api_status": "healthy",
        "database_status": db_status,
        "upload_directory": {
            "exists": upload_dir_exists,
            "writable": upload_dir_writable
        },
        "resnet_model": model_status,
        "version": "2.0.0",
        "max_files_per_request": MAX_FILES_PER_REQUEST,
        "max_file_size_mb": MAX_FILE_SIZE / (1024 * 1024)
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)