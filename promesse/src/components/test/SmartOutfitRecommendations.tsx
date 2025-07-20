import React, { useState, useEffect } from "react";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import { Heart } from "lucide-react";

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
    preview_image_url?: string;
    isFavorite?: boolean;
}

interface Props {
    wardrobeItems: WardrobeItem[];
    userId: string;
}

const occasions = ["Work", "Casual", "Party", "Formal", "Date", "Everyday"];
const seasons = ["All Season", "Spring", "Summer", "Fall", "Winter"];

const SmartOutfitRecommendations: React.FC<Props> = ({ wardrobeItems, userId }) => {
    const [outfits, setOutfits] = useState<Outfit[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [selectedOccasion, setSelectedOccasion] = useState("Work");
    const [selectedSeason, setSelectedSeason] = useState("All Season");
    const [selectedOutfit, setSelectedOutfit] = useState<Outfit | null>(null);

    const fetchOutfits = () => {
        if (!wardrobeItems || wardrobeItems.length === 0) return;

        const preferences = { occasion: selectedOccasion, season: selectedSeason };

        setLoading(true);
        axios
            .post("http://127.0.0.1:8000/api/outfit/generate-smart-outfits", {
                wardrobe_items: wardrobeItems,
                preferences,
            })
            .then((res) => {
                setOutfits(res.data.map((o: Outfit) => ({ ...o, isFavorite: false })));
                setLoading(false);
            })
            .catch(() => {
                setError("Failed to fetch recommendations.");
                setLoading(false);
            });
    };

    useEffect(() => {
        fetchOutfits();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedOccasion, selectedSeason, wardrobeItems]);

    const toggleFavorite = (index: number) => {
        setOutfits((prev) =>
            prev.map((o, i) => (i === index ? { ...o, isFavorite: !o.isFavorite } : o))
        );
    };

    const handleSaveOutfit = (outfit: Outfit) => {
        const clothingItems = outfit.items.map((i) => i.id);
        const clothingParts = outfit.items.map((i) => i.clothing_part);

        axios.post("http://127.0.0.1:8000/api/outfit/custom", {
            name: outfit.description,
            gender: "Unisex",
            clothing_items: clothingItems,
            clothing_parts: clothingParts,
        })
            .then(() => alert("Outfit saved successfully!"))
            .catch(() => alert("Failed to save outfit."));
    };

    return (
        <div className="p-6 space-y-8">
            <h2 className="text-2xl font-semibold text-gray-800">Recommended Outfits</h2>

            <div className="flex flex-wrap gap-4">
                <select
                    className="border rounded-lg px-3 py-2 text-sm"
                    value={selectedOccasion}
                    onChange={(e) => setSelectedOccasion(e.target.value)}
                >
                    {occasions.map((o) => (
                        <option key={o} value={o}>{o}</option>
                    ))}
                </select>

                <select
                    className="border rounded-lg px-3 py-2 text-sm"
                    value={selectedSeason}
                    onChange={(e) => setSelectedSeason(e.target.value)}
                >
                    {seasons.map((s) => (
                        <option key={s} value={s}>{s}</option>
                    ))}
                </select>

                <button
                    onClick={fetchOutfits}
                    className="px-4 py-2 rounded-lg bg-black text-white text-sm"
                >
                    Refresh
                </button>
            </div>

            {loading && <div className="text-center py-10 text-gray-500">Generating outfits...</div>}
            {error && <div className="text-center py-10 text-red-500">{error}</div>}

            <div className="grid md:grid-cols-2 gap-6">
                {outfits.map((outfit, index) => (
                    <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="p-4 bg-white rounded-2xl shadow-md hover:shadow-lg transition space-y-4 relative"
                    >
                        <button
                            onClick={() => toggleFavorite(index)}
                            className="absolute right-4 top-4"
                        >
                            <Heart
                                className={`w-5 h-5 transition ${
                                    outfit.isFavorite ? "fill-red-500 text-red-500" : "text-gray-300"
                                }`}
                                fill={outfit.isFavorite ? "red" : "none"}
                            />
                        </button>

                        <div className="flex justify-between items-center">
                            <div className="font-medium text-gray-700">{outfit.description}</div>
                            <div className="text-xs bg-gray-100 px-3 py-1 rounded-full">
                                Score: {outfit.score.toFixed(2)}
                            </div>
                        </div>

                        {outfit.preview_image_url && (
                            <img
                                src={outfit.preview_image_url}
                                alt="Outfit Preview"
                                onClick={() => setSelectedOutfit(outfit)}
                                className="w-full rounded-xl border object-cover cursor-pointer hover:opacity-90"
                            />
                        )}

                        <div className="flex flex-wrap gap-4">
                            {outfit.items.map((item) => (
                                <motion.div
                                    key={item.id}
                                    whileHover={{ scale: 1.05 }}
                                    className="flex flex-col items-center text-sm w-[100px] space-y-1"
                                >
                                    <img
                                        src={item.image_url}
                                        alt={item.category}
                                        className="h-[120px] w-[100px] object-cover rounded-xl shadow"
                                    />
                                    <div className="text-gray-500">{item.category}</div>
                                    <div className="text-gray-400">{item.style}</div>
                                </motion.div>
                            ))}
                        </div>

                        <button
                            onClick={() => handleSaveOutfit(outfit)}
                            className="w-full py-2 bg-black text-white rounded-xl mt-2 text-sm"
                        >
                            Save Outfit
                        </button>
                    </motion.div>
                ))}
            </div>

            <AnimatePresence>
                {selectedOutfit && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
                        onClick={() => setSelectedOutfit(null)}
                    >
                        <motion.div
                            initial={{ scale: 0.9 }}
                            animate={{ scale: 1 }}
                            exit={{ scale: 0.9 }}
                            className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 relative"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <h3 className="text-lg font-semibold mb-4">{selectedOutfit.description}</h3>
                            {selectedOutfit.preview_image_url && (
                                <img
                                    src={selectedOutfit.preview_image_url}
                                    alt="Outfit Preview"
                                    className="rounded-xl w-full object-cover"
                                />
                            )}
                            <div className="flex gap-4 flex-wrap mt-4">
                                {selectedOutfit.items.map((item) => (
                                    <div key={item.id} className="w-20 text-center space-y-1">
                                        <img
                                            src={item.image_url}
                                            className="h-20 w-20 object-cover rounded-lg shadow"
                                            alt={item.category}
                                        />
                                        <div className="text-xs text-gray-500">{item.category}</div>
                                    </div>
                                ))}
                            </div>
                            <button
                                onClick={() => setSelectedOutfit(null)}
                                className="absolute top-2 right-4 text-gray-500 hover:text-black"
                            >
                                ✕
                            </button>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default SmartOutfitRecommendations;
