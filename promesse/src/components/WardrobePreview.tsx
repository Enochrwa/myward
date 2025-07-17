
import React from 'react';
import { Button } from '@/components/ui/button';
import { Plus, Check } from 'lucide-react';

const WardrobePreview = () => {
  return (
    <section className="py-20 bg-white">
      <div className="container mx-auto px-4 max-w-6xl">
        <div className="text-center mb-16 animate-fade-in">
          <h2 className="text-4xl md:text-5xl font-heading font-bold text-owis-forest mb-6">
            Your Digital Wardrobe
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Seamlessly catalog, organize, and optimize your clothing collection with
            intelligent insights and usage analytics.
          </p>
        </div>
      </div>
    </section>
  );
};

export default WardrobePreview;
