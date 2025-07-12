
import React, { useState, useMemo } from 'react';
import { Calendar, MapPin, Cloud, Clock, Users, Star, Sparkles, Wand2, Heart, TrendingUp, Palette, Sun, Snowflake, Eye } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface EventDetails {
  type: string;
  location: string;
  weather: string;
  timeOfDay: string;
  duration: string;
  attendees: string;
  formality: string;
}

interface OutfitRecommendation {
  id: number;
  items: number[];
  score: number;
  reasons: string[];
  weatherSuitability: number;
  formalityMatch: number;
  stylePoints: string[];
}

interface WardrobeItem {
  id: number;
  name: string;
  category: string;
  color: string;
  brand: string;
  price: number;
  tags: string[];
  favorite: boolean;
  timesWorn: number;
}

interface AIEventRecommenderProps {
  wardrobeItems: WardrobeItem[];
}

const AIEventRecommender = ({ wardrobeItems }: AIEventRecommenderProps) => {
  const [eventDetails, setEventDetails] = useState<EventDetails>({
    type: '',
    location: '',
    weather: 'mild',
    timeOfDay: 'afternoon',
    duration: '2-4 hours',
    attendees: 'small group',
    formality: 'smart casual'
  });
  
  const [isGenerating, setIsGenerating] = useState(false);
  const [recommendations, setRecommendations] = useState<OutfitRecommendation[]>([]);
  const { toast } = useToast();

  const eventTypes = [
    { value: 'business_meeting', label: 'Business Meeting', icon: Star, color: 'from-blue-500 to-indigo-600' },
    { value: 'dinner_date', label: 'Dinner Date', icon: Heart, color: 'from-pink-500 to-red-600' },
    { value: 'wedding', label: 'Wedding', icon: Sparkles, color: 'from-purple-500 to-pink-600' },
    { value: 'job_interview', label: 'Job Interview', icon: TrendingUp, color: 'from-green-500 to-emerald-600' },
    { value: 'cocktail_party', label: 'Cocktail Party', icon: Star, color: 'from-yellow-500 to-orange-600' },
    { value: 'casual_brunch', label: 'Casual Brunch', icon: Sun, color: 'from-orange-400 to-yellow-500' },
    { value: 'gallery_opening', label: 'Gallery Opening', icon: Eye, color: 'from-indigo-500 to-purple-600' },
    { value: 'family_gathering', label: 'Family Gathering', icon: Users, color: 'from-teal-500 to-cyan-600' },
  ];

  const weatherOptions = [
    { value: 'hot', label: 'Hot & Sunny', icon: Sun, temp: '25°C+' },
    { value: 'mild', label: 'Perfect Weather', icon: Cloud, temp: '15-24°C' },
    { value: 'cold', label: 'Cold & Cozy', icon: Snowflake, temp: 'Below 15°C' },
  ];

  const generateRecommendations = () => {
    if (!eventDetails.type) {
      toast({
        title: "Event Type Required",
        description: "Please select an event type to get AI recommendations.",
        variant: "destructive",
      });
      return;
    }

    setIsGenerating(true);
    
    setTimeout(() => {
      // AI-powered recommendation logic simulation
      const mockRecommendations: OutfitRecommendation[] = [
        {
          id: 1,
          items: [1, 2, 5], // Navy Blazer, Silk Blouse, Leather Boots
          score: 95,
          reasons: [
            'Perfect formality level for the occasion',
            'Weather-appropriate fabric choices',
            'Classic color combination creates sophisticated look',
            'Versatile pieces that photograph well'
          ],
          weatherSuitability: 92,
          formalityMatch: 98,
          stylePoints: ['Timeless Elegance', 'Professional Confidence', 'Color Harmony']
        },
        {
          id: 2,
          items: [4, 6, 8], // Red Dress, Necklace, Scarf
          score: 88,
          reasons: [
            'Statement piece perfect for special occasions',
            'Luxurious accessories elevate the look',
            'Bold choice that commands attention',
            'Excellent for evening events'
          ],
          weatherSuitability: 85,
          formalityMatch: 90,
          stylePoints: ['Statement Glamour', 'Luxury Appeal', 'Confidence Boost']
        },
        {
          id: 3,
          items: [3, 7, 2], // Black Jeans, Cashmere Cardigan, Silk Blouse
          score: 82,
          reasons: [
            'Comfortable yet polished combination',
            'Perfect for longer events',
            'Easy to accessorize and personalize',
            'Weather-appropriate layering'
          ],
          weatherSuitability: 88,
          formalityMatch: 78,
          stylePoints: ['Effortless Chic', 'Comfort Meets Style', 'Versatile Appeal']
        }
      ];

      setRecommendations(mockRecommendations);
      setIsGenerating(false);
      
      toast({
        title: "🎯 AI Recommendations Ready!",
        description: `Found ${mockRecommendations.length} perfect outfit combinations for your ${eventDetails.type.replace('_', ' ')}.`,
      });
    }, 2500);
  };

  const getOutfitItems = (itemIds: number[]) => {
    return wardrobeItems.filter(item => itemIds.includes(item.id));
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-blue-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score: number) => {
    if (score >= 90) return 'from-green-500 to-emerald-600';
    if (score >= 80) return 'from-blue-500 to-indigo-600';
    if (score >= 70) return 'from-yellow-500 to-orange-600';
    return 'from-red-500 to-pink-600';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-indigo-50 dark:from-gray-900 dark:via-purple-900 dark:to-indigo-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12 animate-fade-in">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="p-3 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl">
              <Wand2 className="text-white" size={32} />
            </div>
            <h1 className="text-6xl font-heading font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              AI Event Stylist
            </h1>
          </div>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Tell us about your event and our AI will recommend the perfect outfit combinations from your wardrobe
          </p>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          {/* Event Details Form */}
          <div className="owis-card rounded-3xl p-8 backdrop-blur-lg bg-white/70 dark:bg-gray-800/70 shadow-2xl border border-white/50">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-3">
              <Calendar className="text-purple-600" />
              Event Details
            </h2>

            <div className="space-y-6">
              {/* Event Type */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                  Event Type *
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {eventTypes.map((event) => (
                    <button
                      key={event.value}
                      onClick={() => setEventDetails({...eventDetails, type: event.value})}
                      className={`p-3 rounded-xl transition-all text-sm font-medium ${
                        eventDetails.type === event.value
                          ? `bg-gradient-to-r ${event.color} text-white shadow-lg`
                          : 'bg-white/50 dark:bg-black/20 text-gray-700 dark:text-gray-300 hover:bg-purple-100 dark:hover:bg-purple-900/20'
                      }`}
                    >
                      <event.icon size={16} className="mx-auto mb-1" />
                      {event.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Weather */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                  Weather Conditions
                </label>
                <div className="space-y-2">
                  {weatherOptions.map((w) => (
                    <button
                      key={w.value}
                      onClick={() => setEventDetails({...eventDetails, weather: w.value})}
                      className={`w-full flex items-center justify-between p-3 rounded-xl transition-all ${
                        eventDetails.weather === w.value
                          ? 'bg-gradient-to-r from-blue-100 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30 border border-blue-300'
                          : 'bg-white/50 dark:bg-black/20 hover:bg-blue-50 dark:hover:bg-blue-900/10'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <w.icon size={16} className="text-blue-600" />
                        <span className="font-medium text-gray-700 dark:text-gray-300">{w.label}</span>
                      </div>
                      <span className="text-sm text-gray-500 dark:text-gray-400">{w.temp}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Additional Details */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Time of Day
                  </label>
                  <select
                    value={eventDetails.timeOfDay}
                    onChange={(e) => setEventDetails({...eventDetails, timeOfDay: e.target.value})}
                    className="w-full px-3 py-2 bg-white/50 dark:bg-black/20 border border-white/30 dark:border-white/20 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-300 text-gray-700 dark:text-gray-300"
                  >
                    <option value="morning">Morning</option>
                    <option value="afternoon">Afternoon</option>
                    <option value="evening">Evening</option>
                    <option value="night">Night</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Duration
                  </label>
                  <select
                    value={eventDetails.duration}
                    onChange={(e) => setEventDetails({...eventDetails, duration: e.target.value})}
                    className="w-full px-3 py-2 bg-white/50 dark:bg-black/20 border border-white/30 dark:border-white/20 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-300 text-gray-700 dark:text-gray-300"
                  >
                    <option value="1 hour">1 hour</option>
                    <option value="2-4 hours">2-4 hours</option>
                    <option value="half day">Half day</option>
                    <option value="full day">Full day</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Location/Venue
                </label>
                <input
                  type="text"
                  value={eventDetails.location}
                  onChange={(e) => setEventDetails({...eventDetails, location: e.target.value})}
                  placeholder="e.g., Upscale restaurant, Office building, Outdoor venue"
                  className="w-full px-4 py-3 bg-white/50 dark:bg-black/20 border border-white/30 dark:border-white/20 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-300 text-gray-700 dark:text-gray-300 placeholder:text-gray-500 dark:placeholder:text-gray-400"
                />
              </div>

              <button
                onClick={generateRecommendations}
                disabled={isGenerating || !eventDetails.type}
                className="w-full owis-button-primary py-4 rounded-2xl flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGenerating ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    AI is analyzing...
                  </>
                ) : (
                  <>
                    <Wand2 size={20} />
                    Get AI Recommendations
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Recommendations */}
          <div className="xl:col-span-2">
            {recommendations.length > 0 ? (
              <div className="space-y-6 animate-fade-in">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
                  <Sparkles className="text-purple-600" />
                  AI Outfit Recommendations ({recommendations.length})
                </h2>

                {recommendations.map((rec, index) => {
                  const outfitItems = getOutfitItems(rec.items);
                  const totalValue = outfitItems.reduce((sum, item) => sum + item.price, 0);

                  return (
                    <div key={rec.id} className="owis-card rounded-3xl p-6 backdrop-blur-lg bg-white/70 dark:bg-gray-800/70 shadow-2xl border border-white/50">
                      <div className="flex items-start justify-between mb-6">
                        <div className="flex items-center gap-4">
                          <div className={`flex items-center justify-center w-16 h-16 bg-gradient-to-r ${getScoreBg(rec.score)} rounded-2xl shadow-lg`}>
                            <span className="text-xl font-bold text-white">{rec.score}</span>
                          </div>
                          <div>
                            <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                              Recommendation #{index + 1}
                            </h3>
                            <p className="text-gray-600 dark:text-gray-300">
                              Perfect match for your {eventDetails.type.replace('_', ' ')}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold text-purple-600">${totalValue}</div>
                          <div className="text-sm text-gray-500">Total Value</div>
                        </div>
                      </div>

                      {/* Outfit Items */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                        {outfitItems.map((item) => (
                          <div key={item.id} className="flex items-center gap-3 p-3 bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-700 rounded-xl border border-gray-200 dark:border-gray-600">
                            <div className="w-12 h-12 bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-600 dark:to-gray-700 rounded-lg flex items-center justify-center">
                              <span className="text-xs text-gray-600 dark:text-gray-300 font-bold">
                                {item.category.slice(0, 3).toUpperCase()}
                              </span>
                            </div>
                            <div className="flex-1 min-w-0">
                              <h4 className="font-semibold text-gray-900 dark:text-white truncate">
                                {item.name}
                              </h4>
                              <p className="text-sm text-gray-600 dark:text-gray-300 truncate">
                                {item.brand} • ${item.price}
                              </p>
                            </div>
                            {item.favorite && (
                              <Heart className="text-red-500 fill-current" size={14} />
                            )}
                          </div>
                        ))}
                      </div>

                      {/* Score Breakdown */}
                      <div className="grid grid-cols-2 gap-4 mb-6">
                        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <Cloud size={16} className="text-blue-600" />
                            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Weather Match</span>
                          </div>
                          <span className={`text-xl font-bold ${getScoreColor(rec.weatherSuitability)}`}>
                            {rec.weatherSuitability}%
                          </span>
                        </div>
                        
                        <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <Star size={16} className="text-purple-600" />
                            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Formality Match</span>
                          </div>
                          <span className={`text-xl font-bold ${getScoreColor(rec.formalityMatch)}`}>
                            {rec.formalityMatch}%
                          </span>
                        </div>
                      </div>

                      {/* Style Points */}
                      <div className="mb-4">
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                          <Palette size={16} />
                          Style Highlights
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {rec.stylePoints.map((point, idx) => (
                            <span key={idx} className="px-3 py-1 bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 text-purple-700 dark:text-purple-300 rounded-full text-sm font-medium">
                              {point}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* AI Reasons */}
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                          <Sparkles size={16} />
                          Why This Works
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                          {rec.reasons.map((reason, idx) => (
                            <div key={idx} className="flex items-start gap-2 p-2 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg">
                              <TrendingUp size={12} className="text-green-600 mt-1 flex-shrink-0" />
                              <span className="text-sm text-gray-700 dark:text-gray-300">{reason}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="owis-card rounded-3xl p-12 text-center backdrop-blur-lg bg-white/70 dark:bg-gray-800/70 shadow-2xl border border-white/50">
                <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 rounded-full mb-6">
                  <Wand2 className="text-purple-600" size={48} />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                  Ready for AI Magic?
                </h3>
                <p className="text-gray-600 dark:text-gray-300 max-w-md mx-auto">
                  Fill in your event details and let our AI fashion intelligence find the perfect outfit combinations from your wardrobe.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIEventRecommender;
