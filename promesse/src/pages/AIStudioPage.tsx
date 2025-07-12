import React, { useState } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Sparkles, 
  Search, 
  Calendar, 
  Brain, 
  TrendingUp, 
  Palette, 
  Zap,
  ArrowRight,
  Star,
  Heart,
  Users,
  BarChart3,
  Settings,
  ChevronRight
} from 'lucide-react';

// Import the new components
import IntelligentMatching from '@/components/IntelligentMatching';
import AdvancedSearch from '@/components/AdvancedSearch';
import OccasionRecommendations from '@/components/OccasionRecommendations';

const AIStudioPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [activeFeature, setActiveFeature] = useState('overview');

  const aiFeatures = [
    {
      id: 'intelligent-matching',
      title: 'Intelligent Matching',
      description: 'AI-powered clothing combinations using color theory and style analysis',
      icon: Sparkles,
      color: 'purple',
      stats: { accuracy: '92%', combinations: '1000+' },
      component: IntelligentMatching
    },
    {
      id: 'advanced-search',
      title: 'Advanced Search',
      description: 'Smart search with intelligent filters and compatibility scoring',
      icon: Search,
      color: 'blue',
      stats: { filters: '15+', speed: '< 1s' },
      component: AdvancedSearch
    },
    {
      id: 'occasion-recommendations',
      title: 'Occasion Recommendations',
      description: 'Weather-aware and event-specific outfit suggestions',
      icon: Calendar,
      color: 'green',
      stats: { occasions: '15+', accuracy: '89%' },
      component: OccasionRecommendations
    }
  ];

  const handleFeatureClick = (featureId: string) => {
    setActiveFeature(featureId);
    navigate(`/ai-studio/${featureId}`);
  };

  const renderOverview = () => (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4 py-8">
        <div className="flex items-center justify-center gap-3 mb-4">
          <div className="p-3 bg-gradient-to-br from-purple-500 to-blue-600 rounded-xl">
            <Brain className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            AI Studio
          </h1>
        </div>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Unlock the power of artificial intelligence to revolutionize your wardrobe management
        </p>
        <div className="flex items-center justify-center gap-4 pt-4">
          <Badge variant="secondary" className="px-3 py-1">
            <Zap className="h-3 w-3 mr-1" />
            Powered by AI
          </Badge>
          <Badge variant="secondary" className="px-3 py-1">
            <TrendingUp className="h-3 w-3 mr-1" />
            92% Accuracy
          </Badge>
          <Badge variant="secondary" className="px-3 py-1">
            <Users className="h-3 w-3 mr-1" />
            Personalized
          </Badge>
        </div>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {aiFeatures.map((feature) => (
          <Card 
            key={feature.id} 
            className="group hover:shadow-xl transition-all duration-300 cursor-pointer border-2 hover:border-purple-200"
            onClick={() => handleFeatureClick(feature.id)}
          >
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div className={`p-3 rounded-lg bg-${feature.color}-100`}>
                  <feature.icon className={`h-6 w-6 text-${feature.color}-600`} />
                </div>
                <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-purple-600 transition-colors" />
              </div>
              <CardTitle className="text-xl group-hover:text-purple-600 transition-colors">
                {feature.title}
              </CardTitle>
              <CardDescription className="text-base">
                {feature.description}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                {Object.entries(feature.stats).map(([key, value]) => (
                  <div key={key} className="text-center">
                    <div className="font-bold text-lg">{value}</div>
                    <div className="text-xs text-muted-foreground capitalize">{key}</div>
                  </div>
                ))}
              </div>
              <Button 
                className="w-full group-hover:bg-purple-600 transition-colors"
                onClick={(e) => {
                  e.stopPropagation();
                  handleFeatureClick(feature.id);
                }}
              >
                Try {feature.title}
                <ChevronRight className="h-4 w-4 ml-2" />
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Stats Section */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 py-8">
        <Card>
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-purple-600 mb-2">10K+</div>
            <div className="text-sm text-muted-foreground">Outfit Combinations</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">92%</div>
            <div className="text-sm text-muted-foreground">Match Accuracy</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">15+</div>
            <div className="text-sm text-muted-foreground">Occasions Supported</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-orange-600 mb-2">&lt; 1s</div>
            <div className="text-sm text-muted-foreground">Response Time</div>
          </CardContent>
        </Card>
      </div>

      {/* How It Works */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            How AI Studio Works
          </CardTitle>
          <CardDescription>
            Our AI algorithms analyze multiple factors to provide intelligent recommendations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center space-y-3">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto">
                <Palette className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="font-semibold">Color Analysis</h3>
              <p className="text-sm text-muted-foreground">
                Advanced color theory algorithms analyze harmony, contrast, and seasonal palettes
              </p>
            </div>
            <div className="text-center space-y-3">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
                <TrendingUp className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="font-semibold">Style Matching</h3>
              <p className="text-sm text-muted-foreground">
                Machine learning models understand style compatibility and fashion rules
              </p>
            </div>
            <div className="text-center space-y-3">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                <Brain className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="font-semibold">Personal Learning</h3>
              <p className="text-sm text-muted-foreground">
                AI learns from your preferences and feedback to improve recommendations
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Jump into the most popular AI features
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Button 
              variant="outline" 
              className="h-16 justify-start"
              onClick={() => handleFeatureClick('intelligent-matching')}
            >
              <Sparkles className="h-5 w-5 mr-3" />
              <div className="text-left">
                <div className="font-medium">Find Matching Items</div>
                <div className="text-sm text-muted-foreground">Get AI-powered outfit suggestions</div>
              </div>
            </Button>
            <Button 
              variant="outline" 
              className="h-16 justify-start"
              onClick={() => handleFeatureClick('occasion-recommendations')}
            >
              <Calendar className="h-5 w-5 mr-3" />
              <div className="text-left">
                <div className="font-medium">Plan for Occasion</div>
                <div className="text-sm text-muted-foreground">Get weather-aware recommendations</div>
              </div>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
      <div className="container mx-auto p-6">
        <Routes>
          <Route path="/" element={renderOverview()} />
          <Route path="/intelligent-matching" element={<IntelligentMatching />} />
          <Route path="/advanced-search" element={<AdvancedSearch />} />
          <Route path="/occasion-recommendations" element={<OccasionRecommendations />} />
        </Routes>
      </div>
    </div>
  );
};

export default AIStudioPage;

