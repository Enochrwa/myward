// Move all imports to the top
import { UserProfile, UserProfileUpdate } from '@/types/userTypes';
import { PersonalizedWardrobeSuggestions } from '@/types/recommendationTypes';
import { Feedback, FeedbackCreate } from '@/types/outfitTypes';

// Base URL from environment or fallback
const BASE_URL = 'http://localhost:8000/api';

// Helper: get auth token from localStorage
const getAuthToken = () => localStorage.getItem('token');

// Generic API client
interface RequestOptions {
  method?: string;
  headers?: Record<string, string>;
  body?: any;
}

const apiClient = async (endpoint: string, options: RequestOptions = {}) => {
  const { method = 'GET', body } = options;
  const token = getAuthToken();

  const headers: Record<string, string> = { ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  // JSON content-type when needed
  if (body && typeof body === 'object' && !(body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const config: RequestInit = {
    method,
    headers,
    body: headers['Content-Type'] === 'application/json' && body ? JSON.stringify(body) : body,
  };

  const url = `${BASE_URL}${endpoint}`;

  try {
    const res = await fetch(url, config);
    if (res.status === 204) return null;
    const data = await res.json().catch(() => null);
    if (!res.ok) {
      const msg = data?.detail || data?.message || data?.error || res.statusText;
      throw new Error(msg);
    }
    return data;
  } catch (err: any) {
    console.error('API Client Error:', err.message);
    throw err;
  }
};

export default apiClient;

// Types
export interface WardrobeItemData {
  name?: string;
  brand?: string;
  category?: string;
  size?: string;
  price?: number;
  material?: string;
  season?: string;
  image_url?: string | null;
  tags?: string[];
  color?: string;
  notes?: string;
  favorite?: boolean;
}

// Wardrobe Item Types
export interface WardrobeItemData {
    name?: string;
    brand?: string;
    category?: string;
    size?: string;
    price?: number;
    material?: string;
    season?: string;
    image_url?: string | null;
    tags?: string[];
    color?: string;
    notes?: string;
    favorite?: boolean;
    // Fields from the model that might not be in create/update but are in responses
    id?: number;
    user_id?: number;
    times_worn?: number;
    last_worn?: string;
    purchase_date?: string;
    formality_level?: number;
}

export interface WardrobeItemCreate extends WardrobeItemData {}
export interface WardrobeItemUpdate extends WardrobeItemData {}
export interface WardrobeItemResponse extends WardrobeItemData {
    id: number;
    user_id: number;
}

// Category Types
export interface ClothingCategoryCreate {
    name: string;
    description?: string;
}
export interface ClothingCategoryResponse extends ClothingCategoryCreate {
    id: number;
}

// Attribute Types
export interface ClothingAttributeCreate {
    attribute_type: string;
    value: string;
}
export interface ClothingAttributeResponse extends ClothingAttributeCreate {
    id: number;
}


// Wardrobe API Functions

// CREATE
export const createWardrobeItemWithImage = (formData: FormData): Promise<WardrobeItemResponse> => {
    return apiClient('/wardrobe/', { method: 'POST', body: formData });
};

export const createWardrobeItem = (item: WardrobeItemCreate, imageFile?: File): Promise<WardrobeItemResponse> => {
    const formData = new FormData();
    Object.entries(item).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
            if (Array.isArray(value)) {
                value.forEach(v => formData.append(key, v));
            } else {
                formData.append(key, String(value));
            }
        }
    });

    if (imageFile) {
        formData.append('file', imageFile);
    }

    return createWardrobeItemWithImage(formData);
};

// READ ALL
export const getAllItems = (params: URLSearchParams = new URLSearchParams()): Promise<WardrobeItemResponse[]> =>
    apiClient(`/wardrobe/?${params.toString()}`);


export const getAllClothes = (params: URLSearchParams = new URLSearchParams()): Promise<WardrobeItemResponse[]> =>
    apiClient(`/images`);


// READ ONE
export const getItem = (itemId: number): Promise<WardrobeItemResponse> =>
    apiClient(`/wardrobe/wardrobe-items/${itemId}`);

