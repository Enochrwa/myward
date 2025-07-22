
import React, { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';

import PremiumEffects from './PremiumEffects';
import { Sparkles, Star, Heart, Zap, ChevronDown, Award, Users, TrendingUp, Palette, Shirt, Camera, Brain, Clock, Lightbulb, ArrowRight, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const EnhancedHeroSection = () => {
  const [currentWord, setCurrentWord] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const words = ['Intelligent', 'Beautiful', 'Sustainable', 'Revolutionary'];

  useEffect(() => {
    setIsVisible(true);
    const interval = setInterval(() => {
      setCurrentWord((prev) => (prev + 1) % words.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      <PremiumEffects />
      
      {/* Enhanced Background with better contrast */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900/95 via-blue-900/90 to-indigo-900/95"></div>
      
      {/* Hero Content - Ultra Responsive */}
      <div className="relative z-10 container-ultra-responsive text-center safe-top safe-bottom">
        <div className="max-w-7xl mx-auto">
          {/* Award Badge - Responsive */}
          <div 
            className={`inline-flex items-center space-x-2 xs:space-x-3 bg-gradient-to-r from-teal-400/20 to-purple-400/20 border border-teal-400/40 rounded-full px-4 xs:px-6 sm:px-8 py-2 xs:py-3 mb-6 xs:mb-8 backdrop-blur-sm transition-all duration-1000 ${isVisible ? 'animate-fade-in' : 'opacity-0'}`}
          >
            <Award className="w-4 h-4 xs:w-5 xs:h-5 text-teal-400 animate-pulse" />
            <span className="text-white text-xs xs:text-sm font-semibold tracking-wide">
              <span className="hidden xs:inline">AI-Powered Digital Wardrobe Platform</span>
              <span className="xs:hidden">Award-Winning Platform</span>
            </span>
            <div className="flex space-x-1">
              {[...Array(5)].map((_, i) => (
                <Star key={i} className="w-2 h-2 xs:w-3 xs:h-3 text-teal-400 fill-current" />
              ))}
            </div>
          </div>

          {/* Main Title - Ultra Responsive */}
          <h1 
            className={`text-hero-responsive font-display font-black mb-6 xs:mb-8 leading-none transition-all duration-1000 ${isVisible ? 'animate-fade-in' : 'opacity-0'}`}
            style={{ animationDelay: '0.2s' }}
          >
            <span className="block text-white drop-shadow-2xl">
              Your
            </span>
            <span className="block relative">
              <span className="bg-gradient-to-r from-teal-400 via-emerald-400 to-teal-500 bg-clip-text text-transparent animate-gradient-flow font-black drop-shadow-lg">
                {words[currentWord]}
              </span>
            </span>
            <span className="block text-white drop-shadow-2xl">
              Wardrobe
            </span>
          </h1>

          {/* Enhanced Subtitle - Ultra Responsive */}
          <p 
            className={`text-ultra-responsive text-white/95 mb-8 xs:mb-10 sm:mb-12 max-w-xs xs:max-w-sm sm:max-w-2xl md:max-w-4xl lg:max-w-5xl mx-auto leading-relaxed font-medium drop-shadow-lg transition-all duration-1000 ${isVisible ? 'animate-fade-in' : 'opacity-0'}`}
            style={{ animationDelay: '0.4s' }}
          >
            <span className="hidden sm:inline">
              Experience the future of fashion with AI-powered styling, sustainable choices, 
              and a community of style enthusiasts. Join millions who trust our award-winning platform.
            </span>
            <span className="sm:hidden">
              AI-powered styling for your perfect wardrobe. Join millions of style enthusiasts.
            </span>
          </p>

          {/* Enhanced CTA Buttons - Ultra Responsive */}
          <div 
            className={`flex flex-col xs:flex-col sm:flex-row gap-3 xs:gap-4 sm:gap-6 justify-center mb-12 xs:mb-14 sm:mb-16 transition-all duration-1000 ${isVisible ? 'animate-fade-in' : 'opacity-0'}`}
            style={{ animationDelay: '0.6s' }}
          >
            <Link to="/wardrobe" className="w-full sm:w-auto">
              <Button 
                size="lg"
                className="w-full sm:w-auto bg-gradient-to-r from-emerald-400 to-teal-500 hover:from-teal-500 hover:to-emerald-600 text-slate-900 px-6 xs:px-8 sm:px-12 py-4 xs:py-5 sm:py-6 text-sm xs:text-base sm:text-xl font-bold rounded-xl xs:rounded-2xl shadow-2xl hover:shadow-teal-400/25 transition-all duration-300 group relative overflow-hidden"
              >
                <span className="relative z-10 flex items-center justify-center space-x-2 xs:space-x-3">
                  <Sparkles className="w-4 h-4 xs:w-5 xs:h-5 sm:w-6 sm:h-6 group-hover:animate-spin transition-transform" />
                  <span>
                    <span className="hidden xs:inline">Start Your Journey</span>
                    <span className="xs:hidden">Start Journey</span>
                  </span>
                </span>
                <div className="absolute inset-0 bg-gradient-to-r from-emerald-400 to-teal-400 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </Button>
            </Link>
            
            <Link to="/saved-outfits" className="w-full sm:w-auto">
              <Button
                variant="outline"
                size="lg" 
                className="w-full sm:w-auto px-6 xs:px-8 sm:px-12 py-4 xs:py-5 sm:py-6 text-sm xs:text-base sm:text-xl font-bold rounded-xl xs:rounded-2xl border-2 border-white/40 text-white hover:bg-white/10 backdrop-blur-sm transition-all duration-300 group shadow-lg"
              >
                <Zap className="w-4 h-4 xs:w-5 xs:h-5 sm:w-6 sm:h-6 mr-2 xs:mr-3 group-hover:text-emerald-400 transition-colors" />
                <span className="hidden xs:inline">Explore Your Outfits </span>
                <span className="xs:hidden">AI Studio</span>
              </Button>
            </Link>
          </div>

        </div>
      </div>

      {/* Enhanced Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M30 30L0 0h60z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }}></div>
      </div>
    </section>
  );
};




const QuickActionsSection = () => {
  const actions = [
    {
      icon: Camera,
      title: "Snap & Style",
      description: "Take photos of your clothes and get instant outfit suggestions",
      action: "Try Now",
      gradient: "from-pink-500 to-rose-500",
      link:"/dashboard"
    },
    {
      icon: Shirt,
      title: "Virtual Wardrobe",
      description: "Organize your entire wardrobe digitally with smart categorization",
      action: "Explore",
      gradient: "from-blue-500 to-indigo-500",
      link:"/wardrobe"
    },
    {
      icon: Clock,
      title: "Quick Outfits",
      description: "Get ready in seconds with pre-planned outfit combinations",
      action: "View All",
      gradient: "from-emerald-500 to-teal-500",
      link:"/wardrobe"
    }
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-slate-900/95 via-blue-900/90 to-indigo-900/95">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Quick Actions
          </h2>
          <p className="text-xl text-slate-300 max-w-2xl mx-auto">
            Streamline your daily styling routine with these powerful tools
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {actions.map((action, index) => (
            <div
              key={index}
              className="bg-slate-700/50 rounded-2xl p-8 backdrop-blur-sm border border-slate-600/50 hover:bg-slate-700/70 transition-all duration-300 group"
            >
              <div className={`w-16 h-16 rounded-xl bg-gradient-to-r ${action.gradient} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                <action.icon className="w-8 h-8 text-white" />
              </div>
              
              <h3 className="text-xl font-bold text-white mb-3">
                {action.title}
              </h3>
              
              <p className="text-slate-300 mb-6 leading-relaxed">
                {action.description}
              </p>

              <Link to={action?.link}>
                  <button className="flex items-center text-teal-400 hover:text-teal-300 font-semibold transition-colors group">
                {action.action}
                   <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
              </button>
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};


const EnhancedWardrobeHomepage = () => {
  return (
    <div className="min-h-screen">
      <EnhancedHeroSection />
      {/* <AIFeaturesSection /> */}
      <QuickActionsSection />
      {/* <StyleStatsSection /> */}
      {/* <CallToActionSection /> */}
    </div>
  );
};

export default EnhancedWardrobeHomepage