import React, { useState, useEffect, useCallback } from 'react';
import { Brain, Target, Palette, Users, TrendingUp, Heart, Star, BarChart3, PieChart, Activity, Camera, Upload, Sparkles, Zap, Crown, Award, Eye, Share2, Info, Lightbulb, ShoppingBag } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';
import apiClient from "@/lib/apiClient";
import { Loader2 } from 'lucide-react'; // For loading spinner

// Frontend Interfaces (after transformation from backend)
interface StyleProfile {
  primaryStyle: string | null;
  secondaryStyles: string[];
  colorPreferences: string[];
  bodyType: string | null;
  lifestyle: string | null;
  confidenceLevel: number; // 0-100
  versatilityScore: number; // 0-100
  brandAlignment: string[];
  styleSummary?: string | null; // Added from backend
}

interface WardrobeAnalysis {
  totalItems: number;
  categoryBreakdown: { [key: string]: number };
  colorDistribution: { [key: string]: number };
  brandDiversity: number; // 0-100
  averagePrice: number | null;
  styleConsistency: number; // 0-100
  gaps: string[];
  improvementSuggestions: string[]; // Renamed from 'recommendations'
}

interface PersonalizedInsight {
  id: string;
  type: string; // Was: 'style' | 'color' | 'fit' | 'occasion' | 'trend'; Now string to accept backend values
  title: string;
  description: string;
  actionableAdvice: string; // Renamed from 'actionable'
  confidenceScore: number; // 0-100
  impactLevel: string; // Was: 'high' | 'medium' | 'low'; Now string
}

interface OutfitRecommendationPiece { // Helper for displaying pieces
  id: number;
  name: string;
  category: string;
  imageUrl?: string | null;
}
interface OutfitRecommendation {
  id: string; // Unique ID for frontend key, from outfit_id or generated
  title: string;
  imageUrl?: string | null;
  confidence: number; // 0-100
  styleMatchNotes?: string | null;
  occasionSuitability?: string | null;
  itemPieces: OutfitRecommendationPiece[]; // Transformed from backend's items
  dominantColors: string[]; // Derived from items
  description: string; // "Why this outfit is recommended"
  // shoppable: boolean; // Removed for now, can be added later
}

// Backend Schemas (for clarity during transformation)
interface BackendStyleProfileData {
  primary_style?: string | null;
  secondary_styles?: string[] | null;
  color_preferences?: string[] | null;
  body_type?: string | null;
  lifestyle?: string | null;
  brand_alignment?: string[] | null;
  fashion_goals?: string[] | null;
}
interface BackendStyleProfileInsights {
  style_confidence_score?: number | null; // 0.0 - 1.0
  wardrobe_versatility_score?: number | null; // 0.0 - 1.0
  style_summary?: string | null;
}
interface BackendUserStyleProfileResponse {
  profile_data: BackendStyleProfileData;
  generated_insights: BackendStyleProfileInsights;
}
interface BackendWardrobeItem { // Simplified for outfit recommendations
  id: number;
  name: string;
  category: string;
  image_url?: string | null;
  ai_dominant_colors?: string[] | null;
}
interface BackendAIStyleInsightOutfitRecommendation {
  outfit_id?: number | null;
  outfit_name: string;
  description: string;
  image_url?: string | null;
  items: BackendWardrobeItem[];
  confidence_score: number; // 0.0 - 1.0
  style_match_notes?: string | null;
  occasion_suitability?: string | null;
}
interface BackendPersonalizedGeneralInsight {
  id: string;
  insight_type: string;
  title: string;
  description: string;
  actionable_advice: string;
  confidence_score: number; // 0.0 - 1.0
  impact_level: string;
}
interface BackendWardrobeAnalysisDetails {
  total_items: number;
  category_breakdown: { [key: string]: number };
  color_distribution: { [key: string]: number };
  brand_diversity_score?: number | null; // 0.0 - 1.0
  average_item_price?: number | null;
  style_consistency_score?: number | null; // 0.0 - 1.0
  wardrobe_gaps?: string[] | null;
  improvement_suggestions?: string[] | null;
}
interface FullAIStyleInsightsResponse {
  user_profile: BackendUserStyleProfileResponse;
  wardrobe_analysis: BackendWardrobeAnalysisDetails;
  personalized_insights: BackendPersonalizedGeneralInsight[];
  suggested_outfits: BackendAIStyleInsightOutfitRecommendation[];
}

