"""
Database service layer for Digital Wardrobe System
Provides CRUD operations and business logic for database interactions
"""
from typing import List, Optional, Dict, Any, Tuple
from mysql.connector import Error
import logging
import json
from datetime import datetime, date

from app.config.database import get_db_connection
from app.models.database_models import *

logger = logging.getLogger(__name__)

class DatabaseService:
    """Database service for handling all database operations"""
    
    def __init__(self):
        self.connection = None
    
    def get_connection(self):
        """Get database connection"""
        if self.connection is None or not self.connection.is_connected():
            self.connection = get_db_connection()
        return self.connection
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    # User operations
    def create_user(self, user_data: UserCreate) -> Optional[str]:
        """Create a new user"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            user_id = str(uuid.uuid4())
            
            query = """
            INSERT INTO users (id, username, email, password_hash, first_name, last_name, 
                             date_of_birth, gender, location, style_preference)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                user_id, user_data.username, user_data.email, user_data.password,
                user_data.first_name, user_data.last_name, user_data.date_of_birth,
                user_data.gender, user_data.location, user_data.style_preference
            )
            
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            
            logger.info(f"User created successfully: {user_id}")
            return user_id
            
        except Error as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return User(**result)
            return None
            
        except Error as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return User(**result)
            return None
            
        except Error as e:
            logger.error(f"Error getting user by username: {e}")
            return None
    
    def update_user(self, user_id: str, user_data: UserUpdate) -> bool:
        """Update user information"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Build dynamic update query
            update_fields = []
            values = []
            
            for field, value in user_data.dict(exclude_unset=True).items():
                update_fields.append(f"{field} = %s")
                values.append(value)
            
            if not update_fields:
                return True  # Nothing to update
            
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
            values.append(user_id)
            
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            
            logger.info(f"User updated successfully: {user_id}")
            return True
            
        except Error as e:
            logger.error(f"Error updating user: {e}")
            return False
    
    # Clothing item operations
    def create_clothing_item(self, user_id: str, item_data: ClothingItemCreate) -> Optional[str]:
        """Create a new clothing item"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            item_id = str(uuid.uuid4())
            
            query = """
            INSERT INTO clothing_items (id, user_id, original_filename, stored_filename,
                                      clothing_type_id, brand_id, primary_color_id, 
                                      secondary_color_id, pattern_id, size, purchase_date,
                                      purchase_price, care_instructions, notes, is_favorite,
                                      is_available, condition_rating)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                item_id, user_id, item_data.original_filename, item_data.stored_filename,
                item_data.clothing_type_id, item_data.brand_id, item_data.primary_color_id,
                item_data.secondary_color_id, item_data.pattern_id, item_data.size,
                item_data.purchase_date, item_data.purchase_price, item_data.care_instructions,
                item_data.notes, item_data.is_favorite, item_data.is_available,
                item_data.condition_rating
            )
            
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            
            logger.info(f"Clothing item created successfully: {item_id}")
            return item_id
            
        except Error as e:
            logger.error(f"Error creating clothing item: {e}")
            return None
    
    def get_clothing_items_by_user(self, user_id: str, limit: int = 100, offset: int = 0) -> List[ClothingItemResponse]:
        """Get clothing items for a user with related data"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT ci.*, ct.name as clothing_type_name, ct.description as clothing_type_description,
                   ct.formality_level as clothing_type_formality, ct.season_suitability,
                   b.name as brand_name, b.price_range as brand_price_range,
                   pc.name as primary_color_name, pc.hex_code as primary_color_hex,
                   sc.name as secondary_color_name, sc.hex_code as secondary_color_hex,
                   p.name as pattern_name, p.description as pattern_description
            FROM clothing_items ci
            LEFT JOIN clothing_types ct ON ci.clothing_type_id = ct.id
            LEFT JOIN brands b ON ci.brand_id = b.id
            LEFT JOIN colors pc ON ci.primary_color_id = pc.id
            LEFT JOIN colors sc ON ci.secondary_color_id = sc.id
            LEFT JOIN patterns p ON ci.pattern_id = p.id
            WHERE ci.user_id = %s
            ORDER BY ci.created_at DESC
            LIMIT %s OFFSET %s
            """
            
            cursor.execute(query, (user_id, limit, offset))
            results = cursor.fetchall()
            cursor.close()
            
            items = []
            for result in results:
                # Get images for each item
                images = self.get_clothing_images(result['id'])
                
                # Build response object
                item_response = ClothingItemResponse(
                    id=result['id'],
                    user_id=result['user_id'],
                    original_filename=result['original_filename'],
                    stored_filename=result['stored_filename'],
                    clothing_type_id=result['clothing_type_id'],
                    brand_id=result['brand_id'],
                    primary_color_id=result['primary_color_id'],
                    secondary_color_id=result['secondary_color_id'],
                    pattern_id=result['pattern_id'],
                    size=result['size'],
                    purchase_date=result['purchase_date'],
                    purchase_price=result['purchase_price'],
                    care_instructions=result['care_instructions'],
                    notes=result['notes'],
                    is_favorite=result['is_favorite'],
                    is_available=result['is_available'],
                    wear_count=result['wear_count'],
                    last_worn_date=result['last_worn_date'],
                    condition_rating=result['condition_rating'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at'],
                    images=images
                )
                
                items.append(item_response)
            
            return items
            
        except Error as e:
            logger.error(f"Error getting clothing items: {e}")
            return []
    
    def get_clothing_item_by_id(self, item_id: str) -> Optional[ClothingItemResponse]:
        """Get a specific clothing item by ID"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT ci.*, ct.name as clothing_type_name, ct.description as clothing_type_description,
                   ct.formality_level as clothing_type_formality, ct.season_suitability,
                   b.name as brand_name, b.price_range as brand_price_range,
                   pc.name as primary_color_name, pc.hex_code as primary_color_hex,
                   sc.name as secondary_color_name, sc.hex_code as secondary_color_hex,
                   p.name as pattern_name, p.description as pattern_description
            FROM clothing_items ci
            LEFT JOIN clothing_types ct ON ci.clothing_type_id = ct.id
            LEFT JOIN brands b ON ci.brand_id = b.id
            LEFT JOIN colors pc ON ci.primary_color_id = pc.id
            LEFT JOIN colors sc ON ci.secondary_color_id = sc.id
            LEFT JOIN patterns p ON ci.pattern_id = p.id
            WHERE ci.id = %s
            """
            
            cursor.execute(query, (item_id,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                images = self.get_clothing_images(item_id)
                
                return ClothingItemResponse(
                    id=result['id'],
                    user_id=result['user_id'],
                    original_filename=result['original_filename'],
                    stored_filename=result['stored_filename'],
                    clothing_type_id=result['clothing_type_id'],
                    brand_id=result['brand_id'],
                    primary_color_id=result['primary_color_id'],
                    secondary_color_id=result['secondary_color_id'],
                    pattern_id=result['pattern_id'],
                    size=result['size'],
                    purchase_date=result['purchase_date'],
                    purchase_price=result['purchase_price'],
                    care_instructions=result['care_instructions'],
                    notes=result['notes'],
                    is_favorite=result['is_favorite'],
                    is_available=result['is_available'],
                    wear_count=result['wear_count'],
                    last_worn_date=result['last_worn_date'],
                    condition_rating=result['condition_rating'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at'],
                    images=images
                )
            
            return None
            
        except Error as e:
            logger.error(f"Error getting clothing item: {e}")
            return None
    
    def update_clothing_item(self, item_id: str, item_data: ClothingItemUpdate) -> bool:
        """Update clothing item"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Build dynamic update query
            update_fields = []
            values = []
            
            for field, value in item_data.dict(exclude_unset=True).items():
                update_fields.append(f"{field} = %s")
                values.append(value)
            
            if not update_fields:
                return True  # Nothing to update
            
            query = f"UPDATE clothing_items SET {', '.join(update_fields)} WHERE id = %s"
            values.append(item_id)
            
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            
            logger.info(f"Clothing item updated successfully: {item_id}")
            return True
            
        except Error as e:
            logger.error(f"Error updating clothing item: {e}")
            return False
    
    def delete_clothing_item(self, item_id: str) -> bool:
        """Delete clothing item"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Delete related records first (images, features, etc.)
            cursor.execute("DELETE FROM clothing_images WHERE clothing_item_id = %s", (item_id,))
            cursor.execute("DELETE FROM clothing_features WHERE clothing_item_id = %s", (item_id,))
            cursor.execute("DELETE FROM outfit_items WHERE clothing_item_id = %s", (item_id,))
            
            # Delete the clothing item
            cursor.execute("DELETE FROM clothing_items WHERE id = %s", (item_id,))
            
            connection.commit()
            cursor.close()
            
            logger.info(f"Clothing item deleted successfully: {item_id}")
            return True
            
        except Error as e:
            logger.error(f"Error deleting clothing item: {e}")
            return False
    
    # Clothing image operations
    def create_clothing_image(self, image_data: ClothingImageCreate) -> Optional[str]:
        """Create clothing image record"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            image_id = str(uuid.uuid4())
            
            query = """
            INSERT INTO clothing_images (id, clothing_item_id, image_path, image_url,
                                       file_size, image_width, image_height, is_primary)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                image_id, image_data.clothing_item_id, image_data.image_path,
                image_data.image_url, image_data.file_size, image_data.image_width,
                image_data.image_height, image_data.is_primary
            )
            
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            
            logger.info(f"Clothing image created successfully: {image_id}")
            return image_id
            
        except Error as e:
            logger.error(f"Error creating clothing image: {e}")
            return None
    
    def get_clothing_images(self, clothing_item_id: str) -> List[ClothingImage]:
        """Get images for a clothing item"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT * FROM clothing_images 
            WHERE clothing_item_id = %s 
            ORDER BY is_primary DESC, upload_date ASC
            """
            
            cursor.execute(query, (clothing_item_id,))
            results = cursor.fetchall()
            cursor.close()
            
            return [ClothingImage(**result) for result in results]
            
        except Error as e:
            logger.error(f"Error getting clothing images: {e}")
            return []
    
    # Clothing features operations
    def create_clothing_features(self, features_data: ClothingFeaturesCreate) -> Optional[str]:
        """Create clothing features record"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            features_id = str(uuid.uuid4())
            
            query = """
            INSERT INTO clothing_features (id, clothing_item_id, resnet_features, opencv_features,
                                         color_palette, texture_features, style_features)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                features_id, features_data.clothing_item_id,
                json.dumps(features_data.resnet_features),
                json.dumps(features_data.opencv_features),
                json.dumps(features_data.color_palette),
                json.dumps(features_data.texture_features),
                json.dumps(features_data.style_features)
            )
            
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            
            logger.info(f"Clothing features created successfully: {features_id}")
            return features_id
            
        except Error as e:
            logger.error(f"Error creating clothing features: {e}")
            return None
    
    def get_clothing_features(self, clothing_item_id: str) -> Optional[ClothingFeatures]:
        """Get features for a clothing item"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM clothing_features WHERE clothing_item_id = %s"
            cursor.execute(query, (clothing_item_id,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                # Parse JSON fields
                result['resnet_features'] = json.loads(result['resnet_features'])
                result['opencv_features'] = json.loads(result['opencv_features'])
                result['color_palette'] = json.loads(result['color_palette'])
                result['texture_features'] = json.loads(result['texture_features'])
                result['style_features'] = json.loads(result['style_features'])
                
                return ClothingFeatures(**result)
            
            return None
            
        except Error as e:
            logger.error(f"Error getting clothing features: {e}")
            return None
    
    # Lookup table operations
    def get_clothing_types(self) -> List[ClothingType]:
        """Get all clothing types"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM clothing_types ORDER BY name"
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            return [ClothingType(**result) for result in results]
            
        except Error as e:
            logger.error(f"Error getting clothing types: {e}")
            return []
    
    def get_colors(self) -> List[Color]:
        """Get all colors"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM colors ORDER BY name"
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            return [Color(**result) for result in results]
            
        except Error as e:
            logger.error(f"Error getting colors: {e}")
            return []
    
    def get_brands(self) -> List[Brand]:
        """Get all brands"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM brands ORDER BY name"
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            return [Brand(**result) for result in results]
            
        except Error as e:
            logger.error(f"Error getting brands: {e}")
            return []
    
    def get_occasions(self) -> List[Occasion]:
        """Get all occasions"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM occasions ORDER BY name"
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            return [Occasion(**result) for result in results]
            
        except Error as e:
            logger.error(f"Error getting occasions: {e}")
            return []
    
    def get_patterns(self) -> List[Pattern]:
        """Get all patterns"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM patterns ORDER BY name"
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            return [Pattern(**result) for result in results]
            
        except Error as e:
            logger.error(f"Error getting patterns: {e}")
            return []

# Global database service instance
db_service = DatabaseService()