// UPDATE
export const updateItem = (itemId: number, updateData: WardrobeItemUpdate): Promise<WardrobeItemResponse> =>
    apiClient(`/wardrobe/wardrobe-items/${itemId}`, { method: 'PUT', body: updateData });

// DELETE
export const deleteItem = (itemId: number): Promise<{ message: string }> =>
    apiClient(`/wardrobe/wardrobe-items/${itemId}`, { method: 'DELETE' });

// Toggle Favorite
export const toggleFavorite = (itemId: number): Promise<{ favorite: boolean }> =>
    apiClient(`/wardrobe/wardrobe-items/${itemId}/favorite`, { method: 'POST' });

// Mark as Worn
export const markAsWorn = (itemId: number): Promise<{ times_worn: number; last_worn: string }> =>
    apiClient(`/wardrobe/wardrobe-items/${itemId}/worn`, { method: 'POST' });

// Upload Image
export const uploadItemImage = (itemId: number, file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient(`/wardrobe/wardrobe-items/${itemId}/upload-image`, { method: 'POST', body: formData });
};

// Bulk Delete
export const bulkDeleteItems = (itemIds: number[]): Promise<{ deleted_count: number }> =>
    apiClient('/wardrobe/wardrobe-items/bulk-delete', { method: 'DELETE', body: { item_ids: itemIds } });

// Bulk Update
export const bulkUpdateItems = (itemIds: number[], updates: Partial<WardrobeItemUpdate>): Promise<{ updated_count: number }> =>
    apiClient('/wardrobe/wardrobe-items/bulk-update', { method: 'POST', body: { item_ids: itemIds, updates } });


// Category Routes
export const createCategory = (category: ClothingCategoryCreate): Promise<ClothingCategoryResponse> =>
    apiClient('/wardrobe/categories/', { method: 'POST', body: category });

export const getCategories = (skip: number = 0, limit: number = 100): Promise<ClothingCategoryResponse[]> =>
    apiClient(`/wardrobe/categories/?skip=${skip}&limit=${limit}`);

// Attribute Routes
export const createAttribute = (attribute: ClothingAttributeCreate): Promise<ClothingAttributeResponse> =>
    apiClient('/wardrobe/attributes/', { method: 'POST', body: attribute });

export const getAttributes = (type?: string, skip: number = 0, limit: number = 100): Promise<ClothingAttributeResponse[]> => {
    const params = new URLSearchParams();
    if (type) params.append('attribute_type', type);
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    return apiClient(`/wardrobe/attributes/?${params.toString()}`);
};


// Other Wardrobe-related operations from the Python file

// Create Item Classification
export const createItemClassification = (itemId: number, classificationData: any): Promise<any> =>
    apiClient(`/wardrobe/wardrobe-items/${itemId}/classifications`, { method: 'POST', body: classificationData });

// Create Color Analysis
export const createColorAnalysis = (itemId: number, analysisData: any): Promise<any> =>
    apiClient(`/wardrobe/wardrobe-items/${itemId}/color-analysis`, { method: 'POST', body: analysisData });

// Export Wardrobe
export const exportWardrobe = (format: 'json' | 'csv' = 'json'): Promise<any> =>
    apiClient(`/wardrobe/export/wardrobe?format=${format}`);


// User profile
export const getUserProfile = (): Promise<UserProfile> => apiClient('/profile/me');
export const updateUserProfile = (profileData: UserProfileUpdate): Promise<UserProfile> =>
  apiClient('/profile/me', { method: 'PUT', body: profileData });

// Recommendations
export const getWardrobeSuggestions = (
  latitude?: number,
  longitude?: number
): Promise<PersonalizedWardrobeSuggestions> => {
  const params = new URLSearchParams();
  if (latitude != null) params.append('lat', latitude.toString());
  if (longitude != null) params.append('lon', longitude.toString());
  const query = params.toString();
  return apiClient(`/recommendations/wardrobe/${query ? `?${query}` : ''}`);
};

