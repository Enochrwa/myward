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
                        const token = localStorage.getItem("token"); // or use the exact key you stored the token with

                        const allItems = await axios.get("http://127.0.0.1:8000/api/images", {
                            headers: {
                            Authorization: `Bearer ${token}`,
                            },
                        });

                        console.log("Wardrobe Items: ", allItems?.data?.images)
                        setWardrobeItems(allItems?.data?.images)
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
