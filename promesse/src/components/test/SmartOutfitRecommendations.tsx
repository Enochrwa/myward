import React, { useState, useEffect } from "react";
import { saveOutfit, toggleFavoriteOutfit, generateSmartOutfits } from "@/lib/apiClient";
import { motion, AnimatePresence } from "framer-motion";
import { Heart } from "lucide-react";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";

interface WardrobeItem {
    id: string;
    image_url: string;
    category: string;
    clothing_part: string;
    style: string;
    dominant_color: string;
}

interface Outfit {
    id?: string;
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
        generateSmartOutfits(wardrobeItems, preferences)
            .then((data) => {
                setOutfits(data.map((o: Outfit) => ({ ...o, isFavorite: false })));
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
        const outfit = outfits[index];
        if (!outfit) return;

        if (outfit.id) {
            // Optimistically update the UI
            const newOutfits = [...outfits];
            newOutfits[index] = { ...outfit, isFavorite: !outfit.isFavorite };
            setOutfits(newOutfits);
            
            toggleFavoriteOutfit(outfit.id)
                .catch(() => {
                    // Revert the change if the API call fails
                    setOutfits(outfits);
                    alert("Failed to update favorite status.");
                });
        } else {
            // If the outfit doesn't have an ID, it hasn't been saved yet.
            // Just toggle the state locally.
            setOutfits((prev) =>
                prev.map((o, i) => (i === index ? { ...o, isFavorite: !o.isFavorite } : o))
            );
        }
    };

    const handleSaveOutfit = (outfit: Outfit) => {
        const clothingItems = outfit.items.map((i) => i.id);
        const clothingParts = outfit.items.map((i) => i.clothing_part);

        saveOutfit({
            name: outfit.description,
            gender: "Unisex",
            clothing_items: clothingItems,
            clothing_parts: clothingParts,
            score: outfit.score,
            description: outfit.description,
            is_favorite: outfit.isFavorite,
            dominant_colors: outfit.items.map((i) => i.dominant_color),
            styles: [...new Set(outfit.items.map((i) => i.style))],
            occasions: [...new Set(outfit.items.map((i) => i.style
            ))]
        })
            .then(() => alert("Outfit saved successfully!"))
            .catch(() => alert("Failed to save outfit."));
    };

    const [outfitBuilderItems, setOutfitBuilderItems] = useState<WardrobeItem[]>([]);

    const onDragEnd = (result: any) => {
        const { source, destination } = result;

        if (!destination) {
            return;
        }

        if (source.droppableId === destination.droppableId) {
            // Reordering within the same list
            if (source.droppableId === "wardrobe") {
                // Reordering wardrobe items is not supported in this UI
            } else {
                const items = Array.from(outfitBuilderItems);
                const [reorderedItem] = items.splice(source.index, 1);
                items.splice(destination.index, 0, reorderedItem);
                setOutfitBuilderItems(items);
            }
        } else {
            // Moving from one list to another
            if (source.droppableId === "wardrobe" && destination.droppableId === "outfit-builder") {
                const itemToMove = wardrobeItems[source.index];
                const newOutfitBuilderItems = Array.from(outfitBuilderItems);
                newOutfitBuilderItems.splice(destination.index, 0, itemToMove);
                setOutfitBuilderItems(newOutfitBuilderItems);
            } else if (source.droppableId === "outfit-builder" && destination.droppableId === "wardrobe") {
                const newOutfitBuilderItems = Array.from(outfitBuilderItems);
                newOutfitBuilderItems.splice(source.index, 1);
                setOutfitBuilderItems(newOutfitBuilderItems);
            }
        }
    };

    return (
        <DragDropContext onDragEnd={onDragEnd}>
            <div className="p-6 space-y-8 bg-gray-900 text-white min-h-screen">
                <h2 className="text-2xl font-semibold text-white">Recommended Outfits</h2>

                <div className="flex flex-wrap gap-4">
                    <select
                        className="border rounded-lg px-3 py-2 text-sm bg-gray-800 text-white border-gray-700"
                        value={selectedOccasion}
                        onChange={(e) => setSelectedOccasion(e.target.value)}
                    >
                        {occasions.map((o) => (
                            <option key={o} value={o}>{o}</option>
                        ))}
                    </select>

                    <select
                        className="border rounded-lg px-3 py-2 text-sm bg-gray-800 text-white border-gray-700"
                        value={selectedSeason}
                        onChange={(e) => setSelectedSeason(e.target.value)}
                    >
                        {seasons.map((s) => (
                            <option key={s} value={s}>{s}</option>
                        ))}
                    </select>

                    <button
                        onClick={fetchOutfits}
                        className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-sm"
                    >
                        Refresh
                    </button>
                </div>

                {loading && <div className="text-center py-10 text-gray-400">Generating outfits...</div>}
                {error && <div className="text-center py-10 text-red-400">{error}</div>}

                <div className="grid md:grid-cols-2 gap-6">
                    {outfits.map((outfit, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="p-4 bg-gray-800 rounded-2xl shadow-lg hover:shadow-2xl transition space-y-4 relative"
                        >
                            <button
                                onClick={() => toggleFavorite(index)}
                                className="absolute right-4 top-4"
                            >
                                <Heart
                                    className={`w-5 h-5 transition ${
                                        outfit.isFavorite ? "fill-red-500 text-red-500" : "text-gray-500"
                                    }`}
                                    fill={outfit.isFavorite ? "red" : "none"}
                                />
                            </button>

                            <div className="flex justify-between items-center">
                                <div className="font-medium text-gray-300">{outfit.description}</div>
                                <div className="text-xs bg-gray-700 px-3 py-1 rounded-full">
                                    Score: {outfit.score.toFixed(2)}
                                </div>
                            </div>

                            {outfit.preview_image_url && (
                                <img
                                    src={outfit.preview_image_url}
                                    alt="Outfit Preview"
                                    onClick={() => setSelectedOutfit(outfit)}
                                    className="w-full rounded-xl border border-gray-700 object-cover cursor-pointer hover:opacity-90"
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
                                            className="h-[120px] w-[100px] object-cover rounded-xl shadow-md"
                                        />
                                        <div className="text-gray-400">{item.category}</div>
                                        <div className="text-gray-500">{item.style}</div>
                                    </motion.div>
                                ))}
                            </div>

                            <button
                                onClick={() => handleSaveOutfit(outfit)}
                                className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl mt-2 text-sm"
                            >
                                Save Outfit
                            </button>
                        </motion.div>
                    ))}
                </div>
                <div className="flex gap-8">
                    <Droppable droppableId="wardrobe">
                        {(provided) => (
                            <div
                                {...provided.droppableProps}
                                ref={provided.innerRef}
                                className="w-1/2 p-4 bg-gray-800 rounded-lg"
                            >
                                <h3 className="text-lg font-semibold mb-4">Your Wardrobe</h3>
                                <div className="grid grid-cols-3 gap-4">
                                    {wardrobeItems.map((item, index) => (
                                        <Draggable key={item.id} draggableId={item.id} index={index}>
                                            {(provided) => (
                                                <div
                                                    ref={provided.innerRef}
                                                    {...provided.draggableProps}
                                                    {...provided.dragHandleProps}
                                                    className="w-full h-32 rounded-lg overflow-hidden shadow-lg"
                                                >
                                                    <img
                                                        src={item.image_url}
                                                        alt={item.category}
                                                        className="w-full h-full object-cover"
                                                    />
                                                </div>
                                            )}
                                        </Draggable>
                                    ))}
                                </div>
                                {provided.placeholder}
                                {outfitBuilderItems.length > 0 && (
                                    <button
                                        onClick={() => {
                                            const newOutfit: Outfit = {
                                                items: outfitBuilderItems,
                                                score: 0,
                                                description: "Custom Outfit",
                                            };
                                            handleSaveOutfit(newOutfit);
                                            setOutfitBuilderItems([]);
                                        }}
                                        className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl mt-4 text-sm"
                                    >
                                        Save New Outfit
                                    </button>
                                )}
                                {selectedOutfit && (
                                    <button
                                        onClick={() => {
                                            const updatedOutfit = { ...selectedOutfit, items: outfitBuilderItems };
                                            updateOutfit(selectedOutfit.id as string, updatedOutfit)
                                                .then(() => {
                                                    alert("Outfit updated successfully!");
                                                    setSelectedOutfit(null);
                                                    setOutfitBuilderItems([]);
                                                    fetchOutfits();
                                                })
                                                .catch(() => alert("Failed to update outfit."));
                                        }}
                                        className="w-full py-2 bg-green-600 hover:bg-green-700 text-white rounded-xl mt-2 text-sm"
                                    >
                                        Save Changes
                                    </button>
                                )}
                            </div>
                        )}
                    </Droppable>
                    <Droppable droppableId="outfit-builder">
                        {(provided) => (
                            <div
                                {...provided.droppableProps}
                                ref={provided.innerRef}
                                className="w-1/2 p-4 bg-gray-800 rounded-lg"
                            >
                                <h3 className="text-lg font-semibold mb-4">Outfit Builder</h3>
                                <div className="grid grid-cols-3 gap-4">
                                    {outfitBuilderItems.map((item, index) => (
                                        <Draggable key={item.id} draggableId={item.id} index={index}>
                                            {(provided) => (
                                                <div
                                                    ref={provided.innerRef}
                                                    {...provided.draggableProps}
                                                    {...provided.dragHandleProps}
                                                    className="w-full h-32 rounded-lg overflow-hidden shadow-lg"
                                                >
                                                    <img
                                                        src={item.image_url}
                                                        alt={item.category}
                                                        className="w-full h-full object-cover"
                                                    />
                                                </div>
                                            )}
                                        </Draggable>
                                    ))}
                                </div>
                                {provided.placeholder}
                            </div>
                        )}
                    </Droppable>
                </div>


                <AnimatePresence>
                    {selectedOutfit && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
                            onClick={() => setSelectedOutfit(null)}
                        >
                            <motion.div
                                initial={{ scale: 0.9 }}
                                animate={{ scale: 1 }}
                                exit={{ scale: 0.9 }}
                                className="bg-gray-800 rounded-2xl shadow-xl max-w-md w-full p-6 relative"
                                onClick={(e) => e.stopPropagation()}
                            >
                                <h3 className="text-lg font-semibold mb-4 text-white">{selectedOutfit.description}</h3>
                                {selectedOutfit.preview_image_url && (
                                    <img
                                        src={selectedOutfit.preview_image_url}
                                        alt="Outfit Preview"
                                        className="rounded-xl w-full object-cover border border-gray-700"
                                    />
                                )}
                                <div className="flex gap-4 flex-wrap mt-4">
                                    {selectedOutfit.items.map((item) => (
                                        <div key={item.id} className="w-20 text-center space-y-1">
                                            <img
                                                src={item.image_url}
                                                className="h-20 w-20 object-cover rounded-lg shadow-md"
                                                alt={item.category}
                                            />
                                            <div className="text-xs text-gray-400">{item.category}</div>
                                        </div>
                                    ))}
                                </div>
                                <button
                                    onClick={() => setSelectedOutfit(null)}
                                    className="absolute top-2 right-4 text-gray-500 hover:text-white"
                                >
                                    ✕
                                </button>
                            </motion.div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </DragDropContext>
    );
};

export default SmartOutfitRecommendations;
