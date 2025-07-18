import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import * as apiClient from '@/lib/apiClient';
import LoadingSpinner from '@/components/ui/loading';

// Define the actual data structure based on your API response
interface ImageItem {
    id: string;
    batch_id: string;
    category: string;
    color_palette: string[];
    created_at: string;
    dominant_color: string;
    file_size: number;
    filename: string;
    image_height: number;
    image_url: string;
    image_width: number;
    original_name: string;
    upload_date: string;
}

interface ApiResponse {
    images: ImageItem[];
}

const CategorizedWardrobe = () => {
    const [itemsByCategory, setItemsByCategory] = useState<Record<string, ImageItem[]>>({});
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchItems = async () => {
            setIsLoading(true);
            setError(null);
            try {
                // Assuming your API returns the structure you showed
                const response: ApiResponse = await apiClient.getAllClothes(new URLSearchParams());
                const categorizedItems: Record<string, ImageItem[]> = {};
                
                // Access the images array from the response
                const allItems = response.images || [];
                
                for (const item of allItems) {
                    const category = item.category || 'Uncategorized';
                    if (!categorizedItems[category]) {
                        categorizedItems[category] = [];
                    }
                    categorizedItems[category].push(item);
                }
                
                setItemsByCategory(categorizedItems);
            } catch (err: any) {
                setError(err.message || 'Failed to fetch wardrobe items.');
            } finally {
                setIsLoading(false);
            }
        };

        fetchItems();
    }, []);

    const formatFileName = (originalName: string) => {
        // Remove file extension and replace underscores with spaces, then capitalize
        return originalName
            .replace(/\.(jpg|jpeg|png|gif)$/i, '')
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    };

    const formatFileSize = (bytes: number) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    if (isLoading) {
        return (
            <div className="flex justify-center items-center py-6 md:py-12">
                <LoadingSpinner size="lg" />
                <p className="ml-4 text-owis-charcoal/70 text-sm md:text-base">Loading wardrobe...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-6 md:py-12 bg-red-50 p-4 md:p-6 rounded-lg">
                <p className="text-red-600 text-sm md:text-base">{error}</p>
            </div>
        );
    }

    return (
        <div className="w-full space-y-4 md:space-y-6">
            {Object.keys(itemsByCategory).length > 0 ? (
                Object.entries(itemsByCategory).map(([category, items]) => (
                    <div key={category} className="w-full">
                        <h2 className="text-lg md:text-xl lg:text-2xl font-bold text-owis-charcoal mb-3 md:mb-4 capitalize">
                            {category} ({items.length})
                        </h2>
                        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-2 sm:gap-3 md:gap-4">
                            {items.map((item) => (
                                <Card key={item.id} className="overflow-hidden hover:shadow-lg transition-shadow duration-200 border-owis-sage/20">
                                    <CardContent className="p-2 sm:p-3 md:p-4">
                                        <div className="space-y-2 sm:space-y-3">
                                            <div className="relative">
                                                <img 
                                                    src={item.image_url} 
                                                    alt={formatFileName(item.original_name)}
                                                    className="w-full h-32 sm:h-40 md:h-48 object-cover rounded-md"
                                                />
                                                {/* Color palette indicator */}
                                                <div className="absolute top-1 right-1 sm:top-2 sm:right-2 flex gap-1">
                                                    {item.color_palette.slice(0, 3).map((color, index) => (
                                                        <div 
                                                            key={index}
                                                            className="w-2 h-2 sm:w-3 sm:h-3 rounded-full border border-white/50"
                                                            style={{ backgroundColor: color }}
                                                            title={color}
                                                        />
                                                    ))}
                                                </div>
                                            </div>
                                            <div className="space-y-1 sm:space-y-2">
                                                <h3 className="font-semibold text-owis-charcoal text-xs sm:text-sm line-clamp-2">
                                                    {formatFileName(item.original_name)}
                                                </h3>
                                                <div className="flex flex-wrap gap-1">
                                                    <Badge variant="secondary" className="text-[10px] sm:text-xs px-1 py-0">
                                                        {item.category}
                                                    </Badge>
                                                    <Badge variant="outline" className="text-[10px] sm:text-xs px-1 py-0 hidden sm:inline-flex">
                                                        {item.image_width}x{item.image_height}
                                                    </Badge>
                                                </div>
                                                <div className="text-[10px] sm:text-xs text-gray-500 space-y-1 hidden md:block">
                                                    <p>Size: {formatFileSize(item.file_size)}</p>
                                                    <p className="flex items-center">
                                                        <span className="truncate">Dominant:</span>
                                                        <span 
                                                            className="inline-block w-2 h-2 sm:w-3 sm:h-3 rounded-full ml-1 border border-gray-300 flex-shrink-0"
                                                            style={{ backgroundColor: item.dominant_color }}
                                                            title={item.dominant_color}
                                                        />
                                                        <span className="ml-1 text-[9px] sm:text-[10px] truncate">{item.dominant_color}</span>
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    </div>
                ))
            ) : (
                <div className="text-center py-8 md:py-12">
                    <p className="text-sm md:text-base">Your wardrobe is empty. Start by adding some items!</p>
                </div>
            )}
        </div>
    );
};

export default CategorizedWardrobe;