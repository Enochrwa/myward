# Enhanced AI Model Manager with Persistent Caching
# This module manages AI model loading, caching, and persistence to prevent re-downloading

import os
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
import tensorflow as tf
import tensorflow_hub as hub
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Centralized model management with persistent caching and version control
    """
    
    def __init__(self, cache_dir: str = "tmp/wardrobe_models"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.models_cache = {}
        self.model_metadata_file = self.cache_dir / "model_metadata.json"
        self.load_metadata()
        
        # Model configurations
        self.model_configs = {
            "mobilenet_v2": {
                "url": "https://tfhub.dev/google/imagenet/mobilenet_v2_100_224/feature_vector/5", # Updated URL
                "input_shape": (224, 224, 3),
                "cache_key": "mobilenet_v2_embedding",
                "version": "1.1" # Bump version due to URL change
            },
            "efficientdet_lite0": {
                "url": "https://tfhub.dev/tensorflow/efficientdet/lite0/detection/1",
                "input_shape": None,  # Variable input size
                "cache_key": "efficientdet_lite0_detection",
                "version": "1.0"
            }
        }
    
    def load_metadata(self):
        """Load model metadata from cache"""
        try:
            if self.model_metadata_file.exists():
                with open(self.model_metadata_file, 'r') as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {}
        except Exception as e:
            logger.error(f"Error loading model metadata: {e}")
            self.metadata = {}
    
    def save_metadata(self):
        """Save model metadata to cache"""
        try:
            with open(self.model_metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving model metadata: {e}")
    
    def get_model_cache_path(self, model_name: str) -> Path:
        """Get the cache path for a specific model"""
        return self.cache_dir / f"{model_name}_cached"
    
    def is_model_cached(self, model_name: str) -> bool:
        """Check if model is already cached and valid"""
        cache_path = self.get_model_cache_path(model_name)
        if not cache_path.exists():
            return False
        
        # Check metadata for version and expiry
        if model_name in self.metadata:
            cached_version = self.metadata[model_name].get("version")
            expected_version = self.model_configs[model_name]["version"]
            
            if cached_version != expected_version:
                logger.info(f"Model {model_name} version mismatch. Cached: {cached_version}, Expected: {expected_version}")
                return False
            
            # Check if cache is not too old (30 days)
            cached_date = datetime.fromisoformat(self.metadata[model_name].get("cached_date", "1970-01-01"))
            if datetime.now() - cached_date > timedelta(days=30):
                logger.info(f"Model {model_name} cache expired")
                return False
        
        return True
    
    def cache_model(self, model_name: str, model):
        """Cache a loaded model to disk"""
        try:
            cache_path = self.get_model_cache_path(model_name)
            
            # Save the model
            tf.saved_model.save(model, str(cache_path))
            
            # Update metadata
            self.metadata[model_name] = {
                "version": self.model_configs[model_name]["version"],
                "cached_date": datetime.now().isoformat(),
                "cache_path": str(cache_path),
                "url": self.model_configs[model_name]["url"]
            }
            self.save_metadata()
            
            logger.info(f"Model {model_name} cached successfully at {cache_path}")
            
        except Exception as e:
            logger.error(f"Error caching model {model_name}: {e}")
    
    def load_cached_model(self, model_name: str):
        """Load a model from cache"""
        try:
            cache_path = self.get_model_cache_path(model_name)
            model = tf.saved_model.load(str(cache_path))
            logger.info(f"Model {model_name} loaded from cache")
            return model
        except Exception as e:
            logger.error(f"Error loading cached model {model_name}: {e}")
            return None
    
    def get_model(self, model_name: str):
        """Get a model, loading from cache or downloading if necessary"""
        # Check if model is already in memory
        if model_name in self.models_cache:
            return self.models_cache[model_name]
        
        # Check if model is cached on disk
        if self.is_model_cached(model_name):
            model = self.load_cached_model(model_name)
            if model is not None:
                self.models_cache[model_name] = model
                return model
        
        # Download and cache the model
        logger.info(f"Downloading model {model_name}...")
        try:
            config = self.model_configs[model_name]
            
            if model_name == "mobilenet_v2":
                # Load KerasLayer from TF Hub
                keras_layer = hub.KerasLayer(config["url"], trainable=False)
    
                # Remove this problematic check
                # if not isinstance(keras_layer, tf.keras.layers.Layer):
                #     raise TypeError(f"Downloaded module is not a valid Keras Layer: {type(keras_layer)}")

                # ✅ Use Functional API instead of Sequential
                inputs = tf.keras.Input(shape=config["input_shape"])
                outputs = keras_layer(inputs)
                model = tf.keras.Model(inputs=inputs, outputs=outputs)
            else:
                model = hub.load(config["url"])
            
            # Cache the model
            self.cache_model(model_name, model)
            
            # Store in memory cache
            self.models_cache[model_name] = model
            
            logger.info(f"Model {model_name} downloaded and cached successfully")
            return model
            
        except Exception as e:
            logger.error(f"Error downloading model {model_name}: {e}")
            return None
    
    def clear_cache(self, model_name: Optional[str] = None):
        """Clear model cache"""
        if model_name:
            # Clear specific model
            cache_path = self.get_model_cache_path(model_name)
            if cache_path.exists():
                import shutil
                shutil.rmtree(cache_path)
            
            if model_name in self.metadata:
                del self.metadata[model_name]
            
            if model_name in self.models_cache:
                del self.models_cache[model_name]
                
            logger.info(f"Cache cleared for model {model_name}")
        else:
            # Clear all models
            import shutil
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
            self.metadata = {}
            self.models_cache = {}
            
            logger.info("All model caches cleared")
        
        self.save_metadata()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached models"""
        info = {
            "cache_dir": str(self.cache_dir),
            "models": {}
        }
        
        for model_name, config in self.model_configs.items():
            model_info = {
                "configured": True,
                "cached": self.is_model_cached(model_name),
                "in_memory": model_name in self.models_cache,
                "url": config["url"],
                "version": config["version"]
            }
            
            if model_name in self.metadata:
                model_info.update({
                    "cached_date": self.metadata[model_name].get("cached_date"),
                    "cache_path": self.metadata[model_name].get("cache_path")
                })
            
            info["models"][model_name] = model_info
        
        return info

# Global model manager instance
model_manager = ModelManager()

def get_model_manager() -> ModelManager:
    """Get the global model manager instance"""
    return model_manager

