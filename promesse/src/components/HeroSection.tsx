
import React, { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { ArrowDown, Sparkles, Star, Heart } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const HeroSection = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isVisible, setIsVisible] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    setIsVisible(true);
    
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({
        x: (e.clientX / window.innerWidth) * 100,
        y: (e.clientY / window.innerHeight) * 100,
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const floatingElements = Array.from({ length: 8 }, (_, i) => ({
    id: i,
    size: Math.random() * 20 + 10,
    x: Math.random() * 100,
    y: Math.random() * 100,
    delay: Math.random() * 4,
    duration: Math.random() * 2 + 3,
  }));

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Dynamic Background with Parallax */}
      <div className="absolute inset-0">
        {/* Base gradient */}
        <div className="absolute inset-0 owis-gradient opacity-90"></div>
        
        {/* Interactive gradient overlay */}
        <div 
          className="absolute inset-0 opacity-30"
          style={{
            background: `radial-gradient(circle at ${mousePosition.x}% ${mousePosition.y}%, 
              rgba(212, 175, 55, 0.4) 0%, 
              rgba(135, 169, 107, 0.3) 40%, 
              transparent 70%)`
          }}
        ></div>
        
        {/* Mesh gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent"></div>
        
        {/* Animated mesh background */}
        <div className="absolute inset-0 opacity-20">
          {Array.from({ length: 3 }, (_, i) => (
            <div
              key={i}
              className={`absolute morphing-blob w-96 h-96 rounded-full blur-3xl animate-morph opacity-40`}
              style={{
                left: `${20 + i * 30}%`,
                top: `${10 + i * 20}%`,
                animationDelay: `${i * 2}s`,
                animationDuration: `${8 + i * 2}s`,
              }}
            ></div>
          ))}
        </div>
      </div>
      
      {/* Floating Elements with Enhanced Animation */}
      {floatingElements.map((element) => (
        <div
          key={element.id}
          className="absolute floating-element opacity-60 pointer-events-none"
          style={{
            left: `${element.x}%`,
            top: `${element.y}%`,
            width: `${element.size}px`,
            height: `${element.size}px`,
            animationDelay: `${element.delay}s`,
            animationDuration: `${element.duration}s`,
          }}
        >
          {element.id % 4 === 0 && <Sparkles className="w-full h-full text-owis-purple" />}
          {element.id % 4 === 1 && <Star className="w-full h-full text-white" />}
          {element.id % 4 === 2 && <Heart className="w-full h-full text-owis-purple" />}
          {element.id % 4 === 3 && (
            <div className="w-full h-full bg-owis-purple rounded-full opacity-80"></div>
          )}
        </div>
      ))}
      
      {/* Content with Staggered Animations */}
      <div className="relative z-10 text-center px-4 max-w-6xl mx-auto">
        <div className={`transition-all duration-1000 ${isVisible ? 'animate-fade-in' : 'opacity-0'}`}>
          {/* Animated Badge */}
          <div className="inline-flex items-center space-x-2 bg-white/10 backdrop-blur-md border border-white/20 rounded-full px-6 py-2 mb-8 owis-interactive">
            <Sparkles className="w-4 h-4 text-owis-purple animate-pulse" />
            <span className="text-white font-medium text-sm">
              Aesthetic & Dynamic Masterpiece
            </span>
            <div className="w-2 h-2 bg-owis-purple rounded-full animate-pulse"></div>
          </div>

          {/* Main Heading with Text Reveal Animation */}
          <h1 className="text-5xl md:text-8xl font-display font-bold text-white mb-8 text-balance">
            <span className={`block text-animate-in ${isVisible ? '' : 'opacity-0'}`}>
              Your Wardrobe,
            </span>
            <span 
              className={`block gradient-text text-animate-in ${isVisible ? '' : 'opacity-0'}`}
              style={{ animationDelay: '0.3s' }}
            >
              Reimagined
            </span>
            <span 
              className={`block text-owis-purple text-animate-in ${isVisible ? '' : 'opacity-0'}`}
              style={{ animationDelay: '0.6s' }}
            >
              Beautifully
            </span>
          </h1>
          
          {/* Enhanced Subtitle */}
          <p 
            className={`text-xl md:text-3xl text-white/95 mb-12 max-w-4xl mx-auto text-balance leading-relaxed text-animate-in ${isVisible ? '' : 'opacity-0'}`}
            style={{ animationDelay: '0.9s' }}
          >
            Where the art of personal style meets the pinnacle of digital design. 
            Experience the world's most intelligent, personalized, and visually breathtaking 
            digital wardrobe manager.
          </p>
          
          {/* Enhanced CTA Buttons */}
          <div 
            className={`flex flex-col sm:flex-row gap-6 justify-center items-center mb-16 text-animate-in ${isVisible ? '' : 'opacity-0'}`}
            style={{ animationDelay: '1.2s' }}
          >
            <Button 
              size="lg" 
              onClick={() => navigate('/wardrobe')}
              className="owis-button-primary px-12 py-4 text-lg rounded-2xl shadow-glow owis-interactive haptic-feedback group"
            >
              <span className="flex items-center space-x-2">
                <Sparkles className="w-5 h-5 group-hover:animate-pulse" />
                <span>Begin Your Style Journey</span>
              </span>
            </Button>
            
            <Button 
              variant="outline" 
              size="lg"
              onClick={() => navigate('/dashboard')}
              className="border-2 border-white/50 text-white hover:bg-white hover:text-owis-forest px-12 py-4 text-lg rounded-2xl backdrop-blur-md bg-white/10 owis-interactive haptic-feedback transition-smooth"
            >
              <span className="flex items-center space-x-2">
                <Star className="w-5 h-5" />
                <span>View Dashboard</span>
              </span>
            </Button>
          </div>
          
          {/* Enhanced Stats with Visual Appeal */}
          <div 
            className={`grid grid-cols-1 md:grid-cols-3 gap-8 text-animate-in ${isVisible ? '' : 'opacity-0'}`}
            style={{ animationDelay: '1.5s' }}
          >
            {[
              { value: '100M+', label: 'Global Users', color: 'text-owis-purple', icon: Heart },
              { value: '90%', label: 'AI Accuracy', color: 'text-white', icon: Sparkles },
              { value: '$2B', label: 'Market Impact', color: 'text-owis-purple', icon: Star }
            ].map((stat, index) => (
              <div 
                key={stat.label}
                className={`owis-card-premium rounded-2xl p-6 owis-interactive animate-scale-in`}
                style={{ animationDelay: `${1.8 + index * 0.2}s` }}
              >
                <div className="flex items-center justify-center mb-2">
                  <stat.icon className={`w-6 h-6 ${stat.color} animate-pulse`} />
                </div>
                <div className={`text-4xl font-bold ${stat.color} mb-2 gradient-text`}>
                  {stat.value}
                </div>
                <div className="text-sm text-owis-charcoal/80 dark:text-owis-cream/80 font-medium">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* Enhanced Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2">
          <div className="flex flex-col items-center space-y-2 owis-interactive">
            <span className="text-white/60 text-xs font-medium uppercase tracking-wider">
              Discover More
            </span>
            <ArrowDown className="h-6 w-6 text-white/60 animate-bounce" />
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
