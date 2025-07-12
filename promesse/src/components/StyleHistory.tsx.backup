
import React, { useState, useEffect } from 'react';
import { Calendar, Filter, Search, Heart, Star, TrendingUp, Clock, Tag, MapPin } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

interface StyleHistoryProps {
  isOpen: boolean;
  onClose: () => void;
}

interface StyleEntry {
  id: number;
  date: string;
  occasion: string;
  outfit: {
    name: string;
    image: string;
    items: string[];
  };
  rating: number;
  notes: string;
  location?: string;
  weather?: string;
  mood: string;
  tags: string[];
}

const mockStyleHistory: StyleEntry[] = [
  {
    id: 1,
    date: '2024-01-15',
    occasion: 'Wedding',
    outfit: {
      name: 'Elegant Navy Dress',
      image: 'https://images.unsplash.com/photo-1566479179817-a71bf3ce2e85?w=300',
      items: ['Navy Midi Dress', 'Pearl Necklace', 'Block Heels', 'Clutch Bag']
    },
    rating: 5,
    notes: 'Felt confident and received many compliments',
    location: 'Garden Venue',
    weather: 'Sunny, 75°F',
    mood: 'Confident',
    tags: ['formal', 'elegant', 'comfortable']
  },
  {
    id: 2,
    date: '2024-01-10',
    occasion: 'Work Meeting',
    outfit: {
      name: 'Professional Blazer Set',
      image: 'https://images.unsplash.com/photo-1551803091-e20673f05c05?w=300',
      items: ['Black Blazer', 'White Blouse', 'Pencil Skirt', 'Pumps']
    },
    rating: 4,
    notes: 'Perfect for presentation, felt authoritative',
    location: 'Office',
    weather: 'Indoor',
    mood: 'Professional',
    tags: ['business', 'classic', 'powerful']
  },
  {
    id: 3,
    date: '2024-01-05',
    occasion: 'Casual Outing',
    outfit: {
      name: 'Weekend Casual',
      image: 'https://images.unsplash.com/photo-1581044777550-4cfa60707c03?w=300',
      items: ['Denim Jacket', 'Striped Tee', 'Skinny Jeans', 'White Sneakers']
    },
    rating: 4,
    notes: 'Comfortable for walking around the city',
    location: 'Downtown',
    weather: 'Cloudy, 68°F',
    mood: 'Relaxed',
    tags: ['casual', 'comfortable', 'trendy']
  }
];

