# utils/ml_features.py
import numpy as np
import tensorflow as tf
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
import cv2
from typing import List, Dict, Any, Tuple, Optional
import json
import pickle
import os

class StyleClassifier:
    """Machine learning model for style classification"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_extractor = None
        self.is_trained = False
    
    def create_cnn_feature_extractor(self):
        """Create a CNN for extracting image features"""
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(128, 128, 3)),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(32, activation='relu')
        ])
        
        self.feature_extractor = model
        return model
    
    def extract_advanced_features(self, image_path: str) -> np.ndarray:
        """Extract advanced features from image using CNN"""
        if self.feature_extractor is None:
            self.create_cnn_feature_extractor()
        
        # Load and preprocess image
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (128, 128))
        image = image.astype(np.float32) / 255.0
        image = np.expand_dims(image, axis=0)
        
        # Extract features
        features = self.feature_extractor.predict(image, verbose=0)
        return features.flatten()
    
    def train_style_classifier(self, wardrobe_data: List[Dict], 
                             image_directory: str) -> Dict[str, float]:
        """Train a style classifier on wardrobe data"""
        features = []
        labels = []
        
        for item in wardrobe_data:
            if 'filename' in item and 'style' in item and item['style']:
                image_path = os.path.join(image_directory, item['filename'])
                if os.path.exists(image_path):
                    try:
            # Extract features
            img_features = self.extract_advanced_features(image_path)
            
            # Add color and texture features
            color_features = item_data.get('features', [0, 0, 0])
            texture_features = item_data.get('texture_features', {})
            
            combined_features = np.concatenate([
                img_features,
                color_features,
                [texture_features.get('laplacian_variance', 0),
                 texture_features.get('contrast', 0),
                 texture_features.get('brightness', 0)]
            ])
            
            # Scale features
            features_scaled = self.scaler.transform([combined_features])
            
            # Predict
            prediction = self.model.predict(features_scaled)[0]
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            # Get style name
            predicted_style = self.label_encoder.inverse_transform([prediction])[0]
            
            # Get confidence scores for all styles
            style_scores = {}
            for i, style in enumerate(self.label_encoder.classes_):
                style_name = self.label_encoder.inverse_transform([i])[0]
                style_scores[style_name] = float(probabilities[i])
            
            return {
                "predicted_style": predicted_style,
                "confidence": float(max(probabilities)),
                "style_scores": style_scores
            }
        
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}
    
    def save_model(self, filepath: str):
        """Save the trained model"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_extractor': self.feature_extractor
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, filepath: str):
        """Load a trained model"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoder = model_data['label_encoder']
        self.feature_extractor = model_data['feature_extractor']
        self.is_trained = True

class OutfitCompatibilityModel:
    """Advanced ML model for outfit compatibility prediction"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def create_compatibility_features(self, item1: Dict, item2: Dict) -> np.ndarray:
        """Create features for compatibility prediction between two items"""
        features = []
        
        # Color features
        color1 = item1.get('features', [0, 0, 0])
        color2 = item2.get('features', [0, 0, 0])
        
        # Color differences
        color_diff = [abs(c1 - c2) for c1, c2 in zip(color1, color2)]
        features.extend(color_diff)
        
        # Color harmony features
        temp1 = 1 if item1.get('temperature') == 'warm' else 0
        temp2 = 1 if item2.get('temperature') == 'warm' else 0
        features.append(abs(temp1 - temp2))  # Temperature difference
        
        # Tone features
        tone_map = {'light': 3, 'medium': 2, 'dark': 1}
        tone1 = tone_map.get(item1.get('tone', 'medium').lower(), 2)
        tone2 = tone_map.get(item2.get('tone', 'medium').lower(), 2)
        features.append(abs(tone1 - tone2))
        
        # Category compatibility
        cat1 = item1.get('category', '').lower()
        cat2 = item2.get('category', '').lower()
        
        # Define compatible category pairs
        compatible_pairs = [
            ('top', 'bottom'), ('shirt', 'pants'), ('blouse', 'skirt'),
            ('dress', 'jacket'), ('top', 'jeans'), ('shirt', 'shorts')
        ]
        
        compatibility_score = 0
        for pair in compatible_pairs:
            if (cat1 in pair[0] and cat2 in pair[1]) or (cat1 in pair[1] and cat2 in pair[0]):
                compatibility_score = 1
                break
        features.append(compatibility_score)
        
        # Occasion compatibility
        occ1 = item1.get('occasion', '').lower()
        occ2 = item2.get('occasion', '').lower()
        features.append(1 if occ1 == occ2 else 0)
        
        # Texture features (if available)
        tex1 = item1.get('texture_features', {})
        tex2 = item2.get('texture_features', {})
        
        tex_diff = abs(tex1.get('contrast', 0) - tex2.get('contrast', 0)) / 255.0
        features.append(tex_diff)
        
        return np.array(features)
    
    def train_compatibility_model(self, wardrobe_data: List[Dict]) -> Dict[str, float]:
        """Train the compatibility prediction model"""
        features = []
        labels = []
        
        # Generate positive and negative examples
        for i in range(len(wardrobe_data)):
            for j in range(i + 1, len(wardrobe_data)):
                item1, item2 = wardrobe_data[i], wardrobe_data[j]
                
                # Create features
                feature_vector = self.create_compatibility_features(item1, item2)
                features.append(feature_vector)
                
                # Create labels (simplified heuristic)
                # Items are compatible if they have same occasion and complementary categories
                same_occasion = item1.get('occasion') == item2.get('occasion')
                different_category = item1.get('category') != item2.get('category')
                
                # Color compatibility check
                temp1 = item1.get('temperature', 'neutral')
                temp2 = item2.get('temperature', 'neutral')
                temp_compatible = temp1 == temp2 or 'neutral' in [temp1, temp2]
                
                label = 1 if (same_occasion and different_category and temp_compatible) else 0
                labels.append(label)
        
        if not features:
            return {"error": "No training data generated"}
        
        # Convert to numpy arrays
        X = np.array(features)
        y = np.array(labels)
        
        # Balance the dataset (optional)
        positive_indices = np.where(y == 1)[0]
        negative_indices = np.where(y == 0)[0]
        
        # Take equal number of positive and negative samples
        min_samples = min(len(positive_indices), len(negative_indices))
        selected_pos = np.random.choice(positive_indices, min_samples, replace=False)
        selected_neg = np.random.choice(negative_indices, min_samples, replace=False)
        
        balanced_indices = np.concatenate([selected_pos, selected_neg])
        X_balanced = X[balanced_indices]
        y_balanced = y[balanced_indices]
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X_balanced)
        
        # Train model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y_balanced)
        
        # Calculate accuracy
        train_accuracy = self.model.score(X_scaled, y_balanced)
        
        self.is_trained = True
        
        return {
            "train_accuracy": train_accuracy,
            "num_samples": len(X_balanced),
            "positive_samples": np.sum(y_balanced),
            "negative_samples": len(y_balanced) - np.sum(y_balanced)
        }
    
    def predict_compatibility(self, item1: Dict, item2: Dict) -> Dict[str, Any]:
        """Predict compatibility between two items"""
        if not self.is_trained:
            return {"error": "Model not trained"}
        
        try:
            # Create features
            features = self.create_compatibility_features(item1, item2)
            features_scaled = self.scaler.transform([features])
            
            # Predict
            prediction = self.model.predict(features_scaled)[0]
            probability = self.model.predict_proba(features_scaled)[0]
            
            return {
                "compatible": bool(prediction),
                "compatibility_score": float(probability[1]),  # Probability of being compatible
                "confidence": float(max(probability))
            }
        
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}

