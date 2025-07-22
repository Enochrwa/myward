import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
if not API_KEY:
    raise RuntimeError("🔑 OPENWEATHERMAP_API_KEY not found in environment")
print("Using OpenWeather key:", API_KEY)
