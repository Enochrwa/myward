import React, { useEffect, useState } from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";

const occasions = [
    "work", "formal", "leisure", "party", "sport", "outdoor", "smart_casual"
];



// Keep your imports as is

const WeatherOccasionRecommender = ({ wardrobeItems }) => {
    const [city, setCity] = useState("Kigali");
    const [occasion, setOccasion] = useState("work");
    const [outfits, setOutfits] = useState([]);
    const [weather, setWeather] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const recommendOutfitsByWeatherOccasion = async (city, occasion, wardrobeItems) => {
        setLoading(true);
        setError(null);
        try {
            const response = await axios.post("http://127.0.0.1:8000/api/outfit/recommend/weather-occasion", {
                city,
                occasion,
                wardrobe_items: wardrobeItems
            });
            setOutfits(response.data);
        } catch (error) {
            setError("Error fetching outfit recommendations.");
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const fetchWeather = async (city) => {
        try {
            const response = await axios.get(`http://127.0.0.1:8000/api/other/weather/${city}`);
            setWeather(response.data);
        } catch (error) {
            setError("Error fetching weather data.");
            console.error(error);
        }
    }

    const handleRecommendationRequest = () => {
        fetchWeather(city);
        recommendOutfitsByWeatherOccasion(city, occasion, wardrobeItems);
    }

    useEffect(() => {
        if (wardrobeItems.length > 0) {
            handleRecommendationRequest();
        }
    }, [wardrobeItems]);

    return (
        <div className="container mx-auto p-4 bg-gray-50 min-h-screen">
            <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
                <Card className="mb-6 shadow-lg border-0 rounded-xl">
                    <CardHeader className="bg-gray-800 text-white rounded-t-xl">
                        <CardTitle className="text-2xl font-bold">Find Your Perfect Outfit</CardTitle>
                    </CardHeader>
                    <CardContent className="p-6">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
                            <div className="flex flex-col gap-2">
                                <label className="font-semibold text-gray-700">City</label>
                                <Input
                                    placeholder="Enter a city"
                                    value={city}
                                    onChange={(e) => setCity(e.target.value)}
                                />
                            </div>
                            <div className="flex flex-col gap-2">
                                <label className="font-semibold text-gray-700">Occasion</label>
                                <Select onValueChange={setOccasion} defaultValue={occasion}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select an occasion" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {occasions.map(o => <SelectItem key={o} value={o}>{o.charAt(0).toUpperCase() + o.slice(1)}</SelectItem>)}
                                    </SelectContent>
                                </Select>
                            </div>
                            <Button
                                onClick={handleRecommendationRequest}
                                className="w-full md:w-auto bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded-md shadow-md"
                            >
                                Get Recommendations
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </motion.div>

            {error && <p className="text-red-500 text-center mb-4">{error}</p>}

            {weather && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5, delay: 0.2 }}>
                    <Card className="mb-6 shadow-md border-0 rounded-xl">
                        <CardHeader>
                            <CardTitle className="text-xl font-semibold text-gray-400">
                                Current Weather in {city}
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-4 p-6 text-center">
                            <div>
                                <p className="text-4xl font-bold text-indigo-600">{weather.temperature}°C</p>
                                <p className="text-gray-600">Temperature</p>
                            </div>
                            <div>
                                <p className="text-lg font-semibold text-gray-400">{weather.weather_condition}</p>
                                <p className="text-gray-600 capitalize">{weather.description}</p>
                            </div>
                            <div>
                                <p className="text-lg font-semibold">{weather.humidity}%</p>
                                <p className="text-gray-600">Humidity</p>
                            </div>
                            <div>
                                <p className="text-lg font-semibold">{weather.wind_speed} m/s</p>
                                <p className="text-gray-600">Wind</p>
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>
            )}

            {loading ? (
                <div className="flex justify-center items-center h-64">
                    <div className="loader ease-linear rounded-full border-8 border-t-8 border-gray-200 h-32 w-32"></div>
                </div>
            ) : (
                <motion.div
                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.5, delay: 0.4 }}
                >
                    {outfits.map((outfit, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                        >
                            <Card className="shadow-lg hover:shadow-xl rounded-xl">
                                <CardHeader className="flex justify-between items-center bg-gray-100 p-4">
                                    <CardTitle className="text-lg font-bold text-gray-800">Outfit {index + 1}</CardTitle>
                                    <div className="text-sm font-semibold bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full">
                                        Score: {outfit.score.toFixed(2)}
                                    </div>
                                </CardHeader>
                                <CardContent className="p-4 flex justify-center items-center gap-2">
                                    {outfit.items.map((item) => (
                                        <div key={item.id} className="w-28 h-28 rounded-lg overflow-hidden shadow-md">
                                            <img
                                                src={item.image_url}
                                                alt={item.category}
                                                className="w-full h-full object-cover"
                                            />
                                        </div>
                                    ))}
                                </CardContent>
                            </Card>
                        </motion.div>
                    ))}
                </motion.div>
            )}
        </div>
    );
};

export default WeatherOccasionRecommender;
