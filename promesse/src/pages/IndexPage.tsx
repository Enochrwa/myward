
import React from 'react';
import EnhancedHeroSection from '@/components/EnhancedHeroSection';
import FeaturesSection from '@/components/FeaturesSection';
import WardrobePreview from '@/components/WardrobePreview';
import OutfitGenerator from '@/components/OutfitGenerator';
import ProductionFeatures from '@/components/ProductionFeatures';
import Footer from '@/components/Footer';

const IndexPage = () => {
  return (
    <div className="min-h-screen bg-white dark:bg-slate-900 overflow-x-hidden transition-colors duration-300">
      <div className="will-change-transform">
        <EnhancedHeroSection />
        <ProductionFeatures />
        <FeaturesSection />
        <WardrobePreview />
        <OutfitGenerator />
        <Footer />
      </div>
    </div>
  );
};

export default IndexPage;
