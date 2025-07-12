import { Outfit } from './outfitTypes'; // Import the Outfit interface

export interface Occasion {
  id: string; // Or number, depending on backend (using string for consistency)
  name: string;
  date?: string | null; // ISO date string (e.g., "YYYY-MM-DD")
  outfit_id?: string | null; // Or number
  notes?: string | null;
  user_id?: string; // Or number
  created_at?: string; // ISO datetime string
  updated_at?: string; // ISO datetime string
  suggested_outfits?: Outfit[]; // Use the imported Outfit interface
}

export interface OccasionCreate {
  name: string;
  date?: string | null; // Should be in "YYYY-MM-DD" format if sent to backend
  outfit_id?: string | null; // Usually not set on creation unless pre-selected
  notes?: string | null;
}
