import mysql.connector
from mysql.connector import Error
from .settings import settings

def get_db_connection():
    """Get database connection"""
    try:
        connection = mysql.connector.connect(
            host=settings.db_host,
            database=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            port=settings.db_port
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None
