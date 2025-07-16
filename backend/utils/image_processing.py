# utils/image_processing.py
import cv2
import numpy as np
from sklearn.cluster import KMeans
from typing import List, Dict, Tuple
import os

def process_image(path: str) -> Dict:
    """Process image and extract comprehensive features"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image file not found: {path}")
    
    image = cv2.imread(path)
    if image is None:
        raise ValueError(f"Could not read image: {path}")
    
    # Convert BGR to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Resize for consistent processing
    image_resized = cv2.resize(image_rgb, (128, 128))
    
    # Extract features
    features = {
        "avg_color": get_average_color(image_resized),
        "dominant_colors": get_dominant_colors(image_resized, k=3),
        "texture_features": get_texture_features(image_resized),
        "color_distribution": get_color_distribution(image_resized)
    }
    
    return features

def get_average_color(image: np.ndarray) -> List[float]:
    """Get average color of the image"""
    avg_color = np.mean(image, axis=(0, 1))
    return avg_color.tolist()

def get_dominant_colors(image: np.ndarray, k: int = 3) -> List[Dict]:
    """Extract dominant colors using K-means clustering"""
    # Reshape image to be a list of pixels
    pixels = image.reshape(-1, 3)
    
    # Apply K-means clustering
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    # Get the colors and their percentages
    colors = kmeans.cluster_centers_
    labels = kmeans.labels_
    
    # Calculate percentages
    label_counts = np.bincount(labels)
    percentages = label_counts / len(labels)
    
    dominant_colors = []
    for i, (color, percentage) in enumerate(zip(colors, percentages)):
        dominant_colors.append({
            "rgb": color.tolist(),
            "percentage": float(percentage),
            "rank": i + 1
        })
    
    # Sort by percentage (descending)
    dominant_colors.sort(key=lambda x: x["percentage"], reverse=True)
    
    return dominant_colors

def get_texture_features(image: np.ndarray) -> Dict:
    """Extract texture features from the image"""
    # Convert to grayscale for texture analysis
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    # Calculate Laplacian variance (measure of blur/sharpness)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # Calculate standard deviation (measure of contrast)
    std_dev = np.std(gray)
    
    # Calculate mean intensity
    mean_intensity = np.mean(gray)
    
    # Simple texture classification
    if laplacian_var > 500:
        texture_type = "Textured"
    elif laplacian_var > 100:
        texture_type = "Moderate"
    else:
        texture_type = "Smooth"
    
    return {
        "laplacian_variance": float(laplacian_var),
        "contrast": float(std_dev),
        "brightness": float(mean_intensity),
        "texture_type": texture_type
    }

def get_color_distribution(image: np.ndarray) -> Dict:
    """Analyze color distribution in the image"""
    # Convert to HSV for better color analysis
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    
    # Calculate histograms
    hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
    hist_s = cv2.calcHist([hsv], [1], None, [256], [0, 256])
    hist_v = cv2.calcHist([hsv], [2], None, [256], [0, 256])
    
    # Calculate color diversity (entropy-like measure)
    def calculate_diversity(hist):
        hist_norm = hist / hist.sum()
        hist_norm = hist_norm[hist_norm > 0]  # Remove zeros
        return -np.sum(hist_norm * np.log2(hist_norm))
    
    hue_diversity = calculate_diversity(hist_h)
    saturation_diversity = calculate_diversity(hist_s)
    value_diversity = calculate_diversity(hist_v)
    
    return {
        "hue_diversity": float(hue_diversity),
        "saturation_diversity": float(saturation_diversity),
        "value_diversity": float(value_diversity),
        "overall_diversity": float((hue_diversity + saturation_diversity + value_diversity) / 3)
    }

def detect_clothing_type(image: np.ndarray) -> str:
    """Basic clothing type detection based on image shape and features"""
    height, width = image.shape[:2]
    aspect_ratio = height / width
    
    # Simple heuristic based on aspect ratio
    if aspect_ratio > 1.5:
        return "Dress/Long"
    elif aspect_ratio > 1.2:
        return "Shirt/Top"
    elif aspect_ratio < 0.8:
        return "Pants/Bottom"
    else:
        return "Jacket/Outerwear"

def preprocess_for_matching(image_path: str) -> np.ndarray:
    """Preprocess image for feature matching"""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")
    
    # Convert to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Resize to standard size
    image_resized = cv2.resize(image_rgb, (128, 128))
    
    # Normalize pixel values
    image_normalized = image_resized.astype(np.float32) / 255.0
    
    return image_normalized