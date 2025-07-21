import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import { useAuth } from "@/hooks/useAuth";
import axios from "axios";
import { Star, PlusCircle } from "lucide-react";

type WardrobeItem = {
  id: string;
  filename: string;
  category: string;
  clothing_part: string;
  image_url: string;
  gender: string;
};

export default function WardrobeAndOutfits() {
  const { user } = useAuth();
  const [items, setItems] = useState<WardrobeItem[]>([]);
  const [selected, setSelected] = useState<WardrobeItem[]>([]);
  const [filter, setFilter] = useState("");
  const [favorites, setFavorites] = useState<string[]>([]);
  const [savedOutfits, setSavedOutfits] = useState<any[]>([]);

  useEffect(() => {
    if (!user?.id) return;

    const token = localStorage.getItem("token");

    axios
      .get(`http://127.0.0.1:8000/api/wardrobe/user/${user.id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      .then((res) => setItems(res.data))
      .catch((err) => console.error("Wardrobe fetch error:", err));

    axios
      .get(`http://127.0.0.1:8000/api/outfit/user`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      .then((res) => {
        setSavedOutfits(res.data);
      })
      .catch((err) => console.error("Outfits fetch error:", err));
  }, [user?.id]);


  const toggleFavorite = (id: string) => {
    setFavorites((prev) =>
      prev.includes(id) ? prev.filter((f) => f !== id) : [...prev, id]
    );
  };

  const handleDrop = (item: WardrobeItem) => {
    setSelected((prev) =>
      prev.some((i) => i.id === item.id)
        ? prev.filter((i) => i.id !== item.id)
        : [...prev, item]
    );
  };

  const filteredItems = Array.isArray(items)
    ? items.filter((i) =>
        i?.category && filter
          ? i.category.toLowerCase().includes(filter.toLowerCase())
          : true
      )
    : [];

  const stitchedPreviewUrl = `http://127.0.0.1:8000/api/wardrobe/stitch-preview?ids=${selected
    .map((i) => i.id)
    .join(",")}`;

  const saveOutfit = () => {
    const token = localStorage.getItem("token");

    fetch("http://127.0.0.1:8000/api/outfit/custom", {
      method: "POST",
      body: JSON.stringify({
        name: `My Custom Outfit ${Date.now()}`,
        gender: user.gender || "Unisex",
        clothing_items: selected.map((i) => i.id),
        clothing_parts: selected.map((i) => i.clothing_part),
      }),
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    })
      .then(() => {
        setSelected([]);
        return axios.get(`http://127.0.0.1:8000/api/outfit/user`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
      })
      .then((res) => setSavedOutfits(res.data))
      .catch(console.error);
  };

  return (
    <div className="p-8 space-y-10 bg-gray-900 text-white min-h-screen font-sans">
      <div className="text-center">
        <h1 className="text-5xl font-extrabold tracking-tight">Your Personal Style Studio</h1>
        <p className="text-xl text-gray-400 mt-2">Craft your look, define your style.</p>
      </div>

      <Input
        placeholder="Search your wardrobe (e.g., jeans, dress...)"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        className="bg-gray-800 text-white border-gray-700 focus:ring-2 focus:ring-indigo-500 text-lg p-4 rounded-full"
      />

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-6">
        {filteredItems?.map((item) => (
          <motion.div
            key={item.id}
            className={cn(
              "relative w-full h-48 rounded-2xl border-2 border-gray-700 overflow-hidden shadow-lg hover:ring-4 hover:ring-indigo-500 cursor-pointer transition-all duration-300",
              selected.some(s => s.id === item.id) && "ring-4 ring-green-500",
              favorites.includes(item.id) && "border-yellow-400"
            )}
            whileHover={{ scale: 1.05, y: -5 }}
            onClick={() => handleDrop(item)}
          >
            <img
              src={item.image_url}
              alt={item.category}
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
              <p className="text-white font-bold text-lg">{item.category}</p>
            </div>
            <button
              className="absolute top-2 right-2 bg-black bg-opacity-60 text-white p-2 rounded-full text-xs"
              onClick={(e) => {
                e.stopPropagation();
                toggleFavorite(item.id);
              }}
            >
              <Star className={`w-5 h-5 ${favorites.includes(item.id) ? "text-yellow-400 fill-yellow-400" : "text-white"}`} />
            </button>
          </motion.div>
        ))}
      </div>

      {selected.length > 0 && (
        <motion.div
          className="p-8 bg-gray-800 rounded-3xl space-y-6 shadow-2xl"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex justify-between items-center">
            <h2 className="font-semibold text-3xl">Outfit Canvas</h2>
            <Button onClick={saveOutfit} className="bg-indigo-600 hover:bg-indigo-700 rounded-full px-8 py-3 text-lg font-bold">
              <PlusCircle className="mr-2" /> Save Outfit
            </Button>
          </div>
          <div className="flex justify-center gap-4 p-4 bg-gray-900 rounded-2xl">
            {selected.map((item) => (
              <motion.div
                key={item.id}
                className="w-32 h-32 rounded-lg overflow-hidden"
                initial={{ scale: 0.8 }}
                animate={{ scale: 1 }}
              >
                <img
                  src={item.image_url}
                  alt={item.category}
                  className="w-full h-full object-cover"
                />
              </motion.div>
            ))}
          </div>

          <div className="text-center">
            <h3 className="text-2xl mb-4 font-semibold">Live Preview</h3>
            <img
              src={stitchedPreviewUrl}
              alt="Preview"
              className="border-2 border-gray-700 rounded-xl mx-auto"
            />
          </div>
        </motion.div>
      )}

      <div className="space-y-8">
        <h2 className="text-4xl font-bold text-center">Your Curated Outfits</h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-10">
            {savedOutfits.map((outfit) => (
            <motion.div
                key={outfit.id}
                className="rounded-2xl shadow-lg border-2 border-gray-700 bg-gray-800 p-6 flex flex-col items-center space-y-4 transition-all duration-300 hover:shadow-2xl hover:border-indigo-500 hover:scale-105"
            >
                <div className="relative w-full aspect-square rounded-lg overflow-hidden bg-gray-700">
                <img
                    src={outfit.preview_image_url?.replace(/b'|'/g, "")}
                    className="absolute inset-0 w-full h-full object-contain p-4"
                    alt="outfit"
                />
                </div>

                <p className="text-xl text-center font-bold text-white">{outfit.name}</p>
                <div className="flex flex-wrap gap-2 justify-center">
                    {(Array.isArray(outfit.styles) 
                        ? outfit?.styles 
                        : JSON.parse(outfit?.styles || "[]")
                    ).map((style: string, index: number) => (
                        <span key={index} className="text-xs bg-gray-700 px-3 py-1 rounded-full">{style}</span>
                    ))}
                    </div>

                <div className="text-lg text-indigo-400 font-semibold">Score: {outfit.score?.toFixed(2)}</div>
            </motion.div>
            ))}
        </div>
      </div>
    </div>
  );
}
