#!/usr/bin/env python3
"""
Database test script for the Digital Wardrobe application.
Tests the database connection and creates tables if they don't exist.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.database import engine, test_database_connection, Base
from app import model as models  # Import all models to register them with Base

def main():
    print("Testing database connection...")
    
    # Test basic connection
    if test_database_connection():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed!")
        return False
    
    # Create tables
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Test table creation by checking if we can query one of them
        from app.db.database import SessionLocal
        db = SessionLocal()
        try:
            # Try to query the User table
            from sqlalchemy import text
            result = db.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            print(f"✅ Users table exists with {count} records")
        except Exception as e:
            print(f"⚠️  Warning: Could not query users table: {e}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    print("\n🎉 Database setup completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

