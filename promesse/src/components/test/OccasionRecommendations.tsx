import React, { useEffect, useState } from "react";
import axios from "axios";
import apiClient from "@/lib/apiClient";



const recommendOutfitsByWeatherOccasion = async (city, occasion, wardrobeItems) => {
    const data = {
        city,
        occasion,
        wardrobe_items: wardrobeItems
    }
    const response = await apiClient("/outfit/recommend/weather-occasion", {
        method:"POST",
        body:data
    });
    return response.data;
};






function OccasionRecommendations({ wardrobeItems }) {
    const [outfits, setOutfits] = useState([]);

    useEffect(() => {
        recommendOutfitsByWeatherOccasion("Kigali", "business", wardrobeItems).then((data) => {
            setOutfits(data);
        });
    }, [wardrobeItems]);

    return (
        <div className="outfits-grid">
            {outfits.map((outfit, index) => (
                <div key={index} className="outfit-card">
                    <h3>Score: {outfit.score.toFixed(2)}</h3>
                    <div className="outfit-items">
                        {outfit.items.map((item) => (
                            <img
                                key={item.id}
                                src={item.image_url}
                                alt={item.category}
                                style={{ width: 100 }}
                            />
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
}

export default OccasionRecommendations;
