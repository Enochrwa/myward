import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';

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

const calculateAnalytics = (items: WardrobeItem[]): WardrobeAnalytics => {
  if (!items || items.length === 0) {
    return {
      total_images: 0,
      total_size_mb: 0,
      average_dimensions: { width: 0, height: 0 },
      color_distribution: [],
      category_distribution: [],
      style_distribution: [],
      season_distribution: [],
      upload_trends: [],
    };
  }

  const total_images = items.length;
  const total_size_bytes = items.reduce((sum, item) => sum + (item.file_size || 0), 0);
  const total_size_mb = total_size_bytes / (1024 * 1024);

  const total_width = items.reduce((sum, item) => sum + (item.image_width || 0), 0);
  const total_height = items.reduce((sum, item) => sum + (item.image_height || 0), 0);
  const average_dimensions = {
    width: total_width / total_images,
    height: total_height / total_images,
  };

  const getDistribution = (field: keyof WardrobeItem) => {
    const counts = items.reduce((acc, item) => {
      const value = item[field] as string;
      if (value) {
        acc[value] = (acc[value] || 0) + 1;
      }
      return acc;
    }, {} as Record<string, number>);
    return Object.entries(counts).map(([key, value]) => ({ [field]: key, count: value }));
  };

  const color_distribution = getDistribution('dominant_color') as any;
  const category_distribution = getDistribution('category') as any;
  const style_distribution = getDistribution('style') as any;
  const season_distribution = getDistribution('season') as any;

  const upload_trends = items.reduce((acc, item) => {
    const date = new Date(item.upload_date).toISOString().split('T')[0];
    const existing = acc.find(d => d.date === date);
    if (existing) {
      existing.count++;
    } else {
      acc.push({ date, count: 1 });
    }
    return acc;
  }, [] as { date: string; count: number }[]);

  return {
    total_images,
    total_size_mb,
    average_dimensions,
    color_distribution,
    category_distribution,
    style_distribution,
    season_distribution,
    upload_trends,
  };
};

export const useWardrobeAnalytics = () => {
  const [items, setItems] = useState<WardrobeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchItems = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get("http://127.0.0.1:8000/api/images", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setItems(response?.data?.images || []);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchItems();
  }, []);

  const analytics = useMemo(() => calculateAnalytics(items), [items]);

  return { analytics, items, loading, error, setItems };
};
