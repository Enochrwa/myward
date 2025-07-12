
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Shirt, 
  Calendar, 
  TrendingUp, 
  Heart, 
  Sparkles, 
  Eye,
  Plus,
  Target,
  Award,
  Zap,
  Clock,
  Users,
  Star,
  ShoppingBag,
  Palette,
  Sun,
  Cloud,
  Snowflake
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';

const Dashboard = () => {
  const [greeting, setGreeting] = useState('');
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good Morning');
    else if (hour < 18) setGreeting('Good Afternoon');
    else setGreeting('Good Evening');

    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const quickActions = [
    {
      title: 'Add New Item',
      description: 'Upload a new piece to your wardrobe',
      icon: Plus,
      href: '/wardrobe?action=add-item',
      gradient: 'from-emerald-500 to-teal-600',
      bgGradient: 'from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20'
    },
    {
      title: 'Create Outfit',
      description: 'Generate AI-powered outfit combinations',
      icon: Sparkles,
      href: '/wardrobe?action=create-outfit',
      gradient: 'from-purple-500 to-pink-600',
      bgGradient: 'from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20'
    },
    {
      title: 'Plan Week',
      description: 'Organize your outfits for the week',
      icon: Calendar,
      href: '/wardrobe?action=plan-week',
      gradient: 'from-blue-500 to-cyan-600',
      bgGradient: 'from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20'
    },
    {
      title: 'View Analytics',
      description: 'Insights into your style patterns',
      icon: TrendingUp,
      href: '/wardrobe?action=analytics',
      gradient: 'from-orange-500 to-red-600',
      bgGradient: 'from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20'
    }
  ];

  const wardrobeStats = [
    { label: 'Total Items', value: '127', icon: Shirt, color: 'text-purple-600 dark:text-purple-400' },
    { label: 'Outfits Created', value: '43', icon: Target, color: 'text-blue-600 dark:text-blue-400' },
    { label: 'Favorites', value: '28', icon: Heart, color: 'text-pink-600 dark:text-pink-400' },
    { label: 'Weekly Wears', value: '15', icon: Clock, color: 'text-green-600 dark:text-green-400' }
  ];

  const recentActivity = [
    { action: 'Added new jacket', time: '2 hours ago', type: 'add' },
    { action: 'Created summer outfit', time: '5 hours ago', type: 'outfit' },
    { action: 'Favorited blue dress', time: '1 day ago', type: 'favorite' },
    { action: 'Planned week outfits', time: '2 days ago', type: 'plan' }
  ];

  const styleInsights = [
    { category: 'Most Worn Color', value: 'Navy Blue', percentage: 35, color: 'bg-blue-500' },
    { category: 'Favorite Style', value: 'Casual Chic', percentage: 62, color: 'bg-purple-500' },
    { category: 'Season Readiness', value: 'Summer 2024', percentage: 78, color: 'bg-teal-500' },
    { category: 'Sustainability Score', value: 'Excellent', percentage: 89, color: 'bg-green-500' }
  ];

  const weatherOutfit = {
    temperature: '22°C',
    condition: 'Sunny',
    icon: Sun,
    suggestion: 'Light layers recommended',
    outfit: 'Linen shirt + Cotton pants + Canvas sneakers'
  };

  const trendingStyles = [
    { name: 'Cottagecore', popularity: 94, color: 'from-green-400 to-emerald-500' },
    { name: 'Y2K Revival', popularity: 87, color: 'from-pink-400 to-purple-500' },
    { name: 'Dark Academia', popularity: 76, color: 'from-purple-400 to-orange-500' },
    { name: 'Minimalist', popularity: 82, color: 'from-gray-400 to-slate-500' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-blue-900/20 dark:to-purple-900/20 pt-20 pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent">
                {greeting}, Fashionista! ✨
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                Ready to create some amazing outfits today? Your style journey awaits.
              </p>
            </div>
            <div className="hidden md:block text-right">
              <div className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                {currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {currentTime.toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' })}
              </div>
            </div>
          </div>

          {/* Weather-Based Outfit Sugge4tion */}
          <Card className="bg-slate-200 border-blue-200 dark:border-blue-800">
            <CardContent className="p-6">
              <div className="flex items-center justify-between b">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-teal-400 to-emerald-500 rounded-full flex items-center justify-center">
                    <weatherOutfit.icon size={24} className="text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                      Today's Weather: {weatherOutfit.temperature} - {weatherOutfit.condition}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">{weatherOutfit.suggestion}</p>
                  </div>
                </div>
                <Button className="bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700">
                  <Sparkles size={16} className="mr-2" />
                  Get Outfit
                </Button>
              </div>
              <div className="mt-4 p-3 bg-white/50 dark:bg-gray-800/50 rounded-lg">
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  AI Recommendation: {weatherOutfit.outfit}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action, index) => {
              const Icon = action.icon;
              return (
                <Link key={index} to={action.href}>
                  <Card className={`hover:shadow-xl transition-all duration-300 hover:scale-105 bg-gradient-to-br ${action.bgGradient} border-0 shadow-lg`}>
                    <CardContent className="p-6">
                      <div className={`w-12 h-12 bg-gradient-to-br ${action.gradient} rounded-xl flex items-center justify-center mb-4 shadow-lg`}>
                        <Icon size={24} className="text-white" />
                      </div>
                      <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-2">{action.title}</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{action.description}</p>
                    </CardContent>
                  </Card>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-6">
            {/* Wardrobe Stats */}
            <Card className="shadow-lg border-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl text-gray-800 dark:text-gray-200">Wardrobe Overview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  {wardrobeStats.map((stat, index) => {
                    const Icon = stat.icon;
                    return (
                      <div key={index} className="text-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                        <div className="flex justify-center mb-2">
                          <Icon size={24} className={stat.color} />
                        </div>
                        <div className="text-2xl font-bold text-gray-800 dark:text-gray-200">{stat.value}</div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Style Insights */}
            <Card className="shadow-lg border-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl text-gray-800 dark:text-gray-200">Style Insights</CardTitle>
                <CardDescription>Your fashion patterns and preferences</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 ">
                  {styleInsights.map((insight, index) => (
                    <div key={index} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{insight.category}</span>
                        <span className="text-sm text-gray-500 dark:text-gray-400">{insight.value}</span>
                      </div>
                      <Progress value={insight.percentage} className="h-2" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Trending Styles */}
            <Card className="shadow-lg border-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl text-gray-800 dark:text-gray-200">Trending Styles</CardTitle>
                <CardDescription>What's popular in fashion right now</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  {trendingStyles.map((style, index) => (
                    <div key={index} className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-800 dark:text-gray-200">{style.name}</h4>
                        <Badge variant="secondary">{style.popularity}%</Badge>
                      </div>
                      <div className={`h-2 bg-gradient-to-r ${style.color} rounded-full`} 
                           style={{ width: `${style.popularity}%` }} />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            {/* Recent Activity */}
            <Card className="shadow-lg border-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl text-gray-800 dark:text-gray-200">Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {recentActivity.map((activity, index) => (
                    <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                      <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center flex-shrink-0">
                        <div className="w-2 h-2 bg-white rounded-full" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-800 dark:text-gray-200 truncate">
                          {activity.action}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">{activity.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Style Goals */}
            <Card className="shadow-lg border-0 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20">
              <CardHeader>
                <CardTitle className="text-xl text-gray-800 dark:text-gray-200 flex items-center">
                  <Award className="mr-2 text-purple-600 dark:text-purple-400" size={20} />
                  Style Goals
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-3 bg-white/50 dark:bg-gray-800/50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Sustainable Fashion</span>
                      <span className="text-xs text-purple-600 dark:text-purple-400">7/10 items</span>
                    </div>
                    <Progress value={70} className="h-2" />
                  </div>
                  <div className="p-3 bg-white/50 dark:bg-gray-800/50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Color Coordination</span>
                      <span className="text-xs text-blue-600 dark:text-blue-400">Complete!</span>
                    </div>
                    <Progress value={100} className="h-2" />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Community Highlights */}
            <Card className="shadow-lg border-0 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20">
              <CardHeader>
                <CardTitle className="text-xl text-gray-800 dark:text-gray-200 flex items-center">
                  <Users className="mr-2 text-blue-600 dark:text-blue-400" size={20} />
                  Community
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-white/50 dark:bg-gray-800/50 rounded-lg">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Style Challenges</span>
                    <Badge className="bg-gradient-to-r from-blue-500 to-cyan-600">3 Active</Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-white/50 dark:bg-gray-800/50 rounded-lg">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Following</span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">247 stylists</span>
                  </div>
                </div>
                <Button className="w-full mt-4 bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700">
                  <Users size={16} className="mr-2" />
                  Explore Community
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Call to Action */}
        <div className="mt-12 text-center">
          <Card className="bg-gradient-to-r from-purple-500 via-pink-500 to-blue-500 border-0 shadow-2xl">
            <CardContent className="p-8">
              <div className="text-white">
                <h2 className="text-3xl font-bold mb-4">Ready to Elevate Your Style?</h2>
                <p className="text-lg mb-6 text-purple-100">
                  Discover new outfits, plan your week, and connect with fashion enthusiasts worldwide.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Button size="lg" variant="secondary" className="bg-white text-purple-600 hover:bg-gray-100">
                    <Sparkles size={20} className="mr-2" />
                    Create Outfit
                  </Button>
                  <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10">
                    <Eye size={20} className="mr-2" />
                    Browse Wardrobe
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
