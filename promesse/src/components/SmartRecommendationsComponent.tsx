import React, { useState, useEffect, useCallback } from 'react';
import { Sparkles, Shuffle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import * as apiClient from '@/lib/apiClient';
import LoadingSpinner from '@/components/ui/loading';
import { Outfit } from '@/types/outfitTypes';

const SmartRecommendationsComponent: React.FC = () => {
  const [outfit, setOutfit] = useState<Outfit | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [wardrobeItems, setWardrobeItems] = useState<apiClient.WardrobeItemResponse[]>([]);

  const fetchWardrobeItems = useCallback(async () => {
    try {
      const items = await apiClient.getAllItems(new URLSearchParams());
      setWardrobeItems(items || []);
    } catch (err: any) {
      setError('Failed to fetch wardrobe items.');
    }
  }, []);

  useEffect(() => {
    fetchWardrobeItems();
  }, [fetchWardrobeItems]);

  const generateOutfit = useCallback(async () => {
    if (wardrobeItems.length === 0) {
      setError('You need to add items to your wardrobe first.');
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const randomItem = wardrobeItems[Math.floor(Math.random() * wardrobeItems.length)];
      const recommendedOutfit = await apiClient.recommendOutfit(randomItem.id);
      setOutfit(recommendedOutfit);
    } catch (err: any) {
      setError(err.message || 'Failed to generate outfit.');
    } finally {
      setIsLoading(false);
    }
  }, [wardrobeItems]);

  const renderOutfit = () => {
    if (!outfit) return null;

    const outfitCategories = {
      outerwear: [] as any[],
      tops: [] as any[],
      bottoms: [] as any[],
      footwear: [] as any[],
      accessories: [] as any[],
    };

    for (const key in outfit) {
      const item = outfit[key as keyof Outfit];
      if (item && typeof item === 'object' && 'category' in item) {
        const category = item.category?.toLowerCase();
        if (category?.includes('coat') || category?.includes('jacket') || category?.includes('blazer') || category?.includes('cardigan')) {
          outfitCategories.outerwear.push(item);
        } else if (category?.includes('t-shirt') || category?.includes('blouse') || category?.includes('top') || category?.includes('shirt')) {
          outfitCategories.tops.push(item);
        } else if (category?.includes('pants') || category?.includes('jeans') || category?.includes('skirt') || category?.includes('shorts')) {
          outfitCategories.bottoms.push(item);
        } else if (category?.includes('shoes') || category?.includes('boots') || category?.includes('sneakers') || category?.includes('sandals')) {
          outfitCategories.footwear.push(item);
        } else {
          outfitCategories.accessories.push(item);
        }
      }
    }

    return (
      <Card>
        <CardHeader>
          <CardTitle>Your Smart Outfit</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {Object.entries(outfitCategories).map(([category, items]) => (
            items.length > 0 && (
              <div key={category}>
                <h4 className="text-lg font-semibold mb-2 capitalize">{category}</h4>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {items.map((item: any) => (
                    <Card key={item.id}>
                      <CardContent className="p-0">
                        <img src={item.image_url} alt={item.name} className="w-full h-48 object-cover rounded-t-lg" />
                        <div className="p-4">
                          <h5 className="font-semibold">{item.name}</h5>
                          <p className="text-sm text-gray-500">{item.category}</p>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )
          ))}
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5" />
            Smart Outfit Recommendations
          </CardTitle>
          <CardDescription>
            Let our AI create a stylish outfit from your wardrobe.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={generateOutfit} disabled={isLoading || wardrobeItems.length === 0}>
            <Shuffle className="mr-2 h-4 w-4" />
            {isLoading ? 'Generating...' : 'Generate New Outfit'}
          </Button>
        </CardContent>
      </Card>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {isLoading && (
        <div className="flex justify-center py-8">
          <LoadingSpinner />
        </div>
      )}

      {!isLoading && !error && outfit && renderOutfit()}
    </div>
  );
};

export default SmartRecommendationsComponent;
