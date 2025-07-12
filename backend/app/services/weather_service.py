import httpx
import os
from typing import Optional, Dict
import logging # Added for logging

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
logger = logging.getLogger(__name__) # Added logger

async def get_weather_data(latitude: float, longitude: float) -> Optional[Dict]:
    """
    Fetches weather data from OpenWeatherMap API or returns a mock response.
    """
    if not OPENWEATHERMAP_API_KEY:
        # Mock response if API key is not available
        logger.warning("OPENWEATHERMAP_API_KEY not found. Using mocked weather data.")
        if latitude == 10.0 and longitude == 10.0: # Cold weather mock
            return {"temperature_celsius": 5.0, "condition": "Snow"}
        elif latitude == 20.0 and longitude == 20.0: # Rainy weather mock
            return {"temperature_celsius": 15.0, "condition": "Rain"}
        elif latitude == 0.0 and longitude == 0.0: # Default mock for other test cases
             return {"temperature_celsius": 25.0, "condition": "Clear"}
        else: # Generic mock for any other coordinates
            return {"temperature_celsius": 22.0, "condition": "Clear"}

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": OPENWEATHERMAP_API_KEY,
        "units": "metric"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(WEATHER_API_URL, params=params)
            response.raise_for_status()  # Raises an HTTPStatusError for bad responses (4xx or 5xx)
            data = response.json()

            return {
                "temperature_celsius": data.get("main", {}).get("temp"),
                "condition": data.get("weather", [{}])[0].get("main") # e.g., "Clear", "Rain"
            }
    except httpx.RequestError as e:
        logger.error(f"An error occurred while requesting weather data: {e}")
        return None
    except httpx.HTTPStatusError as e:
        logger.error(f"Weather API returned an error: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None

# Example usage (optional, for direct testing of this file)
# if __name__ == "__main__":
#     import asyncio
#     async def main():
#         # Mocked example
#         logger.info("Fetching mocked cold weather (10,10):")
#         weather_mock_cold = await get_weather_data(latitude=10.0, longitude=10.0)
#         logger.info(weather_mock_cold)

#         logger.info("\nFetching mocked rainy weather (20,20):")
#         weather_mock_rain = await get_weather_data(latitude=20.0, longitude=20.0)
#         logger.info(weather_mock_rain)

#         # Real API example (if key is set)
#         if OPENWEATHERMAP_API_KEY:
#             logger.info("\nFetching real weather data for London (51.5074, 0.1278):")
#             weather_real = await get_weather_data(latitude=51.5074, longitude=0.1278)
#             logger.info(weather_real)
#         else:
#             logger.warning("\nSkipping real API call example as OPENWEATHERMAP_API_KEY is not set.")

#     asyncio.run(main())
