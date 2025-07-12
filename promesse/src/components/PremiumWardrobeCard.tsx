
import React, { useState } from 'react';
import { Heart, Eye, Share2, Star, ShoppingBag, Calendar, MoreVertical, Edit, Trash2, Tag } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

interface PremiumWardrobeCardProps {
  item: any;
  onToggleFavorite: (id: number) => void;
  onWearItem: (id: number) => void;
  onSelect: (id: number) => void;
  isSelected: boolean;
}

const PremiumWardrobeCard = ({ item, onToggleFavorite, onWearItem, onSelect, isSelected }: PremiumWardrobeCardProps) => {
  const [showMenu, setShowMenu] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const categoryColors = {
    tops: 'from-blue-500 to-indigo-600',
    bottoms: 'from-green-500 to-emerald-600',
    dresses: 'from-pink-500 to-rose-600',
    outerwear: 'from-purple-500 to-violet-600',
    accessories: 'from-purple-500 to-orange-600',
    shoes: 'from-red-500 to-pink-600'
  };

  const getWearFrequency = (timesWorn: number) => {
    if (timesWorn >= 20) return { label: 'Favorite', color: 'green' };
    if (timesWorn >= 10) return { label: 'Regular', color: 'blue' };
    if (timesWorn >= 5) return { label: 'Occasional', color: 'purple' };
    return { label: 'Rarely worn', color: 'red' };
  };

  const wearFreq = getWearFrequency(item.timesWorn);

  return (
    <Card 
      className={`group relative overflow-hidden transition-all duration-500 hover:shadow-2xl hover:scale-[1.02] cursor-pointer border-2 ${
        isSelected 
          ? 'border-purple-400 shadow-xl ring-4 ring-purple-400/30 bg-purple-50/50 dark:bg-purple-900/20' 
          : 'border-transparent hover:border-white/50 bg-white/80 dark:bg-gray-800/80'
      } backdrop-blur-lg rounded-3xl animate-fade-in`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => onSelect(item.id)}
    >
      {/* Premium Gradient Border */}
      <div className="absolute inset-0 bg-gradient-to-r from-purple-400/20 via-pink-400/20 to-indigo-400/20 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
      
      <CardContent className="p-0">
        {/* Image Section */}
        <div className="relative overflow-hidden rounded-t-3xl">
          <img 
            src={item.image} 
            alt={item.name}
            className="w-full h-64 object-cover transition-transform duration-700 group-hover:scale-110"
          />
          
          {/* Overlay Actions */}
          <div className={`absolute inset-0 bg-black/40 transition-opacity duration-300 ${isHovered ? 'opacity-100' : 'opacity-0'}`}>
            <div className="absolute top-4 right-4 flex gap-2">
              <Button
                size="sm"
                variant="secondary"
                className="bg-white/90 hover:bg-white text-gray-900 rounded-full w-10 h-10 p-0"
                onClick={(e) => {
                  e.stopPropagation();
                  onToggleFavorite(item.id);
                }}
              >
                <Heart size={16} className={item.favorite ? 'fill-red-500 text-red-500' : ''} />
              </Button>
              <Button
                size="sm"
                variant="secondary"
                className="bg-white/90 hover:bg-white text-gray-900 rounded-full w-10 h-10 p-0"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowMenu(!showMenu);
                }}
              >
                <MoreVertical size={16} />
              </Button>
            </div>

            <div className="absolute bottom-4 left-4 right-4 flex gap-2">
              <Button
                size="sm"
                className="flex-1 bg-white/90 hover:bg-white text-gray-900 font-semibold"
                onClick={(e) => {
                  e.stopPropagation();
                  onWearItem(item.id);
                }}
              >
                <Calendar size={16} className="mr-2" />
                Wear Today
              </Button>
            </div>
          </div>

          {/* Category Badge */}
          <div className={`absolute top-4 left-4 px-3 py-1 bg-gradient-to-r ${categoryColors[item.category as keyof typeof categoryColors]} text-white text-xs font-bold rounded-full shadow-lg`}>
            {item.category.charAt(0).toUpperCase() + item.category.slice(1)}
          </div>

          {/* Selection Indicator */}
          {isSelected && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="bg-purple-400 text-gray-900 rounded-full p-2 shadow-2xl border-4 border-white">
                <Star className="fill-gray-900" size={24} />
              </div>
            </div>
          )}

          {/* Dropdown Menu */}
          {showMenu && (
            <div className="absolute top-16 right-4 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden z-20">
              <div className="p-2 space-y-1">
                <button className="w-full text-left px-4 py-2 flex items-center gap-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-sm">
                  <Edit size={16} />
                  Edit Item
                </button>
                <button className="w-full text-left px-4 py-2 flex items-center gap-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-sm">
                  <ShoppingBag size={16} />
                  Shop Similar
                </button>
                <button className="w-full text-left px-4 py-2 flex items-center gap-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-sm">
                  <Share2 size={16} />
                  Share Item
                </button>
                <button className="w-full text-left px-4 py-2 flex items-center gap-2 hover:bg-red-100 dark:hover:bg-red-900/30 text-red-600 dark:text-red-400 rounded-lg text-sm">
                  <Trash2 size={16} />
                  Remove
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Content Section */}
        <div className="p-5">
          <h3 className="font-bold text-lg text-gray-900 dark:text-white mb-1 truncate">
            {item.name}
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{item.brand}</p>
          
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              {/* Material Tag */}
              <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded text-xs">
                {item.material}
              </span>
              
              {/* Size Tag */}
              <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded text-xs">
                {item.size}
              </span>
              
              {/* Wear Frequency */}
              <span className={`px-2 py-1 bg-${wearFreq.color}-100 dark:bg-${wearFreq.color}-900/30 text-${wearFreq.color}-700 dark:text-${wearFreq.color}-300 rounded text-xs`}>
                {item.timesWorn} wears
              </span>
            </div>
            
            <span className="font-bold text-green-600 dark:text-green-400">
              ${item.price.toFixed(2)}
            </span>
          </div>
          
          {/* Tags */}
          {item.tags && item.tags.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {item.tags.slice(0, 3).map((tag: string, i: number) => (
                <span 
                  key={i}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-purple-100 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 rounded text-xs"
                >
                  <Tag size={10} />
                  {tag}
                </span>
              ))}
              {item.tags.length > 3 && (
                <span className="text-xs text-gray-500 dark:text-gray-400 self-center">
                  +{item.tags.length - 3} more
                </span>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default PremiumWardrobeCard;
