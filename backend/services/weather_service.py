"""
Weather service for Digital Wardrobe System
Integrates with OpenWeatherMap API to provide weather-based clothing recommendations
"""
import requests
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
from dataclasses import dataclass

from config.settings import settings

logger = logging.getLogger(__name__)

@dataclass
class WeatherData:
    """Weather data structure"""
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    wind_speed: float
    wind_direction: int
    visibility: int
    weather_main: str
    weather_description: str
    weather_icon: str
    clouds: int
    location: str
    country: str
    timestamp: datetime
    sunrise: datetime
    sunset: datetime
    
    def get_temperature_category(self) -> str:
        """Categorize temperature for clothing recommendations"""
        temp = self.feels_like
        if temp < -10:
            return "extremely_cold"
        elif temp < 0:
            return "very_cold"
        elif temp < 10:
            return "cold"
        elif temp < 20:
            return "cool"
        elif temp < 25:
            return "mild"
        elif temp < 30:
            return "warm"
        elif temp < 35:
            return "hot"
        else:
            return "extremely_hot"
    
    def get_weather_category(self) -> str:
        """Categorize weather condition for clothing recommendations"""
        main = self.weather_main.lower()
        if main in ["rain", "drizzle"]:
            return "rainy"
        elif main == "snow":
            return "snowy"
        elif main == "thunderstorm":
            return "stormy"
        elif main == "mist" or main == "fog":
            return "foggy"
        elif main == "clear":
            return "clear"
        elif main == "clouds":
            if self.clouds > 75:
                return "overcast"
            else:
                return "partly_cloudy"
        else:
            return "other"
    
    def get_wind_category(self) -> str:
        """Categorize wind speed for clothing recommendations"""
        # Convert m/s to km/h for easier understanding
        wind_kmh = self.wind_speed * 3.6
        if wind_kmh < 10:
            return "calm"
        elif wind_kmh < 20:
            return "light"
        elif wind_kmh < 30:
            return "moderate"
        elif wind_kmh < 50:
            return "strong"
        else:
            return "very_strong"
    
    def is_daytime(self) -> bool:
        """Check if it's currently daytime"""
        current_time = self.timestamp.time()
        sunrise_time = self.sunrise.time()
        sunset_time = self.sunset.time()
        return sunrise_time <= current_time <= sunset_time

