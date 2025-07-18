
import React, { useState, useEffect, useRef } from 'react';
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
  Snowflake,
  Upload,
  Loader2
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import CategorizedWardrobe from './CategorizedWardrobe';
import * as apiClient from '@/lib/apiClient';

const Dashboard = () => {
  const [greeting, setGreeting] = useState('');
  const [currentTime, setCurrentTime] = useState(new Date());
  const [uploading, setUploading] = useState(false);
  const [batchProgress, setBatchProgress] = useState<{ total: number; completed: number; failed: number } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good Morning');
    else if (hour < 18) setGreeting('Good Afternoon');
    else setGreeting('Good Evening');

    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      await uploadImages(files);
    }
  };

  const uploadImages = async (files: FileList) => {
    setUploading(true);
    setBatchProgress({
      total: files.length,
      completed: 0,
      failed: 0
    });

    const formData = new FormData();
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await fetch(`http://localhost:8000/upload-images/`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setBatchProgress({
          total: data.total_images,
          completed: data.successful_uploads,
          failed: data.failed_uploads
        });
        // Refresh the categorized wardrobe view by re-fetching
        // This is a simple way to trigger a re-render of the child component
        // A more robust solution might involve a shared state or context
        window.location.reload(); 
      } else {
        console.error('Batch upload failed:', response.statusText);
      }
    } catch (error) {
      console.error('Error uploading images:', error);
    } finally {
      setUploading(false);
      setTimeout(() => setBatchProgress(null), 5000);
    }
  };

  const quickActions = [
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
        </div>

        {/* Upload and Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Upload Area */}
          <Card 
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center bg-white hover:border-blue-400 transition-colors cursor-pointer"
            onClick={() => !uploading && fileInputRef.current?.click()}
          >
            {uploading ? (
              <div className="space-y-4">
                <Loader2 className="w-12 h-12 text-blue-600 mx-auto animate-spin" />
                <p className="text-lg text-gray-600">
                  Processing {batchProgress?.completed || 0} of {batchProgress?.total || 0} images
                </p>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div
                    className="bg-blue-600 h-2.5 rounded-full"
                    style={{
                      width: `${((batchProgress?.completed || 0) / (batchProgress?.total || 1)) * 100}%`
                    }}
                  />
                </div>
                <p className="text-sm text-gray-500">
                  {batchProgress?.failed || 0} failed uploads
                </p>
              </div>
            ) : (
              <>
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">Upload Your Clothes</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Drop images here or click to browse. They'll be automatically categorized.
                </p>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileSelect}
                  accept="image/*"
                  multiple
                  className="hidden"
                />
              </>
            )}
          </Card>
          
          {/* Quick Actions simplified */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {quickActions.map((action, index) => {
              const Icon = action.icon;
              return (
                <Link key={index} to={action.href}>
                  <Card className={`h-full hover:shadow-xl transition-all duration-300 hover:scale-105 bg-gradient-to-br ${action.bgGradient} border-0 shadow-lg`}>
                    <CardContent className="p-6 flex flex-col items-center justify-center text-center h-full">
                      <div className={`w-12 h-12 bg-gradient-to-br ${action.gradient} rounded-xl flex items-center justify-center mb-4 shadow-lg`}>
                        <Icon size={24} className="text-white" />
                      </div>
                      <h3 className="font-semibold text-gray-800 dark:text-gray-200">{action.title}</h3>
                    </CardContent>
                  </Card>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Categorized Wardrobe Display */}
        <Card className="shadow-lg border-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-2xl text-gray-800 dark:text-gray-200">Your Wardrobe</CardTitle>
            <CardDescription>All your clothes, automatically categorized by AI.</CardDescription>
          </CardHeader>
          <CardContent>
            <CategorizedWardrobe />
          </CardContent>
        </Card>

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
                  <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10" asChild>
                    <Link to="/wardrobe">
                      <Eye size={20} className="mr-2" />
                      Browse Wardrobe
                    </Link>
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