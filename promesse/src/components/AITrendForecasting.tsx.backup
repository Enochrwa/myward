
import React, { useState, useEffect } from 'react';
import { TrendingUp, Sparkles, Eye, Heart, Share2, Camera, Upload, Zap, Crown, Star, Globe, Calendar, Users, Award } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';

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
  priceRange: string;
  occasion: string[];
}

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

  useEffect(() => {
    generateForecast();
  }, []);

  const generateForecast = () => {
    setIsForecasting(true);
    
    setTimeout(() => {
      const mockForecast: ForecastResult = {
        trends: [
          {
            id: '1',
            name: 'Neo-Cottagecore',
            category: 'Aesthetic Movement',
            popularity: 94,
            growth: 267,
            description: 'A futuristic take on cottagecore with sustainable tech fabrics and earthy tones',
            colors: ['Sage Green', 'Mushroom Brown', 'Lavender', 'Cream'],
            season: 'Spring 2025',
            confidence: 96,
            outfitImages: [
              'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400',
              'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=400',
              'https://images.unsplash.com/photo-1539008835657-9e8e9680c956?w=400'
            ],
            celebrities: ['Emma Stone', 'Zendaya', 'Anya Taylor-Joy'],
            hashtags: ['#NeoCottagecore', '#SustainableFashion', '#TechNature'],
            priceRange: '$80-$300',
            occasion: ['Casual', 'Work from Home', 'Weekend']
          },
          {
            id: '2',
            name: 'Cyber-Minimalism',
            category: 'Fashion Tech',
            popularity: 89,
            growth: 189,
            description: 'Clean lines meet smart fabrics with embedded tech and holographic accents',
            colors: ['Chrome Silver', 'Deep Black', 'Electric Blue', 'Pure White'],
            season: 'Fall 2025',
            confidence: 92,
            outfitImages: [
              'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=400',
              'https://images.unsplash.com/photo-1566479179817-c08cf5b4394e?w=400',
              'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400'
            ],
            celebrities: ['Grimes', 'Tilda Swinton', 'Janelle Monáe'],
            hashtags: ['#CyberMinimal', '#TechWear', '#FutureFashion'],
            priceRange: '$150-$800',
            occasion: ['Night Out', 'Creative Events', 'Future Work']
          },
          {
            id: '3',
            name: 'Maximalist Renaissance',
            category: 'Aesthetic Revival',
            popularity: 76,
            growth: 234,
            description: 'Bold patterns, rich textures, and ornate details inspired by historical opulence',
            colors: ['Royal Purple', 'Gold', 'Emerald', 'Burgundy'],
            season: 'Year-round',
            confidence: 88,
            outfitImages: [
              'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=400',
              'https://images.unsplash.com/photo-1544957992-20514f595d6f?w=400',
              'https://images.unsplash.com/photo-1495385794356-15371f348c31?w=400'
            ],
            celebrities: ['Billy Porter', 'Lady Gaga', 'Harry Styles'],
            hashtags: ['#MaximalistFashion', '#Renaissance', '#BoldStyle'],
            priceRange: '$200-$1200',
            occasion: ['Formal Events', 'Art Galleries', 'Special Occasions']
          }
        ],
        personalizedRecommendations: {
          mustHave: ['Smart casual blazer with tech integration', 'Sustainable denim with bio-based fibers', 'Color-changing accessories'],
          avoid: ['Fast fashion basics', 'Non-sustainable materials', 'Overly trend-specific pieces'],
          investIn: ['Quality outerwear with climate adaptability', 'Versatile tech-enhanced pieces', 'Timeless silhouettes with modern twists']
        },
        seasonalPredictions: {
          emerging: ['Biometric jewelry', 'Climate-responsive clothing', 'AR-enhanced accessories'],
          declining: ['Logo-heavy designs', 'Single-use fashion', 'Non-functional embellishments'],
          stable: ['Classic denim', 'White button-downs', 'Little black dress']
        }
      };
      
      setForecast(mockForecast);
      setIsForecasting(false);
      
      toast({
        title: "🔮 AI Forecast Complete!",
        description: "Advanced trend analysis using global fashion intelligence.",
      });
    }, 3000);
  };

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
  };

  const getTrendIcon = (category: string) => {
    switch (category) {
      case 'Fashion Tech': return <Zap className="text-blue-500" />;
      case 'Aesthetic Movement': return <Sparkles className="text-green-500" />;
      case 'Aesthetic Revival': return <Crown className="text-purple-500" />;
      default: return <TrendingUp className="text-pink-500" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-indigo-900 dark:to-purple-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Enhanced Header */}
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

        {/* Mode Selector */}
        <div className="flex justify-center mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-2 shadow-xl">
            {[
              { id: 'trends', label: 'Trend Forecast', icon: TrendingUp },
              { id: 'photo', label: 'Photo Analysis', icon: Camera },
              { id: 'ai-generate', label: 'AI Generate', icon: Sparkles }
            ].map(mode => (
              <button
                key={mode.id}
                onClick={() => setAnalysisMode(mode.id as any)}
                className={`px-6 py-3 rounded-xl flex items-center gap-2 transition-all ${
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

        {/* Photo Upload Section */}
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
                        ✨ Detected: Modern Casual • 🎨 Dominant Colors: Navy, White • 📈 Trend Alignment: 87%
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
        )}

        {isForecasting ? (
          <div className="text-center py-20">
            <div className="animate-spin rounded-full h-20 w-20 border-b-4 border-indigo-600 mx-auto mb-6"></div>
            <h3 className="text-2xl font-bold mb-3">AI Fashion Oracle</h3>
            <p className="text-gray-600 dark:text-gray-400">Analyzing global fashion data, celebrity trends, and cultural movements...</p>
            <div className="mt-6 flex justify-center space-x-3">
              <div className="w-3 h-3 bg-indigo-600 rounded-full animate-pulse"></div>
              <div className="w-3 h-3 bg-purple-600 rounded-full animate-pulse delay-100"></div>
              <div className="w-3 h-3 bg-pink-600 rounded-full animate-pulse delay-200"></div>
            </div>
          </div>
        ) : forecast && analysisMode === 'trends' && (
          <div className="space-y-8">
            {/* Trending Now Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {forecast.trends.map(trend => (
                <Card 
                  key={trend.id} 
                  className="group hover:shadow-2xl transition-all duration-300 cursor-pointer border-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg"
                  onClick={() => setSelectedTrend(trend)}
                >
                  <CardHeader className="pb-3">
                    <div className="flex justify-between items-start">
                      <CardTitle className="text-xl flex items-center gap-2">
                        {getTrendIcon(trend.category)}
                        {trend.name}
                      </CardTitle>
                      <span className="text-xs bg-gradient-to-r from-green-500 to-emerald-600 text-white px-2 py-1 rounded-full">
                        +{trend.growth}%
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{trend.category}</p>
                  </CardHeader>
                  
                  <CardContent className="space-y-4">
                    {/* Outfit Images */}
                    <div className="grid grid-cols-3 gap-2">
                      {trend.outfitImages.map((image, i) => (
                        <div key={i} className="relative group">
                          <img 
                            src={image} 
                            alt={`${trend.name} outfit ${i + 1}`}
                            className="w-full h-20 object-cover rounded-lg group-hover:scale-105 transition-transform"
                          />
                          <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center">
                            <Eye size={16} className="text-white" />
                          </div>
                        </div>
                      ))}
                    </div>
                    
                    <p className="text-sm text-gray-700 dark:text-gray-300">{trend.description}</p>
                    
                    {/* Trend Metrics */}
                    <div className="grid grid-cols-2 gap-3">
                      <div className="text-center p-2 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg">
                        <div className="text-lg font-bold text-blue-600">{trend.popularity}%</div>
                        <div className="text-xs text-gray-600">Popularity</div>
                      </div>
                      <div className="text-center p-2 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg">
                        <div className="text-lg font-bold text-green-600">{trend.confidence}%</div>
                        <div className="text-xs text-gray-600">AI Confidence</div>
                      </div>
                    </div>
                    
                    {/* Color Palette */}
                    <div>
                      <h4 className="text-sm font-medium mb-2">Key Colors</h4>
                      <div className="flex gap-1">
                        {trend.colors.map((color, i) => (
                          <div key={i} className="flex-1 h-6 rounded" style={{backgroundColor: color.toLowerCase().replace(' ', '')}}></div>
                        ))}
                      </div>
                    </div>
                    
                    {/* Celebrities */}
                    <div className="flex items-center gap-2">
                      <Star size={14} className="text-yellow-500" />
                      <span className="text-xs text-gray-600">{trend.celebrities.join(', ')}</span>
                    </div>
                    
                    {/* Actions */}
                    <div className="flex gap-2 pt-2">
                      <Button size="sm" className="flex-1 bg-gradient-to-r from-pink-500 to-purple-600">
                        <Heart size={14} className="mr-1" />
                        Save
                      </Button>
                      <Button size="sm" variant="outline" className="flex-1">
                        <Share2 size={14} className="mr-1" />
                        Share
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Personalized Insights */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-green-700 dark:text-green-400">
                    <Award size={20} />
                    Must Have
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {forecast.personalizedRecommendations.mustHave.map((item, i) => (
                      <li key={i} className="text-sm flex items-start gap-2">
                        <span className="text-green-600">•</span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-blue-700 dark:text-blue-400">
                    <Globe size={20} />
                    Invest In
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {forecast.personalizedRecommendations.investIn.map((item, i) => (
                      <li key={i} className="text-sm flex items-start gap-2">
                        <span className="text-blue-600">•</span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-br from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-red-700 dark:text-red-400">
                    <Calendar size={20} />
                    Avoid
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {forecast.personalizedRecommendations.avoid.map((item, i) => (
                      <li key={i} className="text-sm flex items-start gap-2">
                        <span className="text-red-600">•</span>
                        {item}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* Trend Detail Modal */}
        {selectedTrend && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
            <Card className="max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-2xl">{selectedTrend.name}</CardTitle>
                    <p className="text-gray-600">{selectedTrend.description}</p>
                  </div>
                  <Button variant="ghost" onClick={() => setSelectedTrend(null)}>×</Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      {selectedTrend.outfitImages.map((image, i) => (
                        <img key={i} src={image} alt={`Outfit ${i + 1}`} className="w-full h-48 object-cover rounded-lg" />
                      ))}
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-bold mb-2">Hashtags</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedTrend.hashtags.map((tag, i) => (
                          <span key={i} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="font-bold mb-2">Price Range</h4>
                      <p className="text-lg font-semibold text-green-600">{selectedTrend.priceRange}</p>
                    </div>
                    <div>
                      <h4 className="font-bold mb-2">Perfect For</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedTrend.occasion.map((occ, i) => (
                          <span key={i} className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-sm">
                            {occ}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default AITrendForecasting;
