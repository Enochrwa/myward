# Local AI Model Manager - Loads models from local files for offline inference
# This module manages locally stored AI models without internet dependencies

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, Tuple, List
import tensorflow as tf
import numpy as np
from datetime import datetime

# Optional imports for PyTorch/HuggingFace support
try:
    import torch
    from transformers import CLIPProcessor, CLIPModel, AutoModel, AutoTokenizer
    TORCH_AVAILABLE = True
    logger.info("✅ PyTorch and transformers available")
except ImportError as e:
    TORCH_AVAILABLE = False
    logger.info(f"⚠️ PyTorch/transformers not available: {e}")

logger = logging.getLogger(__name__)

class LocalModelManager:
    """
    Manages locally stored AI models for offline inference
    """
    
    def __init__(self, models_dir: str = "backend/ml"):
        self.models_dir = Path(models_dir)
        self.models_cache = {}
        self.processors_cache = {}
        self.model_configs = {}
        self.load_configurations()
        
        # Validate directory structure
        self._validate_directory_structure()
    
    def _validate_directory_structure(self):
        """Validate that the ML directory structure exists"""
        required_dirs = [
            "models/extractors",
            "models/classifiers", 
            "models/recommenders",
            "models/pose",
            "models/segmentation",
            "models/clip",
            "configs"
        ]
        
        for dir_path in required_dirs:
            full_path = self.models_dir / dir_path
            if not full_path.exists():
                logger.warning(f"Directory {full_path} does not exist. Run download_models.py first.")
    
    def load_configurations(self):
        """Load model configurations from config files"""
        try:
            # Load model versions
            config_path = self.models_dir / "configs/model_versions.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                    self.model_configs = config_data.get("models", {})
            
            # Load clothing types
            clothing_config_path = self.models_dir / "configs/clothing_types.json"
            if clothing_config_path.exists():
                with open(clothing_config_path, 'r') as f:
                    self.clothing_config = json.load(f)
            
            # Load event mapping
            event_config_path = self.models_dir / "configs/event_mapping.json"
            if event_config_path.exists():
                with open(event_config_path, 'r') as f:
                    self.event_config = json.load(f)
                    
        except Exception as e:
            logger.error(f"Error loading configurations: {e}")
            self.model_configs = {}
            self.clothing_config = {}
            self.event_config = {}
    
    def get_model_path(self, model_name: str) -> Path:
        """Get the local path for a model"""
        if model_name not in self.model_configs:
            raise ValueError(f"Model {model_name} not found in configuration")
        
        return self.models_dir / self.model_configs[model_name]["path"]
    
    def load_tensorflow_model(self, model_name: str):
        """Load a TensorFlow model from local storage"""
        try:
            model_path = self.get_model_path(model_name)
            
            if not model_path.exists():
                raise FileNotFoundError(f"Model directory {model_path} does not exist")
            
            # Load the saved model
            model = tf.saved_model.load(str(model_path))
            
            logger.info(f"✅ Loaded TensorFlow model {model_name} from {model_path}")
            return model
            
        except Exception as e:
            logger.error(f"❌ Failed to load TensorFlow model {model_name}: {e}")
            return None
    
    def load_clip_model_tensorflow(self) -> Tuple[Optional[Any], Optional[Dict]]:
        """Load CLIP model as TensorFlow SavedModel (if available)"""
        try:
            model_path = self.get_model_path("clip")
            
            if not model_path.exists():
                raise FileNotFoundError(f"CLIP model directory {model_path} does not exist")
            
            # Try to load as TensorFlow SavedModel
            tf_model_path = model_path / "tensorflow_model"
            if tf_model_path.exists():
                model = tf.saved_model.load(str(tf_model_path))
                
                # Load tokenizer/processor config if available
                processor_config = {}
                config_path = model_path / "processor_config.json"
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        processor_config = json.load(f)
                
                logger.info(f"✅ Loaded CLIP TensorFlow model from {model_path}")
                return model, processor_config
            else:
                logger.warning(f"TensorFlow version of CLIP model not found at {tf_model_path}")
                return None, None
            
        except Exception as e:
            logger.error(f"❌ Failed to load CLIP TensorFlow model: {e}")
            return None, None
    
    def load_clip_model_pytorch(self) -> Tuple[Optional[Any], Optional[Any]]:
        """Load CLIP model using PyTorch/HuggingFace (if available)"""
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch/transformers not available for CLIP model loading")
            return None, None
            
        try:
            model_path = self.get_model_path("clip")
            
            if not model_path.exists():
                raise FileNotFoundError(f"CLIP model directory {model_path} does not exist")
            
            # Try to load HuggingFace format
            hf_model_path = model_path / "huggingface_model"
            if hf_model_path.exists():
                model = CLIPModel.from_pretrained(str(hf_model_path))
                processor = CLIPProcessor.from_pretrained(str(hf_model_path))
                
                logger.info(f"✅ Loaded CLIP PyTorch model from {model_path}")
                return model, processor
            else:
                # Try loading from the base model path
                try:
                    model = CLIPModel.from_pretrained(str(model_path))
                    processor = CLIPProcessor.from_pretrained(str(model_path))
                    logger.info(f"✅ Loaded CLIP PyTorch model from {model_path}")
                    return model, processor
                except Exception:
                    logger.warning(f"PyTorch version of CLIP model not found at {model_path}")
                    return None, None
            
        except Exception as e:
            logger.error(f"❌ Failed to load CLIP PyTorch model: {e}")
            return None, None
    
    def load_huggingface_model(self, model_name: str) -> Tuple[Optional[Any], Optional[Any]]:
        """Load a HuggingFace model and tokenizer"""
        if not TORCH_AVAILABLE:
            logger.warning(f"PyTorch/transformers not available for model {model_name}")
            return None, None
            
        try:
            model_path = self.get_model_path(model_name)
            
            if not model_path.exists():
                raise FileNotFoundError(f"Model directory {model_path} does not exist")
            
            # Load model and tokenizer
            model = AutoModel.from_pretrained(str(model_path))
            tokenizer = AutoTokenizer.from_pretrained(str(model_path))
            
            logger.info(f"✅ Loaded HuggingFace model {model_name} from {model_path}")
            return model, tokenizer
            
        except Exception as e:
            logger.error(f"❌ Failed to load HuggingFace model {model_name}: {e}")
            return None, None
    
    def load_text_encoder_tensorflow(self) -> Optional[Any]:
        """Load a separate text encoder model if available"""
        try:
            model_path = self.models_dir / "models/text_encoders/sentence_transformer"
            
            if model_path.exists():
                # Load TensorFlow version of text encoder
                model = tf.saved_model.load(str(model_path))
                logger.info(f"✅ Loaded text encoder from {model_path}")
                return model
            else:
                logger.warning(f"Text encoder not found at {model_path}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to load text encoder: {e}")
            return None
    
    def get_model(self, model_name: str):
        """Get a model, loading from local storage if not already cached"""
        
        # Check if model is already in memory cache
        if model_name in self.models_cache:
            return self.models_cache[model_name]
        
        # Get model configuration
        if model_name not in self.model_configs:
            logger.error(f"Model {model_name} not found in configuration")
            return None
            
        config = self.model_configs[model_name]
        framework = config.get("framework", "tensorflow").lower()
        
        # Load model based on framework
        if model_name == "clip":
            # Special handling for CLIP with framework preference
            if framework == "pytorch" or framework == "huggingface":
                model, processor = self.load_clip_model_pytorch()
                if model is not None:
                    self.models_cache[model_name] = model
                    self.processors_cache[model_name] = processor
                    return model
                else:
                    # Fallback to TensorFlow if PyTorch fails
                    logger.info("Falling back to TensorFlow CLIP model")
                    framework = "tensorflow"
            
            if framework == "tensorflow":
                model, processor_config = self.load_clip_model_tensorflow()
                if model is not None:
                    self.models_cache[model_name] = model
                    self.processors_cache[model_name] = processor_config
                    return model
                    
        elif framework == "huggingface" or framework == "pytorch":
            # HuggingFace/PyTorch model
            model, tokenizer = self.load_huggingface_model(model_name)
            if model is not None:
                self.models_cache[model_name] = model
                self.processors_cache[model_name] = tokenizer
                return model
        elif framework == "tensorflow":
            # TensorFlow model
            model = self.load_tensorflow_model(model_name)
            if model is not None:
                self.models_cache[model_name] = model
                return model
        else:
            logger.error(f"Unknown framework '{framework}' for model {model_name}")
            return None
        
        return None
    
    def get_processor(self, model_name: str):
        """Get a model processor (for models like CLIP)"""
        if model_name in self.processors_cache:
            return self.processors_cache[model_name]
        
        # Load the model which will also load the processor
        self.get_model(model_name)
        return self.processors_cache.get(model_name)
    
    def preprocess_image_for_model(self, image: np.ndarray, model_name: str) -> np.ndarray:
        """Preprocess image for specific model requirements"""
        if model_name not in self.model_configs:
            raise ValueError(f"Unknown model: {model_name}")
        
        config = self.model_configs[model_name]
        input_shape = config.get("input_shape")
        
        if input_shape == "variable":
            # For models like EfficientDet that accept variable input sizes
            return image
        
        if isinstance(input_shape, list) and len(input_shape) == 3:
            target_height, target_width = input_shape[0], input_shape[1]
            
            # Resize image
            image_resized = tf.image.resize(image, [target_height, target_width])
            
            # Normalize to [0, 1] if needed
            if image_resized.dtype != tf.float32:
                image_resized = tf.cast(image_resized, tf.float32) / 255.0
            
            # Add batch dimension if needed
            if len(image_resized.shape) == 3:
                image_resized = tf.expand_dims(image_resized, 0)
            
            return image_resized
        
        return image
    
    def preprocess_text_simple(self, text: str, max_length: int = 77) -> np.ndarray:
        """Simple text preprocessing for CLIP-like models"""
        # This is a simplified tokenization - in practice you'd want proper tokenization
        # Convert text to lowercase and split into tokens
        tokens = text.lower().split()
        
        # Create a simple vocabulary mapping (this would normally be loaded from model)
        # For demonstration - in practice this would come from the model's tokenizer
        vocab = {"<pad>": 0, "<start>": 1, "<end>": 2}
        
        # Convert tokens to IDs (simplified)
        token_ids = [vocab.get(token, len(vocab)) for token in tokens]
        
        # Pad or truncate to max_length
        if len(token_ids) > max_length - 2:
            token_ids = token_ids[:max_length - 2]
        
        # Add start and end tokens
        token_ids = [vocab["<start>"]] + token_ids + [vocab["<end>"]]
        
        # Pad to max_length
        while len(token_ids) < max_length:
            token_ids.append(vocab["<pad>"])
        
        return np.array(token_ids, dtype=np.int32)
    
    def extract_features(self, image: np.ndarray, model_name: str = "mobilenet_v2") -> np.ndarray:
        """Extract features from an image using specified model"""
        try:
            model = self.get_model(model_name)
            if model is None:
                raise ValueError(f"Could not load model {model_name}")
            
            # Preprocess image
            processed_image = self.preprocess_image_for_model(image, model_name)
            
            # Extract features
            if model_name == "mobilenet_v2":
                features = model(processed_image)
                return features.numpy()
            else:
                # Generic feature extraction
                features = model(processed_image)
                return features.numpy()
                
        except Exception as e:
            logger.error(f"Error extracting features with {model_name}: {e}")
            return np.array([])
    
    def detect_objects(self, image: np.ndarray, model_name: str = "efficientdet_lite0") -> Dict[str, Any]:
        """Detect objects in image using specified detection model"""
        try:
            model = self.get_model(model_name)
            if model is None:
                raise ValueError(f"Could not load model {model_name}")
            
            # Preprocess image
            processed_image = self.preprocess_image_for_model(image, model_name)
            
            # Run detection
            detections = model(processed_image)
            
            # Process detections into a readable format
            result = {
                "boxes": detections["detection_boxes"].numpy(),
                "classes": detections["detection_classes"].numpy(),
                "scores": detections["detection_scores"].numpy(),
                "num_detections": int(detections["num_detections"].numpy())
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting objects with {model_name}: {e}")
            return {}
    
    def detect_pose(self, image: np.ndarray, model_name: str = "movenet_singlepose") -> Dict[str, Any]:
        """Detect human pose in image"""
        try:
            model = self.get_model(model_name)
            if model is None:
                raise ValueError(f"Could not load model {model_name}")
            
            # Preprocess image
            processed_image = self.preprocess_image_for_model(image, model_name)
            
            # Run pose detection
            keypoints = model(processed_image)
            
            return {
                "keypoints": keypoints.numpy(),
                "model_used": model_name
            }
            
        except Exception as e:
            logger.error(f"Error detecting pose with {model_name}: {e}")
            return {}
    
    def segment_image(self, image: np.ndarray, model_name: str = "deeplabv3") -> np.ndarray:
        """Segment image to isolate clothing items"""
        try:
            model = self.get_model(model_name)
            if model is None:
                raise ValueError(f"Could not load model {model_name}")
            
            # Preprocess image
            processed_image = self.preprocess_image_for_model(image, model_name)
            
            # Run segmentation
            segmentation = model(processed_image)
            
            return segmentation.numpy()
            
        except Exception as e:
            logger.error(f"Error segmenting image with {model_name}: {e}")
            return np.array([])
    
    def match_text_to_image_pytorch(self, image: np.ndarray, text: str) -> float:
        """Match text description to image using PyTorch CLIP model"""
        if not TORCH_AVAILABLE:
            return 0.0
            
        try:
            clip_model = self.get_model("clip")
            processor = self.get_processor("clip")
            
            if clip_model is None or processor is None:
                raise ValueError("Could not load PyTorch CLIP model or processor")
            
            # Convert numpy array to PIL Image if needed
            from PIL import Image
            if isinstance(image, np.ndarray):
                if image.dtype == np.uint8:
                    pil_image = Image.fromarray(image)
                else:
                    # Convert float to uint8
                    image_uint8 = (image * 255).astype(np.uint8)
                    pil_image = Image.fromarray(image_uint8)
            else:
                pil_image = image
            
            # Process inputs
            inputs = processor(text=[text], images=[pil_image], return_tensors="pt", padding=True)
            
            # Get similarity score
            with torch.no_grad():
                outputs = clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                similarity = torch.softmax(logits_per_image, dim=1)
            
            return float(similarity[0][0])
            
        except Exception as e:
            logger.error(f"Error in PyTorch text-to-image matching: {e}")
            return 0.0
        """Match text description to image using TensorFlow CLIP model"""
        try:
            clip_model = self.get_model("clip")
            processor_config = self.get_processor("clip")
            
            if clip_model is None:
                raise ValueError("Could not load CLIP model")
            
            # Preprocess image for CLIP (typically 224x224)
            image_resized = tf.image.resize(image, [224, 224])
            if image_resized.dtype != tf.float32:
                image_resized = tf.cast(image_resized, tf.float32) / 255.0
            image_batch = tf.expand_dims(image_resized, 0)
            
            # Preprocess text (simplified)
            text_tokens = self.preprocess_text_simple(text)
            text_batch = tf.expand_dims(text_tokens, 0)
            
            # Get embeddings
            try:
                # Assuming the TensorFlow CLIP model has separate image and text encoders
                if hasattr(clip_model, 'encode_image') and hasattr(clip_model, 'encode_text'):
                    image_features = clip_model.encode_image(image_batch)
                    text_features = clip_model.encode_text(text_batch)
                else:
                    # Generic approach - try calling the model with both inputs
                    outputs = clip_model({"image": image_batch, "text": text_batch})
                    if isinstance(outputs, dict):
                        image_features = outputs.get("image_features", outputs.get("image_embeds"))
                        text_features = outputs.get("text_features", outputs.get("text_embeds"))
                    else:
                        logger.warning("Unknown CLIP model output format")
                        return 0.0
                
                # Compute cosine similarity
                if image_features is not None and text_features is not None:
                    # Normalize features
                    image_features = tf.nn.l2_normalize(image_features, axis=-1)
                    text_features = tf.nn.l2_normalize(text_features, axis=-1)
                    
                    # Compute similarity
                    similarity = tf.reduce_sum(image_features * text_features, axis=-1)
                    return float(similarity.numpy()[0])
                else:
                    logger.warning("Could not extract features from CLIP model")
                    return 0.0
                    
            except Exception as model_error:
                logger.error(f"Error running CLIP model: {model_error}")
                return 0.0
            
        except Exception as e:
            logger.error(f"Error matching text to image: {e}")
            return 0.0
    
    def match_text_to_image_alternative(self, image: np.ndarray, text: str) -> float:
        """Alternative text-to-image matching using separate models"""
        try:
            # Use separate image feature extractor and text encoder
            image_features = self.extract_features(image, "mobilenet_v2")
            
            # Try to get text encoder
            text_encoder = self.get_model("text_encoder")
            if text_encoder is not None:
                # Process text with the text encoder
                text_processed = self.preprocess_text_simple(text)
                text_batch = tf.expand_dims(text_processed, 0)
                text_features = text_encoder(text_batch).numpy()
                
                # Simple similarity computation (this would be more sophisticated in practice)
                if len(image_features.shape) > 1:
                    image_features = image_features.flatten()
                if len(text_features.shape) > 1:
                    text_features = text_features.flatten()
                
                # Pad or truncate to same length for comparison
                min_len = min(len(image_features), len(text_features))
                if min_len > 0:
                    image_features = image_features[:min_len]
                    text_features = text_features[:min_len]
                    
                    # Compute cosine similarity
                    dot_product = np.dot(image_features, text_features)
                    norm_img = np.linalg.norm(image_features)
                    norm_text = np.linalg.norm(text_features)
                    
                    if norm_img > 0 and norm_text > 0:
                        similarity = dot_product / (norm_img * norm_text)
                        return float(similarity)
            
            # Fallback: simple keyword matching score
            return self._simple_text_image_matching(text, image)
            
        except Exception as e:
            logger.error(f"Error in alternative text-to-image matching: {e}")
            return 0.0
    
    def _simple_text_image_matching(self, text: str, image: np.ndarray) -> float:
        """Very simple fallback text-image matching based on heuristics"""
        # This is a placeholder for when no proper models are available
        # In practice, you might use color analysis, basic object detection, etc.
        
        # Simple color-based matching
        text_lower = text.lower()
        avg_color = np.mean(image, axis=(0, 1))
        
        color_score = 0.0
        if "red" in text_lower and avg_color[0] > avg_color[1] and avg_color[0] > avg_color[2]:
            color_score += 0.3
        elif "blue" in text_lower and avg_color[2] > avg_color[0] and avg_color[2] > avg_color[1]:
            color_score += 0.3
        elif "green" in text_lower and avg_color[1] > avg_color[0] and avg_color[1] > avg_color[2]:
            color_score += 0.3
        
        # Brightness matching
        brightness = np.mean(avg_color)
        if "dark" in text_lower and brightness < 0.3:
            color_score += 0.2
        elif "bright" in text_lower and brightness > 0.7:
            color_score += 0.2
        
        return min(color_score, 1.0)
    
    def match_text_to_image(self, image: np.ndarray, text: str) -> float:
        """Match text description to image using available methods"""
        # Check which framework is configured for CLIP
        if "clip" in self.model_configs:
            framework = self.model_configs["clip"].get("framework", "tensorflow").lower()
            
            if framework == "pytorch" or framework == "huggingface":
                score = self.match_text_to_image_pytorch(image, text)
                if score > 0.0:
                    return score
            
            # Try TensorFlow CLIP
            score = self.match_text_to_image_tensorflow(image, text)
            if score > 0.0:
                return score
        
        # Fall back to alternative approach
        score = self.match_text_to_image_alternative(image, text)
        return score
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available models with their status and metadata"""
        models_list = []
        
        for model_name, config in self.model_configs.items():
            model_path = self.models_dir / config["path"]
            
            # Check for different framework versions
            framework_versions = {}
            
            # Check TensorFlow version
            if (model_path / "saved_model.pb").exists() or (model_path / "variables").exists():
                framework_versions["tensorflow"] = {
                    "available": True,
                    "path": str(model_path)
                }
            elif model_name == "clip" and (model_path / "tensorflow_model").exists():
                framework_versions["tensorflow"] = {
                    "available": True,
                    "path": str(model_path / "tensorflow_model")
                }
            else:
                framework_versions["tensorflow"] = {
                    "available": False,
                    "path": str(model_path)
                }
            
            # Check PyTorch/HuggingFace version
            if TORCH_AVAILABLE:
                hf_indicators = [
                    "config.json",
                    "pytorch_model.bin",
                    "model.safetensors",
                    "tokenizer.json"
                ]
                
                hf_available = any((model_path / indicator).exists() for indicator in hf_indicators)
                if not hf_available and model_name == "clip":
                    hf_available = (model_path / "huggingface_model").exists()
                
                framework_versions["pytorch"] = {
                    "available": hf_available,
                    "path": str(model_path)
                }
            else:
                framework_versions["pytorch"] = {
                    "available": False,
                    "path": str(model_path),
                    "reason": "PyTorch not installed"
                }
            
            model_info = {
                "name": model_name,
                "type": config.get("type", "unknown"),
                "description": config.get("description", ""),
                "framework": config.get("framework", "tensorflow"),
                "input_shape": config.get("input_shape"),
                "base_path": str(model_path),
                "base_path_exists": model_path.exists(),
                "framework_versions": framework_versions,
                "cached": model_name in self.models_cache,
                "processor_cached": model_name in self.processors_cache
            }
            
            models_list.append(model_info)
        
        return models_list
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive information about available models"""
        info = {
            "models_directory": str(self.models_dir),
            "available_models": {},
            "cached_models": list(self.models_cache.keys()),
            "configurations_loaded": {
                "model_configs": len(self.model_configs) > 0,
                "clothing_config": hasattr(self, 'clothing_config'),
                "event_config": hasattr(self, 'event_config')
            },
            "dependencies": {
                "tensorflow": True,
                "torch": TORCH_AVAILABLE,
                "transformers": TORCH_AVAILABLE
            },
            "models_list": self.list_available_models(),
            "framework_support": {
                "tensorflow": True,
                "pytorch": TORCH_AVAILABLE,
                "huggingface": TORCH_AVAILABLE
            }
        }
        
        # Legacy format for backward compatibility
        for model_name, config in self.model_configs.items():
            model_path = self.models_dir / config["path"]
            info["available_models"][model_name] = {
                "type": config.get("type", "unknown"),
                "description": config.get("description", ""),
                "framework": config.get("framework", "tensorflow"),
                "path": str(model_path),
                "exists": model_path.exists(),
                "cached": model_name in self.models_cache,
                "input_shape": config.get("input_shape")
            }
        
        return info
    
    def clear_cache(self, model_name: Optional[str] = None):
        """Clear model cache from memory"""
        if model_name:
            if model_name in self.models_cache:
                del self.models_cache[model_name]
            if model_name in self.processors_cache:
                del self.processors_cache[model_name]
            logger.info(f"Cleared cache for model {model_name}")
        else:
            self.models_cache.clear()
            self.processors_cache.clear()
            logger.info("Cleared all model caches")
    
    def get_clothing_categories(self) -> Dict[str, Any]:
        """Get supported clothing categories"""
        return getattr(self, 'clothing_config', {})
    
    def get_event_mapping(self) -> Dict[str, Any]:
        """Get event-to-clothing mapping"""
        return getattr(self, 'event_config', {})

# Global model manager instance
local_model_manager = LocalModelManager()

def get_local_model_manager() -> LocalModelManager:
    """Get the global local model manager instance"""
    return local_model_manager