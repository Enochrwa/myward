"""
Database service layer for Digital Wardrobe System
Provides CRUD operations and business logic for database interactions
"""
from typing import List, Optional, Dict, Any, Tuple
import mysql.connector
from mysql.connector import Error
import logging
import json
from datetime import datetime, date
import uuid
from pydantic import BaseModel


logger = logging.getLogger(__name__)

# MySQL Configuration
MYSQL_CONFIG = {
    'host': 'localhost',
    'database': 'image_processing',
    'user': 'enoch',
    'password': 'enoch',  # Change this to your MySQL password
    'port': 3306
}

def get_db_connection():
    """Get MySQL database connection"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        return connection
    except Error as e:
        logger.error(f"Error connecting to database: {str(e)}")
        raise

class ClothingItemResponse(BaseModel):
    id: str
    filename: str
    original_name: str
    file_size: int
    image_width: int
    image_height: int
    dominant_color: str
    color_palette: List[str]
    resnet_features: List[float]
    opencv_features: Dict[str, Any]
    upload_date: datetime
    batch_id: Optional[str] = None
    category: Optional[str] = None
    background_removed: bool = False
    foreground_pixel_count: int = 0
    image_url: Optional[str] = None
    clothing_type_name: Optional[str] = None # for compatibility

class DatabaseService:
    """Database service for handling all database operations"""

    def get_clothing_item_by_id(self, item_id: str) -> Optional[ClothingItemResponse]:
        """Get a specific clothing item by ID from the images table"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM images WHERE id = %s"
            
            cursor.execute(query, (item_id,))
            result = cursor.fetchone()
            
            if result:
                result['resnet_features'] = json.loads(result['resnet_features'])
                result['color_palette'] = json.loads(result['color_palette'])
                result['opencv_features'] = json.loads(result['opencv_features'])
                result['image_url'] = f"http://127.0.0.1:8000/uploads/{result['filename']}"
                result['clothing_type_name'] = result['category']
                return ClothingItemResponse(**result)
            
            return None
            
        except Error as e:
            logger.error(f"Error getting clothing item: {e}")
            return None
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
    
    def get_all_items_in_category(self, category: str) -> List[ClothingItemResponse]:
        """Get all items in a specific category"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True) 
            
            query = "SELECT * FROM images WHERE category = %s"
            
            cursor.execute(query, (category,))
            results = cursor.fetchall()
            
            items = []
            for result in results:
                result['resnet_features'] = json.loads(result['resnet_features'])
                result['color_palette'] = json.loads(result['color_palette'])
                result['opencv_features'] = json.loads(result['opencv_features'])
                result['image_url'] = f"http://127.0.0.1:8000/uploads/{result['filename']}"
                result['clothing_type_name'] = result['category']
                items.append(ClothingItemResponse(**result))

            return items
            
        except Error as e:
            logger.error(f"Error getting clothing items by category: {e}")
            return []
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()


# Global database service instance
db_service = DatabaseService()