// Feedback
export const getFeedbackForOutfit = (id: string | number): Promise<Feedback[]> =>
  apiClient(`/community/outfits/${id}/feedback`);

export const addFeedbackToOutfit = (
  id: string | number,
  feedbackData: FeedbackCreate
): Promise<Feedback> => apiClient(`/community/outfits/${id}/feedback`, { method: 'POST', body: feedbackData });

export const deleteFeedback = (feedbackId: number) =>
  apiClient(`/community/feedback/${feedbackId}`, { method: 'DELETE' });

// ML Features API endpoints

export interface ClassificationResult {
  predicted_category: string;
  confidence_score: number;
  detailed_predictions: Record<string, number>;
  model_name: string;
}

export interface ColorAnalysisResult {
  dominant_color_rgb: number[];
  dominant_color_hex: string;
  dominant_color_name: string;
  color_properties: Record<string, string>;
}

export interface ColorPaletteResult {
  palette: Array<{
    rgb: number[];
    hex: string;
    name: string;
    properties: Record<string, string>;
  }>;
  dominant_color: any;
  harmony_analysis: Record<string, string>;
  color_count: number;
}

export interface UserPreferences {
  preferred_colors?: string[];
  avoided_colors?: string[];
  preferred_styles?: string[];
  preferred_brands?: string[];
  size_preferences?: Record<string, string>;
  budget_range?: [number, number];
}

export interface RecommendationRequest {
  user_preferences?: UserPreferences;
  occasion?: string;
  num_recommendations?: number;
  weather_conditions?: Record<string, any>;
  color_scheme?: string;
}

export interface OutfitRecommendation {
  id?: number;
  name?: string;
  items: Array<{
    id: number;
    name: string;
    category: string;
    brand?: string;
    dominant_color_name?: string;
    image_url?: string;
    similarity_score?: number;
  }>;
  score: number;
  color_score?: number;
  style_score?: number;
  occasion_score?: number;
  recommendation_reason?: string;
}

export interface SimilarItem {
  id: number;
  name: string;
  category: string;
  brand?: string;
  dominant_color_name?: string;
  image_url?: string;
  similarity_score: number;
  similarity_reasons?: string[];
}

// ML API functions

/**
 * Classify a clothing item image using MobileNetV2
 */
export const classifyClothingImage = async (imageFile: File): Promise<ClassificationResult> => {
  const formData = new FormData();
  formData.append('file', imageFile);
  
  return apiClient('/ml/classify-clothing', {
    method: 'POST',
    body: formData
  });
};

/**
 * Detect dominant color from a clothing item image
 */
export const detectDominantColor = async (imageFile: File): Promise<ColorAnalysisResult> => {
  const formData = new FormData();
  formData.append('file', imageFile);
  
  return apiClient('/ml/detect-dominant-color', {
    method: 'POST',
    body: formData
  });
};

/**
 * Extract color palette from a clothing item image
 */
export const extractColorPalette = async (
  imageFile: File, 
  colorCount: number = 5
): Promise<ColorPaletteResult> => {
  const formData = new FormData();
  formData.append('file', imageFile);
  
  return apiClient(`/ml/extract-color-palette?color_count=${colorCount}`, {
    method: 'POST',
    body: formData
  });
};

/**
 * Get outfit recommendations based on user preferences and occasion
 */
export const getOutfitRecommendations = async (
  request: RecommendationRequest
): Promise<OutfitRecommendation[]> => {
  return apiClient('/ml/outfit-recommendations', {
    method: 'POST',
    body: request
  });
};

/**
 * Get items similar to a target item
 */
export const getSimilarItems = async (
  targetItemId: string
): Promise<any[]> => {
  return apiClient(`/recommend/similar/${targetItemId}`, {
    method: 'GET'
  });
};

export const saveOutfit = async (
  outfitData: any
): Promise<any> => {
  return apiClient('/outfit/custom', {
    method: 'POST',
    body: outfitData
  });
};

