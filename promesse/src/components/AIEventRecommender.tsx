import React, { useState, useMemo, useEffect } from 'react';
import { Calendar, Cloud, Star, Sparkles, Wand2, Heart, TrendingUp, Palette, Sun, Snowflake, Eye, Users, Loader2, ImageOff } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import apiClient from '@/lib/apiClient';

// Matches backend schemas.EventDetailsInput
interface EventDetailsInputPayload {
  event_type: string;
  location?: string;
  weather?: string;
  time_of_day?: string;
  formality?: string;
  notes?: string;
}

// Frontend representation of an outfit recommendation
interface OutfitRecommendation {
  id: number; // This will be the backend Outfit.id
  items: number[]; // Array of WardrobeItem IDs (from backend Outfit.item_ids)
  name?: string; // Name of the outfit from backend Outfit.name
  score: number; // Placeholder, as backend Outfit doesn't have this directly
  reasons: string[]; // Placeholder
  weatherSuitability: number; // Placeholder
  formalityMatch: number; // Placeholder
  stylePoints: string[]; // Placeholder
  imageUrl?: string | null; // From backend Outfit.image_url
}

// Frontend representation of a wardrobe item - align with backend schemas.WardrobeItem
interface WardrobeItem {
  id: number;
  name: string;
  category: string;
  brand?: string | null;
  price?: number | null;
  image_url?: string | null;
  // Optional fields from backend if needed later:
  // size?: string | null;
  // material?: string | null;
  // season?: string | null;
  // tags?: string[] | null;
  // favorite?: boolean;
  // times_worn?: number;
  // date_added?: string;
  // last_worn?: string | null;
  // updated_at?: string | null;
  // ai_embedding?: number[] | null;
  // ai_dominant_colors?: string[] | null;
}

// Backend schemas.Outfit structure (for clarity during transformation)
interface BackendOutfit {
  id: number;
  user_id: number;
  name: string;
  item_ids: number[];
  created_at: string;
  updated_at?: string | null;
  tags?: string[] | null;
  image_url?: string | null;
}

