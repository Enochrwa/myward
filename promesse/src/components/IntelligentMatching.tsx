import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Sparkles, 
  Heart, 
  Star, 
  Palette, 
  Shirt, 
  Calendar,
  TrendingUp,
  Filter,
  Search,
  RefreshCw,
  Info
} from 'lucide-react';
import { toast } from 'sonner';

interface WardrobeItem {
  id: string;
  name: string;
  category: string;
  colors: string[];
  style: string;
  image_url?: string;
  brand?: string;
  price?: number;
}

interface MatchResult {
  item: WardrobeItem;
  compatibility_score: number;
  match_reasons: string[];
  recommendation_score?: number;
}

interface MatchingFilters {
  occasion?: string;
  max_results: number;
  include_user_preferences: boolean;
  style_preference?: string;
  color_preference?: string;
  price_range?: [number, number];
}

const IntelligentMatching: React.FC = () => {
  const [selectedItem, setSelectedItem] = useState<WardrobeItem | null>(null);
  const [wardrobeItems, setWardrobeItems] = useState<WardrobeItem[]>([]);
  const [matchResults, setMatchResults] = useState<MatchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<MatchingFilters>({
    max_results: 5,
    include_user_preferences: true
  });

  // Mock data for demonstration
  const mockWardrobeItems: WardrobeItem[] = [
    {
      id: '1',
      name: 'Navy Blue Blazer',
      category: 'outerwear',
      colors: ['#000080'],
      style: 'business',
      brand: 'Hugo Boss',
      price: 299
    },
    {
      id: '2',
      name: 'White Dress Shirt',
      category: 'tops',
      colors: ['#FFFFFF'],
      style: 'business',
      brand: 'Brooks Brothers',
      price: 89
    },
    {
      id: '3',
      name: 'Gray Trousers',
      category: 'bottoms',
      colors: ['#808080'],
      style: 'business',
      brand: 'Banana Republic',
      price: 129
    },
    {
      id: '4',
      name: 'Red Casual T-Shirt',
      category: 'tops',
      colors: ['#FF0000'],
      style: 'casual',
      brand: 'Uniqlo',
      price: 25
    },
    {
      id: '5',
      name: 'Black Leather Shoes',
      category: 'shoes',
      colors: ['#000000'],
      style: 'formal',
      brand: 'Cole Haan',
      price: 199
    }
  ];

  useEffect(() => {
    setWardrobeItems(mockWardrobeItems);
  }, []);

  const handleFindMatches = async () => {
    if (!selectedItem) {
      toast.error('Please select an item to find matches for');
      return;
    }

    setLoading(true);
    try {
      // Simulate API call to intelligent matching service
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock matching results with realistic scores
      const mockResults: MatchResult[] = [
        {
          item: mockWardrobeItems[1], // White Dress Shirt
          compatibility_score: 0.92,
          match_reasons: [
            'Excellent color harmony',
            'Perfect style match (business + business)',
            'Highly recommended combination'
          ],
          recommendation_score: 0.88
        },
        {
          item: mockWardrobeItems[2], // Gray Trousers
          compatibility_score: 0.87,
          match_reasons: [
            'Great color compatibility',
            'Professional style pairing',
            'Suitable for work occasions'
          ],
          recommendation_score: 0.85
        },
        {
          item: mockWardrobeItems[4], // Black Leather Shoes
          compatibility_score: 0.81,
          match_reasons: [
            'Classic color combination',
            'Formal style complement',
            'Perfect for business attire'
          ],
          recommendation_score: 0.79
        }
      ];

      setMatchResults(mockResults);
      toast.success(`Found ${mockResults.length} matching items!`);
    } catch (error) {
      toast.error('Failed to find matches. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBadgeVariant = (score: number) => {
    if (score >= 0.8) return 'default';
    if (score >= 0.6) return 'secondary';
    return 'destructive';
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold flex items-center justify-center gap-2">
          <Sparkles className="h-8 w-8 text-purple-600" />
          Intelligent Matching
        </h1>
        <p className="text-muted-foreground">
          Find perfect clothing combinations using AI-powered style analysis
        </p>
      </div>

      <Tabs defaultValue="matching" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="matching">Smart Matching</TabsTrigger>
          <TabsTrigger value="compatibility">Compatibility Check</TabsTrigger>
          <TabsTrigger value="insights">Style Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="matching" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Item Selection */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shirt className="h-5 w-5" />
                  Select Item
                </CardTitle>
                <CardDescription>
                  Choose an item to find matching pieces
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <ScrollArea className="h-64">
                  <div className="space-y-2">
                    {wardrobeItems.map((item) => (
                      <Card
                        key={item.id}
                        className={`cursor-pointer transition-all hover:shadow-md ${
                          selectedItem?.id === item.id ? 'ring-2 ring-purple-500' : ''
                        }`}
                        onClick={() => setSelectedItem(item)}
                      >
                        <CardContent className="p-3">
                          <div className="flex items-center justify-between">
                            <div>
                              <h4 className="font-medium">{item.name}</h4>
                              <p className="text-sm text-muted-foreground">
                                {item.category} • {item.style}
                              </p>
                            </div>
                            <div className="flex items-center gap-1">
                              {item.colors.map((color, index) => (
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
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Matching Filters */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Filter className="h-5 w-5" />
                  Matching Preferences
                </CardTitle>
                <CardDescription>
                  Customize your matching criteria
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Occasion</Label>
                  <Select
                    value={filters.occasion}
                    onValueChange={(value) => setFilters({ ...filters, occasion: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select occasion" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="work">Work</SelectItem>
                      <SelectItem value="casual">Casual</SelectItem>
                      <SelectItem value="formal">Formal</SelectItem>
                      <SelectItem value="party">Party</SelectItem>
                      <SelectItem value="date">Date</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Maximum Results: {filters.max_results}</Label>
                  <Slider
                    value={[filters.max_results]}
                    onValueChange={(value) => setFilters({ ...filters, max_results: value[0] })}
                    max={10}
                    min={1}
                    step={1}
                  />
                </div>

                <div className="flex items-center space-x-2">
                  <Switch
                    id="preferences"
                    checked={filters.include_user_preferences}
                    onCheckedChange={(checked) => 
                      setFilters({ ...filters, include_user_preferences: checked })
                    }
                  />
                  <Label htmlFor="preferences">Include personal preferences</Label>
                </div>

                <Separator />

                <Button 
                  onClick={handleFindMatches} 
                  disabled={!selectedItem || loading}
                  className="w-full"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Finding Matches...
                    </>
                  ) : (
                    <>
                      <Search className="h-4 w-4 mr-2" />
                      Find Matches
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Match Results */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Star className="h-5 w-5" />
                  Match Results
                </CardTitle>
                <CardDescription>
                  AI-powered clothing combinations
                </CardDescription>
              </CardHeader>
              <CardContent>
                {matchResults.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <Sparkles className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Select an item and click "Find Matches" to see recommendations</p>
                  </div>
                ) : (
                  <ScrollArea className="h-64">
                    <div className="space-y-3">
                      {matchResults.map((result, index) => (
                        <Card key={index} className="border-l-4 border-l-purple-500">
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between mb-2">
                              <div>
                                <h4 className="font-medium">{result.item.name}</h4>
                                <p className="text-sm text-muted-foreground">
                                  {result.item.category} • {result.item.style}
                                </p>
                              </div>
                              <Badge variant={getScoreBadgeVariant(result.compatibility_score)}>
                                {Math.round(result.compatibility_score * 100)}%
                              </Badge>
                            </div>
                            
                            <div className="space-y-2">
                              <div className="flex items-center gap-2">
                                <TrendingUp className="h-4 w-4 text-green-600" />
                                <span className={`text-sm font-medium ${getScoreColor(result.compatibility_score)}`}>
                                  Compatibility: {Math.round(result.compatibility_score * 100)}%
                                </span>
                              </div>
                              
                              <div className="text-xs text-muted-foreground">
                                {result.match_reasons.slice(0, 2).map((reason, i) => (
                                  <div key={i} className="flex items-center gap-1">
                                    <div className="w-1 h-1 bg-purple-500 rounded-full" />
                                    {reason}
                                  </div>
                                ))}
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </ScrollArea>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="compatibility" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5" />
                Compatibility Checker
              </CardTitle>
              <CardDescription>
                Check how well multiple items work together
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <Info className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Select multiple items to check their compatibility</p>
                <Button className="mt-4" variant="outline">
                  Select Items
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Style Insights
              </CardTitle>
              <CardDescription>
                Learn about your style patterns and preferences
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardContent className="p-4">
                    <h4 className="font-medium mb-2">Most Used Colors</h4>
                    <div className="flex gap-2">
                      <div className="w-6 h-6 bg-blue-600 rounded-full" />
                      <div className="w-6 h-6 bg-gray-600 rounded-full" />
                      <div className="w-6 h-6 bg-black rounded-full" />
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="p-4">
                    <h4 className="font-medium mb-2">Preferred Styles</h4>
                    <div className="flex gap-2">
                      <Badge>Business</Badge>
                      <Badge>Casual</Badge>
                      <Badge>Smart-Casual</Badge>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default IntelligentMatching;

