import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import * as apiClient from '@/lib/apiClient';
import LoadingSpinner from '@/components/ui/loading';

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
                const response: ApiResponse = await apiClient.getAllClothes(new URLSearchParams());
                const categorizedItems: Record<string, ImageItem[]> = {};
                
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
            <div className="w-full h-full flex items-center justify-center py-8">
                <div className="flex items-center gap-3">
                    <LoadingSpinner size="lg" />
                    <span className="text-sm text-gray-600">Loading wardrobe...</span>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="w-full h-full flex items-center justify-center py-8">
                <div className="bg-red-50 px-4 py-3 rounded-md max-w-md text-center">
                    <p className="text-red-600 text-sm">{error}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full h-full space-y-6 pb-4">
            {Object.keys(itemsByCategory).length > 0 ? (
                <>
                    {Object.entries(itemsByCategory).map(([category, items]) => (
                        <section key={category} className="space-y-3">
                            <header className="sticky top-0 bg-white/90 backdrop-blur-sm z-10 pb-2 pt-1">
                                <h2 className="text-lg font-semibold text-gray-800 capitalize">
                                    {category} <span className="text-gray-500 font-medium">({items.length})</span>
                                </h2>
                            </header>
                            
                            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
                                {items.map((item) => (
                                    <Card 
                                        key={item.id} 
                                        className="group overflow-hidden hover:shadow-md transition-all duration-200 border border-gray-200 hover:border-gray-300 flex flex-col"
                                    >
                                        <div className="relative aspect-square overflow-hidden">
                                            <img 
                                                src={item.image_url} 
                                                alt={formatFileName(item.original_name)}
                                                className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                                                loading="lazy"
                                            />
                                            
                                            <div className="absolute top-2 right-2 flex gap-1">
                                                {item.color_palette.slice(0, 3).map((color, index) => (
                                                    <div 
                                                        key={index}
                                                        className="w-3 h-3 rounded-full border border-white/50 shadow-sm"
                                                        style={{ backgroundColor: color }}
                                                        title={color}
                                                    />
                                                ))}
                                            </div>
                                        </div>
                                        
                                        <CardContent className="p-3 flex-1 flex flex-col">
                                            <h3 className="font-medium text-gray-900 text-sm line-clamp-2 mb-1">
                                                {formatFileName(item.original_name)}
                                            </h3>
                                            
                                            <div className="mt-auto space-y-2">
                                                <div className="flex flex-wrap gap-1">
                                                    <Badge 
                                                        variant="secondary" 
                                                        className="text-xs font-medium px-1.5 py-0.5 capitalize"
                                                    >
                                                        {item.category.toLowerCase()}
                                                    </Badge>
                                                    <Badge 
                                                        variant="outline" 
                                                        className="text-xs px-1.5 py-0.5 hidden sm:inline-flex"
                                                    >
                                                        {item.image_width}x{item.image_height}
                                                    </Badge>
                                                </div>
                                                
                                                <div className="text-xs text-gray-500 space-y-1 hidden md:block">
                                                    <div className="flex items-center justify-between">
                                                        <span>Size:</span>
                                                        <span className="font-medium">{formatFileSize(item.file_size)}</span>
                                                    </div>
                                                    <div className="flex items-center gap-2">
                                                        <span>Dominant:</span>
                                                        <div className="flex items-center gap-1">
                                                            <span 
                                                                className="w-3 h-3 rounded-full border border-gray-200"
                                                                style={{ backgroundColor: item.dominant_color }}
                                                            />
                                                            <span className="truncate max-w-[80px]">
                                                                {item.dominant_color}
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        </section>
                    ))}
                </>
            ) : (
                <div className="w-full h-full flex items-center justify-center py-12">
                    <div className="text-center max-w-md space-y-2">
                        <h3 className="text-lg font-medium text-gray-700">Your wardrobe is empty</h3>
                        <p className="text-sm text-gray-500">Start by uploading some clothing items to see them organized here.</p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CategorizedWardrobe;