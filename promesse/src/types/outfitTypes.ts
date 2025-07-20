import { WardrobeItemResponse } from "@/lib/apiClient";

export interface Outfit {
    id: number;
    name: string;
    gender: string;
    clothing_items: WardrobeItemResponse[];
    clothing_parts: string[];
}
  
export interface OutfitCreate {
    name: string;
    gender: string;
    clothing_items: number[];
    clothing_parts: string[];
}

export interface SmartOutfit {
    items: WardrobeItemResponse[];
    score: number;
    score_breakdown: any;
    description: string;
    dominant_colors: string[];
    styles: string[];
    occasions: string[];
}

export interface Feedback {
  id: number;
  outfit_id: number;
  user_id: number;
  commenter_username?: string;
  feedback_text?: string;
  rating?: number;
  created_at: string;
}

export interface FeedbackCreate {
  feedback_text?: string;
  rating?: number;
}
