
import React, { useEffect, useRef, useState } from 'react';
import FeatureCard from './FeatureCard';
import { Search, Calendar, User, Image, Sparkles, Zap, Heart, Star } from 'lucide-react';

const FeaturesSection = () => {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef<HTMLDivElement>(null);

  const features = [
    {
      icon: Search,
      title: "AI-Powered Cataloging",
      description: "Instantly organize your wardrobe with intelligent image recognition, automatic tagging, and smart categorization that learns from your style.",
      gradient: "from-owis-forest to-owis-sage",
      accent: Sparkles
    },
    {
      icon: Calendar,
      title: "Smart Outfit Curation",
      description: "Get personalized outfit recommendations with stunning visual previews based on weather, occasion, and your unique style DNA.",
      gradient: "from-owis-purple to-owis-bronze",
      accent: Zap
    },
    {
      icon: User,
      title: "Style Community",
      description: "Connect with fashion enthusiasts worldwide through beautifully designed social feeds, interactive challenges, and inspiring style galleries.",
      gradient: "from-owis-sage to-owis-mint",
      accent: Heart
    },
    {
      icon: Image,
      title: "Sustainability Insights",
      description: "Track your fashion footprint with elegant analytics, discover eco-friendly alternatives, and promote circular fashion through beautiful, actionable insights.",
      gradient: "from-owis-bronze to-owis-purple",
      accent: Star
    }
  ];

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <section 
      ref={sectionRef}
      className="py-24 bg-gradient-to-b from-owis-cream to-white relative overflow-hidden"
    >
      {/* Animated Background Elements */}
      <div className="absolute inset-0 pointer-events-none">
        {Array.from({ length: 6 }, (_, i) => (
          <div
            key={i}
            className={`absolute morphing-blob w-64 h-64 rounded-full blur-3xl opacity-10 animate-morph`}
            style={{
              left: `${10 + i * 15}%`,
              top: `${20 + (i % 2) * 40}%`,
              animationDelay: `${i * 3}s`,
              animationDuration: `${10 + i}s`,
            }}
          ></div>
        ))}
      </div>

      <div className="container mx-auto px-4 max-w-7xl relative">
        {/* Enhanced Section Header */}
        <div className={`text-center mb-20 transition-all duration-1000 ${isVisible ? 'animate-fade-in-up' : 'opacity-0 translate-y-10'}`}>
          {/* Decorative Badge */}
          <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-owis-purple/10 to-owis-bronze/10 border border-owis-purple/20 rounded-full px-6 py-2 mb-6">
            <Sparkles className="w-4 h-4 text-owis-purple animate-pulse" />
            <span className="text-owis-charcoal text-sm font-medium">Revolutionary Features</span>
          </div>

          <h2 className="text-5xl md:text-7xl font-display font-bold text-owis-forest mb-8 text-balance">
            <span className="block">Experience the</span>
            <span className="block gradient-text">Future of Fashion</span>
          </h2>
          
          <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            Discover cutting-edge AI technology seamlessly woven into breathtaking design, 
            creating an experience that's as beautiful as it is intelligent.
          </p>
        </div>
        
        {/* Enhanced Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          {features.map((feature, index) => (
            <div 
              key={feature.title}
              className={`transition-all duration-700 ${
                isVisible ? 'animate-scale-in' : 'opacity-0 scale-95'
              }`}
              style={{ animationDelay: `${index * 0.2}s` }}
            >
              <div className="group owis-card-premium rounded-3xl p-8 h-full owis-interactive relative overflow-hidden">
                {/* Gradient Background */}
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-5 group-hover:opacity-10 transition-opacity duration-500`}></div>
                
                {/* Icon with Accent */}
                <div className="relative mb-6">
                  <div className={`w-16 h-16 bg-gradient-to-br ${feature.gradient} rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-500 shadow-glow`}>
                    <feature.icon className="h-8 w-8 text-white" />
                  </div>
                  <feature.accent className="absolute -top-2 -right-2 w-6 h-6 text-owis-purple animate-pulse opacity-80" />
                </div>
                
                <h3 className="text-2xl font-display font-semibold text-owis-charcoal mb-4 group-hover:text-owis-forest transition-colors duration-300">
                  {feature.title}
                </h3>
                
                <p className="text-muted-foreground leading-relaxed mb-6">
                  {feature.description}
                </p>
                
                {/* Animated Progress Bar */}
                <div className="h-1 w-0 bg-gradient-to-r from-owis-purple to-owis-bronze rounded-full group-hover:w-full transition-all duration-700 ease-out"></div>
                
                {/* Shimmer Effect */}
                <div className="absolute inset-0 shimmer-effect opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              </div>
            </div>
          ))}
        </div>

        {/* Call-to-Action Section */}
        <div className={`text-center transition-all duration-1000 ${isVisible ? 'animate-fade-in-up' : 'opacity-0 translate-y-10'}`} style={{ animationDelay: '1s' }}>
          <div className="owis-card-premium rounded-3xl p-12 max-w-4xl mx-auto owis-interactive">
            <div className="flex items-center justify-center mb-6">
              <div className="flex space-x-2">
                {[Sparkles, Star, Heart].map((Icon, i) => (
                  <Icon key={i} className="w-6 h-6 text-owis-purple animate-pulse" style={{ animationDelay: `${i * 0.2}s` }} />
                ))}
              </div>
            </div>
            
            <h3 className="text-3xl md:text-4xl font-display font-bold text-owis-forest mb-4">
              Ready to Transform Your Style?
            </h3>
            
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Join millions of fashion enthusiasts who have already discovered the beauty of intelligent wardrobe management.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="owis-button-primary px-8 py-4 rounded-2xl text-lg font-semibold owis-interactive haptic-feedback flex items-center space-x-2">
                <Sparkles className="w-5 h-5" />
                <span>Start Your Journey</span>
              </button>
              
              <button className="border-2 border-owis-purple/30 text-owis-charcoal hover:bg-owis-purple/10 px-8 py-4 rounded-2xl text-lg font-semibold owis-interactive haptic-feedback transition-smooth">
                Explore Features
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
