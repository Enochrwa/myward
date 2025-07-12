
import React, { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Sparkles, Star, Heart, Zap, ChevronDown, Award, Users, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';
import PremiumEffects from './PremiumEffects';

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
              <span className="hidden xs:inline">Award-Winning AI Fashion Platform</span>
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
            
            <Link to="/ai-studio" className="w-full sm:w-auto">
              <Button
                variant="outline"
                size="lg" 
                className="w-full sm:w-auto px-6 xs:px-8 sm:px-12 py-4 xs:py-5 sm:py-6 text-sm xs:text-base sm:text-xl font-bold rounded-xl xs:rounded-2xl border-2 border-white/40 text-white hover:bg-white/10 backdrop-blur-sm transition-all duration-300 group shadow-lg"
              >
                <Zap className="w-4 h-4 xs:w-5 xs:h-5 sm:w-6 sm:h-6 mr-2 xs:mr-3 group-hover:text-emerald-400 transition-colors" />
                <span className="hidden xs:inline">Explore AI Studio</span>
                <span className="xs:hidden">AI Studio</span>
              </Button>
            </Link>
          </div>

          {/* Enhanced Stats - Ultra Responsive */}
          <div 
            className={`grid grid-cols-1 sm:grid-cols-3 gap-4 xs:gap-6 sm:gap-8 max-w-xs xs:max-w-sm sm:max-w-4xl mx-auto mb-12 xs:mb-14 sm:mb-16 transition-all duration-1000 ${isVisible ? 'animate-fade-in' : 'opacity-0'}`}
            style={{ animationDelay: '0.8s' }}
          >
            {[
              { icon: Users, title: '10M+ Users', desc: 'Trusted worldwide', color: 'from-blue-400 to-cyan-400' },
              { icon: TrendingUp, title: '98% Accuracy', desc: 'AI recommendations', color: 'from-green-400 to-emerald-400' },
              { icon: Award, title: 'Award Winner', desc: '2024 Innovation Award', color: 'from-teal-400 to-purple-400' }
            ].map((feature, index) => (
              <div 
                key={feature.title}
                className="bg-white/10 backdrop-blur-md rounded-xl xs:rounded-2xl p-4 xs:p-6 sm:p-8 border border-white/20 hover:bg-white/15 transition-all duration-300 group shadow-xl"
                style={{ animationDelay: `${0.8 + index * 0.2}s` }}
              >
                <div className={`w-12 h-12 xs:w-14 xs:h-14 sm:w-16 sm:h-16 mx-auto mb-3 xs:mb-4 rounded-full bg-gradient-to-r ${feature.color} flex items-center justify-center group-hover:scale-110 transition-transform`}>
                  <feature.icon className="w-6 h-6 xs:w-7 xs:h-7 sm:w-8 sm:h-8 text-white" />
                </div>
                <h3 className="text-lg xs:text-xl sm:text-2xl font-bold text-white mb-1 xs:mb-2">
                  {feature.title}
                </h3>
                <p className="text-white/80 font-medium text-xs xs:text-sm">
                  {feature.desc}
                </p>
              </div>
            ))}
          </div>

          {/* Trust Indicators - Responsive */}
          <div 
            className={`flex flex-wrap justify-center items-center gap-3 xs:gap-4 sm:gap-8 mb-12 xs:mb-14 sm:mb-16 opacity-60 transition-all duration-1000 ${isVisible ? 'animate-fade-in' : 'opacity-0'}`}
            style={{ animationDelay: '1s' }}
          >
            <div className="text-white/60 text-xs xs:text-sm font-medium">Featured in:</div>
            {['TechCrunch', 'Forbes', 'Vogue', 'Wired'].map((brand) => (
              <div key={brand} className="text-white/80 text-xs xs:text-sm sm:text-lg font-semibold px-2 xs:px-3 sm:px-4 py-1 xs:py-2 border border-white/20 rounded-lg backdrop-blur-sm">
                {brand}
              </div>
            ))}
          </div>

          {/* Enhanced Scroll Indicator - Responsive */}
          <div className="absolute bottom-4 xs:bottom-6 sm:bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
            <div className="flex flex-col items-center space-y-1 xs:space-y-2">
              <span className="text-white/80 text-2xs xs:text-xs font-medium uppercase tracking-wider">
                <span className="hidden xs:inline">Discover More</span>
                <span className="xs:hidden">More</span>
              </span>
              <ChevronDown className="w-6 h-6 xs:w-7 xs:h-7 sm:w-8 sm:h-8 text-white/80" />
            </div>
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

export default EnhancedHeroSection;
