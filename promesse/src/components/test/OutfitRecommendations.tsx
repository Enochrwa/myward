import React, { useEffect, useState } from "react";
import axios from "axios";

type ItemMetadata = {
    id: string;
    filename: string;
    image_url: string;
    original_name?: string;
    dominant_color?: string;
    color_palette?: string[];
    category: string;
    upload_date?: string;
    style?: string;
    occasion?: string[] | string;
    season?: string[] | string;
};

type OutfitResponse = {
    query_image_id: string;
    base_category: string;
    outfit: { [category: string]: ItemMetadata };
};

const OutfitRecommendations: React.FC = () => {
    const [outfitData, setOutfitData] = useState<OutfitResponse | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    const fetchRandomOutfit = async () => {
        setLoading(true);
        setError(null);

        try {
            const randomImageId = "c19c6edf-5f83-433c-be65-f4b3e1b1925e"; // Replace this later with dynamic logic
            const response = await axios.get<OutfitResponse>(
                `http://127.0.0.1:8000/api/outfit/recommend/${randomImageId}`
            );
            setOutfitData(response.data);
            console.log("Outfits: ", response?.data)
        } catch (err) {
            console.error(err);
            setError("Failed to fetch outfit.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRandomOutfit();
    }, []);

    const renderArrayOrString = (value?: string[] | string): string => {
        if (!value) return "N/A";
        if (Array.isArray(value)) return value.join(", ");
        return value.replace(/"/g, ""); // In case backend sends '"Winter"' instead of 'Winter'
    };

    return (
        <div className="p-4">
            <h1 className="text-2xl font-bold mb-4">Recommended Outfit</h1>

            <button
                className="mb-6 px-4 py-2 bg-black text-white rounded-xl hover:bg-gray-800 transition"
                onClick={fetchRandomOutfit}
                disabled={loading}
            >
                {loading ? "Loading..." : "Show Another Outfit"}
            </button>

            {error && <p className="text-red-500">{error}</p>}

            {outfitData && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {Object.entries(outfitData.outfit).map(([category, item]) => (
                        <div
                            key={item.id}
                            className="border rounded-2xl shadow-md p-4 flex flex-col items-center bg-white hover:shadow-lg transition"
                        >
                            <h2 className="text-xl font-semibold capitalize mb-2">{category}</h2>
                            <div
                                className="w-48 h-48 flex items-center justify-center rounded-xl mb-2"
                                style={{ backgroundColor: item.dominant_color || "#f0f0f0" }}
                            >
                                <img
                                    src={item.image_url}
                                    alt={item.original_name || category}
                                    className="max-w-full max-h-full object-contain rounded"
                                />
                            </div>
                            <p className="text-gray-600">Original Name: {item.original_name || "Unknown"}</p>
                            <p className="text-gray-600">Category: {item.category}</p>
                            <p className="text-gray-500">Season: {renderArrayOrString(item.season)}</p>
                            <p className="text-gray-500">Occasion: {renderArrayOrString(item.occasion)}</p>
                            <p className="text-gray-500">Style: {item.style || "N/A"}</p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default OutfitRecommendations;
