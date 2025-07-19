
from rembg import remove, new_session
from sklearn.cluster import KMeans
import tempfile
import uuid
import os
import json
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

from ..routes.classifier import predict_class_from_pil

from .color_utils import (
    rgb_to_hex, 
    get_color_name, 
    get_tone, 
    get_temperature, 
    get_saturation, 
    get_color_palette
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB per file
MAX_FILES_PER_REQUEST = 20
MIN_FILES_PER_REQUEST = 1




# Load ResNet50 model
try:
    resnet_model = ResNet50(weights='imagenet', include_top=False, pooling='avg')
    logger.info("ResNet50 model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load ResNet50 model: {str(e)}")
    resnet_model = None




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
    



def process_single_image(file_data, batch_id=None, extra_metadata=None):
    """Process a single image - used for parallel processing"""
    if extra_metadata is None:
        extra_metadata = {}
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
        category = predict_class_from_pil(img)
        
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
            "foreground_pixel_count": color_features.get("foreground_pixel_count", 0),  # New field
            "style": extra_metadata.get("style"),
            "occasion": extra_metadata.get("occasion"),
            "season": extra_metadata.get("season"),
            "temperature_range": extra_metadata.get("temperature_range"),
            "gender": extra_metadata.get("gender"),
            "material": extra_metadata.get("material"),
            "pattern": extra_metadata.get("pattern"),
            "user_id": extra_metadata.get("user_id")
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
