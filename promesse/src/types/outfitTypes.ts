// Using WardrobeItem from WardrobeManager for now.
// Ideally, this would be a shared type definition if WardrobeManager also exports it
// or if there's a central types file.
import { WardrobeItem } from '@/components/WardrobeManager'; // Adjust path if WardrobeItem is moved/exported differently

export interface Outfit {
  id: string;
  name: string;
  item_ids: string[];
  user_id?: string;
  created_at?: string;
  updated_at?: string;
  tags?: string[];
  image_url?: string;
  items?: WardrobeItem[]; // For frontend display, populated after fetching item details if needed
  feedbacks?: Feedback[]; // Added for displaying feedback
}

export interface OutfitCreate {
  name: string;
  item_ids: string[];
  tags?: string[];
  image_url?: string;
}

export interface Feedback {
  id: number; // Assuming backend uses number for ID
  outfit_id: number; // Assuming backend uses number for ID
  user_id: number; // Assuming backend uses number for ID
  commenter_username?: string;
  feedback_text?: string;
  rating?: number; // 1-5
  created_at: string; // ISO date string
}

export interface FeedbackCreate {
  feedback_text?: string;
  rating?: number;
}
