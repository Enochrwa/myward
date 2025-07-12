
import React from 'react';
import { ThemeProvider } from '@/contexts/ThemeContext';
import Header from '@/components/Header';
import HeroSection from '@/components/HeroSection';
import FeaturesSection from '@/components/FeaturesSection';
import WardrobePreview from '@/components/WardrobePreview';
import OutfitGenerator from '@/components/OutfitGenerator';
import Footer from '@/components/Footer';

const Index = () => {
  return (
    <ThemeProvider>
      <div className="min-h-screen bg-gradient-to-br from-owis-cream to-owis-mint dark:from-owis-charcoal-dark to-owis-midnight-blue overflow-x-hidden transition-colors duration-300">
        <div className="will-change-transform">
          <Header />
          <HeroSection />
          <FeaturesSection />
          <WardrobePreview />
          <OutfitGenerator />
          <Footer />
        </div>
      </div>
    </ThemeProvider>
  );
};

export default Index;