export const getUserOutfits = async (
    userId: string
): Promise<any> => {
    return apiClient(`/outfit/user/${userId}`, {
        method: 'GET'
    });
};

export const deleteOutfit = async (
    outfitId: string
): Promise<any> => {
    return apiClient(`/outfit/${outfitId}`, {
        method: 'DELETE'
    });
};

export const recommendOutfit = async (
  imageId: number
): Promise<any> => {
  return apiClient(`/outfit/recommend/${imageId}`, {
    method: 'GET'
  });
};

export const updateCategory = (imageId: string, newCategory: string): Promise<{ message: string }> =>
    apiClient('/update-category', { method: 'POST', body: { image_id: imageId, new_category: newCategory } });


/**
 * Train the recommendation model with user's wardrobe
 */
export const trainRecommendationModel = async (): Promise<{
  status: string;
  message: string;
}> => {
  return apiClient('/ml/train-recommendation-model', {
    method: 'POST'
  });
};

/**
 * Enhanced add item function with ML processing
 */
export const addItemWithML = async (
  itemData: WardrobeItemData, 
  imageFile?: File
): Promise<any> => {
  const form = new FormData();
  form.append('item', new Blob([JSON.stringify(itemData)], { type: 'application/json' }));
  if (imageFile) {
    form.append('image', imageFile);
  }
  
  // First add the item normally
  const result = await apiClient('/wardrobe/items/', { method: 'POST', body: form });
  
  // If image was provided, process ML features
  if (imageFile && result?.id) {
    try {
      // Run classification and color detection in parallel
      const [classificationResult, colorResult] = await Promise.allSettled([
        classifyClothingImage(imageFile),
        detectDominantColor(imageFile)
      ]);
      
      // Update the item with ML results
      const mlData: Partial<WardrobeItemData> = {};
      
      if (classificationResult.status === 'fulfilled') {
        // Update category if classification is confident enough
        if (classificationResult.value.confidence_score > 0.7) {
          mlData.category = classificationResult.value.predicted_category;
        }
      }
      
      if (colorResult.status === 'fulfilled') {
        // Add color information to tags or notes
        const colorName = colorResult.value.dominant_color_name;
        mlData.tags = [...(itemData.tags || []), colorName];
      }
      
      // Update the item if we have ML data
      if (Object.keys(mlData).length > 0) {
        await updateItem(result.id.toString(), mlData);
      }
      
    } catch (error) {
      console.warn('ML processing failed, but item was added successfully:', error);
    }
  }
  
  return result;
};

/**
 * Get color suggestions for coordinating with an item
 */
export const getColorSuggestions = async (dominantColorRgb: number[]): Promise<{
  complementary: Array<{ rgb: number[]; hex: string; name: string; }>;
  analogous: Array<{ rgb: number[]; hex: string; name: string; }>;
  neutrals: Array<{ rgb: number[]; hex: string; name: string; }>;
}> => {
  // This would be implemented as a separate endpoint or computed client-side
  // For now, return a placeholder
  return {
    complementary: [],
    analogous: [],
    neutrals: []
  };
};

/**
 * Get smart outfit suggestions for a specific occasion
 */
export const getSmartOutfitSuggestions = async (
  occasion: string,
  weatherConditions?: Record<string, any>,
  userPreferences?: UserPreferences
): Promise<OutfitRecommendation[]> => {
  const request: RecommendationRequest = {
    occasion,
    weather_conditions: weatherConditions,
    user_preferences: userPreferences,
    num_recommendations: 5
  };
  
  return getOutfitRecommendations(request);
};

/**
 * Analyze wardrobe and get insights
 */
export const getWardrobeInsights = async (): Promise<{
  color_distribution: Record<string, number>;
  category_distribution: Record<string, number>;
  style_analysis: Record<string, any>;
  recommendations: string[];
}> => {
  // This would be a new endpoint that analyzes the user's entire wardrobe
  // For now, return a placeholder
  return {
    color_distribution: {},
    category_distribution: {},
    style_analysis: {},
    recommendations: []
  };
};

