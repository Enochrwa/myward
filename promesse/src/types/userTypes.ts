export interface UserProfile {
  user_id: number; // Assuming user_id is returned by the backend for the UserProfile schema
  preferred_styles?: string[];
  preferred_colors?: string[];
  avoided_colors?: string[];
  sizes?: Record<string, string>; // e.g., { shirt: "M", pants_waist: "32" }
  updated_at?: string; // ISO date string
}

export interface UserProfileUpdate {
  preferred_styles?: string[];
  preferred_colors?: string[];
  avoided_colors?: string[];
  sizes?: Record<string, string>;
}

// You might also want a User type if not defined elsewhere
export interface User {
  id: number;
  username: string;
  email: string;
  // Add other user fields if necessary, e.g., from your auth context
}
