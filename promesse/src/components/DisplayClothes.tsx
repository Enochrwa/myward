import React, { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import { useAuth } from '@/hooks/useAuth';
import apiClient from '@/lib/apiClient';
import axios from 'axios';

interface ImageMetadata {
  id: string;
  filename: string;
  original_name: string;
  file_size: number;
  image_width: number;
  image_height: number;
  dominant_color: string;
  color_palette: string[];
  upload_date: string;
  batch_id?: string;
}

const DisplayClothes: React.FC = () => {
  const [images, setImages] = useState<ImageMetadata[]>([]);
  const [currentRow, setCurrentRow] = useState(0);
  const [loading, setLoading] = useState(false);
  const ROW_SIZE = 5;
  const DISPLAY_DURATION = 3000;
  const {  user} = useAuth()

  const API_BASE = 'http://localhost:8000/api';

  const fetchImages = async () => {
    setLoading(true);
    try {
        const token = localStorage.getItem("token"); // or use the exact key you stored the token with

        const allItems = await axios.get("http://127.0.0.1:8000/api/images", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
      setImages(allItems?.data?.images || []);
    } catch (error) {
      console.error('Error fetching images:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchImages();
  }, []);

  // Auto-change row every few seconds
  useEffect(() => {
    if (images.length === 0) return;

    const intervalId = setInterval(() => {
      setCurrentRow((prev) =>
        prev < Math.ceil(images.length / ROW_SIZE) - 1 ? prev + 1 : 0
      );
    }, DISPLAY_DURATION);

    return () => clearInterval(intervalId);
  }, [images]);

  const displayedImages = images.slice(
    currentRow * ROW_SIZE,
    currentRow * ROW_SIZE + ROW_SIZE
  );

  return (
    <div className="bg-gradient-to-br from-gray-900 via-slate-900 to-gray-800">
      <div className="container mx-auto px-4 py-8">
        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
          </div>
        ) : (
          <div className="overflow-hidden">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentRow}
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -50 }}
                transition={{ duration: 0.6 }}
                className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6"
              >
                { displayedImages && displayedImages.map((image) => (
                  <motion.div
                    key={image.id}
                    layout
                    className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 shadow-xl overflow-hidden hover:shadow-2xl hover:scale-[1.02] hover:border-blue-500/50 transition-all duration-300 cursor-pointer group"
                  >
                    <div className="relative aspect-square bg-gradient-to-br from-gray-800 to-gray-700">
                      <img
                        src={`http://127.0.0.1:8000/uploads/${image?.filename}`}
                        alt={image?.original_name}
                        className="w-full h-full object-contain transition-transform duration-300 group-hover:scale-105"
                        onError={(e) => {
                          e.currentTarget.src =
                            'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iIzM3NDE1MSIvPgogIDx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0iY2VudHJhbCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1mYW1pbHk9Im1vbm9zcGFjZSIgZm9udC1zaXplPSIxNHB4IiBmaWxsPSIjOWNhM2FmIj5JbWFnZSBub3QgZm91bmQ8L3RleHQ+Cjwvc3ZnPgo=';
                        }}
                      />
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
};

export default DisplayClothes;
