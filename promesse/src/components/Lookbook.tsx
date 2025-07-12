
import React, { useState, useEffect } from 'react';
import { Camera, Heart, Share2, Bookmark, Eye, Grid, List, Filter, Search, Plus, Sparkles } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface LookbookEntry {
  id: string;
  title: string;
  description: string;
  image: string;
  user: {
    name: string;
    username: string;
    avatar: string;
    verified: boolean;
  };
  outfit: {
    items: string[];
    brands: string[];
    totalValue: number;
    occasion: string;
  };
  engagement: {
    likes: number;
    views: number;
    saves: number;
    shares: number;
    liked: boolean;
    saved: boolean;
  };
  tags: string[];
  category: string;
  createdAt: string;
  featured: boolean;
}

const Lookbook = () => {
  const [entries, setEntries] = useState<LookbookEntry[]>([]);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadLookbookEntries();
  }, [selectedCategory]);

  const loadLookbookEntries = () => {
    setIsLoading(true);
    
    setTimeout(() => {
      const mockEntries: LookbookEntry[] = [
        {
          id: '1',
          title: 'Autumn Office Elegance',
          description: 'Perfect blend of professional and seasonal with warm earth tones',
          image: '/placeholder.svg',
          user: {
            name: 'Emma Rodriguez',
            username: '@emmastyle',
            avatar: '/placeholder.svg',
            verified: true
          },
          outfit: {
            items: ['Camel Wool Coat', 'Cream Silk Blouse', 'Dark Wash Trousers', 'Brown Leather Loafers'],
            brands: ['Zara', 'Theory', 'Everlane', 'Cole Haan'],
            totalValue: 485,
            occasion: 'Business Casual'
          },
          engagement: {
            likes: 1247,
            views: 8934,
            saves: 456,
            shares: 89,
            liked: false,
            saved: true
          },
          tags: ['#AutumnStyle', '#BusinessCasual', '#EarthTones', '#Professional'],
          category: 'Work',
          createdAt: '2024-01-15',
          featured: true
        },
        {
          id: '2',
          title: 'Weekend Boho Vibes',
          description: 'Relaxed and artistic with flowing fabrics and natural textures',
          image: '/placeholder.svg',
          user: {
            name: 'Luna Martinez',
            username: '@lunaboho',
            avatar: '/placeholder.svg',
            verified: false
          },
          outfit: {
            items: ['Flowy Maxi Dress', 'Denim Jacket', 'Ankle Boots', 'Crossbody Bag'],
            brands: ['Free People', 'Levi\'s', 'Dr. Martens', 'Coach'],
            totalValue: 320,
            occasion: 'Casual Weekend'
          },
          engagement: {
            likes: 892,
            views: 5634,
            saves: 234,
            shares: 67,
            liked: true,
            saved: false
          },
          tags: ['#BohoStyle', '#WeekendVibes', '#Casual', '#Artistic'],
          category: 'Casual',
          createdAt: '2024-01-14',
          featured: false
        },
        {
          id: '3',
          title: 'Date Night Glamour',
          description: 'Sophisticated evening look with a touch of sparkle',
          image: '/placeholder.svg',
          user: {
            name: 'Sophia Chen',
            username: '@sophiaglam',
            avatar: '/placeholder.svg',
            verified: true
          },
          outfit: {
            items: ['Black Midi Dress', 'Statement Earrings', 'Heeled Sandals', 'Clutch Bag'],
            brands: ['& Other Stories', 'Mejuri', 'Stuart Weitzman', 'Polene'],
            totalValue: 680,
            occasion: 'Date Night'
          },
          engagement: {
            likes: 2156,
            views: 12450,
            saves: 789,
            shares: 145,
            liked: true,
            saved: true
          },
          tags: ['#DateNight', '#Evening', '#Glamour', '#Sophisticated'],
          category: 'Evening',
          createdAt: '2024-01-13',
          featured: true
        },
        {
          id: '4',
          title: 'Minimalist Chic',
          description: 'Clean lines and neutral tones for effortless elegance',
          image: '/placeholder.svg',
          user: {
            name: 'Alex Kim',
            username: '@alexminimal',
            avatar: '/placeholder.svg',
            verified: false
          },
          outfit: {
            items: ['White Button Shirt', 'Black Trousers', 'White Sneakers', 'Structured Bag'],
            brands: ['COS', 'Arket', 'Common Projects', 'Bottega Veneta'],
            totalValue: 890,
            occasion: 'Everyday Minimal'
          },
          engagement: {
            likes: 1543,
            views: 9876,
            saves: 567,
            shares: 98,
            liked: false,
            saved: false
          },
          tags: ['#MinimalistStyle', '#Monochrome', '#Clean', '#Effortless'],
          category: 'Minimal',
          createdAt: '2024-01-12',
          featured: false
        }
      ];
      
      setEntries(mockEntries);
      setIsLoading(false);
    }, 1000);
  };

  const toggleLike = (entryId: string) => {
    setEntries(prev => prev.map(entry => 
      entry.id === entryId 
        ? {
            ...entry,
            engagement: {
              ...entry.engagement,
              liked: !entry.engagement.liked,
              likes: entry.engagement.liked 
                ? entry.engagement.likes - 1 
                : entry.engagement.likes + 1
            }
          }
        : entry
    ));
  };

  const toggleSave = (entryId: string) => {
    setEntries(prev => prev.map(entry => 
      entry.id === entryId 
        ? {
            ...entry,
            engagement: {
              ...entry.engagement,
              saved: !entry.engagement.saved,
              saves: entry.engagement.saved 
                ? entry.engagement.saves - 1 
                : entry.engagement.saves + 1
            }
          }
        : entry
    ));
  };

  const categories = [
    { id: 'all', label: 'All Looks' },
    { id: 'work', label: 'Work' },
    { id: 'casual', label: 'Casual' },
    { id: 'evening', label: 'Evening' },
    { id: 'minimal', label: 'Minimal' },
    { id: 'party', label: 'Party' }
  ];

  const filteredEntries = entries.filter(entry => {
    const matchesCategory = selectedCategory === 'all' || entry.category.toLowerCase() === selectedCategory;
    const matchesSearch = entry.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
                         entry.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         entry.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  const formatNumber = (num: number) => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'k';
    }
    return num.toString();
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-3 mb-4">
          <div className="p-3 bg-gradient-to-r from-pink-500 to-rose-600 rounded-2xl shadow-lg">
            <Camera className="text-white" size={32} />
          </div>
          <h1 className="text-4xl font-bold gradient-text">Lookbook</h1>
        </div>
        <p className="text-owis-charcoal/70 dark:text-owis-cream/70 text-lg max-w-2xl mx-auto">
          Curated style inspiration and outfit ideas from fashion enthusiasts
        </p>
      </div>

      {/* Controls */}
      <div className="flex flex-col lg:flex-row gap-4 mb-8">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-owis-charcoal/40 dark:text-owis-cream/40" size={20} />
          <Input
            placeholder="Search looks, styles, or tags..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 focus-ring bg-white dark:bg-owis-charcoal border-owis-purple/30"
          />
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline" className="flex items-center gap-2 border-owis-purple text-owis-purple hover:bg-owis-purple hover:text-white">
            <Filter size={16} />
            Filter
          </Button>
          
          <div className="flex bg-white dark:bg-owis-charcoal rounded-lg border border-owis-purple/30">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-l-lg transition-colors ${viewMode === 'grid' ? 'bg-owis-purple text-white' : 'text-owis-charcoal dark:text-owis-cream hover:bg-owis-cream dark:hover:bg-owis-charcoal-light'}`}
            >
              <Grid size={20} />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-r-lg transition-colors ${viewMode === 'list' ? 'bg-owis-purple text-white' : 'text-owis-charcoal dark:text-owis-cream hover:bg-owis-cream dark:hover:bg-owis-charcoal-light'}`}
            >
              <List size={20} />
            </button>
          </div>
          
          <Button className="owis-button-primary flex items-center gap-2">
            <Plus size={16} />
            Add Look
          </Button>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex overflow-x-auto pb-2 mb-8">
        <div className="flex gap-2 min-w-max">
          {categories.map(category => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`px-4 py-2 rounded-xl whitespace-nowrap transition-all ${
                selectedCategory === category.id
                  ? 'bg-gradient-to-r from-owis-purple to-owis-bronze text-white shadow-md'
                  : 'bg-white dark:bg-owis-charcoal text-owis-charcoal dark:text-owis-cream hover:bg-owis-cream dark:hover:bg-owis-charcoal-light border border-owis-purple/20'
              }`}
            >
              {category.label}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className={`grid gap-6 ${viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1'}`}>
          {[1, 2, 3, 4, 5, 6].map(i => (
            <Card key={i} className="animate-pulse owis-card">
              <CardContent className="p-0">
                <div className={`${viewMode === 'grid' ? 'aspect-[3/4]' : 'h-64'} bg-gray-200 dark:bg-gray-700 rounded-t-2xl`}></div>
                <div className="p-4">
                  <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <>
          {/* Featured Looks */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4 flex items-center gap-2 text-owis-charcoal dark:text-owis-cream">
              <Sparkles className="text-owis-purple" />
              Featured Looks
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredEntries
                .filter(entry => entry.featured)
                .slice(0, 3)
                .map(entry => (
                  <Card key={entry.id} className="owis-card owis-interactive relative ring-2 ring-owis-purple shadow-glow">
                    <div className="absolute top-4 right-4 bg-gradient-to-r from-owis-purple to-owis-bronze text-white px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1 z-10">
                      <Sparkles size={10} />
                      Featured
                    </div>
                    
                    <CardContent className="p-0">
                      <div className="aspect-[3/4] rounded-t-2xl overflow-hidden bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800 relative group">
                        <img 
                          src={entry.image} 
                          alt={entry.title}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        />
                        <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                        <div className="absolute bottom-4 left-4 right-4 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                          <div className="flex items-center gap-2 text-sm">
                            <Eye size={14} />
                            <span>{formatNumber(entry.engagement.views)} views</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <img 
                            src={entry.user.avatar} 
                            alt={entry.user.name}
                            className="w-6 h-6 rounded-full object-cover border border-owis-purple/30"
                          />
                          <span className="text-sm font-medium text-owis-charcoal dark:text-owis-cream">{entry.user.name}</span>
                          {entry.user.verified && (
                            <div className="w-4 h-4 bg-owis-purple rounded-full flex items-center justify-center">
                              <span className="text-white text-xs">✓</span>
                            </div>
                          )}
                        </div>
                        
                        <h3 className="font-bold text-lg mb-1 text-owis-charcoal dark:text-owis-cream">{entry.title}</h3>
                        <p className="text-sm text-owis-charcoal/70 dark:text-owis-cream/70 mb-3">{entry.description}</p>
                        
                        <div className="flex flex-wrap gap-1 mb-3">
                          {entry.tags.slice(0, 3).map((tag, i) => (
                            <span key={i} className="px-2 py-1 bg-owis-cream/80 dark:bg-owis-charcoal-light/80 text-owis-charcoal dark:text-owis-cream rounded text-xs border border-owis-purple/20">
                              {tag}
                            </span>
                          ))}
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <button 
                              onClick={() => toggleLike(entry.id)}
                              className={`flex items-center gap-1 transition-colors ${
                                entry.engagement.liked 
                                  ? 'text-red-500' 
                                  : 'text-owis-charcoal dark:text-owis-cream hover:text-red-500'
                              }`}
                            >
                              <Heart size={16} fill={entry.engagement.liked ? 'currentColor' : 'none'} />
                              <span className="text-sm">{formatNumber(entry.engagement.likes)}</span>
                            </button>
                            
                            <button className="flex items-center gap-1 text-owis-charcoal dark:text-owis-cream hover:text-owis-purple transition-colors">
                              <Share2 size={16} />
                              <span className="text-sm">{formatNumber(entry.engagement.shares)}</span>
                            </button>
                          </div>
                          
                          <button 
                            onClick={() => toggleSave(entry.id)}
                            className={`transition-colors ${
                              entry.engagement.saved 
                                ? 'text-owis-purple' 
                                : 'text-owis-charcoal dark:text-owis-cream hover:text-owis-purple'
                            }`}
                          >
                            <Bookmark size={16} fill={entry.engagement.saved ? 'currentColor' : 'none'} />
                          </button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
            </div>
          </div>

          {/* All Looks */}
          <div>
            <h2 className="text-2xl font-bold mb-4 text-owis-charcoal dark:text-owis-cream">
              All Looks ({filteredEntries.length})
            </h2>
            <div className={`grid gap-6 ${viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4' : 'grid-cols-1'}`}>
              {filteredEntries.map(entry => (
                <Card key={entry.id} className="owis-card owis-interactive">
                  <CardContent className="p-0">
                    <div className={`${viewMode === 'grid' ? 'aspect-[3/4]' : 'h-64 md:h-48'} rounded-t-2xl overflow-hidden bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800 relative group`}>
                      <img 
                        src={entry.image} 
                        alt={entry.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                      <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                      <div className="absolute bottom-4 left-4 right-4 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        <div className="flex items-center gap-2 text-sm">
                          <Eye size={14} />
                          <span>{formatNumber(entry.engagement.views)} views</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <img 
                          src={entry.user.avatar} 
                          alt={entry.user.name}
                          className="w-6 h-6 rounded-full object-cover border border-owis-purple/30"
                        />
                        <span className="text-sm font-medium text-owis-charcoal dark:text-owis-cream">{entry.user.name}</span>
                        {entry.user.verified && (
                          <div className="w-4 h-4 bg-owis-purple rounded-full flex items-center justify-center">
                            <span className="text-white text-xs">✓</span>
                          </div>
                        )}
                      </div>
                      
                      <h3 className="font-bold text-lg mb-1 text-owis-charcoal dark:text-owis-cream">{entry.title}</h3>
                      <p className="text-sm text-owis-charcoal/70 dark:text-owis-cream/70 mb-3">{entry.description}</p>
                      
                      <div className="flex flex-wrap gap-1 mb-3">
                        {entry.tags.slice(0, 3).map((tag, i) => (
                          <span key={i} className="px-2 py-1 bg-owis-cream/80 dark:bg-owis-charcoal-light/80 text-owis-charcoal dark:text-owis-cream rounded text-xs border border-owis-purple/20">
                            {tag}
                          </span>
                        ))}
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <button 
                            onClick={() => toggleLike(entry.id)}
                            className={`flex items-center gap-1 transition-colors ${
                              entry.engagement.liked 
                                ? 'text-red-500' 
                                : 'text-owis-charcoal dark:text-owis-cream hover:text-red-500'
                            }`}
                          >
                            <Heart size={16} fill={entry.engagement.liked ? 'currentColor' : 'none'} />
                            <span className="text-sm">{formatNumber(entry.engagement.likes)}</span>
                          </button>
                          
                          <button className="flex items-center gap-1 text-owis-charcoal dark:text-owis-cream hover:text-owis-purple transition-colors">
                            <Share2 size={16} />
                            <span className="text-sm">{formatNumber(entry.engagement.shares)}</span>
                          </button>
                        </div>
                        
                        <button 
                          onClick={() => toggleSave(entry.id)}
                          className={`transition-colors ${
                            entry.engagement.saved 
                              ? 'text-owis-purple' 
                              : 'text-owis-charcoal dark:text-owis-cream hover:text-owis-purple'
                          }`}
                        >
                          <Bookmark size={16} fill={entry.engagement.saved ? 'currentColor' : 'none'} />
                        </button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Lookbook;
