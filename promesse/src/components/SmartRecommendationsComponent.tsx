import React, { useState, useEffect } from 'react';
import { Sparkles, Heart, Shuffle, Calendar, Cloud, Thermometer } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  getOutfitRecommendations, 
  getSmartOutfitSuggestions,
  trainRecommendationModel,
  OutfitRecommendation,
  UserPreferences,
  RecommendationRequest
} from '@/lib/apiClient';

interface SmartRecommendationsProps {
  onOutfitSelect?: (outfit: OutfitRecommendation) => void;
  userPreferences?: UserPreferences;
}

const SmartRecommendationsComponent: React.FC<SmartRecommendationsProps> = ({ 
  onOutfitSelect, 
  userPreferences: initialPreferences 
}) => {
  const [recommendations, setRecommendations] = useState<OutfitRecommendation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedOccasion, setSelectedOccasion] = useState('casual');
  const [preferences, setPreferences] = useState<UserPreferences>(initialPreferences || {});
  const [weatherConditions, setWeatherConditions] = useState({
    temperature: 20,
    weather_type: 'sunny',
    season: 'spring'
  });
  const [isTrainingModel, setIsTrainingModel] = useState(false);
  const [modelTrained, setModelTrained] = useState(false);

  const occasions = [
    { value: 'casual', label: 'Casual Day Out', icon: '👕' },
    { value: 'work', label: 'Work/Office', icon: '💼' },
    { value: 'formal', label: 'Formal Event', icon: '🤵' },
    { value: 'date', label: 'Date Night', icon: '💕' },
    { value: 'wedding', label: 'Wedding Guest', icon: '💒' },
    { value: 'church', label: 'Church Service', icon: '⛪' },
    { value: 'party', label: 'Party/Social', icon: '🎉' },
    { value: 'athletic', label: 'Workout/Sports', icon: '🏃' },
    { value: 'home', label: 'Home/Loungewear', icon: '🏠' },
    { value: 'travel', label: 'Travel', icon: '✈️' }
  ];

  const weatherTypes = [
    { value: 'sunny', label: 'Sunny', icon: '☀️' },
    { value: 'cloudy', label: 'Cloudy', icon: '☁️' },
    { value: 'rainy', label: 'Rainy', icon: '🌧️' },
    { value: 'snowy', label: 'Snowy', icon: '❄️' },
    { value: 'windy', label: 'Windy', icon: '💨' }
  ];

  const seasons = [
    { value: 'spring', label: 'Spring' },
    { value: 'summer', label: 'Summer' },
    { value: 'fall', label: 'Fall' },
    { value: 'winter', label: 'Winter' }
  ];

  const handleTrainModel = async () => {
    setIsTrainingModel(true);
    try {
      const result = await trainRecommendationModel();
      if (result.status === 'success') {
        setModelTrained(true);
      }
    } catch (err: any) {
      console.warn('Model training failed:', err);
    } finally {
      setIsTrainingModel(false);
    }
  };

  const generateRecommendations = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const request: RecommendationRequest = {
        occasion: selectedOccasion,
        user_preferences: preferences,
        weather_conditions: weatherConditions,
        num_recommendations: 5
      };
      
      const results = await getOutfitRecommendations(request);
      setRecommendations(results);
    } catch (err: any) {
      setError(err.message || 'Failed to generate recommendations');
    } finally {
      setIsLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBadgeVariant = (score: number): "default" | "secondary" | "destructive" | "outline" => {
    if (score >= 0.8) return 'default';
    if (score >= 0.6) return 'secondary';
    return 'outline';
  };

  const renderOutfitCard = (outfit: OutfitRecommendation, index: number) => (
    <Card key={index} className="cursor-pointer hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">
            {outfit.name || `Outfit ${index + 1}`}
          </CardTitle>
          <Badge variant={getScoreBadgeVariant(outfit.score)}>
            {(outfit.score * 100).toFixed(0)}% Match
          </Badge>
        </div>
        {outfit.recommendation_reason && (
          <CardDescription>{outfit.recommendation_reason}</CardDescription>
        )}
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Outfit Items */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {outfit.items.map((item, itemIndex) => (
            <div key={itemIndex} className="text-center">
              {item.image_url ? (
                <img 
                  src={item.image_url} 
                  alt={item.name}
                  className="w-full h-20 object-cover rounded-md mb-2"
                />
              ) : (
                <div className="w-full h-20 bg-muted rounded-md mb-2 flex items-center justify-center">
                  <span className="text-xs text-muted-foreground">No Image</span>
                </div>
              )}
              <div className="text-xs font-medium truncate">{item.name}</div>
              <div className="text-xs text-muted-foreground">{item.category}</div>
              {item.dominant_color_name && (
                <Badge variant="outline" className="text-xs mt-1">
                  {item.dominant_color_name}
                </Badge>
              )}
            </div>
          ))}
        </div>
        
        {/* Score Breakdown */}
        {(outfit.color_score || outfit.style_score || outfit.occasion_score) && (
          <div className="space-y-2">
            <div className="text-sm font-medium">Score Breakdown:</div>
            <div className="grid grid-cols-3 gap-2 text-xs">
              {outfit.color_score && (
                <div className="text-center">
                  <div className="text-muted-foreground">Color</div>
                  <div className={getScoreColor(outfit.color_score)}>
                    {(outfit.color_score * 100).toFixed(0)}%
                  </div>
                </div>
              )}
              {outfit.style_score && (
                <div className="text-center">
                  <div className="text-muted-foreground">Style</div>
                  <div className={getScoreColor(outfit.style_score)}>
                    {(outfit.style_score * 100).toFixed(0)}%
                  </div>
                </div>
              )}
              {outfit.occasion_score && (
                <div className="text-center">
                  <div className="text-muted-foreground">Occasion</div>
                  <div className={getScoreColor(outfit.occasion_score)}>
                    {(outfit.occasion_score * 100).toFixed(0)}%
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
        
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            className="flex-1"
            onClick={() => onOutfitSelect?.(outfit)}
          >
            <Heart className="h-4 w-4 mr-1" />
            Select
          </Button>
          <Button variant="outline" size="sm">
            <Shuffle className="h-4 w-4" />
          </Button>
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
            <Sparkles className="h-5 w-5" />
            Smart Outfit Recommendations
          </CardTitle>
          <CardDescription>
            Get AI-powered outfit suggestions based on occasion, weather, and your personal style preferences.
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Model Training */}
      {!modelTrained && (
        <Alert>
          <Sparkles className="h-4 w-4" />
          <AlertDescription className="flex items-center justify-between">
            <span>Train the AI model with your wardrobe for better recommendations.</span>
            <Button 
              size="sm" 
              onClick={handleTrainModel}
              disabled={isTrainingModel}
            >
              {isTrainingModel ? 'Training...' : 'Train Model'}
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Recommendation Settings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Occasion Selection */}
          <div className="space-y-2">
            <Label>Occasion</Label>
            <Select value={selectedOccasion} onValueChange={setSelectedOccasion}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {occasions.map((occasion) => (
                  <SelectItem key={occasion.value} value={occasion.value}>
                    <span className="flex items-center gap-2">
                      <span>{occasion.icon}</span>
                      {occasion.label}
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Weather Conditions */}
          <div className="space-y-4">
            <Label className="flex items-center gap-2">
              <Cloud className="h-4 w-4" />
              Weather Conditions
            </Label>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label className="text-sm">Temperature: {weatherConditions.temperature}°C</Label>
                <Slider
                  value={[weatherConditions.temperature]}
                  onValueChange={([value]) => 
                    setWeatherConditions(prev => ({ ...prev, temperature: value }))
                  }
                  min={-10}
                  max={40}
                  step={1}
                  className="w-full"
                />
              </div>
              
              <div className="space-y-2">
                <Label className="text-sm">Weather Type</Label>
                <Select 
                  value={weatherConditions.weather_type} 
                  onValueChange={(value) => 
                    setWeatherConditions(prev => ({ ...prev, weather_type: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {weatherTypes.map((weather) => (
                      <SelectItem key={weather.value} value={weather.value}>
                        <span className="flex items-center gap-2">
                          <span>{weather.icon}</span>
                          {weather.label}
                        </span>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label className="text-sm">Season</Label>
                <Select 
                  value={weatherConditions.season} 
                  onValueChange={(value) => 
                    setWeatherConditions(prev => ({ ...prev, season: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {seasons.map((season) => (
                      <SelectItem key={season.value} value={season.value}>
                        {season.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Generate Button */}
          <Button 
            onClick={generateRecommendations} 
            disabled={isLoading}
            className="w-full"
          >
            {isLoading ? (
              <>
                <Sparkles className="h-4 w-4 mr-2 animate-spin" />
                Generating Recommendations...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4 mr-2" />
                Generate Smart Recommendations
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Recommended Outfits</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommendations.map((outfit, index) => renderOutfitCard(outfit, index))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && recommendations.length === 0 && !error && (
        <Card>
          <CardContent className="text-center py-8">
            <Calendar className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-medium mb-2">No Recommendations Yet</h3>
            <p className="text-muted-foreground mb-4">
              Configure your preferences and generate smart outfit recommendations.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SmartRecommendationsComponent;