const AIStyleInsights = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [styleProfile, setStyleProfile] = useState<StyleProfile | null>(null);
  const [wardrobeAnalysis, setWardrobeAnalysis] = useState<WardrobeAnalysis | null>(null);
  const [insights, setInsights] = useState<PersonalizedInsight[]>([]);
  const [selectedTab, setSelectedTab] = useState('profile');
  const [uploadedPhoto, setUploadedPhoto] = useState<string | null>(null);
  const [outfitRecommendations, setOutfitRecommendations] = useState<OutfitRecommendation[]>([]);
  const { toast } = useToast();

  const generateStyleInsights = useCallback(async () => {
    setIsAnalyzing(true);
    try {
      const response = await apiClient.get<FullAIStyleInsightsResponse>('/users/me/style-insights');
      const data = response.data;

      // Transform UserProfile
      const profileData = data.user_profile.profile_data;
      const profileInsights = data.user_profile.generated_insights;
      setStyleProfile({
        primaryStyle: profileData.primary_style || 'Not specified',
        secondaryStyles: profileData.secondary_styles || [],
        colorPreferences: profileData.color_preferences || [],
        bodyType: profileData.body_type || 'Not specified',
        lifestyle: profileData.lifestyle || 'Not specified',
        confidenceLevel: Math.round((profileInsights.style_confidence_score || 0) * 100),
        versatilityScore: Math.round((profileInsights.wardrobe_versatility_score || 0) * 100),
        brandAlignment: profileData.brand_alignment || [],
        styleSummary: profileInsights.style_summary,
      });

      // Transform WardrobeAnalysis
      const backendAnalysis = data.wardrobe_analysis;
      setWardrobeAnalysis({
        totalItems: backendAnalysis.total_items,
        categoryBreakdown: backendAnalysis.category_breakdown || {},
        colorDistribution: backendAnalysis.color_distribution || {},
        brandDiversity: Math.round((backendAnalysis.brand_diversity_score || 0) * 100),
        averagePrice: backendAnalysis.average_item_price || null,
        styleConsistency: Math.round((backendAnalysis.style_consistency_score || 0) * 100),
        gaps: backendAnalysis.wardrobe_gaps || [],
        improvementSuggestions: backendAnalysis.improvement_suggestions || [],
      });

      // Transform PersonalizedInsights
      setInsights(data.personalized_insights.map(insight => ({
        id: insight.id,
        type: insight.insight_type,
        title: insight.title,
        description: insight.description,
        actionableAdvice: insight.actionable_advice,
        confidenceScore: Math.round(insight.confidence_score * 100),
        impactLevel: insight.impact_level,
      })));

      // Transform OutfitRecommendations
      setOutfitRecommendations(data.suggested_outfits.map((rec, index) => {
        let dominantColors: string[] = [];
        if (rec.items && rec.items.length > 0) {
          // Simple logic: take colors from the first item, or aggregate if complex logic is desired later
          dominantColors = rec.items[0].ai_dominant_colors || [];
        }
        return {
          id: rec.outfit_id?.toString() ?? `generated-${index}-${new Date().getTime()}`,
          title: rec.outfit_name,
          imageUrl: rec.image_url,
          confidence: Math.round(rec.confidence_score * 100),
          styleMatchNotes: rec.style_match_notes,
          occasionSuitability: rec.occasion_suitability,
          itemPieces: rec.items.map(item => ({
            id: item.id,
            name: item.name,
            category: item.category,
            imageUrl: item.image_url
          })),
          dominantColors: dominantColors,
          description: rec.description,
        };
      }));

      toast({ title: "Insights Generated", description: "Your AI style insights are ready." });
    } catch (error: any) {
      console.error("Failed to generate style insights:", error);
      const errorMsg = error.response?.data?.detail || "Could not load your style insights.";
      toast({ title: "Error", description: errorMsg, variant: "destructive" });
      setStyleProfile(null);
      setWardrobeAnalysis(null);
      setInsights([]);
      setOutfitRecommendations([]);
    } finally {
      setIsAnalyzing(false);
    }
  }, [toast]);

  useEffect(() => {
    generateStyleInsights();
  }, [generateStyleInsights]);

  const handlePhotoUpload = (file: File) => {
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setUploadedPhoto(e.target?.result as string);
        analyzePhoto(); // Call analyzePhoto, which will now show a "coming soon" toast
      };
      reader.readAsDataURL(file);
    }
  };

  const analyzePhoto = () => {
    // For now, this feature is mocked or pending backend integration
    toast({
      title: "Photo Analysis (Coming Soon)",
      description: "This feature is currently under development. Stay tuned!",
      variant: "info",
    });
    // If you had an isAnalyzingPhoto state:
    // setIsAnalyzingPhoto(true);
    // setTimeout(() => {
    //   setIsAnalyzingPhoto(false);
    //   toast({ title: "Mock Analysis Complete!", description: "Photo analysis feature is not yet live." });
    // }, 1500);
  };

  const getImpactColor = (impact: string) => {
    switch (impact.toLowerCase()) {
      case 'high': return 'text-red-600 bg-red-100 dark:text-red-300 dark:bg-red-900/30';
      case 'medium': return 'text-purple-600 bg-purple-100 dark:text-purple-300 dark:bg-purple-900/30';
      case 'low': return 'text-green-600 bg-green-100 dark:text-green-300 dark:bg-green-900/30';
      default: return 'text-gray-600 bg-gray-100 dark:text-gray-300 dark:bg-gray-700/30';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'style': return <Palette size={18} className="mr-2 text-pink-500" />;
      case 'color': return <BarChart3 size={18} className="mr-2 text-blue-500" />;
      case 'fit': return <Target size={18} className="mr-2 text-green-500" />;
      case 'occasion': return <Users size={18} className="mr-2 text-purple-500" />;
      case 'trend': return <TrendingUp size={18} className="mr-2 text-orange-500" />;
      case 'wardrobe_balance': return <PieChart size={18} className="mr-2 text-indigo-500" />;
      default: return <Lightbulb size={18} className="mr-2 text-gray-500" />;
    }
  };

  const renderSkeletonCard = (count = 1) => Array(count).fill(0).map((_, index) => (
    <Card key={`skel-${index}`} className="animate-pulse">
      <CardHeader><div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div></CardHeader>
      <CardContent className="space-y-3">
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
        <div className="h-8 bg-gray-300 dark:bg-gray-600 rounded w-1/2 mt-2"></div>
      </CardContent>
    </Card>
  ));


  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-purple-50 to-indigo-50 dark:from-gray-900 dark:via-purple-900 dark:to-indigo-900 p-4 sm:p-6">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="p-3 bg-gradient-to-r from-pink-600 to-purple-600 rounded-2xl shadow-lg">
              <Brain className="text-white" size={32} />
            </div>
            <h1 className="text-4xl sm:text-5xl font-bold bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent py-1">
              AI Style Oracle
            </h1>
          </div>
          <p className="text-lg sm:text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            Unlock deep insights into your style, wardrobe, and potential outfits.
          </p>
        </div>

        <Card className="mb-8 border-2 border-dashed border-pink-300 dark:border-pink-700/50 bg-white/50 dark:bg-gray-800/30 backdrop-blur-sm">
          <CardContent className="p-6">
            <div className="text-center">
              {uploadedPhoto ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
                  <img src={uploadedPhoto} alt="Uploaded outfit" className="max-h-72 mx-auto rounded-xl shadow-lg object-contain" />
                  <div className="text-left space-y-3 p-4 bg-white/70 dark:bg-gray-800/70 rounded-lg shadow">
                    <h3 className="text-xl font-bold text-gray-800 dark:text-white">AI Photo Analysis (Mock)</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-300">This is a mock analysis. Full feature coming soon!</p>
                    <div className="space-y-2 pt-2">
                      <div className="p-3 bg-green-50 dark:bg-green-900/30 rounded-lg text-sm">✨ Style Detected: Chic & Modern</div>
                      <div className="p-3 bg-blue-50 dark:bg-blue-900/30 rounded-lg text-sm">🎨 Color Harmony: 88%</div>
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  <Upload className="mx-auto mb-3 text-pink-500 dark:text-pink-400" size={40} />
                  <h3 className="text-lg font-semibold mb-2 text-gray-700 dark:text-white">Analyze an Outfit Photo</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">Get AI feedback on a specific look. (Feature coming soon)</p>
                  <label className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-lg cursor-pointer hover:scale-105 transition-transform shadow-md">
                    <Camera size={18} /> Choose Photo
                    <input type="file" accept="image/*" onChange={(e) => e.target.files?.[0] && handlePhotoUpload(e.target.files[0])} className="hidden"/>
                  </label>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-2 sm:grid-cols-4 bg-white/70 dark:bg-gray-800/70 rounded-xl p-1 shadow-lg backdrop-blur-sm">
            {['profile', 'recommendations', 'analysis', 'insights'].map(tabVal => (
               <TabsTrigger key={tabVal} value={tabVal} className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-pink-500 data-[state=active]:to-purple-500 data-[state=active]:text-white data-[state=active]:shadow-md transition-all">
                {tabVal === 'profile' && <Users size={16} />}
                {tabVal === 'recommendations' && <Sparkles size={16} />}
                {tabVal === 'analysis' && <PieChart size={16} />}
                {tabVal === 'insights' && <Brain size={16} />}
                <span className="capitalize">{tabVal === 'recommendations' ? 'Outfit Recs' : tabVal}</span>
              </TabsTrigger>
            ))}
          </TabsList>

          <TabsContent value="profile">
            {isAnalyzing && !styleProfile ? renderSkeletonCard(2) : styleProfile ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card><CardHeader><CardTitle className="flex items-center gap-2"><Palette className="text-pink-500"/>Style Identity</CardTitle></CardHeader>
                  <CardContent className="space-y-3">
                    <div><h4 className="font-medium text-sm text-gray-500 dark:text-gray-400">Primary Style</h4><p className="text-lg font-semibold text-gray-800 dark:text-white">{styleProfile.primaryStyle}</p></div>
                    {styleProfile.styleSummary && <div><h4 className="font-medium text-sm text-gray-500 dark:text-gray-400">AI Summary</h4><p className="text-sm text-gray-700 dark:text-gray-300">{styleProfile.styleSummary}</p></div>}
                    <div><h4 className="font-medium text-sm text-gray-500 dark:text-gray-400">Secondary Influences</h4><div className="flex flex-wrap gap-2 mt-1">{styleProfile.secondaryStyles.map((s,i)=>(<span key={i} className="px-2 py-0.5 bg-pink-100 dark:bg-pink-900/40 text-pink-700 dark:text-pink-300 rounded-full text-xs">{s}</span>))}</div></div>
                    <div><h4 className="font-medium text-sm text-gray-500 dark:text-gray-400">Color Preferences</h4><div className="flex flex-wrap gap-2 mt-1">{styleProfile.colorPreferences.map((c,i)=>(<span key={i} className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700/60 text-gray-700 dark:text-gray-300 rounded-full text-xs">{c}</span>))}</div></div>
                  </CardContent>
                </Card>
                <Card><CardHeader><CardTitle className="flex items-center gap-2"><Target className="text-purple-500"/>Personal Metrics</CardTitle></CardHeader>
                  <CardContent className="space-y-3">
                    <div className="grid grid-cols-2 gap-x-4 gap-y-3">
                      <div><h4 className="font-medium text-sm text-gray-500 dark:text-gray-400">Confidence Level</h4><p className="text-lg font-semibold text-gray-800 dark:text-white">{styleProfile.confidenceLevel}%</p></div>
                      <div><h4 className="font-medium text-sm text-gray-500 dark:text-gray-400">Versatility Score</h4><p className="text-lg font-semibold text-gray-800 dark:text-white">{styleProfile.versatilityScore}%</p></div>
                      <div><h4 className="font-medium text-sm text-gray-500 dark:text-gray-400">Body Type</h4><p className="text-gray-700 dark:text-gray-300">{styleProfile.bodyType}</p></div>
                      <div><h4 className="font-medium text-sm text-gray-500 dark:text-gray-400">Lifestyle</h4><p className="text-gray-700 dark:text-gray-300">{styleProfile.lifestyle}</p></div>
                    </div>
                    <div><h4 className="font-medium text-sm text-gray-500 dark:text-gray-400">Brand Alignment</h4><div className="flex flex-wrap gap-2 mt-1">{styleProfile.brandAlignment.map((b,i)=>(<span key={i} className="px-2 py-0.5 bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 rounded-full text-xs">{b}</span>))}</div></div>
                  </CardContent>
                </Card>
              </div>
            ) : <p className="text-center text-gray-500 dark:text-gray-400 py-8">No style profile data available.</p>}
          </TabsContent>

          <TabsContent value="recommendations">
            {isAnalyzing && outfitRecommendations.length === 0 ? renderSkeletonCard(4) : outfitRecommendations.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {outfitRecommendations.map(rec => (
                  <Card key={rec.id} className="group overflow-hidden transition-all hover:shadow-xl">
                    <div className="relative h-72 bg-gray-100 dark:bg-gray-700/50 flex items-center justify-center">
                      {rec.imageUrl ? <img src={rec.imageUrl} alt={rec.title} className="w-full h-full object-cover transition-transform group-hover:scale-105"/> : <ShoppingBag size={48} className="text-gray-400 dark:text-gray-500"/>}
                      <div className="absolute top-2 right-2 px-2 py-1 bg-black/50 text-white text-xs font-bold rounded">{rec.confidence}% Match</div>
                    </div>
                    <CardContent className="p-4 space-y-2">
                      <h3 className="font-semibold text-lg text-gray-800 dark:text-white truncate" title={rec.title}>{rec.title}</h3>
                      {rec.styleMatchNotes && <p className="text-xs text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/30 px-2 py-1 rounded inline-block">{rec.styleMatchNotes}</p>}
                      {rec.occasionSuitability && <p className="text-xs text-gray-500 dark:text-gray-400">Ideal for: {rec.occasionSuitability}</p>}
                      <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-2">{rec.description}</p>
                      <div><h5 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Key Pieces:</h5>
                        <div className="flex flex-wrap gap-1.5">
                          {rec.itemPieces.slice(0,3).map(p => (<span key={p.id} className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700/80 text-gray-700 dark:text-gray-300 rounded text-xs">{p.name}</span>))}
                          {rec.itemPieces.length > 3 && <span className="text-xs text-gray-500 dark:text-gray-400 self-end"> +{rec.itemPieces.length - 3} more</span>}
                        </div>
                      </div>
                      {rec.dominantColors.length > 0 && <div><h5 className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Dominant Colors:</h5><div className="flex gap-1.5">{rec.dominantColors.map((c,i)=>(<div key={i} className="w-4 h-4 rounded-full border border-gray-300 dark:border-gray-600" style={{backgroundColor:c}}></div>))}</div></div>}
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : <p className="text-center text-gray-500 dark:text-gray-400 py-8">No outfit recommendations available at this time.</p>}
          </TabsContent>

          <TabsContent value="analysis">
            {isAnalyzing && !wardrobeAnalysis ? renderSkeletonCard(3) : wardrobeAnalysis ? (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <Card><CardHeader><CardTitle className="flex items-center gap-2"><PieChart className="text-blue-500"/>Category Breakdown</CardTitle></CardHeader>
                  <CardContent className="space-y-2">{Object.entries(wardrobeAnalysis.categoryBreakdown).map(([cat,cnt])=>(<div key={cat} className="flex justify-between text-sm"><span className="text-gray-700 dark:text-gray-300">{cat}</span><span className="font-medium text-gray-800 dark:text-white">{cnt} items</span></div>))}</CardContent>
                </Card>
                <Card><CardHeader><CardTitle className="flex items-center gap-2"><Palette className="text-green-500"/>Color Distribution</CardTitle></CardHeader>
                  <CardContent className="space-y-2">{Object.entries(wardrobeAnalysis.colorDistribution).map(([col,cnt])=>(<div key={col} className="flex justify-between text-sm"><span className="text-gray-700 dark:text-gray-300">{col}</span><span className="font-medium text-gray-800 dark:text-white">{cnt} items</span></div>))}</CardContent>
                </Card>
                <Card><CardHeader><CardTitle className="flex items-center gap-2"><Activity className="text-purple-500"/>Wardrobe Health</CardTitle></CardHeader>
                  <CardContent className="space-y-3">
                    <div className="grid grid-cols-2 gap-3 text-center">
                      <div><p className="text-2xl font-bold text-gray-800 dark:text-white">{wardrobeAnalysis.totalItems}</p><p className="text-xs text-gray-500 dark:text-gray-400">Total Items</p></div>
                      <div><p className="text-2xl font-bold text-gray-800 dark:text-white">${wardrobeAnalysis.averagePrice?.toFixed(0) ?? 'N/A'}</p><p className="text-xs text-gray-500 dark:text-gray-400">Avg. Price</p></div>
                      <div><p className="text-2xl font-bold text-gray-800 dark:text-white">{wardrobeAnalysis.brandDiversity}%</p><p className="text-xs text-gray-500 dark:text-gray-400">Brand Diversity</p></div>
                      <div><p className="text-2xl font-bold text-gray-800 dark:text-white">{wardrobeAnalysis.styleConsistency}%</p><p className="text-xs text-gray-500 dark:text-gray-400">Style Consistency</p></div>
                    </div>
                    {wardrobeAnalysis.gaps.length > 0 && <div><h5 className="font-medium text-sm text-red-500 dark:text-red-400 mb-1">Identified Gaps:</h5><ul className="list-disc list-inside text-xs text-gray-600 dark:text-gray-300 space-y-0.5">{wardrobeAnalysis.gaps.map((g,i)=>(<li key={i}>{g}</li>))}</ul></div>}
                    {wardrobeAnalysis.improvementSuggestions.length > 0 && <div><h5 className="font-medium text-sm text-green-500 dark:text-green-400 mb-1">Suggestions:</h5><ul className="list-disc list-inside text-xs text-gray-600 dark:text-gray-300 space-y-0.5">{wardrobeAnalysis.improvementSuggestions.map((s,i)=>(<li key={i}>{s}</li>))}</ul></div>}
                  </CardContent>
                </Card>
              </div>
            ) : <p className="text-center text-gray-500 dark:text-gray-400 py-8">No wardrobe analysis data available.</p>}
          </TabsContent>

          <TabsContent value="insights">
            {isAnalyzing && insights.length === 0 ? renderSkeletonCard(3) : insights.length > 0 ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {insights.map(insight => (
                  <Card key={insight.id} className="hover:shadow-lg transition-shadow duration-300">
                    <CardHeader className="pb-3">
                      <div className="flex justify-between items-start">
                        <CardTitle className="text-lg flex items-center text-gray-800 dark:text-white">{getTypeIcon(insight.type)}{insight.title}</CardTitle>
                        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${getImpactColor(insight.impactLevel)}`}>{insight.impactLevel.toUpperCase()}</span>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <p className="text-sm text-gray-600 dark:text-gray-400">{insight.description}</p>
                      <div className="p-3 bg-gray-50 dark:bg-gray-700/30 rounded-md">
                        <h5 className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-0.5 flex items-center"><Info size={12} className="mr-1.5 text-purple-500"/>Actionable Advice:</h5>
                        <p className="text-xs text-purple-700 dark:text-purple-300">{insight.actionableAdvice}</p>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 pt-1">AI Confidence: {insight.confidenceScore}%</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : <p className="text-center text-gray-500 dark:text-gray-400 py-8">No personalized insights available at this time.</p>}
          </TabsContent>
        </Tabs>

        {isAnalyzing && (selectedTab !== 'profile' && selectedTab !== 'analysis' && selectedTab !== 'insights' && selectedTab !== 'recommendations') && ( // More generic loader if tab not matching specific loaders
          <div className="fixed inset-0 bg-black/30 z-50 flex flex-col items-center justify-center backdrop-blur-sm">
            <Loader2 className="h-16 w-16 text-pink-500 animate-spin mb-4" />
            <p className="text-lg text-white font-semibold">AI Oracle is Deep in Thought...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIStyleInsights;
