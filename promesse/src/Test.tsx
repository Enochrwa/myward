import { useState } from "react";
import axios from "axios";
import { useAuth } from "@/hooks/useAuth";

export default function OccasionWeatherRecommendations() {
    const { user } = useAuth();
    const [occasion, setOccasion] = useState("casual");
    const [city, setCity] = useState("New York");
    const [recommendations, setRecommendations] = useState([]);

    const fetchRecommendations = async () => {
        const res = await axios.get("/api/recommendation/occasion-weather", {
            params: {
                user_id: user.id,
                city,
                occasion,
            },
        });
        setRecommendations(res.data.recommendations);
    };

    return (
        <div className="p-6 space-y-6">
            <h2 className="text-xl font-bold">Outfit Recommendations</h2>
            <div className="flex gap-4">
                <select
                    className="border p-2 rounded"
                    value={occasion}
                    onChange={(e) => setOccasion(e.target.value)}
                >
                    <option value="casual">Casual</option>
                    <option value="formal">Formal</option>
                    <option value="business">Business</option>
                    <option value="party">Party</option>
                </select>
                <input
                    type="text"
                    placeholder="City"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    className="border p-2 rounded"
                />
                <button
                    onClick={fetchRecommendations}
                    className="bg-blue-500 text-white px-4 py-2 rounded"
                >
                    Recommend
                </button>
            </div>

            <div className="grid grid-cols-3 gap-4">
                {recommendations.map((outfit, index) => (
                    <div key={index} className="p-4 border rounded shadow hover:scale-105 transition">
                        <h4 className="font-medium mb-2">Score: {outfit.score.toFixed(2)}</h4>
                        <div className="flex gap-2">
                            {outfit.items.map((item: any) => (
                                <img
                                    key={item.id}
                                    src={`/uploads/${item.filename}`}
                                    className="h-24 rounded"
                                    alt={item.category}
                                />
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
