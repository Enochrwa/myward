import React, { useState, useEffect, useCallback } from 'react';
import { TrendingUp, Sparkles, Eye, Heart, Share2, Camera, Upload, Zap, Crown, Star, Globe, Calendar, Users, Award, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import apiClient from '@/lib/apiClient';

// Interface for individual trend item - ensure fields match backend & handle optionality
interface TrendData {
  id: string;
  name: string;
  category: string;
  popularity: number;
  growth: number;
  description: string;
  colors: string[];
  season: string;
  confidence: number;
  outfitImages: string[];
  celebrities: string[];
  hashtags: string[];
  priceRange: string | null;
  occasion: string[];
}

// Matches backend schemas.TrendForecastResponse
interface BackendTrendForecastResponse {
  trends: Array<{
    id: string;
    name: string;
    category: string;
    popularity: number;
    growth: number;
    description: string;
    colors: string[];
    season: string;
    confidence: number;
    outfitImages?: string[] | null;
    celebrities?: string[] | null;
    hashtags?: string[] | null;
    priceRange?: string | null;
    occasion?: string[] | null;
  }>;
  personalizedRecommendations: {
    mustHave: string[];
    avoid: string[];
    investIn: string[];
  };
  seasonalPredictions: {
    emerging: string[];
    declining: string[];
    stable: string[];
  };
}

// Frontend display structure
interface ForecastResult {
  trends: TrendData[];
  personalizedRecommendations: {
    mustHave: string[];
    avoid: string[];
    investIn: string[];
  };
  seasonalPredictions: {
    emerging: string[];
    declining: string[];
    stable: string[];
  };
}

const AITrendForecasting = () => {
  const [isForecasting, setIsForecasting] = useState(false);
  const [forecast, setForecast] = useState<ForecastResult | null>(null);
  const [selectedTrend, setSelectedTrend] = useState<TrendData | null>(null);
  const [uploadedPhoto, setUploadedPhoto] = useState<string | null>(null);
  const [analysisMode, setAnalysisMode] = useState<'trends' | 'photo' | 'ai-generate'>('trends');
  const { toast } = useToast();

  const generateForecast = useCallback(async () => {
    setIsForecasting(true);
    setForecast(null);
    try {
      const response = await apiClient.get<BackendTrendForecastResponse>('/ai/fashion-trends/');
      const backendData = response.data;

      const transformedForecast: ForecastResult = {
        trends: backendData.trends.map(trend => ({
          ...trend,
          outfitImages: trend.outfitImages || [],
          celebrities: trend.celebrities || [],
          hashtags: trend.hashtags || [],
          occasion: trend.occasion || [],
          priceRange: trend.priceRange || null,
        })),
        personalizedRecommendations: backendData.personalizedRecommendations,
        seasonalPredictions: backendData.seasonalPredictions,
      };
      
      setForecast(transformedForecast);
      toast({
        title: "🔮 AI Forecast Complete!",
        description: "Advanced trend analysis using global fashion intelligence.",
      });
    } catch (error: any) {
      console.error("Failed to fetch trend forecast:", error);
      const errorMsg = error.response?.data?.detail || "Could not fetch trend forecast.";
      toast({
        title: "Error Fetching Forecast",
        description: errorMsg,
        variant: "destructive",
      });
      setForecast(null);
    } finally {
      setIsForecasting(false);
    }
  }, [toast]);

  useEffect(() => {
    if (analysisMode === 'trends') {
      generateForecast();
    }
  }, [analysisMode, generateForecast]);

  const handlePhotoUpload = (file: File) => {
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setUploadedPhoto(e.target?.result as string);
        analyzeUploadedPhoto();
      };
      reader.readAsDataURL(file);
    }
  };

  const analyzeUploadedPhoto = () => {
    toast({
      title: "📸 Analyzing Your Style",
      description: "AI is detecting trends and suggesting improvements...",
    });
    // Placeholder for actual photo analysis logic
  };

  const getTrendIcon = (category: string) => {
    switch (category) {
      case 'Fashion Tech': return <Zap className="text-blue-500" />;
      case 'Aesthetic Movement': return <Sparkles className="text-green-500" />;
      case 'Aesthetic Revival': return <Crown className="text-purple-500" />;
      default: return <TrendingUp className="text-pink-500" />;
    }
  };

  const safeColor = (colorName: string) => colorName.toLowerCase().replace(/\s+/g, '');


  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-indigo-900 dark:to-purple-900 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="p-4 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-3xl shadow-lg">
              <TrendingUp className="text-white" size={36} />
            </div>
            <h1 className="text-6xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              AI Trend Oracle
            </h1>
          </div>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-4xl mx-auto">
            Predict the future of fashion with AI-powered trend analysis, celebrity insights, and personalized recommendations
          </p>
        </div>

        <div className="flex justify-center mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-2 shadow-xl inline-flex">
            {[
              { id: 'trends', label: 'Trend Forecast', icon: TrendingUp },
              { id: 'photo', label: 'Photo Analysis', icon: Camera },
              { id: 'ai-generate', label: 'AI Generate', icon: Sparkles }
            ].map(mode => (
              <button
                key={mode.id}
                onClick={() => setAnalysisMode(mode.id as any)}
                className={`px-4 sm:px-6 py-3 rounded-xl flex items-center gap-2 transition-all text-sm sm:text-base ${
                  analysisMode === mode.id 
                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg' 
                    : 'text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100'
                }`}
              >
                <mode.icon size={18} />
                {mode.label}
              </button>
            ))}
          </div>
        </div>

        {analysisMode === 'photo' && (
          <Card className="mb-8 border-2 border-dashed border-purple-300 dark:border-purple-700">
            <CardContent className="p-8">
              <div className="text-center">
                {uploadedPhoto ? (
                  <div className="space-y-4">
                    <img src={uploadedPhoto} alt="Uploaded" className="max-h-64 mx-auto rounded-xl shadow-lg" />
                    <div className="p-4 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-xl">
                      <h3 className="font-bold text-lg mb-2">AI Analysis Results:</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        ✨ Detected: Modern Casual • 🎨 Dominant Colors: Navy, White • 📈 Trend Alignment: 87% (Placeholder)
                      </p>
                    </div>
                  </div>
                ) : (
                  <>
                    <Upload className="mx-auto mb-4 text-purple-500" size={48} />
                    <h3 className="text-xl font-bold mb-2">Upload Your Outfit</h3>
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                      Get instant trend analysis and future-proof recommendations
                    </p>
                    <label className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl cursor-pointer hover:scale-105 transition-transform">
                      <Camera size={20} /> Choose Photo
                      <input type="file" accept="image/*" onChange={(e) => e.target.files?.[0] && handlePhotoUpload(e.target.files[0])} className="hidden"/>
                    </label>
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {isForecasting && analysisMode === 'trends' && (
          <div className="text-center py-20 flex flex-col items-center justify-center">
            <Loader2 className="h-20 w-20 text-indigo-600 animate-spin mb-6" />
            <h3 className="text-2xl font-bold mb-3 text-gray-800 dark:text-gray-200">AI Fashion Oracle is Consulting the Stars...</h3>
            <p className="text-gray-600 dark:text-gray-400">Analyzing global fashion data, celebrity trends, and cultural movements.</p>
          </div>
        )}

        {!isForecasting && forecast && analysisMode === 'trends' && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {forecast.trends.map(trend => (
                <Card key={trend.id} className="group hover:shadow-2xl transition-all duration-300 cursor-pointer border-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg" onClick={() => setSelectedTrend(trend)}>
                  <CardHeader className="pb-3">
                    <div className="flex justify-between items-start">
                      <CardTitle className="text-xl flex items-center gap-2">{getTrendIcon(trend.category)}{trend.name}</CardTitle>
                      <span className="text-xs bg-gradient-to-r from-green-500 to-emerald-600 text-white px-2 py-1 rounded-full">+{trend.growth}%</span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{trend.category}</p>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-3 gap-2">
                      {trend.outfitImages.slice(0,3).map((image, i) => (
                        <div key={i} className="relative group">
                          <img src={image} alt={`${trend.name} outfit ${i + 1}`} className="w-full h-20 object-cover rounded-lg group-hover:scale-105 transition-transform"/>
                          <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center"><Eye size={16} className="text-white" /></div>
                        </div>
                      ))}
                    </div>
                    <p className="text-sm text-gray-700 dark:text-gray-300 h-10 overflow-hidden">{trend.description}</p>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="text-center p-2 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg">
                        <div className="text-lg font-bold text-blue-600">{trend.popularity}%</div><div className="text-xs text-gray-600 dark:text-gray-400">Popularity</div>
                      </div>
                      <div className="text-center p-2 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg">
                        <div className="text-lg font-bold text-green-600">{trend.confidence}%</div><div className="text-xs text-gray-600 dark:text-gray-400">AI Confidence</div>
                      </div>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Key Colors</h4>
                      <div className="flex flex-wrap gap-1">
                        {trend.colors.slice(0,4).map((color, i) => (<div key={i} className="w-1/4 h-6 rounded flex-grow" title={color} style={{backgroundColor: safeColor(color) || 'transparent'}}></div>))}
                      </div>
                    </div>
                    {trend.celebrities && trend.celebrities.length > 0 && (
                      <div className="flex items-center gap-2">
                        <Star size={14} className="text-purple-500 flex-shrink-0" />
                        <span className="text-xs text-gray-600 dark:text-gray-400 truncate">Spotted on: {trend.celebrities.join(', ')}</span>
                      </div>
                    )}
                    <div className="flex gap-2 pt-2">
                      <Button size="sm" className="flex-1 bg-gradient-to-r from-pink-500 to-purple-600 hover:scale-105 transition-transform"><Heart size={14} className="mr-1" />Save</Button>
                      <Button size="sm" variant="outline" className="flex-1 hover:scale-105 transition-transform"><Share2 size={14} className="mr-1" />Share</Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20"><CardHeader><CardTitle className="flex items-center gap-2 text-green-700 dark:text-green-400"><Award size={20} />Must Have</CardTitle></CardHeader><CardContent><ul className="space-y-2">{forecast.personalizedRecommendations.mustHave.map((item, i) => (<li key={i} className="text-sm flex items-start gap-2"><span className="text-green-600">•</span>{item}</li>))}</ul></CardContent></Card>
              <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20"><CardHeader><CardTitle className="flex items-center gap-2 text-blue-700 dark:text-blue-400"><Globe size={20} />Invest In</CardTitle></CardHeader><CardContent><ul className="space-y-2">{forecast.personalizedRecommendations.investIn.map((item, i) => (<li key={i} className="text-sm flex items-start gap-2"><span className="text-blue-600">•</span>{item}</li>))}</ul></CardContent></Card>
              <Card className="bg-gradient-to-br from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20"><CardHeader><CardTitle className="flex items-center gap-2 text-red-700 dark:text-red-400"><Calendar size={20} />Seasonally Avoid</CardTitle></CardHeader><CardContent><ul className="space-y-2">{forecast.personalizedRecommendations.avoid.map((item, i) => (<li key={i} className="text-sm flex items-start gap-2"><span className="text-red-600">•</span>{item}</li>))}</ul></CardContent></Card>
            </div>
          </div>
        )}

        {!isForecasting && !forecast && analysisMode === 'trends' && (
           <div className="text-center py-20">
             <h3 className="text-2xl font-bold mb-3 text-gray-800 dark:text-gray-200">No Forecast Data</h3>
             <p className="text-gray-600 dark:text-gray-400">Could not load trend forecast data. Please try again later.</p>
             <Button onClick={generateForecast} className="mt-4">Retry Forecast</Button>
           </div>
        )}

        {selectedTrend && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center p-4 animate-fade-in">
            <Card className="max-w-2xl w-full max-h-[90vh] overflow-y-auto bg-white dark:bg-gray-800 shadow-2xl rounded-3xl">
              <CardHeader className="sticky top-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm z-10">
                <div className="flex justify-between items-start">
                  <div><CardTitle className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent py-1">{selectedTrend.name}</CardTitle>
                    <p className="text-gray-600 dark:text-gray-400">{selectedTrend.category} - {selectedTrend.season}</p>
                  </div>
                  <Button variant="ghost" size="icon" onClick={() => setSelectedTrend(null)} className="text-gray-500 hover:text-gray-800 dark:text-gray-400 dark:hover:text-white"><Sparkles size={20}/> Close</Button>
                </div>
              </CardHeader>
              <CardContent className="p-6 space-y-6">
                <div className="grid grid-cols-3 gap-3">
                  {selectedTrend.outfitImages.map((image, i) => (<img key={i} src={image} alt={`Outfit ${i + 1}`} className="w-full h-40 object-cover rounded-xl shadow-md hover:scale-105 transition-transform" />))}
                </div>
                <p className="text-base text-gray-700 dark:text-gray-300 leading-relaxed">{selectedTrend.description}</p>

                <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="p-3 bg-gray-100 dark:bg-gray-700/50 rounded-lg"><strong>Popularity:</strong> <span className="text-blue-600 dark:text-blue-400 font-semibold">{selectedTrend.popularity}%</span></div>
                    <div className="p-3 bg-gray-100 dark:bg-gray-700/50 rounded-lg"><strong>AI Confidence:</strong> <span className="text-green-600 dark:text-green-400 font-semibold">{selectedTrend.confidence}%</span></div>
                    <div className="p-3 bg-gray-100 dark:bg-gray-700/50 rounded-lg"><strong>Growth:</strong> <span className="text-pink-600 dark:text-pink-400 font-semibold">+{selectedTrend.growth}%</span></div>
                    {selectedTrend.priceRange && <div className="p-3 bg-gray-100 dark:bg-gray-700/50 rounded-lg"><strong>Price Range:</strong> <span className="font-semibold">{selectedTrend.priceRange}</span></div>}
                </div>

                <div>
                  <h4 className="font-semibold text-lg mb-2 text-gray-800 dark:text-gray-200">Key Colors</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedTrend.colors.map((color, i) => (<div key={i} className="px-3 py-1 text-sm font-medium rounded-full text-white" style={{backgroundColor: safeColor(color)}}>{color}</div>))}
                  </div>
                </div>

                {selectedTrend.hashtags && selectedTrend.hashtags.length > 0 && (<div><h4 className="font-semibold text-lg mb-2 text-gray-800 dark:text-gray-200">Hashtags</h4><div className="flex flex-wrap gap-2">{selectedTrend.hashtags.map((tag, i) => (<span key={i} className="px-3 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300 rounded-full text-sm">{tag}</span>))}</div></div>)}
                {selectedTrend.occasion && selectedTrend.occasion.length > 0 && (<div><h4 className="font-semibold text-lg mb-2 text-gray-800 dark:text-gray-200">Perfect For</h4><div className="flex flex-wrap gap-2">{selectedTrend.occasion.map((occ, i) => (<span key={i} className="px-3 py-1 bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300 rounded-full text-sm">{occ}</span>))}</div></div>)}
                {selectedTrend.celebrities && selectedTrend.celebrities.length > 0 && (<div><h4 className="font-semibold text-lg mb-2 text-gray-800 dark:text-gray-200">Celebrity Spotlight</h4><div className="flex flex-wrap gap-2 items-center">{selectedTrend.celebrities.map((celeb, i) => (<span key={i} className="flex items-center gap-1 px-3 py-1 bg-pink-100 text-pink-800 dark:bg-pink-900/40 dark:text-pink-300 rounded-full text-sm"><Star size={12}/>{celeb}</span>))}</div></div>)}

                <Button className="w-full mt-6 bg-gradient-to-r from-indigo-600 to-purple-600 hover:scale-105 transition-transform" onClick={() => setSelectedTrend(null)}>
                  Close Details
                </Button>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default AITrendForecasting;