const StyleHistory = ({ isOpen, onClose }: StyleHistoryProps) => {
  const [styleHistory, setStyleHistory] = useState<StyleEntry[]>(mockStyleHistory);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [sortBy, setSortBy] = useState('date');

  const filteredHistory = styleHistory.filter(entry => {
    const matchesSearch = entry.occasion.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         entry.outfit.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         entry.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesFilter = selectedFilter === 'all' || entry.occasion.toLowerCase().includes(selectedFilter);
    return matchesSearch && matchesFilter;
  });

  const sortedHistory = [...filteredHistory].sort((a, b) => {
    switch (sortBy) {
      case 'date':
        return new Date(b.date).getTime() - new Date(a.date).getTime();
      case 'rating':
        return b.rating - a.rating;
      case 'occasion':
        return a.occasion.localeCompare(b.occasion);
      default:
        return 0;
    }
  });

  const getStyleStats = () => {
    const totalOutfits = styleHistory.length;
    const avgRating = styleHistory.reduce((sum, entry) => sum + entry.rating, 0) / totalOutfits;
    const topOccasions = styleHistory.reduce((acc, entry) => {
      acc[entry.occasion] = (acc[entry.occasion] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    const mostFrequentOccasion = Object.entries(topOccasions).sort(([,a], [,b]) => b - a)[0];
    
    return {
      totalOutfits,
      avgRating: avgRating.toFixed(1),
      mostFrequentOccasion: mostFrequentOccasion ? mostFrequentOccasion[0] : 'None'
    };
  };

  if (!isOpen) return null;

  const stats = getStyleStats();

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-3xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Style History</h2>
            <p className="text-gray-600 dark:text-gray-400">Track your fashion journey and style evolution</p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>×</Button>
        </div>

        <div className="p-6 space-y-6">
          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20">
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-blue-600">{stats.totalOutfits}</div>
                <div className="text-sm text-blue-700 dark:text-blue-300">Total Outfits</div>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-r from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20">
              <CardContent className="p-4 text-center">
                <div className="flex items-center justify-center gap-1">
                  <span className="text-2xl font-bold text-green-600">{stats.avgRating}</span>
                  <Star className="w-5 h-5 text-yellow-500 fill-current" />
                </div>
                <div className="text-sm text-green-700 dark:text-green-300">Average Rating</div>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-r from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20">
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-purple-600">{stats.mostFrequentOccasion}</div>
                <div className="text-sm text-purple-700 dark:text-purple-300">Top Occasion</div>
              </CardContent>
            </Card>
          </div>

          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <Input
                  placeholder="Search by occasion, outfit, or tags..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="flex gap-2">
              <select 
                value={selectedFilter}
                onChange={(e) => setSelectedFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="all">All Occasions</option>
                <option value="wedding">Wedding</option>
                <option value="work">Work</option>
                <option value="casual">Casual</option>
                <option value="church">Church</option>
              </select>
              
              <select 
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="date">Sort by Date</option>
                <option value="rating">Sort by Rating</option>
                <option value="occasion">Sort by Occasion</option>
              </select>
            </div>
          </div>

          {/* Style History Timeline */}
          <div className="space-y-6">
            {sortedHistory.map((entry) => (
              <Card key={entry.id} className="overflow-hidden hover:shadow-lg transition-all duration-300">
                <div className="flex flex-col lg:flex-row">
                  <div className="lg:w-64 aspect-square lg:aspect-auto">
                    <img 
                      src={entry.outfit.image} 
                      alt={entry.outfit.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  
                  <div className="flex-1 p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white">{entry.outfit.name}</h3>
                        <p className="text-gray-600 dark:text-gray-400">{entry.occasion}</p>
                      </div>
                      
                      <div className="flex items-center gap-1">
                        {[...Array(5)].map((_, i) => (
                          <Star 
                            key={i} 
                            size={16} 
                            className={i < entry.rating ? "text-yellow-500 fill-current" : "text-gray-300"} 
                          />
                        ))}
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                          <Calendar size={16} />
                          <span>{new Date(entry.date).toLocaleDateString()}</span>
                        </div>
                        {entry.location && (
                          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                            <MapPin size={16} />
                            <span>{entry.location}</span>
                          </div>
                        )}
                        {entry.weather && (
                          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                            <TrendingUp size={16} />
                            <span>{entry.weather}</span>
                          </div>
                        )}
                      </div>
                      
                      <div className="space-y-2">
                        <div className="text-sm">
                          <span className="font-medium text-gray-900 dark:text-white">Mood: </span>
                          <span className="text-gray-600 dark:text-gray-400">{entry.mood}</span>
                        </div>
                        <div className="text-sm">
                          <span className="font-medium text-gray-900 dark:text-white">Items: </span>
                          <span className="text-gray-600 dark:text-gray-400">{entry.outfit.items.length} pieces</span>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div>
                        <h4 className="font-medium text-gray-900 dark:text-white mb-2">Outfit Details:</h4>
                        <div className="flex flex-wrap gap-2">
                          {entry.outfit.items.map((item, i) => (
                            <Badge key={i} variant="outline" className="text-xs">
                              {item}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      {entry.notes && (
                        <div>
                          <h4 className="font-medium text-gray-900 dark:text-white mb-1">Notes:</h4>
                          <p className="text-gray-600 dark:text-gray-400 text-sm italic">"{entry.notes}"</p>
                        </div>
                      )}

                      <div className="flex flex-wrap gap-1">
                        {entry.tags.map((tag, i) => (
                          <Badge key={i} className="text-xs bg-owis-gold/10 text-owis-gold">
                            #{tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {sortedHistory.length === 0 && (
            <div className="text-center py-12">
              <Clock className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No Style History Found</h3>
              <p className="text-gray-600 dark:text-gray-400">Start wearing and rating your outfits to build your style timeline!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StyleHistory;
