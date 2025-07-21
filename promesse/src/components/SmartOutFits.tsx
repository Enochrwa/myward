import SmartOutfitRecommendations from "@/components/test/SmartOutfitRecommendations";
import { useEffect, useState } from "react";
import axios from "axios";
import apiClient from "@/lib/apiClient";

export default function WardrobeTestPage() {
        const [ wardrobeItems, setWardrobeItems] = useState<[]>([])

    useEffect(() => {
            (
                async () =>{
                    try {
                        const response = apiClient("/outfit/user-items")
                        if(response?.data){
                            setWardrobeItems(response?.data)
                        }
                        console.log("wardrobe response: ", response)
                    } catch (error: any) {
                        console.error("Error fetching wardrobe Items: ", error)
                    }
                }
            )();
    },[])
  

    return (
        <div className="max-w-3xl mx-auto my-10">
            <h1 className="text-3xl font-bold mb-6">Your Wardrobe</h1>
            <SmartOutfitRecommendations wardrobeItems={wardrobeItems} />
        </div>
    );
}
