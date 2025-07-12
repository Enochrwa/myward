import os

class Settings:
    # Weather API
    weather_api_key: str = os.getenv("OPENWEATHERMAP_API_KEY", "")

    # Database
    db_user: str = os.getenv("DB_USER", "user")
    db_password: str = os.getenv("DB_PASSWORD", "password")
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", 3306))
    db_name: str = os.getenv("DB_NAME", "wardrobe")

    # JWT
    secret_key: str = os.getenv("SECRET_KEY", "a_very_secret_key")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # File uploads
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_image_extensions: list = [".jpg", ".jpeg", ".png"]
    max_files_per_request: int = 20

    # ML Models
    custom_models_dir: str = "models"


settings = Settings()
