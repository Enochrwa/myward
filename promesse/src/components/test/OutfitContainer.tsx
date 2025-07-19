import React, { useEffect, useState } from "react";
import axios from "axios";
import OutfitRecommendation from "./OutfitRecommendations";

const OutfitContainer: React.FC<{ imageId: string }> = ({ imageId }) => {
    const [outfitData, setOutfitData] = useState<any | null>(null);

    useEffect(() => {
        (
            async () =>{
                try {
                   const response =  axios.get(`http://127.0.0.1:8000/api/outfit/recommend/${imageId}`)
                   if(response?.data){
                    setOutfitData(response?.data)
                   }
                   console.log("Outfits: ", response?.data)
                } catch (error:any) {
                    console.error("Error getting outfit recommendations: ", error)
                }
            }
        )
    }, [imageId]);

    if (!outfitData) return <p>Loading outfit...</p>;

    return <OutfitRecommendation outfitData={outfitData} />;
};

export default OutfitContainer;


        