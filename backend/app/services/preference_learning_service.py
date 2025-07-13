"""
Machine learning service for user preference learning in Digital Wardrobe System
Learns user preferences and improves recommendations over time
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib
import os
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import json

from config.settings import settings
from services.database_service import db_service

logger = logging.getLogger(__name__)

class UserPreferenceModel:
    """Machine learning model for learning user preferences"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.model_dir = os.path.join(settings.custom_models_dir, f"user_{user_id}")
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Models for different aspects
        self.color_preference_model = None
        self.style_preference_model = None
        self.outfit_rating_model = None
        
        # Scalers and encoders
        self.feature_scaler = StandardScaler()
        self.color_encoder = LabelEncoder()
        self.style_encoder = LabelEncoder()
        
        # Model paths
        self.color_model_path = os.path.join(self.model_dir, "color_preference_model.pkl")
        self.style_model_path = os.path.join(self.model_dir, "style_preference_model.pkl")
        self.rating_model_path = os.path.join(self.model_dir, "outfit_rating_model.pkl")
        self.scaler_path = os.path.join(self.model_dir, "feature_scaler.pkl")
        self.encoders_path = os.path.join(self.model_dir, "encoders.pkl")
        
        # Load existing models if available
        self.load_models()
    
    def extract_user_behavior_features(self) -> Dict[str, Any]:
        """Extract features from user behavior and preferences"""
        try:
            # Get user's clothing items
            clothing_items = db_service.get_clothing_items_by_user(self.user_id, limit=1000)
            
            # Get user's outfit history (when implemented)
            # outfit_history = db_service.get_user_outfit_history(self.user_id)
            
            # Get user interactions (favorites, ratings, etc.)
            favorite_items = [item for item in clothing_items if item.is_favorite]
            
            features = {
                'total_items': len(clothing_items),
                'favorite_items': len(favorite_items),
                'favorite_ratio': len(favorite_items) / len(clothing_items) if clothing_items else 0,
                'color_preferences': self._analyze_color_preferences(clothing_items),
                'style_preferences': self._analyze_style_preferences(clothing_items),
                'brand_preferences': self._analyze_brand_preferences(clothing_items),
                'category_preferences': self._analyze_category_preferences(clothing_items),
                'formality_preferences': self._analyze_formality_preferences(clothing_items)
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting user behavior features: {e}")
            return {}
    
    def _analyze_color_preferences(self, clothing_items: List) -> Dict[str, float]:
        """Analyze user's color preferences"""
        color_counts = {}
        favorite_color_counts = {}
        
        for item in clothing_items:
            if hasattr(item, 'primary_color') and item.primary_color:
                color_name = item.primary_color.name
                color_counts[color_name] = color_counts.get(color_name, 0) + 1
                
                if item.is_favorite:
                    favorite_color_counts[color_name] = favorite_color_counts.get(color_name, 0) + 1
        
        # Calculate preference scores
        color_preferences = {}
        for color, count in color_counts.items():
            favorite_count = favorite_color_counts.get(color, 0)
            preference_score = (favorite_count / count) if count > 0 else 0
            color_preferences[color] = {
                'frequency': count / len(clothing_items) if clothing_items else 0,
                'preference_score': preference_score,
                'total_count': count,
                'favorite_count': favorite_count
            }
        
        return color_preferences
    
    def _analyze_style_preferences(self, clothing_items: List) -> Dict[str, float]:
        """Analyze user's style preferences"""
        style_data = {}
        
        for item in clothing_items:
            # Get style from features if available
            features = db_service.get_clothing_features(item.id)
            if features and features.style_features:
                style_info = features.style_features.get('style', {})
                if isinstance(style_info, dict) and 'style' in style_info:
                    style = style_info['style']
                    if style not in style_data:
                        style_data[style] = {'count': 0, 'favorites': 0}
                    
                    style_data[style]['count'] += 1
                    if item.is_favorite:
                        style_data[style]['favorites'] += 1
        
        # Calculate preference scores
        style_preferences = {}
        for style, data in style_data.items():
            preference_score = (data['favorites'] / data['count']) if data['count'] > 0 else 0
            style_preferences[style] = {
                'frequency': data['count'] / len(clothing_items) if clothing_items else 0,
                'preference_score': preference_score,
                'total_count': data['count'],
                'favorite_count': data['favorites']
            }
        
        return style_preferences
    
    def _analyze_brand_preferences(self, clothing_items: List) -> Dict[str, float]:
        """Analyze user's brand preferences"""
        brand_data = {}
        
        for item in clothing_items:
            if hasattr(item, 'brand') and item.brand:
                brand_name = item.brand.name
                if brand_name not in brand_data:
                    brand_data[brand_name] = {'count': 0, 'favorites': 0}
                
                brand_data[brand_name]['count'] += 1
                if item.is_favorite:
                    brand_data[brand_name]['favorites'] += 1
        
        # Calculate preference scores
        brand_preferences = {}
        for brand, data in brand_data.items():
            preference_score = (data['favorites'] / data['count']) if data['count'] > 0 else 0
            brand_preferences[brand] = {
                'frequency': data['count'] / len(clothing_items) if clothing_items else 0,
                'preference_score': preference_score,
                'total_count': data['count'],
                'favorite_count': data['favorites']
            }
        
        return brand_preferences
    
    def _analyze_category_preferences(self, clothing_items: List) -> Dict[str, float]:
        """Analyze user's clothing category preferences"""
        category_data = {}
        
        for item in clothing_items:
            if hasattr(item, 'clothing_type') and item.clothing_type:
                category_name = item.clothing_type.name
                if category_name not in category_data:
                    category_data[category_name] = {'count': 0, 'favorites': 0}
                
                category_data[category_name]['count'] += 1
                if item.is_favorite:
                    category_data[category_name]['favorites'] += 1
        
        # Calculate preference scores
        category_preferences = {}
        for category, data in category_data.items():
            preference_score = (data['favorites'] / data['count']) if data['count'] > 0 else 0
            category_preferences[category] = {
                'frequency': data['count'] / len(clothing_items) if clothing_items else 0,
                'preference_score': preference_score,
                'total_count': data['count'],
                'favorite_count': data['favorites']
            }
        
        return category_preferences
    
    def _analyze_formality_preferences(self, clothing_items: List) -> Dict[str, float]:
        """Analyze user's formality level preferences"""
        formality_data = {}
        
        for item in clothing_items:
            if hasattr(item, 'clothing_type') and item.clothing_type:
                formality = item.clothing_type.formality_level
                if formality not in formality_data:
                    formality_data[formality] = {'count': 0, 'favorites': 0}
                
                formality_data[formality]['count'] += 1
                if item.is_favorite:
                    formality_data[formality]['favorites'] += 1
        
        # Calculate preference scores
        formality_preferences = {}
        for formality, data in formality_data.items():
            preference_score = (data['favorites'] / data['count']) if data['count'] > 0 else 0
            formality_preferences[formality] = {
                'frequency': data['count'] / len(clothing_items) if clothing_items else 0,
                'preference_score': preference_score,
                'total_count': data['count'],
                'favorite_count': data['favorites']
            }
        
        return formality_preferences
    
    def prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Prepare training data from user behavior"""
        try:
            # Get user's clothing items
            clothing_items = db_service.get_clothing_items_by_user(self.user_id, limit=1000)
            
            if len(clothing_items) < 10:  # Need minimum data for training
                logger.warning(f"Insufficient data for user {self.user_id}: {len(clothing_items)} items")
                return np.array([]), np.array([]), np.array([])
            
            features = []
            color_labels = []
            style_labels = []
            preference_scores = []
            
            for item in clothing_items:
                # Extract features for this item
                item_features = self._extract_item_features(item)
                if item_features is not None:
                    features.append(item_features)
                    
                    # Color label
                    color = item.primary_color.name if hasattr(item, 'primary_color') and item.primary_color else 'unknown'
                    color_labels.append(color)
                    
                    # Style label
                    item_features_data = db_service.get_clothing_features(item.id)
                    if item_features_data and item_features_data.style_features:
                        style_info = item_features_data.style_features.get('style', {})
                        style = style_info.get('style', 'unknown') if isinstance(style_info, dict) else 'unknown'
                    else:
                        style = 'unknown'
                    style_labels.append(style)
                    
                    # Preference score (based on favorites and usage)
                    preference_score = 1.0 if item.is_favorite else 0.5
                    preference_scores.append(preference_score)
            
            if not features:
                return np.array([]), np.array([]), np.array([])
            
            return np.array(features), np.array(color_labels), np.array(style_labels), np.array(preference_scores)
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            return np.array([]), np.array([]), np.array([])
    
    def _extract_item_features(self, item) -> Optional[List[float]]:
        """Extract numerical features from a clothing item"""
        try:
            features = []
            
            # Basic item features
            features.append(1.0 if item.is_favorite else 0.0)
            features.append(1.0 if item.is_available else 0.0)
            
            # Color features
            if hasattr(item, 'primary_color') and item.primary_color:
                # Convert color to HSV for better representation
                color_hex = item.primary_color.hex_code
                if color_hex and len(color_hex) == 7:
                    r = int(color_hex[1:3], 16) / 255.0
                    g = int(color_hex[3:5], 16) / 255.0
                    b = int(color_hex[5:7], 16) / 255.0
                    
                    # Convert to HSV
                    import colorsys
                    h, s, v = colorsys.rgb_to_hsv(r, g, b)
                    features.extend([h, s, v])
                else:
                    features.extend([0.0, 0.0, 0.0])
            else:
                features.extend([0.0, 0.0, 0.0])
            
            # Clothing type features
            if hasattr(item, 'clothing_type') and item.clothing_type:
                # Encode formality level
                formality_map = {'very_casual': 0.0, 'casual': 0.2, 'smart_casual': 0.4, 
                               'business': 0.6, 'formal': 0.8, 'black_tie': 1.0}
                formality_score = formality_map.get(item.clothing_type.formality_level, 0.5)
                features.append(formality_score)
            else:
                features.append(0.5)
            
            # Get ResNet features if available
            item_features = db_service.get_clothing_features(item.id)
            if item_features and item_features.resnet_features:
                # Use first 10 ResNet features to keep dimensionality manageable
                resnet_features = item_features.resnet_features[:10]
                features.extend(resnet_features)
            else:
                features.extend([0.0] * 10)
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting item features: {e}")
            return None
    
    def train_models(self) -> Dict[str, float]:
        """Train preference learning models"""
        try:
            # Prepare training data
            features, color_labels, style_labels, preference_scores = self.prepare_training_data()
            
            if len(features) == 0:
                logger.warning(f"No training data available for user {self.user_id}")
                return {"error": "insufficient_data"}
            
            # Scale features
            features_scaled = self.feature_scaler.fit_transform(features)
            
            # Train color preference model
            color_accuracy = 0.0
            if len(np.unique(color_labels)) > 1:
                try:
                    self.color_encoder.fit(color_labels)
                    color_labels_encoded = self.color_encoder.transform(color_labels)
                    
                    X_train, X_test, y_train, y_test = train_test_split(
                        features_scaled, color_labels_encoded, test_size=0.2, random_state=42
                    )
                    
                    self.color_preference_model = RandomForestClassifier(n_estimators=50, random_state=42)
                    self.color_preference_model.fit(X_train, y_train)
                    
                    y_pred = self.color_preference_model.predict(X_test)
                    color_accuracy = accuracy_score(y_test, y_pred)
                    
                except Exception as e:
                    logger.error(f"Error training color model: {e}")
            
            # Train style preference model
            style_accuracy = 0.0
            if len(np.unique(style_labels)) > 1:
                try:
                    self.style_encoder.fit(style_labels)
                    style_labels_encoded = self.style_encoder.transform(style_labels)
                    
                    X_train, X_test, y_train, y_test = train_test_split(
                        features_scaled, style_labels_encoded, test_size=0.2, random_state=42
                    )
                    
                    self.style_preference_model = RandomForestClassifier(n_estimators=50, random_state=42)
                    self.style_preference_model.fit(X_train, y_train)
                    
                    y_pred = self.style_preference_model.predict(X_test)
                    style_accuracy = accuracy_score(y_test, y_pred)
                    
                except Exception as e:
                    logger.error(f"Error training style model: {e}")
            
            # Train outfit rating model
            rating_mse = 0.0
            try:
                X_train, X_test, y_train, y_test = train_test_split(
                    features_scaled, preference_scores, test_size=0.2, random_state=42
                )
                
                self.outfit_rating_model = GradientBoostingRegressor(n_estimators=50, random_state=42)
                self.outfit_rating_model.fit(X_train, y_train)
                
                y_pred = self.outfit_rating_model.predict(X_test)
                rating_mse = mean_squared_error(y_test, y_pred)
                
            except Exception as e:
                logger.error(f"Error training rating model: {e}")
            
            # Save models
            self.save_models()
            
            training_results = {
                "color_accuracy": color_accuracy,
                "style_accuracy": style_accuracy,
                "rating_mse": rating_mse,
                "training_samples": len(features),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Models trained for user {self.user_id}: {training_results}")
            return training_results
            
        except Exception as e:
            logger.error(f"Error training models for user {self.user_id}: {e}")
            return {"error": str(e)}
    
    def predict_item_preference(self, item) -> Dict[str, float]:
        """Predict user preference for a clothing item"""
        try:
            if not self.models_loaded():
                return {"preference_score": 0.5, "confidence": 0.0}
            
            # Extract features
            item_features = self._extract_item_features(item)
            if item_features is None:
                return {"preference_score": 0.5, "confidence": 0.0}
            
            # Scale features
            features_scaled = self.feature_scaler.transform([item_features])
            
            # Predict preference score
            preference_score = 0.5
            confidence = 0.0
            
            if self.outfit_rating_model:
                try:
                    preference_score = float(self.outfit_rating_model.predict(features_scaled)[0])
                    confidence = 0.8
                except Exception as e:
                    logger.error(f"Error predicting preference: {e}")
            
            # Predict color preference
            color_preference = 0.5
            if self.color_preference_model and hasattr(item, 'primary_color') and item.primary_color:
                try:
                    color_proba = self.color_preference_model.predict_proba(features_scaled)[0]
                    color_preference = np.max(color_proba)
                except Exception as e:
                    logger.error(f"Error predicting color preference: {e}")
            
            # Predict style preference
            style_preference = 0.5
            if self.style_preference_model:
                try:
                    style_proba = self.style_preference_model.predict_proba(features_scaled)[0]
                    style_preference = np.max(style_proba)
                except Exception as e:
                    logger.error(f"Error predicting style preference: {e}")
            
            # Combine predictions
            combined_score = (preference_score * 0.5 + color_preference * 0.25 + style_preference * 0.25)
            
            return {
                "preference_score": float(combined_score),
                "color_preference": float(color_preference),
                "style_preference": float(style_preference),
                "confidence": float(confidence)
            }
            
        except Exception as e:
            logger.error(f"Error predicting item preference: {e}")
            return {"preference_score": 0.5, "confidence": 0.0}
    
    def models_loaded(self) -> bool:
        """Check if models are loaded"""
        return (self.color_preference_model is not None or 
                self.style_preference_model is not None or 
                self.outfit_rating_model is not None)
    
    def save_models(self):
        """Save trained models to disk"""
        try:
            if self.color_preference_model:
                joblib.dump(self.color_preference_model, self.color_model_path)
            
            if self.style_preference_model:
                joblib.dump(self.style_preference_model, self.style_model_path)
            
            if self.outfit_rating_model:
                joblib.dump(self.outfit_rating_model, self.rating_model_path)
            
            # Save scaler and encoders
            joblib.dump(self.feature_scaler, self.scaler_path)
            
            encoders = {
                'color_encoder': self.color_encoder,
                'style_encoder': self.style_encoder
            }
            joblib.dump(encoders, self.encoders_path)
            
            logger.info(f"Models saved for user {self.user_id}")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            # Load models
            if os.path.exists(self.color_model_path):
                self.color_preference_model = joblib.load(self.color_model_path)
            
            if os.path.exists(self.style_model_path):
                self.style_preference_model = joblib.load(self.style_model_path)
            
            if os.path.exists(self.rating_model_path):
                self.outfit_rating_model = joblib.load(self.rating_model_path)
            
            # Load scaler and encoders
            if os.path.exists(self.scaler_path):
                self.feature_scaler = joblib.load(self.scaler_path)
            
            if os.path.exists(self.encoders_path):
                encoders = joblib.load(self.encoders_path)
                self.color_encoder = encoders.get('color_encoder', LabelEncoder())
                self.style_encoder = encoders.get('style_encoder', LabelEncoder())
            
            if self.models_loaded():
                logger.info(f"Models loaded for user {self.user_id}")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")

class PreferenceLearningService:
    """Service for managing user preference learning"""
    
    def __init__(self):
        self.user_models = {}
    
    def get_user_model(self, user_id: str) -> UserPreferenceModel:
        """Get or create user preference model"""
        if user_id not in self.user_models:
            self.user_models[user_id] = UserPreferenceModel(user_id)
        return self.user_models[user_id]
    
    def train_user_model(self, user_id: str) -> Dict[str, Any]:
        """Train preference model for a user"""
        try:
            user_model = self.get_user_model(user_id)
            results = user_model.train_models()
            return results
        except Exception as e:
            logger.error(f"Error training user model: {e}")
            return {"error": str(e)}
    
    def predict_item_preference(self, user_id: str, item) -> Dict[str, float]:
        """Predict user preference for an item"""
        try:
            user_model = self.get_user_model(user_id)
            return user_model.predict_item_preference(item)
        except Exception as e:
            logger.error(f"Error predicting item preference: {e}")
            return {"preference_score": 0.5, "confidence": 0.0}
    
    def get_user_preferences_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user preferences"""
        try:
            user_model = self.get_user_model(user_id)
            return user_model.extract_user_behavior_features()
        except Exception as e:
            logger.error(f"Error getting user preferences summary: {e}")
            return {}

# Global preference learning service instance
preference_learning_service = PreferenceLearningService()

