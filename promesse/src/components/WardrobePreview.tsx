
import React from 'react';
import { Button } from '@/components/ui/button';
import { Plus, Check } from 'lucide-react';

const WardrobePreview = () => {
  const wardrobeItems = [
    { id: 1, name: "Silk Blouse", category: "Tops", color: "Ivory", image: "bg-gradient-to-br from-gray-100 to-gray-200", uses: 12 },
    { id: 2, name: "Wool Blazer", category: "Outerwear", color: "Navy", image: "bg-gradient-to-br from-blue-900 to-blue-700", uses: 8 },
    { id: 3, name: "Midi Skirt", category: "Bottoms", color: "Forest", image: "bg-gradient-to-br from-green-800 to-green-600", uses: 15 },
    { id: 4, name: "Cashmere Sweater", category: "Tops", color: "Cream", image: "bg-gradient-to-br from-purple-100 to-purple-200", uses: 20 },
    { id: 5, name: "Denim Jacket", category: "Outerwear", color: "Indigo", image: "bg-gradient-to-br from-indigo-600 to-indigo-800", uses: 25 },
    { id: 6, name: "Leather Boots", category: "Shoes", color: "Brown", image: "bg-gradient-to-br from-purple-800 to-purple-900", uses: 18 }
  ];

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

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-12">
          {wardrobeItems.map((item, index) => (
            <div 
              key={item.id}
              className="group owis-card rounded-xl p-3 owis-hover animate-scale-in"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className={`${item.image} h-32 rounded-lg mb-3 relative overflow-hidden`}>
                <div className="absolute top-2 right-2 bg-white/90 backdrop-blur-sm rounded-full px-2 py-1 text-xs font-medium text-owis-charcoal">
                  {item.uses}×
                </div>
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-300"></div>
              </div>
              
              <h4 className="font-medium text-sm text-owis-charcoal mb-1 truncate">
                {item.name}
              </h4>
              <p className="text-xs text-muted-foreground mb-2">
                {item.category} • {item.color}
              </p>
              
              <div className="flex items-center justify-between">
                <div className={`h-1 flex-1 rounded-full ${
                  item.uses > 20 ? 'bg-green-500' : 
                  item.uses > 10 ? 'bg-owis-purple' : 'bg-gray-300'
                }`}></div>
                <Button 
                  variant="ghost" 
                  size="sm"
                  className="ml-2 h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Check className="h-3 w-3" />
                </Button>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center">
          <Button 
            size="lg"
            className="bg-owis-forest hover:bg-owis-charcoal text-white px-8 py-3 owis-hover"
          >
            <Plus className="h-5 w-5 mr-2" />
            Build Your Digital Wardrobe
          </Button>
        </div>

        {/* Stats Row */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
          <div className="animate-fade-in" style={{ animationDelay: '0.5s' }}>
            <div className="text-3xl font-bold text-owis-purple mb-2">127</div>
            <div className="text-sm text-muted-foreground">Total Items</div>
          </div>
          <div className="animate-fade-in" style={{ animationDelay: '0.7s' }}>
            <div className="text-3xl font-bold text-owis-sage mb-2">89%</div>
            <div className="text-sm text-muted-foreground">Utilization Rate</div>
          </div>
          <div className="animate-fade-in" style={{ animationDelay: '0.9s' }}>
            <div className="text-3xl font-bold text-owis-bronze mb-2">$2.4K</div>
            <div className="text-sm text-muted-foreground">Wardrobe Value</div>
          </div>
          <div className="animate-fade-in" style={{ animationDelay: '1.1s' }}>
            <div className="text-3xl font-bold text-green-600 mb-2">-40%</div>
            <div className="text-sm text-muted-foreground">Carbon Footprint</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default WardrobePreview;
