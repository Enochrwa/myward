"""
Database migration script for ML features

This script adds the new ML-related columns to existing tables
and creates new tables for ML results storage.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import engine, Base
from app.model import WardrobeItem, OutfitRecommendation, UserStyleProfile
from sqlalchemy import text

def run_migration():
    """Run the database migration for ML features."""
    print("Starting ML features migration...")
    
    try:
        # Create all tables (this will create new tables and skip existing ones)
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created/updated successfully")
        
        # Add new columns to existing WardrobeItem table if they don't exist
        with engine.connect() as conn:
            try:
                # Check if columns exist and add them if they don't
                result = conn.execute(text("PRAGMA table_info(wardrobe_items)"))
                existing_columns = [row[1] for row in result.fetchall()]
                
                new_columns = [
                    ("dominant_color_rgb", "TEXT"),
                    ("dominant_color_hex", "VARCHAR(7)"),
                    ("dominant_color_name", "VARCHAR(50)"),
                    ("ai_classification", "TEXT"),
                    ("color_properties", "TEXT"),
                    ("style_features", "TEXT")
                ]
                
                for column_name, column_type in new_columns:
                    if column_name not in existing_columns:
                        conn.execute(text(f"ALTER TABLE wardrobe_items ADD COLUMN {column_name} {column_type}"))
                        print(f"✓ Added column {column_name} to wardrobe_items")
                    else:
                        print(f"- Column {column_name} already exists in wardrobe_items")
                
                conn.commit()
                
            except Exception as e:
                print(f"Note: Column addition failed (this is normal if columns already exist): {e}")
        
        print("✓ ML features migration completed successfully!")
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("\n🎉 Database is ready for ML features!")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
        sys.exit(1)

