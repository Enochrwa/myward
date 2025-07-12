import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Checkbox } from '@/components/ui/checkbox';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { 
  Search, 
  Filter, 
  SlidersHorizontal,
  Grid,
  List,
  Star,
  Heart,
  ShoppingBag,
  Palette,
  Calendar,
  DollarSign,
  Tag,
  TrendingUp,
  X,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { toast } from 'sonner';

interface WardrobeItem {
  id: string;
  name: string;
  category: string;
  colors: string[];
  style: string;
  brand?: string;
  price?: number;
  season?: string;
  image_url?: string;
  created_at: string;
}

interface SearchFilters {
  colors?: string[];
  styles?: string[];
  categories?: string[];
  occasions?: string[];
  price_min?: number;
  price_max?: number;
  brands?: string[];
  seasons?: string[];
}

interface SearchRequest {
  query?: string;
  filters?: SearchFilters;
  sort_by: 'name' | 'date_added' | 'price' | 'category' | 'compatibility';
  sort_desc: boolean;
  page: number;
  page_size: number;
}

interface SearchResult {
  item: WardrobeItem;
  compatibility_score?: number;
  match_reasons?: string[];
  recommendation_score?: number;
}

interface SearchResponse {
  results: SearchResult[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
}

const AdvancedSearch: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchRequest, setSearchRequest] = useState<SearchRequest>({
    sort_by: 'name',
    sort_desc: false,
    page: 1,
    page_size: 12
  });
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showFilters, setShowFilters] = useState(false);
  const [availableFilters, setAvailableFilters] = useState<any>({});
  const [activeFilters, setActiveFilters] = useState<SearchFilters>({});
  const [suggestions, setSuggestions] = useState<string[]>([]);

  // Mock data for demonstration
  const mockSearchResults: SearchResponse = {
    results: [
      {
        item: {
          id: '1',
          name: 'Navy Blue Blazer',
          category: 'outerwear',
          colors: ['#000080'],
          style: 'business',
          brand: 'Hugo Boss',
          price: 299,
          season: 'all',
          created_at: '2024-01-15T10:00:00Z'
        },
        compatibility_score: 0.92
      },
      {
        item: {
          id: '2',
          name: 'White Dress Shirt',
          category: 'tops',
          colors: ['#FFFFFF'],
          style: 'business',
          brand: 'Brooks Brothers',
          price: 89,
          season: 'all',
          created_at: '2024-01-10T14:30:00Z'
        },
        compatibility_score: 0.88
      },
      {
        item: {
          id: '3',
          name: 'Casual Denim Jeans',
          category: 'bottoms',
          colors: ['#4169E1'],
          style: 'casual',
          brand: 'Levi\'s',
          price: 79,
          season: 'all',
          created_at: '2024-01-05T09:15:00Z'
        },
        compatibility_score: 0.75
      },
      {
        item: {
          id: '4',
          name: 'Summer Floral Dress',
          category: 'dresses',
          colors: ['#FFB6C1', '#90EE90'],
          style: 'casual',
          brand: 'Zara',
          price: 59,
          season: 'summer',
          created_at: '2024-01-20T16:45:00Z'
        },
        compatibility_score: 0.82
      }
    ],
    total_count: 4,
    page: 1,
    page_size: 12,
    total_pages: 1
  };

  const mockAvailableFilters = {
    categories: ['tops', 'bottoms', 'outerwear', 'dresses', 'shoes', 'accessories'],
    brands: ['Hugo Boss', 'Brooks Brothers', 'Levi\'s', 'Zara', 'Nike', 'Adidas'],
    seasons: ['spring', 'summer', 'autumn', 'winter', 'all'],
    styles: ['casual', 'formal', 'business', 'sporty', 'elegant', 'trendy'],
    occasions: ['work', 'casual', 'formal', 'party', 'date', 'wedding'],
    price_range: { min: 0, max: 500 }
  };

  useEffect(() => {
    setAvailableFilters(mockAvailableFilters);
  }, []);

  const handleSearch = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSearchResults(mockSearchResults);
      toast.success(`Found ${mockSearchResults.total_count} items`);
    } catch (error) {
      toast.error('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (filterType: keyof SearchFilters, value: any) => {
    setActiveFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const clearFilters = () => {
    setActiveFilters({});
  };

  const getActiveFilterCount = () => {
    return Object.values(activeFilters).filter(value => 
      Array.isArray(value) ? value.length > 0 : value !== undefined
    ).length;
  };

  const handleSuggestionSearch = async (query: string) => {
    if (query.length > 2) {
      // Mock suggestions
      const mockSuggestions = [
        'Blue shirt',
        'Blue blazer',
        'Blue jeans',
        'Business attire',
        'Casual wear'
      ].filter(s => s.toLowerCase().includes(query.toLowerCase()));
      setSuggestions(mockSuggestions);
    } else {
      setSuggestions([]);
    }
  };

  const renderGridView = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {searchResults?.results.map((result) => (
        <Card key={result.item.id} className="group hover:shadow-lg transition-all duration-200">
          <CardContent className="p-4">
            <div className="aspect-square bg-gray-100 rounded-lg mb-3 flex items-center justify-center">
              <ShoppingBag className="h-12 w-12 text-gray-400" />
            </div>
            
            <div className="space-y-2">
              <h3 className="font-medium line-clamp-2">{result.item.name}</h3>
              
              <div className="flex items-center justify-between">
                <Badge variant="secondary">{result.item.category}</Badge>
                {result.compatibility_score && (
                  <Badge variant="default">
                    {Math.round(result.compatibility_score * 100)}%
                  </Badge>
                )}
              </div>
              
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <span>{result.item.brand}</span>
                <span>${result.item.price}</span>
              </div>
              
              <div className="flex items-center gap-1">
                {result.item.colors.map((color, index) => (
                  <div
                    key={index}
                    className="w-4 h-4 rounded-full border"
                    style={{ backgroundColor: color }}
                  />
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );

  const renderListView = () => (
    <div className="space-y-3">
      {searchResults?.results.map((result) => (
        <Card key={result.item.id} className="hover:shadow-md transition-shadow">
          <CardContent className="p-4">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center">
                <ShoppingBag className="h-8 w-8 text-gray-400" />
              </div>
              
              <div className="flex-1 space-y-1">
                <h3 className="font-medium">{result.item.name}</h3>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <span>{result.item.category}</span>
                  <span>•</span>
                  <span>{result.item.style}</span>
                  <span>•</span>
                  <span>{result.item.brand}</span>
                </div>
                <div className="flex items-center gap-2">
                  {result.item.colors.map((color, index) => (
                    <div
                      key={index}
                      className="w-3 h-3 rounded-full border"
                      style={{ backgroundColor: color }}
                    />
                  ))}
                </div>
              </div>
              
              <div className="text-right space-y-1">
                <div className="font-medium">${result.item.price}</div>
                {result.compatibility_score && (
                  <Badge variant="default">
                    {Math.round(result.compatibility_score * 100)}% match
                  </Badge>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold flex items-center justify-center gap-2">
          <Search className="h-8 w-8 text-blue-600" />
          Advanced Search
        </h1>
        <p className="text-muted-foreground">
          Find exactly what you're looking for with intelligent filters
        </p>
      </div>

      {/* Search Bar */}
      <Card>
        <CardContent className="p-4">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search your wardrobe..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  handleSuggestionSearch(e.target.value);
                }}
                className="pl-10"
              />
              
              {/* Search Suggestions */}
              {suggestions.length > 0 && (
                <Card className="absolute top-full left-0 right-0 z-10 mt-1">
                  <CardContent className="p-2">
                    {suggestions.map((suggestion, index) => (
                      <div
                        key={index}
                        className="px-3 py-2 hover:bg-gray-100 cursor-pointer rounded"
                        onClick={() => {
                          setSearchQuery(suggestion);
                          setSuggestions([]);
                        }}
                      >
                        {suggestion}
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}
            </div>
            
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
              className="relative"
            >
              <Filter className="h-4 w-4 mr-2" />
              Filters
              {getActiveFilterCount() > 0 && (
                <Badge className="ml-2 h-5 w-5 p-0 text-xs">
                  {getActiveFilterCount()}
                </Badge>
              )}
            </Button>
            
            <Button onClick={handleSearch} disabled={loading}>
              {loading ? 'Searching...' : 'Search'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Filters Panel */}
      {showFilters && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <SlidersHorizontal className="h-5 w-5" />
                Search Filters
              </CardTitle>
              <Button variant="ghost" size="sm" onClick={clearFilters}>
                Clear All
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="basic" className="w-full">
              <TabsList>
                <TabsTrigger value="basic">Basic</TabsTrigger>
                <TabsTrigger value="style">Style</TabsTrigger>
                <TabsTrigger value="price">Price & Brand</TabsTrigger>
              </TabsList>
              
              <TabsContent value="basic" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label>Categories</Label>
                    <div className="space-y-2">
                      {availableFilters.categories?.map((category: string) => (
                        <div key={category} className="flex items-center space-x-2">
                          <Checkbox
                            id={category}
                            checked={activeFilters.categories?.includes(category)}
                            onCheckedChange={(checked) => {
                              const current = activeFilters.categories || [];
                              if (checked) {
                                handleFilterChange('categories', [...current, category]);
                              } else {
                                handleFilterChange('categories', current.filter(c => c !== category));
                              }
                            }}
                          />
                          <Label htmlFor={category} className="capitalize">
                            {category}
                          </Label>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label>Seasons</Label>
                    <div className="space-y-2">
                      {availableFilters.seasons?.map((season: string) => (
                        <div key={season} className="flex items-center space-x-2">
                          <Checkbox
                            id={season}
                            checked={activeFilters.seasons?.includes(season)}
                            onCheckedChange={(checked) => {
                              const current = activeFilters.seasons || [];
                              if (checked) {
                                handleFilterChange('seasons', [...current, season]);
                              } else {
                                handleFilterChange('seasons', current.filter(s => s !== season));
                              }
                            }}
                          />
                          <Label htmlFor={season} className="capitalize">
                            {season}
                          </Label>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label>Occasions</Label>
                    <div className="space-y-2">
                      {availableFilters.occasions?.map((occasion: string) => (
                        <div key={occasion} className="flex items-center space-x-2">
                          <Checkbox
                            id={occasion}
                            checked={activeFilters.occasions?.includes(occasion)}
                            onCheckedChange={(checked) => {
                              const current = activeFilters.occasions || [];
                              if (checked) {
                                handleFilterChange('occasions', [...current, occasion]);
                              } else {
                                handleFilterChange('occasions', current.filter(o => o !== occasion));
                              }
                            }}
                          />
                          <Label htmlFor={occasion} className="capitalize">
                            {occasion}
                          </Label>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </TabsContent>
              
              <TabsContent value="style" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Styles</Label>
                    <div className="space-y-2">
                      {availableFilters.styles?.map((style: string) => (
                        <div key={style} className="flex items-center space-x-2">
                          <Checkbox
                            id={style}
                            checked={activeFilters.styles?.includes(style)}
                            onCheckedChange={(checked) => {
                              const current = activeFilters.styles || [];
                              if (checked) {
                                handleFilterChange('styles', [...current, style]);
                              } else {
                                handleFilterChange('styles', current.filter(s => s !== style));
                              }
                            }}
                          />
                          <Label htmlFor={style} className="capitalize">
                            {style}
                          </Label>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </TabsContent>
              
              <TabsContent value="price" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-4">
                    <Label>Price Range</Label>
                    <div className="space-y-2">
                      <div className="flex gap-2">
                        <Input
                          type="number"
                          placeholder="Min"
                          value={activeFilters.price_min || ''}
                          onChange={(e) => handleFilterChange('price_min', Number(e.target.value))}
                        />
                        <Input
                          type="number"
                          placeholder="Max"
                          value={activeFilters.price_max || ''}
                          onChange={(e) => handleFilterChange('price_max', Number(e.target.value))}
                        />
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label>Brands</Label>
                    <div className="space-y-2 max-h-32 overflow-y-auto">
                      {availableFilters.brands?.map((brand: string) => (
                        <div key={brand} className="flex items-center space-x-2">
                          <Checkbox
                            id={brand}
                            checked={activeFilters.brands?.includes(brand)}
                            onCheckedChange={(checked) => {
                              const current = activeFilters.brands || [];
                              if (checked) {
                                handleFilterChange('brands', [...current, brand]);
                              } else {
                                handleFilterChange('brands', current.filter(b => b !== brand));
                              }
                            }}
                          />
                          <Label htmlFor={brand}>
                            {brand}
                          </Label>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}

      {/* Results Header */}
      {searchResults && (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-semibold">
              {searchResults.total_count} items found
            </h2>
            
            <Select
              value={searchRequest.sort_by}
              onValueChange={(value) => setSearchRequest(prev => ({ ...prev, sort_by: value as any }))}
            >
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="name">Name</SelectItem>
                <SelectItem value="date_added">Date Added</SelectItem>
                <SelectItem value="price">Price</SelectItem>
                <SelectItem value="category">Category</SelectItem>
                <SelectItem value="compatibility">Compatibility</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant={viewMode === 'grid' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('grid')}
            >
              <Grid className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('list')}
            >
              <List className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      {/* Search Results */}
      {searchResults && (
        <div>
          {viewMode === 'grid' ? renderGridView() : renderListView()}
          
          {/* Pagination */}
          {searchResults.total_pages > 1 && (
            <div className="flex justify-center mt-6">
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  disabled={searchResults.page === 1}
                  onClick={() => setSearchRequest(prev => ({ ...prev, page: prev.page - 1 }))}
                >
                  Previous
                </Button>
                <span className="text-sm text-muted-foreground">
                  Page {searchResults.page} of {searchResults.total_pages}
                </span>
                <Button
                  variant="outline"
                  disabled={searchResults.page === searchResults.total_pages}
                  onClick={() => setSearchRequest(prev => ({ ...prev, page: prev.page + 1 }))}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AdvancedSearch;

