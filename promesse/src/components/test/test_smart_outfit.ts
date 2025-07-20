import axios from "axios";

export const generateSmartOutfits = async (wardrobeItems, preferences) => {
    const response = await axios.post("http://127.0.0.1:8000/api/outfit/generate-smart-outfits", {
        wardrobe_items: wardrobeItems,
        preferences: preferences,
    });
    return response.data;
};
