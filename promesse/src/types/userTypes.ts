export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  gender: string;
  role: string;
  created_at: string;
}

export interface UserProfile {
  user_id: number;
  preferred_styles?: string[];
  preferred_colors?: string[];
  avoided_colors?: string[];
  sizes?: Record<string, string>;
  updated_at?: string;
}

export interface UserProfileUpdate {
  preferred_styles?: string[];
  preferred_colors?: string[];
  avoided_colors?: string[];
  sizes?: Record<string, string>;
}
