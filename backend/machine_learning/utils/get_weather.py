import requests
import json
from dotenv import load_dotenv
import os
load_dotenv()



def get_weather(api_key, city_name="kigali", units="metric"):
    """
    Fetches real-time weather data for a given city using OpenWeatherMap API.

    Args:
        api_key (str): Your OpenWeatherMap API key.
        city_name (str): The name of the city.
        units (str, optional): Units of measurement. Can be "metric" (Celsius),
                               "imperial" (Fahrenheit), or "standard" (Kelvin).
                               Defaults to "metric".

    Returns:
        dict or None: A dictionary containing weather data if successful,
                      otherwise None.
    """
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city_name}&appid={api_key}&units={units}"

    try:
        response = requests.get(complete_url)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        data = response.json()
        return data

        # if data["cod"] == 200:  # Check if the city was found
        #     main_data = data["main"]
        #     weather_description = data["weather"][0]["description"]
        #     wind_speed = data["wind"]["speed"]

        #     temperature = main_data["temp"]
        #     feels_like = main_data["feels_like"]
        #     humidity = main_data["humidity"]
        #     pressure = main_data["pressure"]

        #     print(f"Weather in {city_name}:")
        #     print(f"  Temperature: {temperature}°{'C' if units == 'metric' else ('F' if units == 'imperial' else 'K')}")
        #     print(f"  Feels like: {feels_like}°{'C' if units == 'metric' else ('F' if units == 'imperial' else 'K')}")
        #     print(f"  Humidity: {humidity}%")
        #     print(f"  Pressure: {pressure} hPa")
        #     print(f"  Wind Speed: {wind_speed} m/s")
        #     print(f"  Description: {weather_description.capitalize()}")
        #     return data
        # else:
        #     print(f"Error: City '{city_name}' not found.")
        #     return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response from API.")
        return None

if __name__ == "__main__":
    # Replace 'YOUR_API_KEY' with your actual OpenWeatherMap API key
    api_key = os.getenv("OPENWEATHERMAP_API_KEY") 

    if api_key == "YOUR_API_KEY":
        print("Please replace 'YOUR_API_KEY' with your actual OpenWeatherMap API key.")
        print("You can get one from: https://openweathermap.org/api")
    else:
        data = get_weather(api_key)
        print(data)