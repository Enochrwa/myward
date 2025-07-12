import React, { useState, useEffect } from 'react';
import { Search, Filter, Sparkles, Palette, Target, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { getSimilarItems, SimilarItem } from '@/lib/apiClient';

interface SimilarItemsFinderProps {
  targetItemId?: number;
  onItemSelect?: (item: SimilarItem) => void;
  wardrobeItems?: Array<{
    id: number;
    name: string;
    category: string;
    brand?: string;
    image_url?: string;
    dominant_color_name?: string;
  }>;
}

const SimilarItemsFinderComponent: React.FC<SimilarItemsFinderProps> = ({
  targetItemId: initialTargetId,
  onItemSelect,
  wardrobeItems = []
}) => {
  const [targetItemId, setTargetItemId] = useState<number | null>(initialTargetId || null);
  const [similarItems, setSimilarItems] = useState<SimilarItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [numSimilar, setNumSimilar] = useState(5);

  // Get unique categories from wardrobe items
  const categories = ['all', ...new Set(wardrobeItems.map(item => item.category))];

  // Filter wardrobe items based on search and category
  const filteredWardrobeItems = wardrobeItems.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (item.brand && item.brand.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesCategory = categoryFilter === 'all' || item.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  const findSimilarItems = async (itemId: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const results = await getSimilarItems(itemId, numSimilar);
      setSimilarItems(results);
    } catch (err: any) {
      setError(err.message || 'Failed to find similar items');
      setSimilarItems([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleItemSelection = (itemId: number) => {
    setTargetItemId(itemId);
    findSimilarItems(itemId);
  };

  const getTargetItem = () => {
    return wardrobeItems.find(item => item.id === targetItemId);
  };

  const getSimilarityColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSimilarityBadgeVariant = (score: number): "default" | "secondary" | "destructive" | "outline" => {
    if (score >= 0.8) return 'default';
    if (score >= 0.6) return 'secondary';
    return 'outline';
  };

  const renderWardrobeItemCard = (item: typeof wardrobeItems[0]) => (
    <Card 
      key={item.id} 
      className={`cursor-pointer transition-all hover:shadow-md ${
        targetItemId === item.id ? 'ring-2 ring-primary' : ''
      }`}
      onClick={() => handleItemSelection(item.id)}
    >
      <CardContent className="p-4">
        <div className="space-y-3">
          {item.image_url ? (
            <img 
              src={item.image_url} 
              alt={item.name}
              className="w-full h-32 object-cover rounded-md"
            />
          ) : (
            <div className="w-full h-32 bg-muted rounded-md flex items-center justify-center">
              <span className="text-sm text-muted-foreground">No Image</span>
            </div>
          )}
          
          <div className="space-y-1">
            <h4 className="font-medium text-sm truncate">{item.name}</h4>
            <p className="text-xs text-muted-foreground">{item.category}</p>
            {item.brand && (
              <p className="text-xs text-muted-foreground">{item.brand}</p>
            )}
            {item.dominant_color_name && (
              <Badge variant="outline" className="text-xs">
                {item.dominant_color_name}
              </Badge>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderSimilarItemCard = (item: SimilarItem) => (
    <Card 
      key={item.id} 
      className="cursor-pointer hover:shadow-md transition-shadow"
      onClick={() => onItemSelect?.(item)}
    >
      <CardContent className="p-4">
        <div className="space-y-3">
          {item.image_url ? (
            <img 
              src={item.image_url} 
              alt={item.name}
              className="w-full h-32 object-cover rounded-md"
            />
          ) : (
            <div className="w-full h-32 bg-muted rounded-md flex items-center justify-center">
              <span className="text-sm text-muted-foreground">No Image</span>
            </div>
          )}
          
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-sm truncate">{item.name}</h4>
              <Badge variant={getSimilarityBadgeVariant(item.similarity_score)}>
                {(item.similarity_score * 100).toFixed(0)}%
              </Badge>
            </div>
            
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground">{item.category}</p>
              {item.brand && (
                <p className="text-xs text-muted-foreground">{item.brand}</p>
              )}
              {item.dominant_color_name && (
                <Badge variant="outline" className="text-xs">
                  {item.dominant_color_name}
                </Badge>
              )}
            </div>
            
            {item.similarity_reasons && item.similarity_reasons.length > 0 && (
              <div className="space-y-1">
                <p className="text-xs font-medium">Similar because:</p>
                <div className="flex flex-wrap gap-1">
                  {item.similarity_reasons.slice(0, 2).map((reason, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {reason}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Find Similar Items
          </CardTitle>
          <CardDescription>
            Discover items in your wardrobe that are similar to a selected piece using AI-powered similarity analysis.
          </CardDescription>
        </CardHeader>
      </Card>

      <Tabs defaultValue="select" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="select">Select Target Item</TabsTrigger>
          <TabsTrigger value="results" disabled={!targetItemId}>
            Similar Items {similarItems.length > 0 && `(${similarItems.length})`}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="select" className="space-y-4">
          {/* Search and Filter */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Choose a Target Item</CardTitle>
              <CardDescription>
                Select an item from your wardrobe to find similar pieces.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search items..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full"
                  />
                </div>
                <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                  <SelectTrigger className="w-48">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((category) => (
                      <SelectItem key={category} value={category}>
                        {category === 'all' ? 'All Categories' : category}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="flex items-center gap-4">
                <label className="text-sm font-medium">Number of similar items:</label>
                <Select value={numSimilar.toString()} onValueChange={(value) => setNumSimilar(parseInt(value))}>
                  <SelectTrigger className="w-24">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {[3, 5, 8, 10].map((num) => (
                      <SelectItem key={num} value={num.toString()}>
                        {num}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Wardrobe Items Grid */}
          {filteredWardrobeItems.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {filteredWardrobeItems.map(renderWardrobeItemCard)}
            </div>
          ) : (
            <Card>
              <CardContent className="text-center py-8">
                <Search className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-medium mb-2">No Items Found</h3>
                <p className="text-muted-foreground">
                  {searchTerm || categoryFilter !== 'all' 
                    ? 'Try adjusting your search or filter criteria.'
                    : 'Add some items to your wardrobe to get started.'
                  }
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="results" className="space-y-4">
          {/* Target Item Display */}
          {targetItemId && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Target Item</CardTitle>
                <CardDescription>
                  Finding items similar to this piece from your wardrobe.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {(() => {
                  const targetItem = getTargetItem();
                  if (!targetItem) return null;
                  
                  return (
                    <div className="flex items-center gap-4">
                      {targetItem.image_url ? (
                        <img 
                          src={targetItem.image_url} 
                          alt={targetItem.name}
                          className="w-20 h-20 object-cover rounded-md"
                        />
                      ) : (
                        <div className="w-20 h-20 bg-muted rounded-md flex items-center justify-center">
                          <span className="text-xs text-muted-foreground">No Image</span>
                        </div>
                      )}
                      <div className="space-y-1">
                        <h4 className="font-medium">{targetItem.name}</h4>
                        <p className="text-sm text-muted-foreground">{targetItem.category}</p>
                        {targetItem.brand && (
                          <p className="text-sm text-muted-foreground">{targetItem.brand}</p>
                        )}
                        {targetItem.dominant_color_name && (
                          <Badge variant="outline">
                            {targetItem.dominant_color_name}
                          </Badge>
                        )}
                      </div>
                    </div>
                  );
                })()}
              </CardContent>
            </Card>
          )}

          {/* Loading State */}
          {isLoading && (
            <Card>
              <CardContent className="text-center py-8">
                <Sparkles className="h-12 w-12 mx-auto mb-4 text-muted-foreground animate-spin" />
                <h3 className="text-lg font-medium mb-2">Finding Similar Items</h3>
                <p className="text-muted-foreground">
                  Analyzing your wardrobe for similar pieces...
                </p>
              </CardContent>
            </Card>
          )}

          {/* Error Display */}
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Similar Items Results */}
          {!isLoading && similarItems.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Similar Items Found</h3>
                <Badge variant="outline">
                  {similarItems.length} items
                </Badge>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {similarItems.map(renderSimilarItemCard)}
              </div>
            </div>
          )}

          {/* No Results */}
          {!isLoading && !error && similarItems.length === 0 && targetItemId && (
            <Card>
              <CardContent className="text-center py-8">
                <TrendingUp className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-medium mb-2">No Similar Items Found</h3>
                <p className="text-muted-foreground mb-4">
                  We couldn't find any items similar to your selected piece.
                </p>
                <Button 
                  variant="outline" 
                  onClick={() => findSimilarItems(targetItemId)}
                >
                  <Sparkles className="h-4 w-4 mr-2" />
                  Try Again
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SimilarItemsFinderComponent;

