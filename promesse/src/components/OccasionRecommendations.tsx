import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { 
  Calendar as CalendarIcon,
  MapPin,
  Cloud,
  Sun,
  CloudRain,
  Snowflake,
  Wind,
  Thermometer,
  Clock,
  Users,
  Sparkles,
  TrendingUp,
  Heart,
  Star,
  ChevronRight,
  Plus,
  Settings
} from 'lucide-react';
import { format } from 'date-fns';
import { toast } from 'sonner';

interface WardrobeItem {
  id: string;
  name: string;
  category: string;
  colors: string[];
  style: string;
  brand?: string;
  price?: number;
  image_url?: string;
}

interface OutfitRecommendation {
  outfit_id?: string;
  items: WardrobeItem[];
  compatibility_score: number;
  occasion_appropriateness: number;
  weather_suitability?: number;
  formality_match?: number;
  reasons: string[];
  styling_tips?: string[];
}

interface OccasionRequest {
  occasion_type: string;
  date_time?: Date;
  location?: string;
  weather_condition?: string;
  temperature?: number;
  formality_level?: string;
  duration?: number;
  notes?: string;
  max_outfits: number;
}

interface EventPlanningRequest {
  event_name: string;
  start_date: Date;
  end_date?: Date;
  occasion_type: string;
  location?: string;
  formality_level?: string;
  special_requirements?: string[];
}