class TrendAnalyzer:
    """Analyze fashion trends from wardrobe data"""
    
    def __init__(self):
        self.color_trends = {}
        self.style_trends = {}
        self.seasonal_trends = {}
    
    def analyze_color_trends(self, wardrobe_data: List[Dict], 
                           time_window_days: int = 30) -> Dict[str, Any]:
        """Analyze color trends over time"""
        from datetime import datetime, timedelta
        
        color_timeline = {}
        
        for item in wardrobe_data:
            upload_date = item.get('upload_date')
            if upload_date:
                try:
                    date = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                    color = item.get('color_name', 'unknown')
                    
                    date_key = date.strftime('%Y-%m-%d')
                    if date_key not in color_timeline:
                        color_timeline[date_key] = {}
                    
                    color_timeline[date_key][color] = color_timeline[date_key].get(color, 0) + 1
                
                except ValueError:
                    continue
        
        # Find trending colors
        recent_colors = {}
        older_colors = {}
        cutoff_date = datetime.now() - timedelta(days=time_window_days)
        
        for date_str, colors in color_timeline.items():
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                target_dict = recent_colors if date >= cutoff_date else older_colors
                
                for color, count in colors.items():
                    target_dict[color] = target_dict.get(color, 0) + count
            except ValueError:
                continue
        
        # Calculate trend scores
        trending_colors = {}
        for color in set(list(recent_colors.keys()) + list(older_colors.keys())):
            recent_count = recent_colors.get(color, 0)
            older_count = older_colors.get(color, 0)
            
            if older_count > 0:
                trend_score = (recent_count - older_count) / older_count
            else:
                trend_score = 1.0 if recent_count > 0 else 0.0
            
            trending_colors[color] = {
                'trend_score': trend_score,
                'recent_count': recent_count,
                'older_count': older_count
            }
        
        # Sort by trend score
        sorted_trends = sorted(trending_colors.items(), 
                             key=lambda x: x[1]['trend_score'], reverse=True)
        
        return {
            'trending_colors': dict(sorted_trends[:10]),
            'analysis_period': f"{time_window_days} days",
            'total_recent_items': sum(recent_colors.values()),
            'total_older_items': sum(older_colors.values())
        }
    
    def analyze_outfit_patterns(self, wardrobe_data: List[Dict]) -> Dict[str, Any]:
        """Analyze common outfit patterns and combinations"""
        category_combinations = {}
        color_combinations = {}
        
        # Group items by occasion and date
        occasion_groups = {}
        for item in wardrobe_data:
            occasion = item.get('occasion', 'casual')
            upload_date = item.get('upload_date', '')
            
            key = f"{occasion}_{upload_date[:10]}"  # Group by occasion and day
            
            if key not in occasion_groups:
                occasion_groups[key] = []
            occasion_groups[key].append(item)
        
        # Analyze combinations within each group
        for group_items in occasion_groups.values():
            if len(group_items) >= 2:  # Need at least 2 items for combination
                categories = [item.get('category', '') for item in group_items]
                colors = [item.get('color_name', '') for item in group_items]
                
                # Category combinations
                cat_combo = tuple(sorted(categories))
                category_combinations[cat_combo] = category_combinations.get(cat_combo, 0) + 1
                
                # Color combinations
                color_combo = tuple(sorted(colors))
                color_combinations[color_combo] = color_combinations.get(color_combo, 0) + 1
        
        # Find most common patterns
        top_category_combos = sorted(category_combinations.items(), 
                                   key=lambda x: x[1], reverse=True)[:10]
        top_color_combos = sorted(color_combinations.items(), 
                                key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'popular_category_combinations': [
                {'combination': list(combo), 'frequency': freq} 
                for combo, freq in top_category_combos
            ],
            'popular_color_combinations': [
                {'combination': list(combo), 'frequency': freq} 
                for combo, freq in top_color_combos
            ],
            'total_combinations_analyzed': len(occasion_groups)
        }
    
    def predict_seasonal_needs(self, wardrobe_data: List[Dict], 
                             target_season: str) -> Dict[str, Any]:
        """Predict what items might be needed for upcoming season"""
        from collections import Counter
        
        # Define seasonal categories
        seasonal_categories = {
            'spring': ['light_jacket', 'cardigan', 'light_dress', 'sneakers'],
            'summer': ['shorts', 't-shirt', 'sundress', 'sandals', 'tank_top'],
            'autumn': ['sweater', 'boots', 'jacket', 'jeans', 'scarf'],
            'winter': ['coat', 'boots', 'sweater', 'warm_pants', 'gloves']
        }
        
        if target_season not in seasonal_categories:
            return {"error": "Invalid season"}
        
        # Count current items by category
        current_categories = Counter(item.get('category', '').lower() 
                                   for item in wardrobe_data)
        
        # Recommended items for the season
        recommended_categories = seasonal_categories[target_season]
        
        # Find gaps
        missing_items = []
        low_items = []
        
        for category in recommended_categories:
            count = sum(current_categories[cat] for cat in current_categories 
                       if category.replace('_', ' ') in cat or cat in category)
            
            if count == 0:
                missing_items.append(category.replace('_', ' '))
            elif count < 2:  # Consider having at least 2 of each essential category
                low_items.append({
                    'category': category.replace('_', ' '),
                    'current_count': count,
                    'recommended_count': 2
                })
        
        return {
            'target_season': target_season,
            'missing_items': missing_items,
            'low_stock_items': low_items,
            'current_wardrobe_size': len(wardrobe_data),
            'seasonal_readiness_score': 1.0 - (len(missing_items) + len(low_items)) / len(recommended_categories)
        }:
                        # Extract features
                        img_features = self.extract_advanced_features(image_path)
                        
                        # Add color and texture features
                        color_features = item.get('features', [0, 0, 0])
                        texture_features = item.get('texture_features', {})
                        
                        combined_features = np.concatenate([
                            img_features,
                            color_features,
                            [texture_features.get('laplacian_variance', 0),
                             texture_features.get('contrast', 0),
                             texture_features.get('brightness', 0)]
                        ])
                        
                        features.append(combined_features)
                        labels.append(item['style'])
                    except Exception as e:
                        print(f"Error processing {image_path}: {e}")
                        continue
        
        if not features:
            return {"error": "No valid training data found"}
        
        # Convert to numpy arrays
        X = np.array(features)
        y = np.array(labels)
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train classifier
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y_encoded)
        
        # Calculate accuracy (simple validation)
        train_accuracy = self.model.score(X_scaled, y_encoded)
        
        self.is_trained = True
        
        return {
            "train_accuracy": train_accuracy,
            "num_samples": len(features),
            "num_styles": len(set(labels)),
            "styles": list(set(labels))
        }
    
    def predict_style(self, image_path: str, item_data: Dict) -> Dict[str, Any]:
        """Predict style of a clothing item"""
        if not self.is_trained:
            return {"error": "Model not trained"}
        
        try