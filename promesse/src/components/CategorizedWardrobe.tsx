import React, { useState, useEffect } from 'react';
import namer from 'color-namer';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import * as apiClient from '@/lib/apiClient';
import axios from 'axios';
import LoadingSpinner from '@/components/ui/loading';
import { DndContext, useDraggable, useDroppable } from '@dnd-kit/core';


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

// API now returns direct array of ImageItem
type ApiResponse = ImageItem[];

const DraggableImage = ({ image, children }: { image: ImageItem; children: React.ReactNode }) => {
    const { attributes, listeners, setNodeRef, transform } = useDraggable({
        id: image.id,
        data: { image },
    });
    const style = transform ? {
        transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
    } : undefined;

    return (
        <div ref={setNodeRef} style={style} {...listeners} {...attributes}>
            {children}
        </div>
    );
};

const DroppableCategory = ({ category, children }: { category: string; children: React.ReactNode }) => {
    const { isOver, setNodeRef } = useDroppable({
        id: category,
    });

    return (
        <div ref={setNodeRef} className={`p-4 rounded-lg ${isOver ? 'bg-owis-mint' : 'bg-transparent'}`}>
            {children}
        </div>
    );
};

const CategorizedWardrobe = () => {
    const [itemsByCategory, setItemsByCategory] = useState<Record<string, ImageItem[]>>({});
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [clotheId, setClotheId] = useState<string>("")

    const navigate = useNavigate();



    useEffect(() => {
        const fetchItems = async () => {
            setIsLoading(true);
            setError(null);
            try {
                // API returns direct array of items
                const allItems: ApiResponse = await apiClient.getAllClothes(new URLSearchParams());
                const categorizedItems: Record<string, ImageItem[]> = {};
            
                
                for (const item of allItems?.images) {
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

    const getColorName = (hex: string) => {
        try {
            const result = namer(hex);
            return result.basic[0].name; // or 'pantone', 'html', etc.
        } catch (error) {
            return 'Unknown';
        }
    };

    const formatFileSize = (bytes: number) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const handleDragEnd = (event: any) => {
        const { active, over } = event;
        if (!over) return;

        const image = active.data.current.image;
        const oldCategory = image.category || 'Uncategorized';
        const newCategory = over.id;

        if (oldCategory === newCategory) return;

        // Optimistic UI update
        setItemsByCategory(prev => {
            const newItems = { ...prev };
            // Remove from old category
            newItems[oldCategory] = newItems[oldCategory].filter(item => item.id !== image.id);
            if (newItems[oldCategory].length === 0) {
                delete newItems[oldCategory];
            }
            // Add to new category
            if (!newItems[newCategory]) {
                newItems[newCategory] = [];
            }
            newItems[newCategory].push({ ...image, category: newCategory });
            return newItems;
        });

        // API call to update backend
        apiClient.updateCategory(image.id, newCategory).catch(() => {
            // Revert on failure
            setItemsByCategory(prev => {
                const newItems = { ...prev };
                // Remove from new category
                newItems[newCategory] = newItems[newCategory].filter(item => item.id !== image.id);
                if (newItems[newCategory].length === 0) {
                    delete newItems[newCategory];
                }
                // Add back to old category
                if (!newItems[oldCategory]) {
                    newItems[oldCategory] = [];
                }
                newItems[oldCategory].push(image);
                return newItems;
            });
            // Optionally show an error toast
        });
    };

    if (isLoading) {
        return (
            <div className="w-full h-full grid place-items-center py-6 md:py-12">
                <div className="grid grid-flow-col gap-4 items-center">
                    <LoadingSpinner size="lg" />
                    <p className="text-owis-charcoal/70 text-sm md:text-base">Loading wardrobe...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="w-full h-full grid place-items-center py-6 md:py-12">
                <div className="bg-red-50 p-4 md:p-6 rounded-lg">
                    <p className="text-red-600 text-sm md:text-base text-center">{error}</p>
                </div>
            </div>
        );
    }

    return (
        <DndContext onDragEnd={handleDragEnd}>
            <div className="w-full h-full grid grid-rows-[auto_1fr] gap-4 md:gap-6">
                {Object.keys(itemsByCategory).length > 0 ? (
                    <div className="grid gap-4 md:gap-6 auto-rows-max">
                        {Object.entries(itemsByCategory).map(([category, items]) => (
                            <DroppableCategory key={category} category={category}>
                                <h2 className="text-lg md:text-xl lg:text-2xl font-bold text-owis-charcoal capitalize">
                                    {category} ({items.length})
                                </h2>
                                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-2 sm:gap-3 md:gap-4 auto-rows-fr">
                                    {items.map((item) => (
                                        <DraggableImage key={item.id} image={item}>
                                            <Card className="overflow-hidden hover:shadow-lg transition-shadow duration-200 border-owis-sage/20 grid grid-rows-[1fr_auto]">
                                                <div className="grid">
                                                    <div className="relative" onDoubleClick={() => navigate(`/outfit-builder/${item?.id}`)}>
                                                        <img
                                                            src={item.image_url}
                                                            alt={formatFileName(item.original_name)}
                                                            className="w-full h-32 sm:h-40 md:h-48 object-cover rounded-md"
                                                        />
                                                        {/* Color palette indicator */}
                                                        <div className="absolute top-1 right-1 sm:top-2 sm:right-2 grid grid-cols-3 gap-1">
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
                                                </div>
                                                <CardContent className="p-2 sm:p-3 md:p-4 grid gap-1 sm:gap-2">
                                                    <h3 className="font-semibold text-owis-charcoal text-xs sm:text-sm line-clamp-2">
                                                        {formatFileName(item.original_name)}
                                                    </h3>
                                                    <div className="grid grid-flow-col gap-1 justify-start">
                                                        <Badge variant="secondary" className="text-[10px] sm:text-xs px-1 py-0 justify-self-start">
                                                            {item.category}
                                                        </Badge>
                                                        <Badge variant="outline" className="text-[10px] sm:text-xs px-1 py-0 justify-self-start hidden sm:inline-flex">
                                                            {item.image_width}x{item.image_height}
                                                        </Badge>
                                                    </div>
                                                    <div className="text-[10px] sm:text-xs text-gray-500 grid gap-1 hidden md:grid">
                                                        <p>Size: {formatFileSize(item.file_size)}</p>
                                                        <div className="grid grid-cols-[auto_auto_1fr] gap-1 items-center">
                                                            <span className="truncate">Dominant:</span>
                                                            <span
                                                                className="w-2 h-2 sm:w-3 sm:h-3 rounded-full border border-gray-300"
                                                                style={{ backgroundColor: item.dominant_color }}
                                                                title={item.dominant_color}
                                                            />
                                                            <div className="grid gap-0">
                                                                <span className="text-[9px] sm:text-[10px] truncate">{item.dominant_color}</span>
                                                                <span className="text-[9px] sm:text-[10px] truncate">{getColorName(item.dominant_color)}</span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </CardContent>
                                            </Card>
                                        </DraggableImage>
                                    ))}
                                </div>
                            </DroppableCategory>
                        ))}
                    </div>
                ) : (
                    <div className="grid place-items-center py-8 md:py-12">
                        <p className="text-sm md:text-base">Your wardrobe is empty. Start by adding some items!</p>
                    </div>
                )}
            </div>
        </DndContext>
    );
};

export default CategorizedWardrobe;