class WeatherService:
    """Service for fetching and processing weather data using OpenWeatherMap API"""
    
    def __init__(self):
        self.api_key = settings.weather_api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
        self.geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
        
        # Weather-based clothing recommendations
        self.temperature_clothing_map = {
            "extremely_cold": {
                "required": ["heavy_winter_coat", "thermal_underwear", "winter_boots", "warm_gloves", "winter_hat", "scarf"],
                "recommended": ["wool_socks", "layered_clothing", "face_protection"],
                "avoid": ["shorts", "sandals", "tank_tops", "light_fabrics", "cotton_only"],
                "fabrics": ["wool", "down", "fleece", "thermal", "merino_wool"],
                "colors": ["dark_colors", "neutral_tones"],
                "layers": 4
            },
            "very_cold": {
                "required": ["winter_coat", "warm_layers", "closed_shoes", "gloves", "hat"],
                "recommended": ["scarf", "warm_socks", "thermal_layer"],
                "avoid": ["shorts", "sandals", "sleeveless", "thin_fabrics"],
                "fabrics": ["wool", "fleece", "cotton_blend", "synthetic_insulation"],
                "colors": ["dark_colors", "neutral_tones"],
                "layers": 3
            },
            "cold": {
                "required": ["jacket_or_coat", "long_sleeves", "long_pants", "closed_shoes"],
                "recommended": ["light_gloves", "scarf"],
                "avoid": ["shorts", "sandals", "tank_tops"],
                "fabrics": ["cotton", "wool", "denim", "fleece"],
                "colors": ["any"],
                "layers": 2
            },
            "cool": {
                "required": ["light_jacket_or_cardigan", "long_sleeves"],
                "recommended": ["jeans", "comfortable_shoes"],
                "optional": ["light_sweater"],
                "fabrics": ["cotton", "light_wool", "denim", "knit"],
                "colors": ["any"],
                "layers": 2
            },
            "mild": {
                "required": ["comfortable_clothing"],
                "recommended": ["t_shirt", "jeans_or_chinos", "sneakers"],
                "optional": ["light_cardigan"],
                "fabrics": ["cotton", "linen", "light_blends"],
                "colors": ["any"],
                "layers": 1
            },
            "warm": {
                "required": ["light_clothing", "breathable_fabrics"],
                "recommended": ["shorts_or_light_pants", "t_shirt", "sandals_or_sneakers"],
                "avoid": ["heavy_jackets", "wool", "dark_colors"],
                "fabrics": ["cotton", "linen", "bamboo", "moisture_wicking"],
                "colors": ["light_colors", "bright_colors"],
                "layers": 1
            },
            "hot": {
                "required": ["very_light_clothing", "sun_protection"],
                "recommended": ["shorts", "tank_top", "sandals", "sun_hat", "sunglasses"],
                "avoid": ["dark_colors", "heavy_fabrics", "long_sleeves", "synthetic_materials"],
                "fabrics": ["linen", "cotton", "moisture_wicking", "bamboo"],
                "colors": ["white", "light_colors", "pastels"],
                "layers": 1
            },
            "extremely_hot": {
                "required": ["minimal_light_clothing", "maximum_sun_protection"],
                "recommended": ["loose_shorts", "breathable_tank_top", "sandals", "wide_brim_hat", "sunglasses"],
                "avoid": ["dark_colors", "synthetic_fabrics", "tight_clothing", "layers"],
                "fabrics": ["linen", "bamboo", "moisture_wicking", "UV_protective"],
                "colors": ["white", "very_light_colors"],
                "layers": 1
            }
        }
        
        self.weather_clothing_map = {
            "clear": {
                "considerations": ["UV protection if sunny", "comfortable clothing"],
                "accessories": ["sunglasses", "hat"]
            },
            "partly_cloudy": {
                "considerations": ["Variable conditions", "easy to adjust layers"],
                "accessories": ["light_jacket"]
            },
            "overcast": {
                "considerations": ["Cooler than expected", "possible light rain"],
                "accessories": ["light_jacket", "umbrella"]
            },
            "rainy": {
                "required": ["waterproof_jacket", "waterproof_shoes", "umbrella"],
                "recommended": ["rain_pants", "waterproof_bag"],
                "avoid": ["suede", "canvas", "light_colors", "delicate_fabrics"],
                "accessories": ["umbrella", "waterproof_bag"]
            },
            "snowy": {
                "required": ["waterproof_winter_boots", "warm_waterproof_jacket", "gloves", "hat"],
                "recommended": ["snow_pants", "gaiters", "warm_socks"],
                "avoid": ["cotton_clothing", "non_waterproof_shoes"],
                "accessories": ["scarf", "hand_warmers"]
            },
            "stormy": {
                "required": ["sturdy_waterproof_jacket", "secure_footwear"],
                "avoid": ["umbrellas", "loose_clothing", "metal_accessories"],
                "considerations": ["Stay indoors if possible", "avoid tall objects"]
            },
            "foggy": {
                "recommended": ["layers", "reflective_clothing"],
                "considerations": ["Reduced visibility", "may be cooler than expected"],
                "accessories": ["reflective_elements"]
            }
        }
        
        self.wind_clothing_map = {
            "calm": {},
            "light": {
                "recommended": ["light_windbreaker"]
            },
            "moderate": {
                "required": ["windproof_jacket"],
                "avoid": ["loose_clothing", "light_scarves"],
                "considerations": ["Secure accessories"]
            },
            "strong": {
                "required": ["heavy_windproof_jacket", "secure_accessories"],
                "avoid": ["loose_clothing", "hats", "scarves", "umbrellas"],
                "considerations": ["Be cautious outdoors"]
            },
            "very_strong": {
                "required": ["heavy_windproof_gear"],
                "avoid": ["loose_clothing", "any_loose_accessories", "umbrellas"],
                "considerations": ["Avoid outdoor activities", "stay indoors if possible"]
            }
        }
    
    def get_coordinates_by_city(self, city_name: str, country_code: Optional[str] = None) -> Optional[Tuple[float, float]]:
        """Get coordinates for a city using OpenWeatherMap geocoding API"""
        try:
            params = {
                "q": f"{city_name},{country_code}" if country_code else city_name,
                "limit": 1,
                "appid": self.api_key
            }
            
            response = requests.get(self.geocoding_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                result = data[0]
                latitude = result["lat"]
                longitude = result["lon"]
                logger.info(f"Found coordinates for {city_name}: {latitude}, {longitude}")
                return (latitude, longitude)
            else:
                logger.warning(f"No coordinates found for city: {city_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting coordinates for {city_name}: {e}")
            return None
    
    def get_current_weather(self, city_name: str, country_code: Optional[str] = None, units: str = "metric") -> Optional[WeatherData]:
        """Get current weather data for a given city"""
        try:
            params = {
                "q": f"{city_name},{country_code}" if country_code else city_name,
                "appid": self.api_key,
                "units": units
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("cod") == 200:
                main_data = data["main"]
                weather_data_item = data["weather"][0]
                wind_data = data.get("wind", {})
                sys_data = data.get("sys", {})
                
                weather_data = WeatherData(
                    temperature=main_data["temp"],
                    feels_like=main_data["feels_like"],
                    humidity=main_data["humidity"],
                    pressure=main_data["pressure"],
                    wind_speed=wind_data.get("speed", 0),
                    wind_direction=wind_data.get("deg", 0),
                    visibility=data.get("visibility", 10000),
                    weather_main=weather_data_item["main"],
                    weather_description=weather_data_item["description"],
                    weather_icon=weather_data_item["icon"],
                    clouds=data.get("clouds", {}).get("all", 0),
                    location=data["name"],
                    country=sys_data.get("country", ""),
                    timestamp=datetime.now(),
                    sunrise=datetime.fromtimestamp(sys_data.get("sunrise", 0)),
                    sunset=datetime.fromtimestamp(sys_data.get("sunset", 0))
                )
                
                logger.info(f"Retrieved weather data for {weather_data.location}: {weather_data.temperature}°C, {weather_data.weather_description}")
                return weather_data
            else:
                logger.error(f"Error from weather API: {data.get('message', 'Unknown error')}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather data: {e}")
            return None
        except json.JSONDecodeError:
            logger.error("Error: Could not decode JSON response from weather API")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting weather data: {e}")
            return None
    
    def get_weather_by_coordinates(self, latitude: float, longitude: float, units: str = "metric") -> Optional[WeatherData]:
        """Get current weather data for given coordinates"""
        try:
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": units
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("cod") == 200:
                main_data = data["main"]
                weather_data_item = data["weather"][0]
                wind_data = data.get("wind", {})
                sys_data = data.get("sys", {})
                
                weather_data = WeatherData(
                    temperature=main_data["temp"],
                    feels_like=main_data["feels_like"],
                    humidity=main_data["humidity"],
                    pressure=main_data["pressure"],
                    wind_speed=wind_data.get("speed", 0),
                    wind_direction=wind_data.get("deg", 0),
                    visibility=data.get("visibility", 10000),
                    weather_main=weather_data_item["main"],
                    weather_description=weather_data_item["description"],
                    weather_icon=weather_data_item["icon"],
                    clouds=data.get("clouds", {}).get("all", 0),
                    location=data["name"],
                    country=sys_data.get("country", ""),
                    timestamp=datetime.now(),
                    sunrise=datetime.fromtimestamp(sys_data.get("sunrise", 0)),
                    sunset=datetime.fromtimestamp(sys_data.get("sunset", 0))
                )
                
                logger.info(f"Retrieved weather data for coordinates {latitude}, {longitude}: {weather_data.temperature}°C")
                return weather_data
            else:
                logger.error(f"Error from weather API: {data.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting weather data for coordinates: {e}")
            return None
    
    def get_weather_forecast(self, city_name: str, country_code: Optional[str] = None, units: str = "metric") -> List[WeatherData]:
        """Get 5-day weather forecast for a city"""
        try:
            params = {
                "q": f"{city_name},{country_code}" if country_code else city_name,
                "appid": self.api_key,
                "units": units
            }
            
            response = requests.get(self.forecast_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            forecast_data = []
            if data.get("cod") == "200":
                city_data = data.get("city", {})
                
                for item in data.get("list", []):
                    main_data = item["main"]
                    weather_data_item = item["weather"][0]
                    wind_data = item.get("wind", {})
                    
                    weather_data = WeatherData(
                        temperature=main_data["temp"],
                        feels_like=main_data["feels_like"],
                        humidity=main_data["humidity"],
                        pressure=main_data["pressure"],
                        wind_speed=wind_data.get("speed", 0),
                        wind_direction=wind_data.get("deg", 0),
                        visibility=item.get("visibility", 10000),
                        weather_main=weather_data_item["main"],
                        weather_description=weather_data_item["description"],
                        weather_icon=weather_data_item["icon"],
                        clouds=item.get("clouds", {}).get("all", 0),
                        location=city_data.get("name", city_name),
                        country=city_data.get("country", ""),
                        timestamp=datetime.fromtimestamp(item["dt"]),
                        sunrise=datetime.fromtimestamp(city_data.get("sunrise", 0)),
                        sunset=datetime.fromtimestamp(city_data.get("sunset", 0))
                    )
                    forecast_data.append(weather_data)
            
            logger.info(f"Retrieved {len(forecast_data)} forecast entries for {city_name}")
            return forecast_data
            
        except Exception as e:
            logger.error(f"Error getting weather forecast: {e}")
            return []
    
    def generate_weather_clothing_recommendations(self, weather_data: WeatherData) -> Dict[str, Any]:
        """Generate comprehensive clothing recommendations based on weather data"""
        try:
            recommendations = {
                "weather_summary": {
                    "location": f"{weather_data.location}, {weather_data.country}",
                    "temperature": weather_data.temperature,
                    "feels_like": weather_data.feels_like,
                    "description": weather_data.weather_description.title(),
                    "humidity": weather_data.humidity,
                    "wind_speed": weather_data.wind_speed,
                    "wind_speed_kmh": round(weather_data.wind_speed * 3.6, 1),
                    "pressure": weather_data.pressure,
                    "visibility": weather_data.visibility,
                    "clouds": weather_data.clouds,
                    "is_daytime": weather_data.is_daytime()
                },
                "clothing_recommendations": {
                    "required": [],
                    "recommended": [],
                    "optional": [],
                    "avoid": []
                },
                "fabric_recommendations": [],
                "color_recommendations": [],
                "accessories": [],
                "special_considerations": [],
                "layering_advice": {
                    "recommended_layers": 1,
                    "layer_types": []
                }
            }
            
            # Temperature-based recommendations
            temp_category = weather_data.get_temperature_category()
            temp_recommendations = self.temperature_clothing_map.get(temp_category, {})
            
            for key in ["required", "recommended", "optional", "avoid"]:
                if key in temp_recommendations:
                    recommendations["clothing_recommendations"][key].extend(temp_recommendations[key])
            
            if "fabrics" in temp_recommendations:
                recommendations["fabric_recommendations"].extend(temp_recommendations["fabrics"])
            
            if "colors" in temp_recommendations:
                recommendations["color_recommendations"].extend(temp_recommendations["colors"])
            
            if "layers" in temp_recommendations:
                recommendations["layering_advice"]["recommended_layers"] = temp_recommendations["layers"]
            
            # Weather condition-based recommendations
            weather_category = weather_data.get_weather_category()
            weather_recommendations = self.weather_clothing_map.get(weather_category, {})
            
            for key in ["required", "recommended", "avoid"]:
                if key in weather_recommendations:
                    recommendations["clothing_recommendations"][key].extend(weather_recommendations[key])
            
            if "accessories" in weather_recommendations:
                recommendations["accessories"].extend(weather_recommendations["accessories"])
            
            if "considerations" in weather_recommendations:
                if isinstance(weather_recommendations["considerations"], list):
                    recommendations["special_considerations"].extend(weather_recommendations["considerations"])
                else:
                    recommendations["special_considerations"].append(weather_recommendations["considerations"])
            
            # Wind-based recommendations
            wind_category = weather_data.get_wind_category()
            wind_recommendations = self.wind_clothing_map.get(wind_category, {})
            
            for key in ["required", "recommended", "avoid"]:
                if key in wind_recommendations:
                    recommendations["clothing_recommendations"][key].extend(wind_recommendations[key])
            
            if "considerations" in wind_recommendations:
                if isinstance(wind_recommendations["considerations"], list):
                    recommendations["special_considerations"].extend(wind_recommendations["considerations"])
                else:
                    recommendations["special_considerations"].append(wind_recommendations["considerations"])
            
            # Additional considerations based on specific conditions
            
            # High humidity
            if weather_data.humidity > 80:
                recommendations["special_considerations"].append("High humidity - choose breathable, moisture-wicking fabrics")
                recommendations["fabric_recommendations"].append("moisture_wicking")
                recommendations["clothing_recommendations"]["avoid"].append("cotton_in_humid_conditions")
            
            # Strong wind
            if weather_data.wind_speed > 10:  # > 36 km/h
                recommendations["special_considerations"].append("Strong winds - secure loose clothing and accessories")
            
            # Low visibility
            if weather_data.visibility < 5000:
                recommendations["special_considerations"].append("Low visibility - consider bright or reflective clothing")
                recommendations["color_recommendations"].append("bright_colors")
                recommendations["accessories"].append("reflective_elements")
            
            # UV protection for clear/sunny conditions
            if weather_data.weather_main.lower() == "clear" and weather_data.is_daytime():
                recommendations["accessories"].extend(["sunglasses", "sun_hat", "sunscreen"])
                recommendations["special_considerations"].append("Clear sunny weather - UV protection recommended")
            
            # Night time considerations
            if not weather_data.is_daytime():
                recommendations["special_considerations"].append("Evening/night - consider visibility and warmth")
                recommendations["color_recommendations"].append("reflective_elements")
            
            # High cloud cover
            if weather_data.clouds > 80:
                recommendations["special_considerations"].append("Overcast conditions - temperature may feel cooler")
            
            # Remove duplicates and clean up
            for key in ["fabric_recommendations", "color_recommendations", "accessories", "special_considerations"]:
                if key in recommendations:
                    recommendations[key] = list(set(recommendations[key]))
            
            for key in recommendations["clothing_recommendations"]:
                recommendations["clothing_recommendations"][key] = list(set(recommendations["clothing_recommendations"][key]))
            
            # Generate layering advice
            if recommendations["layering_advice"]["recommended_layers"] > 1:
                layer_advice = []
                if recommendations["layering_advice"]["recommended_layers"] >= 2:
                    layer_advice.append("Base layer: moisture-wicking material")
                if recommendations["layering_advice"]["recommended_layers"] >= 3:
                    layer_advice.append("Insulating layer: fleece or wool")
                if recommendations["layering_advice"]["recommended_layers"] >= 4:
                    layer_advice.append("Outer layer: windproof/waterproof shell")
                
                recommendations["layering_advice"]["layer_types"] = layer_advice
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating weather clothing recommendations: {e}")
            return {"error": str(e)}
    
    def get_seasonal_recommendations(self, season: str, location: Optional[str] = None) -> Dict[str, Any]:
        """Get general seasonal clothing recommendations"""
        seasonal_recommendations = {
            "spring": {
                "clothing_types": ["light_jackets", "cardigans", "long_sleeves", "jeans", "comfortable_shoes"],
                "fabrics": ["cotton", "light_wool", "denim", "linen_blends"],
                "colors": ["pastels", "light_colors", "fresh_tones"],
                "accessories": ["light_scarf", "umbrella"],
                "considerations": ["Layering for temperature changes", "Rain protection", "Transitional weather"]
            },
            "summer": {
                "clothing_types": ["shorts", "tank_tops", "sundresses", "sandals", "light_shirts"],
                "fabrics": ["cotton", "linen", "bamboo", "moisture_wicking"],
                "colors": ["light_colors", "white", "bright_colors"],
                "accessories": ["sunglasses", "hat", "sunscreen"],
                "considerations": ["UV protection", "Breathability", "Cooling fabrics"]
            },
            "fall": {
                "clothing_types": ["sweaters", "jackets", "boots", "long_pants", "layers"],
                "fabrics": ["wool", "fleece", "denim", "cotton_blends"],
                "colors": ["earth_tones", "warm_colors", "darker_shades"],
                "accessories": ["scarf", "light_gloves"],
                "considerations": ["Layering", "Warmth", "Transitional weather"]
            },
            "winter": {
                "clothing_types": ["heavy_coats", "sweaters", "boots", "warm_layers", "thermal_wear"],
                "fabrics": ["wool", "down", "fleece", "thermal", "waterproof"],
                "colors": ["dark_colors", "neutral_tones"],
                "accessories": ["gloves", "hat", "scarf", "warm_socks"],
                "considerations": ["Insulation", "Wind protection", "Waterproofing", "Layering"]
            }
        }
        
        return seasonal_recommendations.get(season.lower(), {})

# Global weather service instance
weather_service = WeatherService()

