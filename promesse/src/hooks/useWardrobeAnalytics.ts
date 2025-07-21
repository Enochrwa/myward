import { useState, useEffect } from 'react';

const API_BASE = 'http://127.0.0.1:8000/api';

interface WardrobeAnalytics {
  total_images: number;
  total_size_mb: number;
  average_dimensions: {
    width: number;
    height: number;
  };
  color_distribution: { color: string; count: number }[];
  category_distribution: { category: string; count: number }[];
  style_distribution: { style: string; count: number }[];
  season_distribution: { season: string; count: number }[];
  upload_trends: { date: string; count: number }[];
}

interface WardrobeItem {
  id: string;
  filename: string;
  original_name: string;
  file_size: number;
  image_width: number;
  image_height: number;
  dominant_color: string;
  color_palette: string[];
  upload_date: string;
  category: string;
  style: string;
  season: string;
  image_url: string;
}

export const useWardrobeAnalytics = () => {
  const [analytics, setAnalytics] = useState<WardrobeAnalytics | null>(null);
  const [items, setItems] = useState<WardrobeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await fetch(`${API_BASE}/analytics`);
        if (!response.ok) {
          throw new Error('Failed to fetch analytics data');
        }
        const data = await response.json();
        setAnalytics(data);
      } catch (err) {
        setError(err.message);
      }
    };

    const fetchItems = async () => {
      try {
        const response = await fetch(`${API_BASE}/images?limit=1000`); // Fetch a large number of items
        if (!response.ok) {
          throw new Error('Failed to fetch wardrobe items');
        }
        const data = await response.json();
        setItems(data.images || []);
      } catch (err) {
        setError(err.message);
      }
    };

    const fetchAllData = async () => {
      setLoading(true);
      await Promise.all([fetchAnalytics(), fetchItems()]);
      setLoading(false);
    };

    fetchAllData();
  }, []);

  return { analytics, items, loading, error };
};
