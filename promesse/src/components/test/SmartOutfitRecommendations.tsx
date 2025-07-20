import React, { useEffect, useState } from "react";
import axios from "axios";

interface WardrobeItem {
    id: string;
    image_url: string;
    category: string;
    clothing_part: string;
    style: string;
    dominant_color: string;
}

interface Outfit {
    score: number;
    description: string;
    items: WardrobeItem[];
}

interface Props {
    wardrobeItems: WardrobeItem[];
}

const SmartOutfitRecommendations: React.FC<Props> = ({ wardrobeItems }) => {
    const [outfits, setOutfits] = useState<Outfit[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!wardrobeItems || wardrobeItems.length === 0) return;

        const preferences = {
            occasion: "Work",
            season: "All Season",
        };

        setLoading(true);
        axios
            .post("http://127.0.0.1:8000/api/outfit/generate-smart-outfits", {
                wardrobe_items: wardrobeItems,
                preferences,
            })
            .then((res) => {
                setOutfits(res.data);
                setLoading(false);
            })
            .catch((err) => {
                setError("Failed to fetch recommendations.");
                setLoading(false);
            });
    }, [wardrobeItems]);

    if (loading) {
        return <div className="text-center py-10 text-gray-500">Generating smart outfits...</div>;
    }

    if (error) {
        return <div className="text-center py-10 text-red-500">{error}</div>;
    }

    if (!outfits.length) {
        return <div className="text-center py-10 text-gray-500">No recommendations found.</div>;
    }

    return (
        <div className="p-6 space-y-8">
            <h2 className="text-2xl font-semibold text-gray-800">Recommended Outfits for You</h2>
            {outfits.map((outfit, index) => (
                <div
                    key={index}
                    className="p-4 bg-white rounded-2xl shadow-md hover:shadow-lg transition flex flex-col space-y-4"
                >
                    <div className="flex justify-between items-center">
                        <div className="font-medium text-gray-700">{outfit.description}</div>
                        <div className="text-xs bg-gray-100 px-3 py-1 rounded-full">
                            Score: {outfit.score.toFixed(2)}
                        </div>
                    </div>

                    <div className="flex flex-wrap gap-4">
                        {outfit.items.map((item) => (
                            <div
                                key={item.id}
                                className="flex flex-col items-center text-sm w-[100px] space-y-1"
                            >
                                <img
                                    src={item.image_url}
                                    alt={item.category}
                                    className="h-[120px] w-[100px] object-cover rounded-xl shadow"
                                />
                                <div className="text-gray-500">{item.category}</div>
                                <div className="text-gray-400">{item.style}</div>
                            </div>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
};

export default SmartOutfitRecommendations;
