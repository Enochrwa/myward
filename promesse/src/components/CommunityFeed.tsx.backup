
import React, { useState, useEffect } from 'react';
import { Heart, MessageCircle, Share2, Bookmark, MoreHorizontal, Camera, Plus, Filter, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import FeedbackSection from './FeedbackSection'; // Import the new component

interface Post {
  id: string;
  user: {
    name: string;
    username: string;
    avatar: string;
    verified: boolean;
    followers: number;
  };
  content: {
    caption: string;
    image: string;
    tags: string[];
    outfit: {
      items: string[];
      brands: string[];
      totalValue: number;
    };
  };
  engagement: {
    likes: number;
    comments: number;
    shares: number;
    saves: number;
    liked: boolean;
    saved: boolean;
  };
  timestamp: string;
  location?: string;
}

const CommunityFeed = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [filter, setFilter] = useState('following');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadPosts();
  }, [filter]);

  const loadPosts = () => {
    setIsLoading(true);
    
    setTimeout(() => {
      const mockPosts: Post[] = [
        {
          id: '1',
          user: {
            name: 'Emma Rodriguez',
            username: '@emmastyle',
            avatar: '/placeholder.svg',
            verified: true,
            followers: 12500
          },
          content: {
            caption: 'Perfect autumn vibes with this cozy yet chic ensemble! The camel coat is everything 🧥✨ #AutumnStyle #OOTD',
            image: '/placeholder.svg',
            tags: ['#AutumnStyle', '#OOTD', '#CamelCoat', '#CozyChic'],
            outfit: {
              items: ['Camel Wool Coat', 'Cream Turtleneck', 'Dark Wash Jeans', 'Brown Leather Boots'],
              brands: ['Zara', 'Uniqlo', 'Levi\'s', 'Madewell'],
              totalValue: 420
            }
          },
          engagement: {
            likes: 1247,
            comments: 83,
            shares: 29,
            saves: 156,
            liked: false,
            saved: true
          },
          timestamp: '2h',
          location: 'New York, NY'
        },
        {
          id: '2',
          user: {
            name: 'Sofia Chen',
            username: '@sofiasfashion',
            avatar: '/placeholder.svg',
            verified: false,
            followers: 3200
          },
          content: {
            caption: 'Mixing prints like a pro! Who says you can\'t wear stripes with florals? 🌸',
            image: '/placeholder.svg',
            tags: ['#MixedPrints', '#PatternMixing', '#BoldFashion'],
            outfit: {
              items: ['Striped Blazer', 'Floral Midi Skirt', 'White Sneakers', 'Gold Jewelry'],
              brands: ['H&M', 'Zara', 'Adidas', 'Local Boutique'],
              totalValue: 180
            }
          },
          engagement: {
            likes: 892,
            comments: 67,
            shares: 45,
            saves: 203,
            liked: true,
            saved: false
          },
          timestamp: '4h',
          location: 'San Francisco, CA'
        },
        {
          id: '3',
          user: {
            name: 'Marcus Johnson',
            username: '@marcusstyle',
            avatar: '/placeholder.svg',
            verified: true,
            followers: 8900
          },
          content: {
            caption: 'Minimalist Monday mood. Sometimes less really is more 🖤',
            image: '/placeholder.svg',
            tags: ['#MinimalistStyle', '#MonochromeOutfit', '#LessIsMore'],
            outfit: {
              items: ['Black Turtleneck', 'Black Trousers', 'Black Leather Shoes', 'Silver Watch'],
              brands: ['COS', 'Acne Studios', 'Common Projects', 'Rolex'],
              totalValue: 1200
            }
          },
          engagement: {
            likes: 2156,
            comments: 124,
            shares: 67,
            saves: 445,
            liked: true,
            saved: true
          },
          timestamp: '6h',
          location: 'London, UK'
        }
      ];
      
      setPosts(mockPosts);
      setIsLoading(false);
    }, 1000);
  };

  const toggleLike = (postId: string) => {
    setPosts(prev => prev.map(post => 
      post.id === postId 
        ? {
            ...post,
            engagement: {
              ...post.engagement,
              liked: !post.engagement.liked,
              likes: post.engagement.liked 
                ? post.engagement.likes - 1 
                : post.engagement.likes + 1
            }
          }
        : post
    ));
  };

  const toggleSave = (postId: string) => {
    setPosts(prev => prev.map(post => 
      post.id === postId 
        ? {
            ...post,
            engagement: {
              ...post.engagement,
              saved: !post.engagement.saved,
              saves: post.engagement.saved 
                ? post.engagement.saves - 1 
                : post.engagement.saves + 1
            }
          }
        : post
    ));
  };

  const formatNumber = (num: number) => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'k';
    }
    return num.toString();
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold gradient-text">Style Feed</h1>
          <p className="text-owis-charcoal/70 dark:text-owis-cream/70">
            Discover and share fashion inspiration
          </p>
        </div>
        
        <div className="flex gap-3">
          <Button variant="outline" className="flex items-center gap-2">
            <Filter size={16} />
            Filter
          </Button>
          <Button className="owis-button-primary flex items-center gap-2">
            <Plus size={16} />
            Create Post
          </Button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-1 mb-6 bg-white dark:bg-owis-charcoal rounded-2xl p-1 shadow-sm">
        {[
          { id: 'following', label: 'Following', icon: Heart },
          { id: 'trending', label: 'Trending', icon: TrendingUp },
          { id: 'discover', label: 'Discover', icon: Camera }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setFilter(tab.id)}
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl transition-all ${
              filter === tab.id
                ? 'bg-gradient-to-r from-owis-gold to-owis-bronze text-white shadow-md'
                : 'text-owis-charcoal/70 dark:text-owis-cream/70 hover:bg-gray-50 dark:hover:bg-owis-charcoal-light'
            }`}
          >
            <tab.icon size={16} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Posts */}
      {isLoading ? (
        <div className="space-y-6">
          {[1, 2, 3].map(i => (
            <Card key={i} className="animate-pulse">
              <CardHeader className="flex flex-row items-center gap-4">
                <div className="w-12 h-12 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-2"></div>
                  <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-20"></div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="aspect-square bg-gray-200 dark:bg-gray-700 rounded-xl mb-4"></div>
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full mb-2"></div>
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="space-y-6">
          {posts.map(post => (
            <Card key={post.id} className="owis-card owis-interactive">
              {/* Post Header */}
              <CardHeader className="flex flex-row items-center gap-4 pb-4">
                <div className="relative">
                  <img 
                    src={post.user.avatar} 
                    alt={post.user.name}
                    className="w-12 h-12 rounded-full object-cover"
                  />
                  {post.user.verified && (
                    <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-owis-gold rounded-full flex items-center justify-center">
                      <span className="text-white text-xs">✓</span>
                    </div>
                  )}
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-owis-charcoal dark:text-owis-cream">
                      {post.user.name}
                    </h3>
                    <span className="text-owis-charcoal/60 dark:text-owis-cream/60 text-sm">
                      {post.user.username}
                    </span>
                    <span className="text-owis-charcoal/40 dark:text-owis-cream/40 text-sm">
                      • {post.timestamp}
                    </span>
                  </div>
                  {post.location && (
                    <p className="text-owis-charcoal/60 dark:text-owis-cream/60 text-sm">
                      📍 {post.location}
                    </p>
                  )}
                </div>
                
                <Button variant="ghost" size="icon" className="text-owis-charcoal/60 dark:text-owis-cream/60">
                  <MoreHorizontal size={20} />
                </Button>
              </CardHeader>

              <CardContent className="space-y-4">
                {/* Post Image */}
                <div className="aspect-square rounded-2xl overflow-hidden bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800">
                  <img 
                    src={post.content.image} 
                    alt="Outfit post"
                    className="w-full h-full object-cover"
                  />
                </div>

                {/* Engagement Actions */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <button 
                      onClick={() => toggleLike(post.id)}
                      className={`flex items-center gap-2 transition-colors ${
                        post.engagement.liked 
                          ? 'text-red-500' 
                          : 'text-owis-charcoal dark:text-owis-cream hover:text-red-500'
                      }`}
                    >
                      <Heart size={20} fill={post.engagement.liked ? 'currentColor' : 'none'} />
                      <span className="text-sm font-medium">
                        {formatNumber(post.engagement.likes)}
                      </span>
                    </button>
                    
                    <button className="flex items-center gap-2 text-owis-charcoal dark:text-owis-cream hover:text-owis-gold transition-colors">
                      <MessageCircle size={20} />
                      <span className="text-sm font-medium">
                        {formatNumber(post.engagement.comments)}
                      </span>
                    </button>
                    
                    <button className="flex items-center gap-2 text-owis-charcoal dark:text-owis-cream hover:text-owis-gold transition-colors">
                      <Share2 size={20} />
                      <span className="text-sm font-medium">
                        {formatNumber(post.engagement.shares)}
                      </span>
                    </button>
                  </div>
                  
                  <button 
                    onClick={() => toggleSave(post.id)}
                    className={`transition-colors ${
                      post.engagement.saved 
                        ? 'text-owis-gold' 
                        : 'text-owis-charcoal dark:text-owis-cream hover:text-owis-gold'
                    }`}
                  >
                    <Bookmark size={20} fill={post.engagement.saved ? 'currentColor' : 'none'} />
                  </button>
                </div>

                {/* Post Caption */}
                <div>
                  <p className="text-owis-charcoal dark:text-owis-cream mb-2">
                    <span className="font-semibold mr-2">{post.user.username}</span>
                    {post.content.caption}
                  </p>
                  
                  <div className="flex flex-wrap gap-1 mb-3">
                    {post.content.tags.map((tag, i) => (
                      <span key={i} className="text-owis-gold hover:underline cursor-pointer text-sm">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Outfit Details */}
                <div className="bg-owis-cream/50 dark:bg-owis-charcoal-light rounded-xl p-4">
                  <h4 className="font-semibold text-owis-charcoal dark:text-owis-cream mb-2">
                    Outfit Details
                  </h4>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="font-medium text-owis-charcoal/80 dark:text-owis-cream/80 mb-1">Items:</p>
                      <div className="space-y-1">
                        {post.content.outfit.items.map((item, i) => (
                          <div key={i} className="text-owis-charcoal/70 dark:text-owis-cream/70">
                            • {item}
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <p className="font-medium text-owis-charcoal/80 dark:text-owis-cream/80 mb-1">Brands:</p>
                      <div className="space-y-1">
                        {post.content.outfit.brands.map((brand, i) => (
                          <div key={i} className="text-owis-charcoal/70 dark:text-owis-cream/70">
                            • {brand}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-3 pt-3 border-t border-owis-charcoal/10 dark:border-owis-cream/10">
                    <p className="text-sm font-medium text-owis-charcoal dark:text-owis-cream">
                      Total Outfit Value: <span className="text-owis-gold">${post.content.outfit.totalValue}</span>
                    </p>
                  </div>
                </div>

                {/* Feedback Section Integration */}
                <FeedbackSection outfitId={post.id} />

              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default CommunityFeed;
