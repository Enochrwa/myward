
import React from 'react';
import EnhancedHeroSection from '@/components/EnhancedHeroSection';
import FeaturesSection from '@/components/FeaturesSection';
import HowItWorks from '@/components/HowItWorks';
import Footer from '@/components/Footer';
import ImageGallery from '@/components/ImageGallery';
import DisplayClothes from '@/components/DisplayClothes';
import ClotheAnalytics from '@/components/ClotheAnalytics';

const IndexPage = () => {
  return (
    <div className="min-h-screen bg-white dark:bg-slate-900 overflow-x-hidden transition-colors duration-300">
      <div className="will-change-transform">
        <EnhancedHeroSection />
        <DisplayClothes/>
  
        <Footer />
      </div>
    </div>
  );
};

export default IndexPage;
