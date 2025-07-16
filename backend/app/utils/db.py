import mysql.connector
from typing import Dict, Any
import json
from datetime import datetime

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="your_mysql_user",
        password="your_mysql_password",
        database="your_database_name"
    )

def insert_outfit_item(item: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    
    insert_sql = """
    INSERT INTO wardrobe_items (
        id, filename, category, occasion, style, features,
        color_name, tone, temperature, saturation, hex_color,
        color_palette, texture_features, color_distribution,
        dominant_colors, detected_type, upload_date
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    cursor.execute(insert_sql, (
        item["id"],
        item["filename"],
        item["category"],
        item["occasion"],
        item["style"],
        json.dumps(item["features"]),
        item["color_name"],
        item["tone"],
        item["temperature"],
        item["saturation"],
        item["hex_color"],
        json.dumps(item["color_palette"]),
        json.dumps(item.get("texture_features", {})),
        json.dumps(item.get("color_distribution", {})),
        json.dumps(item.get("dominant_colors", [])),
        item["detected_type"],
        datetime.fromisoformat(item["upload_date"])
    ))
    
    conn.commit()
    cursor.close()
    conn.close()
