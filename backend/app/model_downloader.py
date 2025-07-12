#!/usr/bin/env python3
"""
Model Download Script for Wardrobe AI Backend
Downloads and saves all required ML models locally for offline inference
"""

import os
import json
import logging
import urllib.request
import zipfile
import tarfile
from pathlib import Path
from typing import Dict, Any, List
import tensorflow as tf
import tensorflow_hub as hub
from transformers import CLIPProcessor, CLIPModel
# import torch
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelDownloader:
    """Download and save ML models locally for offline inference"""
    
    def __init__(self, base_dir: str = "ml/models"):
        self.base_dir = Path(base_dir)
        self.setup_directories()
        self.load_config()
    
    def setup_directories(self):
        """Create the ML backend directory structure"""
        directories = [
            "models/classifiers",
            "models/extractors", 
            "models/recommenders",
            "models/pose",
            "models/segmentation",
            "models/clip",
            "matchers",
            "utils",
            "data/samples",
            "configs"
        ]
        
        for directory in directories:
            (self.base_dir / directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {self.base_dir / directory}")
    
    def load_config(self):
        """Load model configuration"""
        self.models_config = {
            "mobilenet_v2": {
                "url": "https://tfhub.dev/google/imagenet/mobilenet_v2_100_224/feature_vector/5",
                "path": "models/extractors/mobilenet_v2",
                "type": "feature_extractor",
                "input_shape": [224, 224, 3],
                "description": "Lightweight feature extractor for clothing similarity"
            },
            "efficientdet_lite0": {
                "url": "https://tfhub.dev/tensorflow/efficientdet/lite0/detection/1",
                "path": "models/classifiers/efficientdet_lite0",
                "type": "object_detection",
                "input_shape": "variable",
                "description": "Detect multiple clothing items in photos"
            },
            "movenet_singlepose": {
                "url": "https://tfhub.dev/google/movenet/singlepose/lightning/4",
                "path": "models/pose/movenet_singlepose",
                "type": "pose_detection",
                "input_shape": [192, 192, 3],
                "description": "Human pose detection for virtual try-on"
            },
            "movenet_multipose": {
                "url": "https://tfhub.dev/google/movenet/multipose/lightning/1",
                "path": "models/pose/movenet_multipose", 
                "type": "pose_detection",
                "input_shape": [256, 256, 3],
                "description": "Multi-person pose detection"
            },
            "deeplabv3": {
                "url": "https://tfhub.dev/tensorflow/deeplabv3/1",
                "path": "models/segmentation/deeplabv3",
                "type": "segmentation",
                "input_shape": [513, 513, 3],
                "description": "Segment clothes from background"
            },
            "clip": {
                "model_name": "openai/clip-vit-base-patch32",
                "path": "models/clip/clip_vit_base",
                "type": "visual_text_matching",
                "description": "Match text queries to clothing images"
            }
        }
    
    def download_tensorflow_hub_model(self, model_name: str, config: Dict[str, Any]) -> bool:
        """Download and save TensorFlow Hub model"""
        try:
            logger.info(f"Downloading {model_name} from TF Hub...")
            model_path = self.base_dir / config["path"]
            
            # Load model from TF Hub
            model = hub.load(config["url"])
            
            # Save model locally
            tf.saved_model.save(model, str(model_path))
            
            # Save model metadata
            metadata = {
                "name": model_name,
                "url": config["url"],
                "type": config["type"],
                "input_shape": config["input_shape"],
                "description": config["description"],
                "download_date": str(pd.Timestamp.now()),
                "framework": "tensorflow"
            }
            
            with open(model_path / "metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"✅ {model_name} downloaded successfully to {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download {model_name}: {e}")
            return False
    
    def download_clip_model(self, config: Dict[str, Any]) -> bool:
        """Download and save CLIP model from Hugging Face"""
        try:
            logger.info("Downloading CLIP model from Hugging Face...")
            model_path = self.base_dir / config["path"]
            
            # Download CLIP model and processor
            model = CLIPModel.from_pretrained(config["model_name"])
            processor = CLIPProcessor.from_pretrained(config["model_name"])
            
            # Save model and processor
            model.save_pretrained(str(model_path / "model"))
            processor.save_pretrained(str(model_path / "processor"))
            
            # Save metadata
            metadata = {
                "name": "clip",
                "model_name": config["model_name"],
                "type": config["type"],
                "description": config["description"],
                "download_date": str(pd.Timestamp.now()),
                "framework": "transformers"
            }
            
            with open(model_path / "metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"✅ CLIP model downloaded successfully to {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download CLIP model: {e}")
            return False
    
    def create_config_files(self):
        """Create configuration files"""
        
        # Model versions config
        model_versions = {
            "models": self.models_config,
            "last_updated": str(pd.Timestamp.now()),
            "version": "1.0"
        }
        
        with open(self.base_dir / "configs/model_versions.json", "w") as f:
            json.dump(model_versions, f, indent=2)
        
        # Clothing types config
        clothing_types = {
            "categories": {
                "tops": ["shirt", "t-shirt", "blouse", "sweater", "hoodie", "jacket", "blazer"],
                "bottoms": ["jeans", "pants", "shorts", "skirt", "leggings"],
                "dresses": ["dress", "gown", "sundress"],
                "outerwear": ["coat", "jacket", "cardigan", "vest"],
                "footwear": ["shoes", "boots", "sneakers", "sandals", "heels"],
                "accessories": ["hat", "scarf", "belt", "bag", "jewelry"]
            },
            "colors": [
                "black", "white", "gray", "navy", "blue", "red", "green", 
                "yellow", "orange", "purple", "pink", "brown", "beige", "cream"
            ],
            "styles": [
                "casual", "formal", "business", "sporty", "bohemian", 
                "vintage", "modern", "classic", "trendy", "minimalist"
            ]
        }
        
        with open(self.base_dir / "configs/clothing_types.json", "w") as f:
            json.dump(clothing_types, f, indent=2)
        
        # Event types config
        event_types = {
            "occasions": {
                "work": {
                    "styles": ["business", "formal", "professional"],
                    "colors": ["navy", "black", "gray", "white"],
                    "categories": ["blazer", "shirt", "pants", "dress"]
                },
                "casual": {
                    "styles": ["casual", "relaxed"],
                    "colors": ["any"],
                    "categories": ["jeans", "t-shirt", "sneakers"]
                },
                "date": {
                    "styles": ["elegant", "romantic"],
                    "colors": ["any"],
                    "categories": ["dress", "blouse", "heels"]
                },
                "workout": {
                    "styles": ["sporty", "athletic"],
                    "colors": ["any"],
                    "categories": ["leggings", "t-shirt", "sneakers"]
                },
                "party": {
                    "styles": ["trendy", "glamorous"],
                    "colors": ["any"],
                    "categories": ["dress", "heels", "jewelry"]
                }
            }
        }
        
        with open(self.base_dir / "configs/event_mapping.json", "w") as f:
            json.dump(event_types, f, indent=2)
        
        logger.info("✅ Configuration files created")
    
    def download_all_models(self) -> Dict[str, bool]:
        """Download all configured models"""
        results = {}
        
        # Download TensorFlow Hub models
        tf_models = ["mobilenet_v2", "efficientdet_lite0", "movenet_singlepose", 
                    "movenet_multipose", "deeplabv3"]
        
        for model_name in tf_models:
            if model_name in self.models_config:
                results[model_name] = self.download_tensorflow_hub_model(
                    model_name, self.models_config[model_name]
                )
        
        # Download CLIP model
        results["clip"] = self.download_clip_model(self.models_config["clip"])
        
        return results
    
    def verify_downloads(self) -> Dict[str, bool]:
        """Verify all models were downloaded correctly"""
        verification = {}
        
        for model_name, config in self.models_config.items():
            model_path = self.base_dir / config["path"]
            metadata_path = model_path / "metadata.json"
            
            exists = model_path.exists() and metadata_path.exists()
            verification[model_name] = exists
            
            if exists:
                logger.info(f"✅ {model_name} verified")
            else:
                logger.warning(f"❌ {model_name} missing or incomplete")
        
        return verification

def main():
    """Main function to download all models"""
    import pandas as pd  # Import here to avoid issues if not installed
    
    print("🚀 Starting ML Model Download Process...")
    
    downloader = ModelDownloader()
    
    
    # Create config files
    downloader.create_config_files()
    
    # Download all models
    results = downloader.download_all_models()
    
    # Verify downloads
    verification = downloader.verify_downloads()
    
    # Print summary
    print("\n" + "="*50)
    print("📊 DOWNLOAD SUMMARY")
    print("="*50)
    
    successful = sum(results.values())
    total = len(results)
    
    for model_name, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{model_name:<20} {status}")
    
    print(f"\n📈 Overall: {successful}/{total} models downloaded successfully")
    
    if successful == total:
        print("🎉 All models downloaded successfully! Your ML backend is ready for offline inference.")
    else:
        print("⚠️  Some models failed to download. Check the logs above for details.")

if __name__ == "__main__":
    main()