const OccasionRecommendations: React.FC = () => {
  const [activeTab, setActiveTab] = useState('occasion');
  const [occasionRequest, setOccasionRequest] = useState<OccasionRequest>({
    occasion_type: '',
    max_outfits: 3
  });
  const [eventRequest, setEventRequest] = useState<EventPlanningRequest>({
    event_name: '',
    start_date: new Date(),
    occasion_type: ''
  });
  const [recommendations, setRecommendations] = useState<OutfitRecommendation[]>([]);
  const [eventPlan, setEventPlan] = useState<Record<string, OutfitRecommendation[]>>({});
  const [loading, setLoading] = useState(false);
  const [weatherData, setWeatherData] = useState<any>(null);

  // Mock data
  const occasionTypes = [
    { value: 'work', label: 'Work', description: 'Professional workplace attire' },
    { value: 'casual', label: 'Casual', description: 'Relaxed, everyday wear' },
    { value: 'formal', label: 'Formal', description: 'Formal events and ceremonies' },
    { value: 'party', label: 'Party', description: 'Social gatherings and celebrations' },
    { value: 'date', label: 'Date', description: 'Romantic or social outings' },
    { value: 'wedding', label: 'Wedding', description: 'Wedding ceremonies and receptions' },
    { value: 'church', label: 'Church', description: 'Religious services and gatherings' },
    { value: 'interview', label: 'Interview', description: 'Job interviews and professional meetings' },
    { value: 'graduation', label: 'Graduation', description: 'Graduation ceremonies' },
    { value: 'dinner', label: 'Dinner', description: 'Dinner parties and fine dining' }
  ];

  const formalityLevels = [
    { value: 'very_casual', label: 'Very Casual' },
    { value: 'casual', label: 'Casual' },
    { value: 'smart_casual', label: 'Smart Casual' },
    { value: 'business', label: 'Business' },
    { value: 'formal', label: 'Formal' },
    { value: 'black_tie', label: 'Black Tie' }
  ];

  const weatherConditions = [
    { value: 'sunny', label: 'Sunny', icon: Sun },
    { value: 'cloudy', label: 'Cloudy', icon: Cloud },
    { value: 'rainy', label: 'Rainy', icon: CloudRain },
    { value: 'snowy', label: 'Snowy', icon: Snowflake },
    { value: 'windy', label: 'Windy', icon: Wind }
  ];

  const mockRecommendations: OutfitRecommendation[] = [
    {
      items: [
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
        }
      ],
      compatibility_score: 0.92,
      occasion_appropriateness: 0.95,
      weather_suitability: 0.88,
      formality_match: 0.90,
      reasons: [
        'Perfect for work occasions',
        'Excellent color harmony',
        'Professional style consistency'
      ],
      styling_tips: [
        'Add a leather belt to complete the look',
        'Consider a pocket square for extra sophistication',
        'Ensure clothes are well-fitted and wrinkle-free'
      ]
    },
    {
      items: [
        {
          id: '4',
          name: 'Black Dress',
          category: 'dresses',
          colors: ['#000000'],
          style: 'formal',
          brand: 'Zara',
          price: 89
        },
        {
          id: '5',
          name: 'Pearl Necklace',
          category: 'accessories',
          colors: ['#FFFFFF'],
          style: 'elegant',
          brand: 'Tiffany',
          price: 199
        }
      ],
      compatibility_score: 0.88,
      occasion_appropriateness: 0.92,
      weather_suitability: 0.85,
      formality_match: 0.95,
      reasons: [
        'Classic formal combination',
        'Timeless elegance',
        'Appropriate for evening events'
      ],
      styling_tips: [
        'Add elegant heels',
        'Consider a clutch bag',
        'Light makeup for sophistication'
      ]
    }
  ];

  const handleGetRecommendations = async () => {
    if (!occasionRequest.occasion_type) {
      toast.error('Please select an occasion type');
      return;
    }

    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      setRecommendations(mockRecommendations);
      toast.success(`Found ${mockRecommendations.length} outfit recommendations!`);
    } catch (error) {
      toast.error('Failed to get recommendations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleEventPlanning = async () => {
    if (!eventRequest.event_name || !eventRequest.occasion_type) {
      toast.error('Please fill in event name and occasion type');
      return;
    }

    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock event plan for 3 days
      const mockEventPlan = {
        'day_1_2024-01-15': mockRecommendations.slice(0, 1),
        'day_2_2024-01-16': mockRecommendations.slice(1, 2),
        'day_3_2024-01-17': mockRecommendations.slice(0, 1)
      };
      
      setEventPlan(mockEventPlan);
      toast.success('Event outfits planned successfully!');
    } catch (error) {
      toast.error('Failed to plan event outfits. Please try again.');
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

  const renderOutfitCard = (recommendation: OutfitRecommendation, index: number) => (
    <Card key={index} className="group hover:shadow-lg transition-all duration-200">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Outfit {index + 1}</CardTitle>
          <div className="flex gap-2">
            <Badge variant={getScoreBadgeVariant(recommendation.compatibility_score)}>
              {Math.round(recommendation.compatibility_score * 100)}% match
            </Badge>
            <Badge variant="outline">
              {Math.round(recommendation.occasion_appropriateness * 100)}% appropriate
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Items */}
        <div className="space-y-2">
          <h4 className="font-medium text-sm">Items:</h4>
          <div className="grid grid-cols-1 gap-2">
            {recommendation.items.map((item, itemIndex) => (
              <div key={itemIndex} className="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
                <div className="w-8 h-8 bg-gray-200 rounded flex items-center justify-center">
                  <div
                    className="w-4 h-4 rounded-full border"
                    style={{ backgroundColor: item.colors[0] }}
                  />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-sm">{item.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {item.category} • {item.brand}
                  </p>
                </div>
                <span className="text-sm font-medium">${item.price}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Scores */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span>Compatibility</span>
              <span className={getScoreColor(recommendation.compatibility_score)}>
                {Math.round(recommendation.compatibility_score * 100)}%
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span>Occasion Fit</span>
              <span className={getScoreColor(recommendation.occasion_appropriateness)}>
                {Math.round(recommendation.occasion_appropriateness * 100)}%
              </span>
            </div>
          </div>
          <div className="space-y-1">
            {recommendation.weather_suitability && (
              <div className="flex items-center justify-between text-sm">
                <span>Weather Fit</span>
                <span className={getScoreColor(recommendation.weather_suitability)}>
                  {Math.round(recommendation.weather_suitability * 100)}%
                </span>
              </div>
            )}
            {recommendation.formality_match && (
              <div className="flex items-center justify-between text-sm">
                <span>Formality</span>
                <span className={getScoreColor(recommendation.formality_match)}>
                  {Math.round(recommendation.formality_match * 100)}%
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Reasons */}
        <div className="space-y-2">
          <h4 className="font-medium text-sm">Why this works:</h4>
          <div className="space-y-1">
            {recommendation.reasons.slice(0, 3).map((reason, reasonIndex) => (
              <div key={reasonIndex} className="flex items-center gap-2 text-sm text-muted-foreground">
                <div className="w-1 h-1 bg-green-500 rounded-full" />
                {reason}
              </div>
            ))}
          </div>
        </div>

        {/* Styling Tips */}
        {recommendation.styling_tips && recommendation.styling_tips.length > 0 && (
          <div className="space-y-2">
            <h4 className="font-medium text-sm">Styling tips:</h4>
            <div className="space-y-1">
              {recommendation.styling_tips.slice(0, 2).map((tip, tipIndex) => (
                <div key={tipIndex} className="flex items-center gap-2 text-sm text-blue-600">
                  <Sparkles className="w-3 h-3" />
                  {tip}
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex gap-2 pt-2">
          <Button size="sm" variant="outline" className="flex-1">
            <Heart className="w-4 h-4 mr-2" />
            Save
          </Button>
          <Button size="sm" className="flex-1">
            <Plus className="w-4 h-4 mr-2" />
            Create Outfit
          </Button>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold flex items-center justify-center gap-2">
          <Calendar className="h-8 w-8 text-purple-600" />
          Occasion Recommendations
        </h1>
        <p className="text-muted-foreground">
          Get perfect outfit suggestions for any occasion, weather, or event
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="occasion">Occasion</TabsTrigger>
          <TabsTrigger value="weather">Weather-Aware</TabsTrigger>
          <TabsTrigger value="seasonal">Seasonal</TabsTrigger>
          <TabsTrigger value="events">Event Planning</TabsTrigger>
        </TabsList>

        <TabsContent value="occasion" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Occasion Setup */}
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Occasion Details
                </CardTitle>
                <CardDescription>
                  Tell us about your occasion
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Occasion Type</Label>
                  <Select
                    value={occasionRequest.occasion_type}
                    onValueChange={(value) => setOccasionRequest(prev => ({ ...prev, occasion_type: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select occasion" />
                    </SelectTrigger>
                    <SelectContent>
                      {occasionTypes.map((occasion) => (
                        <SelectItem key={occasion.value} value={occasion.value}>
                          <div>
                            <div className="font-medium">{occasion.label}</div>
                            <div className="text-xs text-muted-foreground">{occasion.description}</div>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Date & Time</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="outline" className="w-full justify-start text-left">
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {occasionRequest.date_time ? format(occasionRequest.date_time, 'PPP') : 'Pick a date'}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        selected={occasionRequest.date_time}
                        onSelect={(date) => setOccasionRequest(prev => ({ ...prev, date_time: date }))}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>

                <div className="space-y-2">
                  <Label>Location</Label>
                  <Input
                    placeholder="e.g., Office, Restaurant, Church"
                    value={occasionRequest.location || ''}
                    onChange={(e) => setOccasionRequest(prev => ({ ...prev, location: e.target.value }))}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Formality Level</Label>
                  <Select
                    value={occasionRequest.formality_level}
                    onValueChange={(value) => setOccasionRequest(prev => ({ ...prev, formality_level: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select formality" />
                    </SelectTrigger>
                    <SelectContent>
                      {formalityLevels.map((level) => (
                        <SelectItem key={level.value} value={level.value}>
                          {level.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Weather Condition</Label>
                  <Select
                    value={occasionRequest.weather_condition}
                    onValueChange={(value) => setOccasionRequest(prev => ({ ...prev, weather_condition: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select weather" />
                    </SelectTrigger>
                    <SelectContent>
                      {weatherConditions.map((weather) => (
                        <SelectItem key={weather.value} value={weather.value}>
                          <div className="flex items-center gap-2">
                            <weather.icon className="h-4 w-4" />
                            {weather.label}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Temperature (°C)</Label>
                  <Input
                    type="number"
                    placeholder="e.g., 20"
                    value={occasionRequest.temperature || ''}
                    onChange={(e) => setOccasionRequest(prev => ({ ...prev, temperature: Number(e.target.value) }))}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Additional Notes</Label>
                  <Textarea
                    placeholder="Any special requirements or preferences..."
                    value={occasionRequest.notes || ''}
                    onChange={(e) => setOccasionRequest(prev => ({ ...prev, notes: e.target.value }))}
                  />
                </div>

                <Button onClick={handleGetRecommendations} disabled={loading} className="w-full">
                  {loading ? 'Getting Recommendations...' : 'Get Outfit Recommendations'}
                </Button>
              </CardContent>
            </Card>

            {/* Recommendations */}
            <div className="lg:col-span-2">
              {recommendations.length === 0 ? (
                <Card className="h-full">
                  <CardContent className="flex items-center justify-center h-64">
                    <div className="text-center space-y-4">
                      <Sparkles className="h-16 w-16 mx-auto text-muted-foreground opacity-50" />
                      <div>
                        <h3 className="font-medium">No recommendations yet</h3>
                        <p className="text-sm text-muted-foreground">
                          Fill in the occasion details and click "Get Outfit Recommendations"
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h2 className="text-xl font-semibold">
                      Recommended Outfits for {occasionRequest.occasion_type}
                    </h2>
                    <Badge variant="outline">
                      {recommendations.length} suggestions
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-1 gap-4">
                    {recommendations.map((recommendation, index) => 
                      renderOutfitCard(recommendation, index)
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="weather" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Cloud className="h-5 w-5" />
                Weather-Aware Recommendations
              </CardTitle>
              <CardDescription>
                Get outfit suggestions based on current weather conditions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Thermometer className="h-16 w-16 mx-auto text-muted-foreground opacity-50 mb-4" />
                <h3 className="font-medium mb-2">Weather Integration Coming Soon</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  This feature will automatically fetch weather data and suggest appropriate outfits
                </p>
                <Button variant="outline">
                  <MapPin className="h-4 w-4 mr-2" />
                  Enable Location Access
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="seasonal" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Seasonal Recommendations
              </CardTitle>
              <CardDescription>
                Discover outfits perfect for each season
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {['Spring', 'Summer', 'Autumn', 'Winter'].map((season) => (
                  <Card key={season} className="cursor-pointer hover:shadow-md transition-shadow">
                    <CardContent className="p-4 text-center">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full mx-auto mb-3 flex items-center justify-center">
                        <Sparkles className="h-6 w-6 text-purple-600" />
                      </div>
                      <h3 className="font-medium">{season}</h3>
                      <p className="text-sm text-muted-foreground">View outfits</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="events" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Event Planning Setup */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  Event Planning
                </CardTitle>
                <CardDescription>
                  Plan outfits for multi-day events
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Event Name</Label>
                  <Input
                    placeholder="e.g., Business Conference"
                    value={eventRequest.event_name}
                    onChange={(e) => setEventRequest(prev => ({ ...prev, event_name: e.target.value }))}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Start Date</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="outline" className="w-full justify-start text-left">
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {format(eventRequest.start_date, 'PPP')}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        selected={eventRequest.start_date}
                        onSelect={(date) => date && setEventRequest(prev => ({ ...prev, start_date: date }))}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>

                <div className="space-y-2">
                  <Label>End Date (Optional)</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="outline" className="w-full justify-start text-left">
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {eventRequest.end_date ? format(eventRequest.end_date, 'PPP') : 'Select end date'}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        selected={eventRequest.end_date}
                        onSelect={(date) => setEventRequest(prev => ({ ...prev, end_date: date }))}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>

                <div className="space-y-2">
                  <Label>Occasion Type</Label>
                  <Select
                    value={eventRequest.occasion_type}
                    onValueChange={(value) => setEventRequest(prev => ({ ...prev, occasion_type: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select occasion" />
                    </SelectTrigger>
                    <SelectContent>
                      {occasionTypes.map((occasion) => (
                        <SelectItem key={occasion.value} value={occasion.value}>
                          {occasion.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Location</Label>
                  <Input
                    placeholder="e.g., Convention Center"
                    value={eventRequest.location || ''}
                    onChange={(e) => setEventRequest(prev => ({ ...prev, location: e.target.value }))}
                  />
                </div>

                <Button onClick={handleEventPlanning} disabled={loading} className="w-full">
                  {loading ? 'Planning Event...' : 'Plan Event Outfits'}
                </Button>
              </CardContent>
            </Card>

            {/* Event Plan Results */}
            <div className="lg:col-span-2">
              {Object.keys(eventPlan).length === 0 ? (
                <Card className="h-full">
                  <CardContent className="flex items-center justify-center h-64">
                    <div className="text-center space-y-4">
                      <Calendar className="h-16 w-16 mx-auto text-muted-foreground opacity-50" />
                      <div>
                        <h3 className="font-medium">No event plan yet</h3>
                        <p className="text-sm text-muted-foreground">
                          Fill in the event details and click "Plan Event Outfits"
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-4">
                  <h2 className="text-xl font-semibold">
                    Event Plan: {eventRequest.event_name}
                  </h2>
                  
                  <div className="space-y-4">
                    {Object.entries(eventPlan).map(([day, outfits]) => (
                      <Card key={day}>
                        <CardHeader>
                          <CardTitle className="text-lg">
                            {day.replace('day_', 'Day ').replace('_', ' - ')}
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="grid grid-cols-1 gap-4">
                            {outfits.map((outfit, index) => 
                              renderOutfitCard(outfit, index)
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default OccasionRecommendations;

