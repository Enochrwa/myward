import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import { useAuth } from "@/hooks/useAuth";
import axios from "axios";

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

    axios
      .get(`http://127.0.0.1:8000/api/wardrobe/user/${user.id}`)
      .then((res) => setItems(res.data));

    axios
      .get(`http://127.0.0.1:8000/api/outfit/user/${user.id}`)
      .then((res) => {
        console.log("Saved outfits: ", res.data);
        setSavedOutfits(res.data);
      });
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
    fetch("http://127.0.0.1:8000/api/outfit/custom", {
      method: "POST",
      body: JSON.stringify({
        name: `Outfit ${Date.now()}`,
        gender: user.gender || "Unisex",
        clothing_items: selected.map((i) => i.id),
        clothing_parts: selected.map((i) => i.clothing_part),
      }),
      headers: { "Content-Type": "application/json" },
    })
      .then(() => {
        setSelected([]);
        return axios.get(`http://127.0.0.1:8000/api/outfit/user/${user?.id}`);
      })
      .then((res) => setSavedOutfits(res.data))
      .catch(console.error);
  };

  return (
    <div className="p-8 space-y-10">
      <h1 className="text-3xl font-bold">Your Wardrobe & Outfits</h1>

      <Input
        placeholder="Filter by category (jeans, dress...)"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
      />

      <div className="flex flex-wrap gap-4">
        {filteredItems?.map((item) => (
          <motion.div
            key={item.id}
            className={cn(
              "relative w-32 h-32 rounded-lg border overflow-hidden shadow hover:ring-2 hover:ring-primary cursor-pointer",
              favorites.includes(item.id) && "border-yellow-400"
            )}
            whileHover={{ scale: 1.05 }}
            onClick={() => handleDrop(item)}
          >
            <img
              src={item.image_url}
              alt={item.category}
              className="w-full h-full object-cover"
            />
            <button
              className="absolute top-1 right-1 bg-black bg-opacity-50 text-white px-1 rounded"
              onClick={(e) => {
                e.stopPropagation();
                toggleFavorite(item.id);
              }}
            >
              {favorites.includes(item.id) ? "★" : "☆"}
            </button>
          </motion.div>
        ))}
      </div>

      {selected.length > 0 && (
        <motion.div
          className="p-4 border rounded-xl space-y-4 shadow-md"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h2 className="font-semibold">Selected Items</h2>
          <div className="flex gap-4">
            {selected.map((item) => (
              <div key={item.id} className="w-24 h-24">
                <img
                  src={item.image_url}
                  alt={item.category}
                  className="w-full h-full object-cover rounded"
                />
              </div>
            ))}
          </div>

          <div>
            <h3 className="text-sm mb-2">Preview:</h3>
            <img
              src={stitchedPreviewUrl}
              alt="Preview"
              className="border rounded-xl"
            />
          </div>

          <Dialog>
            <DialogTrigger asChild>
              <Button variant="default">Save Outfit</Button>
            </DialogTrigger>
            <DialogContent>
              <h2 className="font-bold">Confirm Save Outfit?</h2>
              <Button onClick={saveOutfit} className="mt-4 w-full">
                Confirm Save
              </Button>
            </DialogContent>
          </Dialog>
        </motion.div>
      )}

      <div className="space-y-4">
        <h2 className="text-xl font-bold">Your Saved Outfits</h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
            {savedOutfits.map((outfit) => (
            <div
                key={outfit.id}
                className="rounded-xl shadow border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 p-4 flex flex-col items-center space-y-4 transition hover:shadow-lg"
            >
                <div className="relative w-full aspect-[2/1] rounded overflow-hidden bg-gray-50 dark:bg-gray-800">
                <img
                    src={outfit.preview_image_url?.replace(/b'|'/g, "")}
                    className="absolute inset-0 w-full h-full object-contain p-4"
                    alt="outfit"
                />
                </div>

                <p className="text-sm text-center dark:text-gray-300">{outfit.name}</p>
            </div>
            ))}
        </div>
        </div>

    </div>
  );
}