const AIEventRecommender = () => {
  const [eventDetails, setEventDetails] = useState({
    type: '',
    location: '',
    weather: 'mild',
    timeOfDay: 'afternoon',
    formality: 'smart_casual',
    notes: '',
  });
  
  const [actualWardrobeItems, setActualWardrobeItems] = useState<WardrobeItem[]>([]);
  const [isLoadingWardrobe, setIsLoadingWardrobe] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [recommendations, setRecommendations] = useState<OutfitRecommendation[]>([]);
  const { toast } = useToast();

  useEffect(() => {
    const fetchWardrobe = async () => {
      setIsLoadingWardrobe(true);
      try {
        // Assuming WardrobeItem from backend matches the frontend interface more closely after this change
        const response = await apiClient.get<WardrobeItem[]>('/wardrobe/items/');
        setActualWardrobeItems(response.data || []);
      } catch (error) {
        console.error("Failed to fetch wardrobe items:", error);
        toast({
          title: "Error Loading Wardrobe",
          description: "Could not load your wardrobe items. Please try refreshing the page.",
          variant: "destructive",
        });
      } finally {
        setIsLoadingWardrobe(false);
      }
    };
    fetchWardrobe();
  }, [toast]);

  const eventTypes = [
    { value: 'business_meeting', label: 'Business Meeting', icon: Star, color: 'from-blue-500 to-indigo-600' },
    { value: 'dinner_date', label: 'Dinner Date', icon: Heart, color: 'from-pink-500 to-red-600' },
    { value: 'wedding', label: 'Wedding', icon: Sparkles, color: 'from-purple-500 to-pink-600' },
    { value: 'job_interview', label: 'Job Interview', icon: TrendingUp, color: 'from-green-500 to-emerald-600' },
    { value: 'cocktail_party', label: 'Cocktail Party', icon: Star, color: 'from-purple-500 to-orange-600' },
    { value: 'casual_brunch', label: 'Casual Brunch', icon: Sun, color: 'from-orange-400 to-purple-500' },
    { value: 'gallery_opening', label: 'Gallery Opening', icon: Eye, color: 'from-indigo-500 to-purple-600' },
    { value: 'family_gathering', label: 'Family Gathering', icon: Users, color: 'from-teal-500 to-cyan-600' },
  ];

  const weatherOptions = [
    { value: 'hot', label: 'Hot & Sunny', icon: Sun, temp: '25°C+' },
    { value: 'mild', label: 'Mild & Pleasant', icon: Cloud, temp: '15-24°C' },
    { value: 'cold', label: 'Cold & Cozy', icon: Snowflake, temp: '< 15°C' },
  ];

  const formalityOptions = [
    { value: 'casual', label: 'Casual' },
    { value: 'smart_casual', label: 'Smart Casual' },
    { value: 'business_casual', label: 'Business Casual' },
    { value: 'semi_formal', label: 'Semi-Formal' },
    { value: 'formal', label: 'Formal' },
  ];

  const generateRecommendations = async () => {
    if (!eventDetails.type) {
      toast({ title: "Event Type Required", description: "Please select an event type.", variant: "destructive" });
      return;
    }
    if (isLoadingWardrobe) {
        toast({ title: "Wardrobe Loading", description: "Please wait for your wardrobe items to finish loading.", variant: "warning" });
        return;
    }
    if (actualWardrobeItems.length === 0) {
      toast({ title: "Empty Wardrobe", description: "No items in your wardrobe to make recommendations. Please add some items first.", variant: "warning" });
      return;
    }

    setIsGenerating(true);
    setRecommendations([]);

    const payload: EventDetailsInputPayload = {
      event_type: eventDetails.type,
      location: eventDetails.location || undefined,
      weather: eventDetails.weather || undefined,
      time_of_day: eventDetails.timeOfDay || undefined,
      formality: eventDetails.formality || undefined,
      notes: eventDetails.notes || undefined,
    };

    try {
      const response = await apiClient.post<BackendOutfit[]>('/recommendations/event/', payload);
      if (response.data && response.data.length > 0) {
        const transformedRecommendations: OutfitRecommendation[] = response.data.map((outfit, index) => ({
          id: outfit.id,
          items: outfit.item_ids,
          name: outfit.name || `Recommended Outfit ${index + 1}`,
          score: 75 + Math.floor(Math.random() * 20), // Placeholder score (75-94)
          reasons: ['AI suggested based on event criteria', 'Matches your wardrobe selection'],
          weatherSuitability: 70 + Math.floor(Math.random() * 25),
          formalityMatch: 70 + Math.floor(Math.random() * 25),
          stylePoints: ['Versatile', 'Event-Appropriate'],
          imageUrl: outfit.image_url,
        }));
        setRecommendations(transformedRecommendations);
        toast({
          title: "🎯 AI Recommendations Ready!",
          description: `Found ${transformedRecommendations.length} outfits for your ${eventDetails.type.replace(/_/g, ' ')}.`,
        });
      } else {
        setRecommendations([]);
        toast({
          title: "No Outfits Found",
          description: "Our AI couldn't find suitable outfits for this event with your current wardrobe. Try adjusting event details or adding more items.",
        });
      }
    } catch (error: any) {
      console.error("Failed to generate recommendations:", error);
      const errorMsg = error.response?.data?.detail || "Something went wrong. Please try again.";
      toast({
        title: "Error Generating Recommendations",
        description: errorMsg,
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const getOutfitItems = (itemIds: number[]): WardrobeItem[] => {
    if (!itemIds || itemIds.length === 0) return [];
    return actualWardrobeItems.filter(item => itemIds.includes(item.id));
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-blue-600';
    return 'text-purple-600'; // For 70-79
  };

  const getScoreBg = (score: number) => {
    if (score >= 90) return 'from-green-500 to-emerald-600';
    if (score >= 80) return 'from-blue-500 to-indigo-600';
    return 'from-purple-500 to-orange-600'; // For 70-79
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-indigo-50 dark:from-gray-900 dark:via-purple-900 dark:to-indigo-900 p-6">
      <div className="max-w-7xl mx-auto">
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
            Describe your event, and our AI will craft the perfect outfit from your wardrobe.
          </p>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          <div className="owis-card rounded-3xl p-8 backdrop-blur-lg bg-white/70 dark:bg-gray-800/70 shadow-2xl border border-white/50">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-3">
              <Calendar className="text-purple-600" />
              Event Details
            </h2>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Event Type *</label>
                <div className="grid grid-cols-2 gap-3">
                  {eventTypes.map((event) => (
                    <button
                      key={event.value}
                      onClick={() => setEventDetails(prev => ({...prev, type: event.value}))}
                      className={`p-3 rounded-xl transition-all text-sm font-medium ${eventDetails.type === event.value ? `bg-gradient-to-r ${event.color} text-white shadow-lg` : 'bg-white/50 dark:bg-black/20 text-gray-700 dark:text-gray-300 hover:bg-purple-100 dark:hover:bg-purple-900/20'}`}
                    >
                      <event.icon size={16} className="mx-auto mb-1" />{event.label}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Weather Conditions</label>
                <div className="space-y-2">
                  {weatherOptions.map((w) => (
                    <button
                      key={w.value}
                      onClick={() => setEventDetails(prev => ({...prev, weather: w.value}))}
                      className={`w-full flex items-center justify-between p-3 rounded-xl transition-all ${eventDetails.weather === w.value ? 'bg-gradient-to-r from-blue-100 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30 border border-blue-300' : 'bg-white/50 dark:bg-black/20 hover:bg-blue-50 dark:hover:bg-blue-900/10'}`}
                    >
                      <div className="flex items-center gap-3"><w.icon size={16} className="text-blue-600" /><span className="font-medium text-gray-700 dark:text-gray-300">{w.label}</span></div>
                      <span className="text-sm text-gray-500 dark:text-gray-400">{w.temp}</span>
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label htmlFor="formality" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Formality</label>
                <select id="formality" value={eventDetails.formality} onChange={(e) => setEventDetails(prev => ({ ...prev, formality: e.target.value }))}
                  className="w-full px-3 py-2 bg-white/50 dark:bg-black/20 border border-white/30 dark:border-white/20 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-300 text-gray-700 dark:text-gray-300">
                  {formalityOptions.map(opt => (<option key={opt.value} value={opt.value}>{opt.label}</option>))}
                </select>
              </div>
              <div>
                <label htmlFor="timeOfDay" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Time of Day</label>
                <select id="timeOfDay" value={eventDetails.timeOfDay} onChange={(e) => setEventDetails(prev => ({...prev, timeOfDay: e.target.value}))}
                  className="w-full px-3 py-2 bg-white/50 dark:bg-black/20 border border-white/30 dark:border-white/20 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-300 text-gray-700 dark:text-gray-300">
                  <option value="morning">Morning</option><option value="afternoon">Afternoon</option><option value="evening">Evening</option><option value="night">Night</option>
                </select>
              </div>
              <div>
                <label htmlFor="location" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Location/Venue (Optional)</label>
                <input id="location" type="text" value={eventDetails.location} onChange={(e) => setEventDetails(prev => ({...prev, location: e.target.value}))}
                  placeholder="e.g., Beach party, Office, Michelin restaurant"
                  className="w-full px-4 py-3 bg-white/50 dark:bg-black/20 border border-white/30 dark:border-white/20 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-300 text-gray-700 dark:text-gray-300 placeholder:text-gray-500 dark:placeholder:text-gray-400"/>
              </div>
              <div>
                <label htmlFor="notes" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Additional Notes (Optional)</label>
                <textarea id="notes" value={eventDetails.notes} onChange={(e) => setEventDetails(prev => ({...prev, notes: e.target.value}))}
                  placeholder="e.g., Specific dress code (all-white), outdoor event, long periods of standing"
                  rows={3}
                  className="w-full px-4 py-3 bg-white/50 dark:bg-black/20 border border-white/30 dark:border-white/20 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-300 text-gray-700 dark:text-gray-300 placeholder:text-gray-500 dark:placeholder:text-gray-400"/>
              </div>
              <button onClick={generateRecommendations} disabled={isGenerating || isLoadingWardrobe || !eventDetails.type}
                className="w-full owis-button-primary py-4 rounded-2xl flex items-center justify-center gap-3 disabled:opacity-60 disabled:cursor-not-allowed">
                {isGenerating ? (<><Loader2 className="animate-spin mr-2" size={20}/>AI is analyzing...</>) :
                isLoadingWardrobe ? (<><Loader2 className="animate-spin mr-2" size={20}/>Loading Wardrobe...</>) :
                (<><Wand2 size={20} />Get AI Recommendations</>)}
              </button>
            </div>
          </div>

          <div className="xl:col-span-2">
            {recommendations.length > 0 ? (
              <div className="space-y-6 animate-fade-in">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
                  <Sparkles className="text-purple-600" />AI Outfit Recommendations ({recommendations.length})
                </h2>
                {recommendations.map((rec, index) => {
                  const outfitItems = getOutfitItems(rec.items);
                  const totalValue = outfitItems.reduce((sum, item) => sum + (item.price || 0), 0);
                  return (
                    <div key={rec.id} className="owis-card rounded-3xl p-6 backdrop-blur-lg bg-white/70 dark:bg-gray-800/70 shadow-2xl border border-white/50">
                      <div className="flex items-start justify-between mb-6">
                        <div className="flex items-center gap-4">
                          <div className={`flex items-center justify-center w-16 h-16 bg-gradient-to-r ${getScoreBg(rec.score)} rounded-2xl shadow-lg`}>
                            <span className="text-xl font-bold text-white">{rec.score}</span>
                          </div>
                          <div><h3 className="text-xl font-bold text-gray-900 dark:text-white">{rec.name}</h3>
                            <p className="text-gray-600 dark:text-gray-300">Match for your {eventDetails.type.replace(/_/g, ' ')}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold text-purple-600">${totalValue.toFixed(2)}</div>
                          <div className="text-sm text-gray-500">Est. Value</div>
                        </div>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                        {outfitItems.map((item) => (
                          <div key={item.id} className="flex items-center gap-3 p-3 bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-700 rounded-xl border border-gray-200 dark:border-gray-600">
                            {item.image_url ? (<img src={item.image_url} alt={item.name} className="w-12 h-12 rounded-lg object-cover" />) :
                            (<div className="w-12 h-12 bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-600 dark:to-gray-700 rounded-lg flex items-center justify-center"><ImageOff size={24} className="text-gray-400 dark:text-gray-500" /></div>)}
                            <div className="flex-1 min-w-0">
                              <h4 className="font-semibold text-gray-900 dark:text-white truncate">{item.name}</h4>
                              <p className="text-sm text-gray-600 dark:text-gray-300 truncate">{item.brand || 'N/A'} • ${item.price?.toFixed(2) || 'N/A'}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                      <div className="grid grid-cols-2 gap-4 mb-6">
                        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-4">
                          <div className="flex items-center gap-2 mb-2"><Cloud size={16} className="text-blue-600" /><span className="text-sm font-medium text-gray-700 dark:text-gray-300">Weather Match</span></div>
                          <span className={`text-xl font-bold ${getScoreColor(rec.weatherSuitability)}`}>{rec.weatherSuitability}%</span>
                        </div>
                        <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl p-4">
                          <div className="flex items-center gap-2 mb-2"><Star size={16} className="text-purple-600" /><span className="text-sm font-medium text-gray-700 dark:text-gray-300">Formality Match</span></div>
                          <span className={`text-xl font-bold ${getScoreColor(rec.formalityMatch)}`}>{rec.formalityMatch}%</span>
                        </div>
                      </div>
                      <div className="mb-4">
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2"><Palette size={16} />Style Highlights</h4>
                        <div className="flex flex-wrap gap-2">
                          {rec.stylePoints.map((point, idx) => (<span key={idx} className="px-3 py-1 bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 text-purple-700 dark:text-purple-300 rounded-full text-sm font-medium">{point}</span>))}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2"><Sparkles size={16} />Why This Works (Placeholder)</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                          {rec.reasons.map((reason, idx) => (
                            <div key={idx} className="flex items-start gap-2 p-2 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg">
                              <TrendingUp size={12} className="text-green-600 mt-1 flex-shrink-0" /><span className="text-sm text-gray-700 dark:text-gray-300">{reason}</span>
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
                {isLoadingWardrobe ? (
                  <div className="flex flex-col items-center justify-center">
                    <Loader2 className="w-16 h-16 text-purple-600 animate-spin mb-4" />
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Loading Your Wardrobe...</h3>
                    <p className="text-gray-600 dark:text-gray-300">Please wait while we fetch your items.</p>
                  </div>
                ) : (
                  <>
                    <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 rounded-full mb-6">
                      <Wand2 className="text-purple-600" size={48} />
                    </div>
                    <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">Ready for AI Magic?</h3>
                    <p className="text-gray-600 dark:text-gray-300 max-w-md mx-auto">
                      {actualWardrobeItems.length === 0 && !isLoadingWardrobe ? "Your wardrobe is empty. Add some items to get started!" : "Fill in your event details and let our AI find the perfect outfits."}
                    </p>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIEventRecommender;
