import { WardrobeItemResponse } from '@/lib/apiClient';

export interface Outfit {
  [category: string]: WardrobeItemResponse;
}

export interface OutfitCreate {
  name: string;
  item_ids: number[];
  tags?: string[];
  image_url?: string;
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
