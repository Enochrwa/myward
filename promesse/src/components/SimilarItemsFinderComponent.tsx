import React, { useState, useEffect } from 'react';
import { Search, Sparkles, Target, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import * as apiClient from '@/lib/apiClient';
import LoadingSpinner from '@/components/ui/loading';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';

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

const SimilarItemsFinderComponent: React.FC = () => {
    const [items, setItems] = useState<ImageItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [recommendations, setRecommendations] = useState<any[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedImage, setSelectedImage] = useState<ImageItem | null>(null);

    useEffect(() => {
        const fetchItems = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const response = await apiClient.getAllClothes(new URLSearchParams());
                setItems(response.images);
            } catch (err: any) {
                setError(err.message || 'Failed to fetch wardrobe items.');
            } finally {
                setIsLoading(false);
            }
        };

        fetchItems();
    }, []);

    const handleItemClick = async (item: ImageItem) => {
        setSelectedImage(item);
        setIsLoading(true);
        try {
            const similarItems = await apiClient.getSimilarItems(item.id);
            setRecommendations(similarItems.recommendations);
            setIsModalOpen(true);
        } catch (error: any) {
            setError(error.message || 'Failed to get recommendations.');
        } finally {
            setIsLoading(false);
        }
    };

    const filteredItems = items.filter(item =>
        item.original_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.category.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const formatFileName = (originalName: string) => {
        return originalName
            .replace(/\.(jpg|jpeg|png|gif)$/i, '')
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    };

    return (
        <div className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Target className="h-5 w-5" />
                        Find Similar Items
                    </CardTitle>
                    <CardDescription>
                        Select an item from your wardrobe to find similar pieces using AI-powered similarity analysis.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="relative">
                        <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-owis-charcoal/40" />
                        <Input
                            placeholder="Search your wardrobe..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="pl-10 border-owis-sage/30 focus:border-owis-sage"
                        />
                    </div>
                </CardContent>
            </Card>

            {isLoading && !selectedImage && (
                <div className="flex justify-center items-center py-12">
                    <LoadingSpinner size="lg" />
                    <p className="ml-4 text-owis-charcoal/70">Loading items...</p>
                </div>
            )}

            {!isLoading && error && (
                <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
            )}

            {!isLoading && !error && (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {filteredItems.map((item) => (
                        <Card key={item.id} className="cursor-pointer hover:shadow-lg transition-shadow duration-200" onClick={() => handleItemClick(item)}>
                            <CardContent className="p-0">
                                <img src={item.image_url} alt={item.original_name} className="w-full h-48 object-cover rounded-t-lg" />
                                <div className="p-4">
                                    <h3 className="font-semibold text-sm truncate">{formatFileName(item.original_name)}</h3>
                                    <Badge variant="secondary" className="mt-2">{item.category}</Badge>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}

            <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
                <DialogContent className="max-w-4xl">
                    <DialogHeader>
                        <DialogTitle>Similar Items to {selectedImage && formatFileName(selectedImage.original_name)}</DialogTitle>
                        <Button variant="ghost" size="icon" onClick={() => setIsModalOpen(false)} className="absolute top-4 right-4">
                            <X className="h-4 w-4" />
                        </Button>
                    </DialogHeader>
                    {isLoading && (
                        <div className="flex justify-center items-center py-12">
                            <Sparkles className="h-12 w-12 mx-auto mb-4 text-muted-foreground animate-spin" />
                            <h3 className="text-lg font-medium mb-2">Finding Similar Items</h3>
                        </div>
                    )}
                    {!isLoading && recommendations.length > 0 && (
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 p-4">
                            {recommendations.map((rec) => (
                                <Card key={rec.id} className="hover:shadow-lg transition-shadow duration-200">
                                    <CardContent className="p-0">
                                        <img src={rec.image_url} alt={rec.original_name} className="w-full h-48 object-cover rounded-t-lg" />
                                        <div className="p-4">
                                            <h3 className="font-semibold text-sm truncate">{formatFileName(rec.original_name)}</h3>
                                            <Badge variant="secondary" className="mt-2">{rec.category}</Badge>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    )}
                    {!isLoading && recommendations.length === 0 && (
                        <div className="text-center py-12">
                            <p>No similar items found.</p>
                        </div>
                    )}
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default SimilarItemsFinderComponent;

