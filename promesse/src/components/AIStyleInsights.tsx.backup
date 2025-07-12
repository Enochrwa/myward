import React, { useState, useEffect } from 'react';
import { Brain, Target, Palette, Users, TrendingUp, Heart, Star, BarChart3, PieChart, Activity, Camera, Upload, Sparkles, Zap, Crown, Award, Eye, Share2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';

interface StyleProfile {
  primaryStyle: string;
  secondaryStyles: string[];
  colorPreferences: string[];
  bodyType: string;
  lifestyle: string;
  confidenceLevel: number;
  versatilityScore: number;
  brandAlignment: string[];
}

interface WardrobeAnalysis {
  totalItems: number;
  categoryBreakdown: { [key: string]: number };
  colorDistribution: { [key: string]: number };
  brandDiversity: number;
  averagePrice: number;
  styleConsistency: number;
  gaps: string[];
  recommendations: string[];
}

interface PersonalizedInsight {
  id: string;
  type: 'style' | 'color' | 'fit' | 'occasion' | 'trend';
  title: string;
  description: string;
  actionable: string;
  confidence: number;
  impact: 'high' | 'medium' | 'low';
}

interface OutfitRecommendation {
  id: string;
  title: string;
  image: string;
  confidence: number;
  style: string;
  occasion: string;
  colors: string[];
  pieces: string[];
  why: string;
  shoppable: boolean;
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

  useEffect(() => {
    generateStyleInsights();
  }, []);

  const generateStyleInsights = () => {
    setIsAnalyzing(true);
    
    setTimeout(() => {
      const mockProfile: StyleProfile = {
        primaryStyle: 'Modern Minimalist',
        secondaryStyles: ['Classic Professional', 'Casual Chic', 'Bohemian Touch'],
        colorPreferences: ['Navy', 'White', 'Beige', 'Black', 'Soft Pink'],
        bodyType: 'Rectangular',
        lifestyle: 'Professional Creative',
        confidenceLevel: 78,
        versatilityScore: 85,
        brandAlignment: ['Everlane', 'COS', 'Uniqlo', 'Madewell']
      };

      const mockAnalysis: WardrobeAnalysis = {
        totalItems: 127,
        categoryBreakdown: {
          'Tops': 35,
          'Bottoms': 18,
          'Dresses': 12,
          'Outerwear': 8,
          'Shoes': 24,
          'Accessories': 30
        },
        colorDistribution: {
          'Black': 28,
          'White': 22,
          'Navy': 18,
          'Gray': 15,
          'Beige': 12,
          'Other': 32
        },
        brandDiversity: 67,
        averagePrice: 89,
        styleConsistency: 82,
        gaps: ['Formal Evening Wear', 'Casual Summer Dresses', 'Statement Jewelry'],
        recommendations: [
          'Add colorful statement pieces to brighten your wardrobe',
          'Invest in quality leather accessories',
          'Consider textured fabrics for visual interest',
          'Expand your occasion wear collection'
        ]
      };

      const mockInsights: PersonalizedInsight[] = [
        {
          id: '1',
          type: 'style',
          title: 'Style Evolution Opportunity',
          description: 'Your style leans heavily minimalist, but incorporating 15% more texture and pattern could enhance visual interest while maintaining your aesthetic.',
          actionable: 'Try adding a textured blazer or patterned scarf to your next outfit',
          confidence: 89,
          impact: 'high'
        },
        {
          id: '2',
          type: 'color',
          title: 'Color Psychology Insight',
          description: 'Your neutral palette projects professionalism, but adding strategic pops of coral or emerald could boost your confidence and presence.',
          actionable: 'Introduce one colorful accent piece per week',
          confidence: 76,
          impact: 'medium'
        },
        {
          id: '3',
          type: 'fit',
          title: 'Silhouette Optimization',
          description: 'Based on your body type, high-waisted bottoms and structured shoulders would enhance your natural proportions.',
          actionable: 'Focus on high-waisted pants and blazers with defined shoulders',
          confidence: 92,
          impact: 'high'
        },
        {
          id: '4',
          type: 'occasion',
          title: 'Versatility Gap',
          description: 'Your wardrobe excels in professional settings but lacks options for formal evening events.',
          actionable: 'Invest in one elegant dress and statement jewelry',
          confidence: 84,
          impact: 'medium'
        },
        {
          id: '5',
          type: 'trend',
          title: 'Trend Integration',
          description: 'The "quiet luxury" trend aligns perfectly with your aesthetic. Embrace subtle textures and refined fabrics.',
          actionable: 'Look for cashmere, silk, or high-quality cotton pieces',
          confidence: 91,
          impact: 'high'
        }
      ];

      const mockRecommendations: OutfitRecommendation[] = [
        {
          id: '1',
          title: 'Power Professional',
          image: 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400',
          confidence: 95,
          style: 'Business Chic',
          occasion: 'Important Meeting',
          colors: ['Navy', 'White', 'Gold'],
          pieces: ['Tailored blazer', 'Silk blouse', 'High-waisted trousers', 'Statement watch'],
          why: 'Perfect for commanding respect while maintaining elegance',
          shoppable: true
        },
        {
          id: '2',
          title: 'Weekend Wanderer',
          image: 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=400',
          confidence: 92,
          style: 'Casual Chic',
          occasion: 'Weekend Brunch',
          colors: ['Sage', 'Cream', 'Tan'],
          pieces: ['Oversized sweater', 'High-waisted jeans', 'White sneakers', 'Canvas bag'],
          why: 'Effortlessly stylish for relaxed weekend activities',
          shoppable: true
        },
        {
          id: '3',
          title: 'Evening Elegance',
          image: 'https://images.unsplash.com/photo-1539008835657-9e8e9680c956?w=400',
          confidence: 88,
          style: 'Sophisticated Glam',
          occasion: 'Dinner Date',
          colors: ['Black', 'Gold', 'Deep Red'],
          pieces: ['Little black dress', 'Statement earrings', 'Heeled boots', 'Clutch'],
          why: 'Timeless elegance with modern edge',
          shoppable: true
        },
        {
          id: '4',
          title: 'Creative Catalyst',
          image: 'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=400',
          confidence: 90,
          style: 'Artistic Edge',
          occasion: 'Gallery Opening',
          colors: ['Black', 'White', 'Electric Blue'],
          pieces: ['Asymmetric top', 'Wide-leg pants', 'Statement jewelry', 'Bold shoes'],
          why: 'Express your creative side with architectural silhouettes',
          shoppable: true
        }
      ];

      setStyleProfile(mockProfile);
      setWardrobeAnalysis(mockAnalysis);
      setInsights(mockInsights);
      setOutfitRecommendations(mockRecommendations);
      setIsAnalyzing(false);
    }, 2500);
  };

  const handlePhotoUpload = (file: File) => {
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setUploadedPhoto(e.target?.result as string);
        analyzePhoto();
      };
      reader.readAsDataURL(file);
      
      toast({
        title: "📸 Photo Analysis Started",
        description: "AI is analyzing your outfit and generating personalized insights...",
      });
    }
  };

  const analyzePhoto = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
      toast({
        title: "✨ Analysis Complete!",
        description: "Your style has been analyzed with advanced AI fashion intelligence.",
      });
    }, 2000);
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'text-red-600 bg-red-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'style': return <Palette size={16} />;
      case 'color': return <BarChart3 size={16} />;
      case 'fit': return <Target size={16} />;
      case 'occasion': return <Users size={16} />;
      case 'trend': return <TrendingUp size={16} />;
      default: return <Brain size={16} />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-purple-50 to-indigo-50 dark:from-gray-900 dark:via-purple-900 dark:to-indigo-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Enhanced Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="p-3 bg-gradient-to-r from-pink-600 to-purple-600 rounded-2xl">
              <Brain className="text-white" size={32} />
            </div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
              AI Style Oracle
            </h1>
          </div>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            Advanced style intelligence with outfit recommendations and photo analysis
          </p>
        </div>

        {/* Photo Upload Section */}
        <Card className="mb-8 border-2 border-dashed border-pink-300 dark:border-pink-700">
          <CardContent className="p-6">
            <div className="text-center">
              {uploadedPhoto ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <img src={uploadedPhoto} alt="Uploaded outfit" className="max-h-64 mx-auto rounded-xl shadow-lg" />
                  </div>
                  <div className="text-left space-y-4">
                    <h3 className="text-xl font-bold">AI Style Analysis</h3>
                    <div className="space-y-2">
                      <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <p className="text-sm"><strong>Style Detected:</strong> Modern Minimalist</p>
                      </div>
                      <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <p className="text-sm"><strong>Color Harmony:</strong> 92% (Excellent)</p>
                      </div>
                      <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                        <p className="text-sm"><strong>Fit Assessment:</strong> Well-tailored</p>
                      </div>
                      <div className="p-3 bg-pink-50 dark:bg-pink-900/20 rounded-lg">
                        <p className="text-sm"><strong>Occasion Match:</strong> Professional/Casual</p>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  <Upload className="mx-auto mb-4 text-pink-500" size={48} />
                  <h3 className="text-xl font-bold mb-2">Upload Your Outfit Photo</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Get instant AI analysis and personalized style recommendations
                  </p>
                  <label className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-pink-600 to-purple-600 text-white rounded-xl cursor-pointer hover:scale-105 transition-transform">
                    <Camera size={20} />
                    Choose Photo
                    <input
                      type="file"
                      accept="image/*"
                      onChange={(e) => e.target.files?.[0] && handlePhotoUpload(e.target.files[0])}
                      className="hidden"
                    />
                  </label>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Enhanced Tabs */}
        <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-8">
          <TabsList className="grid w-full grid-cols-4 bg-white dark:bg-gray-800 rounded-xl p-1 shadow-lg">
            <TabsTrigger value="profile" className="flex items-center gap-2">
              <Users size={16} />
              Style Profile
            </TabsTrigger>
            <TabsTrigger value="recommendations" className="flex items-center gap-2">
              <Sparkles size={16} />
              Outfit Recs
            </TabsTrigger>
            <TabsTrigger value="analysis" className="flex items-center gap-2">
              <PieChart size={16} />
              Wardrobe Analysis
            </TabsTrigger>
            <TabsTrigger value="insights" className="flex items-center gap-2">
              <Brain size={16} />
              AI Insights
            </TabsTrigger>
          </TabsList>

          {/* Outfit Recommendations Tab */}
          <TabsContent value="recommendations" className="space-y-6">
            <div className="text-center mb-6">
              <h2 className="text-3xl font-bold mb-2">AI Outfit Recommendations</h2>
              <p className="text-gray-600 dark:text-gray-400">Curated looks based on your style profile and current trends</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
              {outfitRecommendations.map(outfit => (
                <Card key={outfit.id} className="group hover:shadow-2xl transition-all duration-300 overflow-hidden">
                  <div className="relative">
                    <img 
                      src={outfit.image} 
                      alt={outfit.title}
                      className="w-full h-64 object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                    <div className="absolute top-3 right-3 bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm px-2 py-1 rounded-full">
                      <span className="text-xs font-bold text-green-600">{outfit.confidence}%</span>
                    </div>
                    <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                      <div className="absolute bottom-4 left-4 right-4 flex gap-2">
                        <Button size="sm" className="flex-1 bg-white/20 backdrop-blur-sm border border-white/30">
                          <Eye size={14} className="mr-1" />
                          View
                        </Button>
                        <Button size="sm" className="flex-1 bg-white/20 backdrop-blur-sm border border-white/30">
                          <Heart size={14} className="mr-1" />
                          Save
                        </Button>
                      </div>
                    </div>
                  </div>
                  
                  <CardContent className="p-4">
                    <div className="space-y-3">
                      <div>
                        <h3 className="font-bold text-lg">{outfit.title}</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{outfit.style} • {outfit.occasion}</p>
                      </div>
                      
                      <div className="flex gap-1">
                        {outfit.colors.map((color, i) => (
                          <div 
                            key={i} 
                            className="w-6 h-6 rounded-full border-2 border-white shadow-sm" 
                            style={{backgroundColor: color.toLowerCase()}}
                          ></div>
                        ))}
                      </div>
                      
                      <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2">{outfit.why}</p>
                      
                      <div className="flex gap-2">
                        <Button size="sm" className="flex-1 bg-gradient-to-r from-pink-500 to-purple-600">
                          <Sparkles size={14} className="mr-1" />
                          Try It
                        </Button>
                        <Button size="sm" variant="outline" className="flex-1">
                          <Share2 size={14} className="mr-1" />
                          Shop
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Style Profile Tab */}
          <TabsContent value="profile" className="space-y-6">
            {styleProfile && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Palette className="text-pink-600" />
                      Style Identity
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="font-medium mb-2">Primary Style</h4>
                      <div className="text-2xl font-bold text-pink-600">{styleProfile.primaryStyle}</div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium mb-2">Secondary Influences</h4>
                      <div className="flex flex-wrap gap-2">
                        {styleProfile.secondaryStyles.map((style, i) => (
                          <span key={i} className="px-3 py-1 bg-pink-100 dark:bg-pink-900/30 text-pink-700 dark:text-pink-300 rounded-full text-sm">
                            {style}
                          </span>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium mb-2">Color Preferences</h4>
                      <div className="flex gap-2">
                        {styleProfile.colorPreferences.map((color, i) => (
                          <div key={i} className="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded text-sm">
                            {color}
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Target className="text-purple-600" />
                      Personal Metrics
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-medium mb-1">Style Confidence</h4>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div 
                              className="bg-gradient-to-r from-pink-600 to-purple-600 h-2 rounded-full" 
                              style={{width: `${styleProfile.confidenceLevel}%`}}
                            ></div>
                          </div>
                          <span className="text-sm font-medium">{styleProfile.confidenceLevel}%</span>
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="font-medium mb-1">Versatility Score</h4>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div 
                              className="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded-full" 
                              style={{width: `${styleProfile.versatilityScore}%`}}
                            ></div>
                          </div>
                          <span className="text-sm font-medium">{styleProfile.versatilityScore}%</span>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium mb-2">Body Type</h4>
                      <div className="text-lg">{styleProfile.bodyType}</div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium mb-2">Lifestyle</h4>
                      <div className="text-lg">{styleProfile.lifestyle}</div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium mb-2">Brand Alignment</h4>
                      <div className="flex flex-wrap gap-2">
                        {styleProfile.brandAlignment.map((brand, i) => (
                          <span key={i} className="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded text-sm">
                            {brand}
                          </span>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>

          {/* Wardrobe Analysis Tab */}
          <TabsContent value="analysis" className="space-y-6">
            {wardrobeAnalysis && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <PieChart className="text-blue-600" />
                      Category Breakdown
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {Object.entries(wardrobeAnalysis.categoryBreakdown).map(([category, count]) => (
                        <div key={category} className="flex justify-between items-center">
                          <span className="text-sm">{category}</span>
                          <div className="flex items-center gap-2">
                            <div className="w-20 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                              <div 
                                className="bg-blue-600 h-2 rounded-full" 
                                style={{width: `${(count / wardrobeAnalysis.totalItems) * 100}%`}}
                              ></div>
                            </div>
                            <span className="text-sm font-medium">{count}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Palette className="text-green-600" />
                      Color Distribution
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {Object.entries(wardrobeAnalysis.colorDistribution).map(([color, count]) => (
                        <div key={color} className="flex justify-between items-center">
                          <span className="text-sm">{color}</span>
                          <div className="flex items-center gap-2">
                            <div className="w-20 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                              <div 
                                className="bg-green-600 h-2 rounded-full" 
                                style={{width: `${(count / wardrobeAnalysis.totalItems) * 100}%`}}
                              ></div>
                            </div>
                            <span className="text-sm font-medium">{count}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Activity className="text-purple-600" />
                      Wardrobe Health
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-center">
                      <div>
                        <div className="text-2xl font-bold text-purple-600">{wardrobeAnalysis.totalItems}</div>
                        <div className="text-sm text-gray-600">Total Items</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold text-green-600">${wardrobeAnalysis.averagePrice}</div>
                        <div className="text-sm text-gray-600">Avg. Price</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold text-blue-600">{wardrobeAnalysis.brandDiversity}%</div>
                        <div className="text-sm text-gray-600">Brand Diversity</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold text-pink-600">{wardrobeAnalysis.styleConsistency}%</div>
                        <div className="text-sm text-gray-600">Style Consistency</div>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium mb-2 text-red-600">Wardrobe Gaps</h4>
                      <div className="space-y-1">
                        {wardrobeAnalysis.gaps.map((gap, i) => (
                          <div key={i} className="text-sm text-gray-600 dark:text-gray-400">• {gap}</div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>

          {/* AI Insights Tab */}
          <TabsContent value="insights" className="space-y-6">
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold">Personalized Recommendations</h2>
                <Button onClick={generateStyleInsights} className="bg-gradient-to-r from-pink-600 to-purple-600">
                  <Brain className="mr-2" size={16} />
                  Refresh Insights
                </Button>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {insights.map(insight => (
                  <Card key={insight.id} className="hover:shadow-lg transition-shadow">
                    <CardHeader className="pb-3">
                      <div className="flex justify-between items-start">
                        <CardTitle className="text-lg flex items-center gap-2">
                          {getTypeIcon(insight.type)}
                          {insight.title}
                        </CardTitle>
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(insight.impact)}`}>
                            {insight.impact.toUpperCase()}
                          </span>
                          <span className="text-sm text-gray-500">{insight.confidence}%</span>
                        </div>
                      </div>
                    </CardHeader>
                    
                    <CardContent>
                      <p className="text-gray-600 dark:text-gray-400 mb-3">{insight.description}</p>
                      <div className="p-3 bg-gradient-to-r from-pink-50 to-purple-50 dark:from-pink-900/20 dark:to-purple-900/20 rounded-lg">
                        <h4 className="font-medium text-sm mb-1">Actionable Step:</h4>
                        <p className="text-sm">{insight.actionable}</p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </TabsContent>
        </Tabs>

        {isAnalyzing && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
            <Card className="p-8 text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-pink-600 mx-auto mb-4"></div>
              <h3 className="text-xl font-bold mb-2">AI Style Intelligence</h3>
              <p className="text-gray-600 dark:text-gray-400">Analyzing your style patterns, preferences, and wardrobe data...</p>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIStyleInsights;
