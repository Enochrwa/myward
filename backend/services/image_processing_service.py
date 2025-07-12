"""
Enhanced image processing service for Digital Wardrobe System
Handles clothing classification, feature extraction, and intelligent naming
"""
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing import image
from sklearn.cluster import KMeans
from colorthief import ColorThief
import os
import uuid
import logging
from typing import Dict, List, Tuple, Optional, Any
import json
from datetime import datetime

from config.settings import settings
from models.database_models import ClothingItemCreate, ClothingImageCreate, ClothingFeaturesCreate
from utils.color_utils import rgb_to_hex, get_color_name, get_tone, get_temperature, get_saturation
from .database_service import db_service

logger = logging.getLogger(__name__)

class ClothingClassifier:
    """AI-powered clothing classification and analysis"""
    
    def __init__(self):
        self.resnet_model = None
        self.load_models()
        
        # Clothing type mappings based on visual features
        self.clothing_type_keywords = {
            'shirt': ['shirt', 'blouse', 'top', 'tee', 't-shirt'],
            'pants': ['pants', 'trousers', 'jeans', 'chinos'],
            'dress': ['dress', 'gown', 'frock'],
            'jacket': ['jacket', 'blazer', 'coat', 'cardigan'],
            'shoes': ['shoes', 'boots', 'sneakers', 'heels', 'sandals'],
            'skirt': ['skirt', 'mini', 'maxi'],
            'shorts': ['shorts', 'bermuda'],
            'sweater': ['sweater', 'pullover', 'jumper', 'hoodie'],
            'suit': ['suit', 'tuxedo'],
            'accessories': ['hat', 'bag', 'belt', 'scarf', 'tie']
        }
        
        # Style classification keywords
        self.style_keywords = {
            'formal': ['formal', 'business', 'professional', 'dress', 'suit', 'blazer'],
            'casual': ['casual', 'everyday', 'relaxed', 'jeans', 't-shirt'],
            'sporty': ['sport', 'athletic', 'gym', 'workout', 'running'],
            'elegant': ['elegant', 'sophisticated', 'classy', 'evening'],
            'trendy': ['trendy', 'fashionable', 'modern', 'stylish'],
            'vintage': ['vintage', 'retro', 'classic', 'traditional']
        }
        
        # Occasion mappings
        self.occasion_keywords = {
            'work': ['work', 'office', 'business', 'professional', 'meeting'],
            'casual': ['casual', 'everyday', 'weekend', 'relaxed'],
            'formal': ['formal', 'evening', 'gala', 'wedding', 'ceremony'],
            'party': ['party', 'celebration', 'festive', 'social'],
            'sport': ['sport', 'gym', 'workout', 'exercise', 'fitness'],
            'vacation': ['vacation', 'travel', 'holiday', 'beach', 'summer']
        }
        
        # Season/weather suitability
        self.season_indicators = {
            'summer': ['light', 'thin', 'breathable', 'cotton', 'linen', 'short'],
            'winter': ['warm', 'thick', 'wool', 'heavy', 'long', 'coat'],
            'spring': ['light', 'medium', 'layering', 'transitional'],
            'fall': ['medium', 'layering', 'warm', 'long-sleeve']
        }
    
    def load_models(self):
        """Load AI models for image analysis"""
        try:
            # Load ResNet50 for feature extraction
            self.resnet_model = ResNet50(
                weights='imagenet',
                include_top=False,
                pooling='avg',
                input_shape=(224, 224, 3)
            )
            logger.info("ResNet50 model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load ResNet50 model: {e}")
            self.resnet_model = None
    
    def extract_resnet_features(self, image_path: str) -> List[float]:
        """Extract deep learning features using ResNet50"""
        try:
            if self.resnet_model is None:
                logger.warning("ResNet50 model not available")
                return []
            
            # Load and preprocess image
            img = image.load_img(image_path, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = preprocess_input(img_array)
            
            # Extract features
            features = self.resnet_model.predict(img_array, verbose=0)
            return features.flatten().tolist()
            
        except Exception as e:
            logger.error(f"Error extracting ResNet features: {e}")
            return []
    
    def extract_opencv_features(self, image_path: str) -> Dict[str, Any]:
        """Extract computer vision features using OpenCV"""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Convert to different color spaces
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            
            # Basic statistics
            height, width = img.shape[:2]
            aspect_ratio = height / width
            
            # Color analysis
            mean_bgr = np.mean(img, axis=(0, 1)).tolist()
            std_bgr = np.std(img, axis=(0, 1)).tolist()
            
            # Brightness and contrast
            brightness = float(np.mean(gray))
            contrast = float(np.std(gray))
            
            # Texture analysis
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Edge detection
            edges = cv2.Canny(gray, 100, 200)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            # Color histograms
            hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
            hist_s = cv2.calcHist([hsv], [1], None, [256], [0, 256])
            hist_v = cv2.calcHist([hsv], [2], None, [256], [0, 256])
            
            # Dominant hue
            dominant_hue = int(np.argmax(hist_h))
            
            # Saturation analysis
            avg_saturation = float(np.mean(hsv[:, :, 1]))
            
            # Shape analysis (basic)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                contour_area = cv2.contourArea(largest_contour)
                contour_perimeter = cv2.arcLength(largest_contour, True)
                if contour_perimeter > 0:
                    circularity = 4 * np.pi * contour_area / (contour_perimeter * contour_perimeter)
                else:
                    circularity = 0
            else:
                circularity = 0
            
            return {
                "dimensions": {"width": width, "height": height, "aspect_ratio": aspect_ratio},
                "color_stats": {
                    "mean_bgr": mean_bgr,
                    "std_bgr": std_bgr,
                    "brightness": brightness,
                    "contrast": contrast,
                    "dominant_hue": dominant_hue,
                    "avg_saturation": avg_saturation
                },
                "texture": {
                    "laplacian_variance": float(laplacian_var),
                    "edge_density": float(edge_density)
                },
                "shape": {
                    "circularity": float(circularity)
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting OpenCV features: {e}")
            return {}
    
    def extract_color_features(self, image_path: str) -> Dict[str, Any]:
        """Extract comprehensive color features"""
        try:
            # Get dominant colors using ColorThief
            color_thief = ColorThief(image_path)
            dominant_color = color_thief.get_color(quality=1)
            palette = color_thief.get_palette(color_count=5, quality=1)
            
            # Convert to hex and get color names
            dominant_hex = rgb_to_hex(*dominant_color)
            palette_hex = [rgb_to_hex(*color) for color in palette]
            
            # Get color properties
            dominant_color_name = get_color_name(list(dominant_color))
            tone = get_tone(list(dominant_color))
            temperature = get_temperature(list(dominant_color))
            saturation = get_saturation(list(dominant_color))
            
            # Analyze color harmony
            color_harmony = self._analyze_color_harmony(palette)
            
            return {
                "dominant_color": {
                    "rgb": list(dominant_color),
                    "hex": dominant_hex,
                    "name": dominant_color_name,
                    "tone": tone,
                    "temperature": temperature,
                    "saturation": saturation
                },
                "palette": {
                    "colors": [{"rgb": list(color), "hex": rgb_to_hex(*color)} for color in palette],
                    "hex_codes": palette_hex,
                    "harmony": color_harmony
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting color features: {e}")
            return {}
    
    def _analyze_color_harmony(self, palette: List[Tuple[int, int, int]]) -> Dict[str, Any]:
        """Analyze color harmony in the palette"""
        try:
            if len(palette) < 2:
                return {"type": "monochromatic", "score": 1.0}
            
            # Convert to HSV for better color analysis
            hsv_colors = []
            for rgb in palette:
                r, g, b = [x/255.0 for x in rgb]
                h, s, v = cv2.cvtColor(np.uint8([[[r*255, g*255, b*255]]]), cv2.COLOR_RGB2HSV)[0][0]
                hsv_colors.append((h, s, v))
            
            # Analyze hue differences
            hues = [color[0] for color in hsv_colors]
            hue_range = max(hues) - min(hues)
            
            # Determine harmony type
            if hue_range < 30:
                harmony_type = "monochromatic"
                score = 0.9
            elif hue_range < 60:
                harmony_type = "analogous"
                score = 0.8
            elif 150 < hue_range < 210:
                harmony_type = "complementary"
                score = 0.85
            else:
                harmony_type = "triadic"
                score = 0.7
            
            return {
                "type": harmony_type,
                "score": score,
                "hue_range": float(hue_range)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing color harmony: {e}")
            return {"type": "unknown", "score": 0.5}
    
    def classify_clothing_type(self, image_path: str, filename: str) -> Dict[str, Any]:
        """Classify clothing type using multiple approaches"""
        try:
            # Filename-based classification
            filename_lower = filename.lower()
            filename_type = None
            filename_confidence = 0.0
            
            for clothing_type, keywords in self.clothing_type_keywords.items():
                for keyword in keywords:
                    if keyword in filename_lower:
                        filename_type = clothing_type
                        filename_confidence = 0.8
                        break
                if filename_type:
                    break
            
            # Image-based classification (using aspect ratio and features)
            opencv_features = self.extract_opencv_features(image_path)
            image_type = None
            image_confidence = 0.0
            
            if opencv_features:
                aspect_ratio = opencv_features.get("dimensions", {}).get("aspect_ratio", 1.0)
                
                # Simple heuristic based on aspect ratio
                if aspect_ratio > 1.5:
                    image_type = "dress" if "dress" in filename_lower else "pants"
                    image_confidence = 0.6
                elif aspect_ratio > 1.2:
                    image_type = "shirt"
                    image_confidence = 0.6
                elif aspect_ratio < 0.8:
                    image_type = "shoes" if any(word in filename_lower for word in ["shoe", "boot", "sneaker"]) else "pants"
                    image_confidence = 0.6
                else:
                    image_type = "jacket"
                    image_confidence = 0.5
            
            # Combine results
            if filename_confidence > image_confidence:
                final_type = filename_type
                final_confidence = filename_confidence
            else:
                final_type = image_type
                final_confidence = image_confidence
            
            return {
                "clothing_type": final_type or "unknown",
                "confidence": final_confidence,
                "filename_suggestion": filename_type,
                "image_suggestion": image_type
            }
            
        except Exception as e:
            logger.error(f"Error classifying clothing type: {e}")
            return {"clothing_type": "unknown", "confidence": 0.0}
    
    def classify_style(self, image_path: str, filename: str, color_features: Dict) -> Dict[str, Any]:
        """Classify clothing style"""
        try:
            filename_lower = filename.lower()
            style_scores = {}
            
            # Filename-based style detection
            for style, keywords in self.style_keywords.items():
                score = 0.0
                for keyword in keywords:
                    if keyword in filename_lower:
                        score += 0.3
                style_scores[style] = score
            
            # Color-based style hints
            if color_features:
                dominant_color = color_features.get("dominant_color", {})
                tone = dominant_color.get("tone", "").lower()
                temperature = dominant_color.get("temperature", "").lower()
                
                # Formal styles tend to have darker, cooler colors
                if tone == "dark" and temperature == "cool":
                    style_scores["formal"] = style_scores.get("formal", 0) + 0.2
                    style_scores["elegant"] = style_scores.get("elegant", 0) + 0.2
                
                # Bright, warm colors suggest casual or trendy
                if tone == "light" and temperature == "warm":
                    style_scores["casual"] = style_scores.get("casual", 0) + 0.2
                    style_scores["trendy"] = style_scores.get("trendy", 0) + 0.2
            
            # Find the highest scoring style
            if style_scores:
                best_style = max(style_scores, key=style_scores.get)
                confidence = min(style_scores[best_style], 1.0)
            else:
                best_style = "casual"
                confidence = 0.3
            
            return {
                "style": best_style,
                "confidence": confidence,
                "all_scores": style_scores
            }
            
        except Exception as e:
            logger.error(f"Error classifying style: {e}")
            return {"style": "casual", "confidence": 0.3}
    
    def classify_occasion(self, clothing_type: str, style: str, color_features: Dict) -> Dict[str, Any]:
        """Classify suitable occasions"""
        try:
            occasion_scores = {}
            
            # Base scores from clothing type
            type_occasion_map = {
                "suit": {"work": 0.9, "formal": 0.9},
                "dress": {"formal": 0.8, "party": 0.7, "work": 0.6},
                "shirt": {"work": 0.7, "casual": 0.6},
                "jeans": {"casual": 0.9, "weekend": 0.8},
                "sneakers": {"sport": 0.9, "casual": 0.8},
                "heels": {"formal": 0.8, "party": 0.8}
            }
            
            if clothing_type in type_occasion_map:
                for occasion, score in type_occasion_map[clothing_type].items():
                    occasion_scores[occasion] = score
            
            # Adjust based on style
            style_adjustments = {
                "formal": {"work": 0.3, "formal": 0.3},
                "casual": {"casual": 0.3, "weekend": 0.2},
                "sporty": {"sport": 0.4, "casual": 0.2},
                "elegant": {"formal": 0.3, "party": 0.2}
            }
            
            if style in style_adjustments:
                for occasion, adjustment in style_adjustments[style].items():
                    occasion_scores[occasion] = occasion_scores.get(occasion, 0) + adjustment
            
            # Color-based adjustments
            if color_features:
                dominant_color = color_features.get("dominant_color", {})
                tone = dominant_color.get("tone", "").lower()
                
                if tone == "dark":
                    occasion_scores["formal"] = occasion_scores.get("formal", 0) + 0.1
                    occasion_scores["work"] = occasion_scores.get("work", 0) + 0.1
                elif tone == "light":
                    occasion_scores["casual"] = occasion_scores.get("casual", 0) + 0.1
            
            # Normalize scores
            if occasion_scores:
                max_score = max(occasion_scores.values())
                if max_score > 1.0:
                    occasion_scores = {k: v/max_score for k, v in occasion_scores.items()}
            
            return {
                "primary_occasion": max(occasion_scores, key=occasion_scores.get) if occasion_scores else "casual",
                "all_occasions": occasion_scores,
                "confidence": max(occasion_scores.values()) if occasion_scores else 0.5
            }
            
        except Exception as e:
            logger.error(f"Error classifying occasion: {e}")
            return {"primary_occasion": "casual", "confidence": 0.5}
    
    def classify_season(self, clothing_type: str, color_features: Dict, opencv_features: Dict) -> Dict[str, Any]:
        """Classify season suitability"""
        try:
            season_scores = {"spring": 0.5, "summer": 0.5, "fall": 0.5, "winter": 0.5}
            
            # Clothing type based seasons
            type_season_map = {
                "shorts": {"summer": 0.9},
                "tank": {"summer": 0.8},
                "coat": {"winter": 0.9, "fall": 0.7},
                "sweater": {"winter": 0.8, "fall": 0.8},
                "dress": {"spring": 0.7, "summer": 0.7},
                "boots": {"winter": 0.8, "fall": 0.7}
            }
            
            for type_key, seasons in type_season_map.items():
                if type_key in clothing_type.lower():
                    for season, score in seasons.items():
                        season_scores[season] = max(season_scores[season], score)
            
            # Color-based season hints
            if color_features:
                dominant_color = color_features.get("dominant_color", {})
                temperature = dominant_color.get("temperature", "").lower()
                tone = dominant_color.get("tone", "").lower()
                
                if temperature == "warm":
                    season_scores["summer"] += 0.2
                    season_scores["spring"] += 0.1
                elif temperature == "cool":
                    season_scores["winter"] += 0.2
                    season_scores["fall"] += 0.1
                
                if tone == "light":
                    season_scores["spring"] += 0.1
                    season_scores["summer"] += 0.1
                elif tone == "dark":
                    season_scores["fall"] += 0.1
                    season_scores["winter"] += 0.1
            
            # Normalize scores
            max_score = max(season_scores.values())
            if max_score > 1.0:
                season_scores = {k: v/max_score for k, v in season_scores.items()}
            
            # Find primary and secondary seasons
            sorted_seasons = sorted(season_scores.items(), key=lambda x: x[1], reverse=True)
            
            return {
                "primary_season": sorted_seasons[0][0],
                "secondary_season": sorted_seasons[1][0] if len(sorted_seasons) > 1 else None,
                "all_seasons": season_scores,
                "confidence": sorted_seasons[0][1]
            }
            
        except Exception as e:
            logger.error(f"Error classifying season: {e}")
            return {"primary_season": "all_seasons", "confidence": 0.5}

class ImageProcessingService:
    """Main image processing service for the wardrobe system"""
    
    def __init__(self):
        self.classifier = ClothingClassifier()
        self.upload_dir = settings.upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def generate_intelligent_filename(self, 
                                    original_filename: str,
                                    clothing_type: str,
                                    color_name: str,
                                    occasion: str,
                                    style: str) -> str:
        """Generate intelligent filename based on analysis results"""
        try:
            # Clean inputs
            color_clean = color_name.lower().replace(" ", "_")
            type_clean = clothing_type.lower().replace(" ", "_")
            occasion_clean = occasion.lower().replace(" ", "_")
            style_clean = style.lower().replace(" ", "_")
            
            # Get file extension
            _, ext = os.path.splitext(original_filename)
            if not ext:
                ext = ".jpg"
            
            # Generate counter for uniqueness
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create intelligent filename
            # Format: color_type_style_occasion_timestamp.ext
            intelligent_name = f"{color_clean}_{type_clean}_{style_clean}_{occasion_clean}_{timestamp}{ext}"
            
            # Ensure filename is not too long
            if len(intelligent_name) > 100:
                intelligent_name = f"{color_clean}_{type_clean}_{timestamp}{ext}"
            
            return intelligent_name
            
        except Exception as e:
            logger.error(f"Error generating intelligent filename: {e}")
            # Fallback to UUID-based naming
            return f"{uuid.uuid4().hex}{os.path.splitext(original_filename)[1] or '.jpg'}"
    
    def process_clothing_image(self, 
                             image_data: bytes,
                             original_filename: str,
                             user_id: str) -> Optional[Dict[str, Any]]:
        """Process uploaded clothing image with full analysis"""
        try:
            # Generate temporary filename for processing
            temp_filename = f"temp_{uuid.uuid4().hex}{os.path.splitext(original_filename)[1] or '.jpg'}"
            temp_path = os.path.join(self.upload_dir, temp_filename)
            
            # Save temporary file
            with open(temp_path, "wb") as f:
                f.write(image_data)
            
            # Get image dimensions
            with Image.open(temp_path) as img:
                width, height = img.size
            
            # Extract all features
            resnet_features = self.classifier.extract_resnet_features(temp_path)
            opencv_features = self.classifier.extract_opencv_features(temp_path)
            color_features = self.classifier.extract_color_features(temp_path)
            
            # Classify clothing attributes
            clothing_classification = self.classifier.classify_clothing_type(temp_path, original_filename)
            style_classification = self.classifier.classify_style(temp_path, original_filename, color_features)
            occasion_classification = self.classifier.classify_occasion(
                clothing_classification["clothing_type"],
                style_classification["style"],
                color_features
            )
            season_classification = self.classifier.classify_season(
                clothing_classification["clothing_type"],
                color_features,
                opencv_features
            )
            
            # Generate intelligent filename
            intelligent_filename = self.generate_intelligent_filename(
                original_filename,
                clothing_classification["clothing_type"],
                color_features.get("dominant_color", {}).get("name", "unknown"),
                occasion_classification["primary_occasion"],
                style_classification["style"]
            )
            
            # Move file to final location with intelligent name
            final_path = os.path.join(self.upload_dir, intelligent_filename)
            os.rename(temp_path, final_path)
            
            # Prepare comprehensive analysis results
            analysis_results = {
                "file_info": {
                    "original_filename": original_filename,
                    "stored_filename": intelligent_filename,
                    "file_size": len(image_data),
                    "dimensions": {"width": width, "height": height}
                },
                "clothing_analysis": {
                    "type": clothing_classification,
                    "style": style_classification,
                    "occasion": occasion_classification,
                    "season": season_classification
                },
                "features": {
                    "resnet": resnet_features,
                    "opencv": opencv_features,
                    "color": color_features
                },
                "image_url": f"/uploads/{intelligent_filename}"
            }
            
            logger.info(f"Successfully processed clothing image: {intelligent_filename}")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error processing clothing image: {e}")
            # Clean up temporary file if it exists
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            return None
    
    def enhance_image_quality(self, image_path: str) -> str:
        """Enhance image quality for better analysis"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Enhance contrast and sharpness
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.2)
                
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(1.1)
                
                # Save enhanced image
                enhanced_path = image_path.replace('.', '_enhanced.')
                img.save(enhanced_path, quality=95)
                
                return enhanced_path
                
        except Exception as e:
            logger.error(f"Error enhancing image: {e}")
            return image_path

# Global image processing service instance
image_processing_service = ImageProcessingService()

