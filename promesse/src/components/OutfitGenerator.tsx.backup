
import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Calendar, Cloud, Heart, Church, Home, Users, Star, MapPin, Sparkles, Compass, Zap, AlertTriangle } from 'lucide-react';
import { Checkbox } from '@/components/ui/checkbox'; // For "Use current location"
import { Input } from '@/components/ui/input'; // For manual lat/lon
import { Label } from '@/components/ui/label'; // For form elements
import { useToast } from '@/components/ui/use-toast';
import useGeolocation from '@/hooks/useGeolocation';
import * as apiClient from '@/lib/apiClient';
import { PersonalizedWardrobeSuggestions } from '@/types/recommendationTypes';
import LoadingSpinner from './ui/loading'; // Assuming a loading spinner component

const OutfitGenerator = () => {
  const [selectedOccasion, setSelectedOccasion] = useState('work'); // This might be used to influence recommendations later
  
  // Geolocation states
  const { coordinates: geoCoordinates, error: geoError, isLoading: geoIsLoading, getLocation } = useGeolocation();
  const [useCurrentLocation, setUseCurrentLocation] = useState(false);
  const [manualLatitude, setManualLatitude] = useState('');
  const [manualLongitude, setManualLongitude] = useState('');

  // Recommendation states
  const [recommendations, setRecommendations] = useState<PersonalizedWardrobeSuggestions | null>(null);
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false);
  const [recommendationError, setRecommendationError] = useState<string | null>(null);

  const { toast } = useToast();

  const occasions = [
    { id: 'work', label: 'Work Meeting', icon: '💼', color: 'from-blue-500 to-blue-600' },
    { id: 'casual', label: 'Casual Day', icon: '👕', color: 'from-green-500 to-green-600' },
    { id: 'formal', label: 'Formal Event', icon: '👔', color: 'from-purple-500 to-purple-600' },
    { id: 'weekend', label: 'Weekend Out', icon: '🌟', color: 'from-orange-500 to-orange-600' },
    { id: 'wedding', label: 'Wedding', icon: '💒', color: 'from-pink-500 to-rose-500' },
    { id: 'church', label: 'Church', icon: '⛪', color: 'from-indigo-500 to-indigo-600' },
    { id: 'home', label: 'Home Comfort', icon: '🏠', color: 'from-emerald-500 to-emerald-600' },
    { id: 'date', label: 'Date Night', icon: '💕', color: 'from-red-500 to-red-600' }
  ];

  const outfitSuggestions = {
    work: {
      items: ['Navy Blazer', 'White Silk Blouse', 'Charcoal Trousers', 'Black Leather Loafers'],
      confidence: 94,
      sustainability: 'High',
      weather: 'Perfect for 72°F partly cloudy',
      image: 'https://images.unsplash.com/photo-1551803091-e20673f05c05?w=300'
    },
    casual: {
      items: ['Denim Jacket', 'Striped T-Shirt', 'Dark Jeans', 'White Sneakers'],
      confidence: 87,
      sustainability: 'Medium',
      weather: 'Great for sunny weather',
      image: 'https://images.unsplash.com/photo-1581044777550-4cfa60707c03?w=300'
    },
    formal: {
      items: ['Black Suit', 'Crisp White Shirt', 'Silk Tie', 'Oxford Shoes'],
      confidence: 96,
      sustainability: 'High',
      weather: 'Indoor event ready',
      image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300'
    },
    weekend: {
      items: ['Cashmere Sweater', 'High-waisted Jeans', 'Ankle Boots', 'Crossbody Bag'],
      confidence: 91,
      sustainability: 'High',
      weather: 'Comfortable for all day',
      image: 'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=300'
    },
    wedding: {
      items: ['Elegant Midi Dress', 'Pearl Necklace', 'Block Heels', 'Small Clutch'],
      confidence: 93,
      sustainability: 'High',
      weather: 'Perfect for outdoor ceremony',
      image: 'https://images.unsplash.com/photo-1566479179817-a71bf3ce2e85?w=300'
    },
    church: {
      items: ['Modest Blouse', 'Knee-length Skirt', 'Light Cardigan', 'Low Heels'],
      confidence: 89,
      sustainability: 'High',
      weather: 'Respectful and comfortable',
      image: 'https://images.unsplash.com/photo-1544966503-7ba37778b4d7?w=300'
    },
    home: {
      items: ['Soft Loungewear', 'Cozy Slippers', 'Hair Scrunchie', 'Warm Socks'],
      confidence: 95,
      sustainability: 'Medium',
      weather: 'Maximum comfort at home',
      image: 'https://images.unsplash.com/photo-1571513722275-4b41940f54b8?w=300'
    },
    date: {
      items: ['Silk Dress', 'Statement Earrings', 'Heeled Sandals', 'Evening Bag'],
      confidence: 92,
      sustainability: 'High',
      weather: 'Perfect for romantic evening',
      image: 'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=300'
    }
  };

  // const currentOutfit = outfitSuggestions[selectedOccasion as keyof typeof outfitSuggestions]; // Mock data removed

  useEffect(() => {
    if (geoError) {
      toast({ title: "Geolocation Error", description: geoError, variant: "destructive" });
    }
    if (geoCoordinates) {
      toast({ title: "Location Fetched", description: `Lat: ${geoCoordinates.lat.toFixed(2)}, Lon: ${geoCoordinates.lon.toFixed(2)}` });
    }
  }, [geoCoordinates, geoError, toast]);

  const handleGenerateOutfit = async () => {
    setIsLoadingRecommendations(true);
    setRecommendationError(null);
    setRecommendations(null);

    let lat: number | undefined = undefined;
    let lon: number | undefined = undefined;

    if (useCurrentLocation && geoCoordinates) {
      lat = geoCoordinates.lat;
      lon = geoCoordinates.lon;
    } else if (!useCurrentLocation && manualLatitude && manualLongitude) {
      lat = parseFloat(manualLatitude);
      lon = parseFloat(manualLongitude);
      if (isNaN(lat) || isNaN(lon)) {
        toast({ title: "Invalid Coordinates", description: "Manual latitude and longitude must be valid numbers.", variant: "destructive" });
        setIsLoadingRecommendations(false);
        return;
      }
    }

    try {
      const data = await apiClient.getWardrobeSuggestions(lat, lon);
      setRecommendations(data);
      if (data.newOutfitIdeas.length === 0 && data.itemsToAcquire.length === 0) {
        toast({ title: "No specific suggestions", description: "Try adjusting your wardrobe or preferences for more ideas.", variant: "default" });
      }
    } catch (err: any) {
      setRecommendationError(err.message || "Failed to fetch recommendations.");
      toast({ title: "Recommendation Error", description: err.message, variant: "destructive" });
    } finally {
      setIsLoadingRecommendations(false);
    }
  };

  return (
    <section className="py-12 md:py-20 bg-gradient-to-br from-owis-mint to-owis-cream">
      <div className="container mx-auto px-4 max-w-6xl">
        <div className="text-center mb-12 md:mb-16 animate-fade-in">
          <h2 className="text-3xl md:text-5xl font-heading font-bold text-owis-forest mb-4 md:mb-6">
            AI Outfit Generator
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
            Let our AI curate the perfect outfit, considering weather, your style, and sustainability.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 md:gap-12 items-start">
          {/* Controls Column */}
          <div className="lg:col-span-1 space-y-6 md:space-y-8 animate-fade-in">
            <div>
              <h3 className="text-xl md:text-2xl font-heading font-semibold text-owis-charcoal mb-4 md:mb-6">
                1. Choose Occasion
              </h3>
              <div className="grid grid-cols-2 gap-2 md:gap-3">
                {occasions.map((occasion) => (
                  <button
                    key={occasion.id}
                    onClick={() => setSelectedOccasion(occasion.id)}
                    className={`p-3 md:p-4 rounded-lg md:rounded-xl border-2 transition-all duration-300 flex flex-col items-center justify-center text-center ${
                      selectedOccasion === occasion.id
                        ? 'border-owis-gold bg-owis-gold/10 text-owis-forest shadow-lg scale-105'
                        : 'border-gray-200 bg-white/50 hover:border-owis-gold/50 hover:bg-white/80'
                    }`}
                  >
                    <span className="text-xl md:text-2xl mb-1 md:mb-2">{occasion.icon}</span>
                    <span className="font-medium text-xs md:text-sm">{occasion.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Weather Options */}
            <div>
              <h3 className="text-xl md:text-2xl font-heading font-semibold text-owis-charcoal mb-4 md:mb-6">
                2. Weather Options
              </h3>
              <div className="p-4 bg-white/60 rounded-lg space-y-3">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="useCurrentLocation"
                    checked={useCurrentLocation}
                    onCheckedChange={(checked) => setUseCurrentLocation(Boolean(checked))}
                  />
                  <Label htmlFor="useCurrentLocation" className="text-sm md:text-base">Use current location</Label>
                </div>
                {useCurrentLocation && (
                  <Button onClick={getLocation} disabled={geoIsLoading} variant="outline" size="sm" className="w-full">
                    {geoIsLoading ? <LoadingSpinner size="xs" className="mr-2" /> : <Compass size={16} className="mr-2" />}
                    {geoCoordinates ? 'Refresh Location' : 'Get My Location'}
                  </Button>
                )}
                {geoCoordinates && useCurrentLocation && (
                    <p className="text-xs text-gray-600">Using: Lat {geoCoordinates.lat.toFixed(2)}, Lon {geoCoordinates.lon.toFixed(2)}</p>
                )}
                {geoError && useCurrentLocation && (
                    <p className="text-xs text-red-500">{geoError}</p>
                )}

                {!useCurrentLocation && (
                  <div className="space-y-2 pt-2">
                    <Label htmlFor="manualLatitude" className="text-sm">Or enter manually:</Label>
                    <div className="flex gap-2">
                      <Input
                        id="manualLatitude"
                        placeholder="Latitude"
                        value={manualLatitude}
                        onChange={(e) => setManualLatitude(e.target.value)}
                        className="text-sm"
                      />
                      <Input
                        id="manualLongitude"
                        placeholder="Longitude"
                        value={manualLongitude}
                        onChange={(e) => setManualLongitude(e.target.value)}
                        className="text-sm"
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>

            <Button 
              size="lg"
              onClick={handleGenerateOutfit}
              disabled={isLoadingRecommendations || (useCurrentLocation && geoIsLoading)}
              className="w-full bg-gradient-to-r from-owis-gold to-owis-bronze hover:from-owis-gold-dark hover:to-owis-bronze-dark text-owis-forest font-semibold py-3 md:py-4 text-base md:text-lg rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
            >
              {isLoadingRecommendations ? <LoadingSpinner className="mr-2" /> : <Sparkles className="w-5 h-5 mr-2" />}
              Generate Outfit Ideas
            </Button>
          </div>

          {/* Outfit Display Column */}
          <div className="lg:col-span-2 bg-white/80 backdrop-blur-sm rounded-2xl p-6 md:p-8 shadow-xl animate-scale-in border border-white/30 min-h-[400px]">
            <h3 className="text-xl md:text-2xl font-heading font-semibold text-owis-charcoal mb-4 md:mb-6">
              AI Suggestions
            </h3>
            {isLoadingRecommendations && (
              <div className="flex flex-col items-center justify-center h-full">
                <LoadingSpinner size="lg" />
                <p className="mt-4 text-owis-charcoal/70">Generating your outfit ideas...</p>
              </div>
            )}
            {!isLoadingRecommendations && recommendationError && (
              <div className="text-center py-10 text-red-500 bg-red-50 p-4 rounded-md">
                 <AlertTriangle size={32} className="mx-auto mb-2" />
                <p>{recommendationError}</p>
              </div>
            )}
            {!isLoadingRecommendations && !recommendationError && recommendations && (
              <div className="space-y-6">
                {recommendations.newOutfitIdeas.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-lg mb-2 text-owis-sage">New Outfit Ideas:</h4>
                    <ul className="list-disc list-inside space-y-2 pl-2">
                      {recommendations.newOutfitIdeas.map((idea, index) => (
                        <li key={`idea-${index}`} className="text-sm md:text-base text-gray-700">{idea}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {recommendations.itemsToAcquire.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-lg mb-2 text-owis-sage">Consider Adding These To Your Wardrobe:</h4>
                    <ul className="list-disc list-inside space-y-2 pl-2">
                      {recommendations.itemsToAcquire.map((item, index) => (
                        <li key={`acquire-${index}`} className="text-sm md:text-base text-gray-700">{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {recommendations.newOutfitIdeas.length === 0 && recommendations.itemsToAcquire.length === 0 && (
                   <p className="text-center py-10 text-gray-500">No specific suggestions generated. Try different options or broaden your wardrobe!</p>
                )}
              </div>
            )}
             {!isLoadingRecommendations && !recommendationError && !recommendations && (
                <div className="text-center py-10">
                    <Zap size={48} className="mx-auto text-gray-300 mb-4" />
                    <p className="text-gray-500">Click "Generate Outfit Ideas" to see AI magic!</p>
                </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default OutfitGenerator;
