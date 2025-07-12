"""
Clothing Item Classification Service using MobileNetV2

This module provides functionality to classify uploaded clothing images into categories
using a pre-trained MobileNetV2 model from TensorFlow/Keras.
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
from PIL import Image
import io
import logging
from typing import Dict, List, Tuple, Optional
import json
import asyncio
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClothingClassifier:
    """
    Clothing item classification service using MobileNetV2.
    
    This class handles loading the pre-trained MobileNetV2 model and provides
    methods to classify clothing items from uploaded images.
    """
    
    def __init__(self, model_cache_dir: str = "models"):
        """
        Initialize the clothing classifier.
        
        Args:
            model_cache_dir: Directory to cache the model files
        """
        self.model_cache_dir = model_cache_dir
        self.model = None
        self.clothing_categories = self._load_clothing_categories()
        
        # Ensure model cache directory exists
        os.makedirs(model_cache_dir, exist_ok=True)
        
        # Load the model
        self._load_model()
    
    def _load_clothing_categories(self) -> Dict[str, List[str]]:
        """
        Load clothing category mappings from ImageNet classes to clothing types.
        
        Returns:
            Dictionary mapping clothing types to ImageNet class names
        """
        return {
            "shirts": [
                "jersey", "sweatshirt", "cardigan", "sweater", "polo_shirt",
                "tee_shirt", "tank_top", "blouse", "shirt"
            ],
            "pants": [
                "jean", "trouser", "sweatpants", "leggings", "shorts",
                "cargo_pants", "chinos"
            ],
            "dresses": [
                "gown", "dress", "cocktail_dress", "wedding_dress",
                "evening_dress", "sundress"
            ],
            "shoes": [
                "running_shoe", "loafer", "oxford_shoe", "sandal",
                "boot", "sneaker", "high_heel", "flip_flop"
            ],
            "outerwear": [
                "jacket", "coat", "blazer", "windbreaker", "parka",
                "trench_coat", "bomber_jacket", "hoodie"
            ],
            "accessories": [
                "hat", "cap", "scarf", "tie", "bow_tie", "belt",
                "glove", "mitten", "sunglasses", "watch", "bag", "purse"
            ],
            "underwear": [
                "bra", "bikini", "swimsuit", "underwear", "lingerie"
            ],
            "skirts": [
                "skirt", "miniskirt", "pleated_skirt"
            ]
        }
    
    def _load_model(self):
        """Load the MobileNetV2 model with ImageNet weights."""
        try:
            logger.info("Loading MobileNetV2 model...")
            
            # Load MobileNetV2 with ImageNet weights
            self.model = MobileNetV2(
                weights='imagenet',
                include_top=True,
                input_shape=(224, 224, 3)
            )
            
            # Set the model to inference mode
            self.model.trainable = False
            
            logger.info("MobileNetV2 model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading MobileNetV2 model: {str(e)}")
            raise
    
    def preprocess_image(self, image_data: bytes) -> np.ndarray:
        """
        Preprocess image data for MobileNetV2 input.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Preprocessed image array ready for model input
        """
        try:
            # Open image from bytes
            img = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize to 224x224 (MobileNetV2 input size)
            img = img.resize((224, 224))
            
            # Convert to numpy array
            img_array = np.array(img)
            
            # Add batch dimension
            img_array = np.expand_dims(img_array, axis=0)
            
            # Preprocess for MobileNetV2
            img_array = preprocess_input(img_array)
            
            return img_array
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise
    
    def classify_clothing_item(self, image_data: bytes) -> Dict[str, any]:
        """
        Classify a clothing item from image data.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary containing classification results
        """
        try:
            if self.model is None:
                raise ValueError("Model not loaded")
            
            # Preprocess the image
            processed_image = self.preprocess_image(image_data)
            
            # Make prediction
            predictions = self.model.predict(processed_image, verbose=0)
            
            # Decode predictions to get top 5 classes
            decoded_predictions = decode_predictions(predictions, top=5)[0]
            
            # Map predictions to clothing categories
            clothing_type, confidence = self._map_to_clothing_category(decoded_predictions)
            
            # Prepare detailed results
            detailed_predictions = [
                {
                    "class_name": pred[1],
                    "description": pred[2],
                    "confidence": float(pred[2])
                }
                for pred in decoded_predictions
            ]
            
            result = {
                "clothing_type": clothing_type,
                "confidence": confidence,
                "detailed_predictions": detailed_predictions,
                "model_used": "MobileNetV2",
                "success": True
            }
            
            logger.info(f"Classification result: {clothing_type} with confidence {confidence:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error classifying clothing item: {str(e)}")
            return {
                "clothing_type": "unknown",
                "confidence": 0.0,
                "detailed_predictions": [],
                "model_used": "MobileNetV2",
                "success": False,
                "error": str(e)
            }
    
    def _map_to_clothing_category(self, predictions: List[Tuple]) -> Tuple[str, float]:
        """
        Map ImageNet predictions to clothing categories.
        
        Args:
            predictions: List of (class_id, class_name, confidence) tuples
            
        Returns:
            Tuple of (clothing_type, confidence)
        """
        # Check each prediction against our clothing categories
        for class_id, class_name, confidence in predictions:
            class_name_lower = class_name.lower().replace('_', ' ')
            
            for clothing_type, keywords in self.clothing_categories.items():
                for keyword in keywords:
                    if keyword.lower() in class_name_lower or class_name_lower in keyword.lower():
                        return clothing_type, float(confidence)
        
        # If no specific clothing category found, try to infer from top prediction
        top_prediction = predictions[0]
        class_name = top_prediction[1].lower()
        
        # Basic keyword matching for common clothing terms
        if any(term in class_name for term in ['shirt', 'top', 'blouse', 'jersey']):
            return "shirts", float(top_prediction[2])
        elif any(term in class_name for term in ['jean', 'trouser', 'pant']):
            return "pants", float(top_prediction[2])
        elif any(term in class_name for term in ['dress', 'gown']):
            return "dresses", float(top_prediction[2])
        elif any(term in class_name for term in ['shoe', 'boot', 'sandal']):
            return "shoes", float(top_prediction[2])
        elif any(term in class_name for term in ['jacket', 'coat']):
            return "outerwear", float(top_prediction[2])
        elif any(term in class_name for term in ['skirt']):
            return "skirts", float(top_prediction[2])
        else:
            return "accessories", float(top_prediction[2])
    
    def get_supported_categories(self) -> List[str]:
        """
        Get list of supported clothing categories.
        
        Returns:
            List of supported clothing category names
        """
        return list(self.clothing_categories.keys())
    
    def batch_classify(self, image_data_list: List[bytes]) -> List[Dict[str, any]]:
        """
        Classify multiple clothing items in batch.
        
        Args:
            image_data_list: List of raw image bytes
            
        Returns:
            List of classification results
        """
        results = []
        for image_data in image_data_list:
            result = self.classify_clothing_item(image_data)
            results.append(result)
        
        return results

# Global classifier instance
_classifier_instance = None
_classifier_lock = asyncio.Lock() # Lock for async instance creation

async def get_clothing_classifier_async() -> ClothingClassifier:
    """
    Asynchronously get or create the global clothing classifier instance.
    Ensures model loading happens in a thread-safe manner for async contexts.
    """
    global _classifier_instance
    if _classifier_instance is None:
        async with _classifier_lock:
            if _classifier_instance is None: # Double check after acquiring lock
                # Model loading can be I/O bound (disk) or CPU bound (TF init)
                # Offload the instantiation if ClothingClassifier._load_model is heavy
                _classifier_instance = await asyncio.to_thread(ClothingClassifier)
    return _classifier_instance

def get_clothing_classifier() -> ClothingClassifier:
    """
    Get or create the global clothing classifier instance (synchronous).
    Note: If called after async initialization, it will return the same instance.
    If called first in a purely synchronous environment, it initializes synchronously.
    It's generally recommended to initialize such heavy objects at application startup.
    """
    global _classifier_instance
    if _classifier_instance is None:
        # This direct instantiation might block if called in an async event loop
        # without prior async initialization.
        _classifier_instance = ClothingClassifier()
    return _classifier_instance

async def classify_clothing_image_async(image_data: bytes) -> Dict[str, any]:
    """
    Asynchronously classify a clothing image.
    Offloads synchronous TensorFlow operations to a thread pool.
    """
    classifier = await get_clothing_classifier_async()
    # The actual prediction is CPU-bound
    return await asyncio.to_thread(classifier.classify_clothing_item, image_data)

def classify_clothing_image(image_data: bytes) -> Dict[str, any]:
    """
    Convenience function to classify a clothing image (synchronous).
    """
    classifier = get_clothing_classifier()
    return classifier.classify_clothing_item(image_data)

# Need to import asyncio at the top of the file


