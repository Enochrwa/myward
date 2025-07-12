
import React, { useState, useEffect } from 'react';
import { Users, Plus, Crown, MessageCircle, Camera, Heart, Star, Search, Filter } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface Community {
  id: string;
  name: string;
  description: string;
  memberCount: number;
  category: string;
  tags: string[];
  isPrivate: boolean;
  isJoined: boolean;
  coverImage: string;
  avatar: string;
  recentActivity: {
    posts: number;
    activeMembers: number;
  };
  moderators: string[];
  featured: boolean;
}

interface CommunityPost {
  id: string;
  communityId: string;
  user: {
    name: string;
    username: string;
    avatar: string;
  };
  content: string;
  image?: string;
  likes: number;
  comments: number;
  timestamp: string;
}

const StyleCommunities = () => {
  const [communities, setCommunities] = useState<Community[]>([]);
  const [posts, setPosts] = useState<CommunityPost[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadCommunities();
    loadPosts();
  }, [selectedCategory]);

  const loadCommunities = () => {
    setIsLoading(true);
    
    setTimeout(() => {
      const mockCommunities: Community[] = [
        {
          id: '1',
          name: 'Sustainable Fashion Lovers',
          description: 'Dedicated to ethical and eco-friendly fashion choices',
          memberCount: 15420,
          category: 'Sustainability',
          tags: ['#EcoFashion', '#Sustainable', '#Ethical'],
          isPrivate: false,
          isJoined: true,
          coverImage: '/placeholder.svg',
          avatar: '/placeholder.svg',
          recentActivity: {
            posts: 342,
            activeMembers: 89
          },
          moderators: ['@ecofashionista', '@sustainablestyle'],
          featured: true
        },
        {
          id: '2',
          name: 'Vintage Collectors',
          description: 'Sharing and discovering authentic vintage pieces',
          memberCount: 8750,
          category: 'Vintage',
          tags: ['#Vintage', '#Retro', '#Antique'],
          isPrivate: false,
          isJoined: false,
          coverImage: '/placeholder.svg',
          avatar: '/placeholder.svg',
          recentActivity: {
            posts: 156,
            activeMembers: 45
          },
          moderators: ['@vintagequeen', '@retrohunter'],
          featured: true
        },
        {
          id: '3',
          name: 'Street Style Society',
          description: 'Urban fashion inspiration from around the world',
          memberCount: 23100,
          category: 'Street Style',
          tags: ['#StreetStyle', '#Urban', '#Casual'],
          isPrivate: false,
          isJoined: true,
          coverImage: '/placeholder.svg',
          avatar: '/placeholder.svg',
          recentActivity: {
            posts: 789,
            activeMembers: 156
          },
          moderators: ['@streetfashion', '@urbanstyle'],
          featured: false
        },
        {
          id: '4',
          name: 'Minimalist Wardrobe',
          description: 'Less is more - curating the perfect capsule wardrobe',
          memberCount: 12890,
          category: 'Minimalism',
          tags: ['#Minimalist', '#CapsuleWardrobe', '#LessIsMore'],
          isPrivate: true,
          isJoined: false,
          coverImage: '/placeholder.svg',
          avatar: '/placeholder.svg',
          recentActivity: {
            posts: 234,
            activeMembers: 67
          },
          moderators: ['@minimalstyle', '@capsulewardrobe'],
          featured: false
        },
        {
          id: '5',
          name: 'Luxury Fashion Hub',
          description: 'High-end fashion enthusiasts and luxury brand discussions',
          memberCount: 6540,
          category: 'Luxury',
          tags: ['#Luxury', '#HighEnd', '#Designer'],
          isPrivate: true,
          isJoined: true,
          coverImage: '/placeholder.svg',
          avatar: '/placeholder.svg',
          recentActivity: {
            posts: 98,
            activeMembers: 23
          },
          moderators: ['@luxurystyle', '@designerfashion'],
          featured: true
        }
      ];
      
      setCommunities(mockCommunities);
      setIsLoading(false);
    }, 1000);
  };

  const loadPosts = () => {
    const mockPosts: CommunityPost[] = [
      {
        id: '1',
        communityId: '1',
        user: {
          name: 'Maya Green',
          username: '@mayagreen',
          avatar: '/placeholder.svg'
        },
        content: 'Found this amazing organic cotton dress at a local thrift store! Proof that sustainable fashion can be affordable 🌱',
        image: '/placeholder.svg',
        likes: 234,
        comments: 45,
        timestamp: '2h'
      },
      {
        id: '2',
        communityId: '3',
        user: {
          name: 'Alex Kim',
          username: '@alexkim',
          avatar: '/placeholder.svg'
        },
        content: 'Street style inspiration from Tokyo! Love how they mix traditional and modern elements 🏮',
        image: '/placeholder.svg',
        likes: 567,
        comments: 89,
        timestamp: '4h'
      }
    ];
    
    setPosts(mockPosts);
  };

  const joinCommunity = (communityId: string) => {
    setCommunities(prev => prev.map(community => 
      community.id === communityId 
        ? { ...community, isJoined: !community.isJoined, memberCount: community.isJoined ? community.memberCount - 1 : community.memberCount + 1 }
        : community
    ));
  };

  const categories = [
    { id: 'all', label: 'All Communities' },
    { id: 'sustainability', label: 'Sustainability' },
    { id: 'vintage', label: 'Vintage' },
    { id: 'street-style', label: 'Street Style' },
    { id: 'minimalism', label: 'Minimalism' },
    { id: 'luxury', label: 'Luxury' }
  ];

  const filteredCommunities = communities.filter(community => {
    const matchesCategory = selectedCategory === 'all' || community.category.toLowerCase().replace(' ', '-') === selectedCategory;
    const matchesSearch = community.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                         community.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-3 mb-4">
          <div className="p-3 bg-gradient-to-r from-purple-500 to-pink-600 rounded-2xl shadow-lg">
            <Users className="text-white" size={32} />
          </div>
          <h1 className="text-4xl font-bold gradient-text">Style Communities</h1>
        </div>
        <p className="text-owis-charcoal/70 dark:text-owis-cream/70 text-lg max-w-2xl mx-auto">
          Connect with like-minded fashion enthusiasts and share your style journey
        </p>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-owis-charcoal/40 dark:text-owis-cream/40" size={20} />
          <Input
            placeholder="Search communities..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 focus-ring bg-white dark:bg-owis-charcoal border-owis-gold/30"
          />
        </div>
        <Button variant="outline" className="flex items-center gap-2 border-owis-gold text-owis-gold hover:bg-owis-gold hover:text-white">
          <Filter size={16} />
          Filters
        </Button>
        <Button className="owis-button-primary flex items-center gap-2">
          <Plus size={16} />
          Create Community
        </Button>
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
                  ? 'bg-gradient-to-r from-owis-gold to-owis-bronze text-white shadow-md'
                  : 'bg-white dark:bg-owis-charcoal text-owis-charcoal dark:text-owis-cream hover:bg-owis-cream dark:hover:bg-owis-charcoal-light border border-owis-gold/20'
              }`}
            >
              {category.label}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <Card key={i} className="animate-pulse owis-card">
              <CardHeader>
                <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded-xl mb-4"></div>
                <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
              </CardHeader>
            </Card>
          ))}
        </div>
      ) : (
        <>
          {/* Featured Communities */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4 flex items-center gap-2 text-owis-charcoal dark:text-owis-cream">
              <Star className="text-owis-gold" />
              Featured Communities
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredCommunities
                .filter(community => community.featured)
                .slice(0, 3)
                .map(community => (
                  <Card key={community.id} className="owis-card owis-interactive relative ring-2 ring-owis-gold shadow-glow">
                    <div className="absolute top-4 right-4 bg-gradient-to-r from-owis-gold to-owis-bronze text-white px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1">
                      <Crown size={10} />
                      Featured
                    </div>
                    
                    <CardHeader className="p-0">
                      <div className="relative h-32 rounded-t-2xl overflow-hidden bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800">
                        <img 
                          src={community.coverImage} 
                          alt={community.name}
                          className="w-full h-full object-cover"
                        />
                        <div className="absolute bottom-4 left-4">
                          <img 
                            src={community.avatar} 
                            alt={community.name}
                            className="w-12 h-12 rounded-full border-3 border-white shadow-lg"
                          />
                        </div>
                      </div>
                    </CardHeader>

                    <CardContent className="p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h3 className="font-bold text-lg text-owis-charcoal dark:text-owis-cream">{community.name}</h3>
                          <p className="text-sm text-owis-charcoal/60 dark:text-owis-cream/60">
                            {community.memberCount.toLocaleString()} members
                          </p>
                        </div>
                        {community.isPrivate && (
                          <div className="bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 px-2 py-1 rounded-full text-xs">
                            Private
                          </div>
                        )}
                      </div>

                      <p className="text-sm text-owis-charcoal/70 dark:text-owis-cream/70 mb-3">
                        {community.description}
                      </p>

                      <div className="flex flex-wrap gap-1 mb-4">
                        {community.tags.map((tag, i) => (
                          <span key={i} className="px-2 py-1 bg-owis-cream/80 dark:bg-owis-charcoal-light/80 text-owis-charcoal dark:text-owis-cream rounded text-xs border border-owis-gold/20">
                            {tag}
                          </span>
                        ))}
                      </div>

                      <div className="flex items-center justify-between mb-4 text-sm text-owis-charcoal/60 dark:text-owis-cream/60">
                        <div className="flex items-center gap-1">
                          <MessageCircle size={14} />
                          <span>{community.recentActivity.posts} posts</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Users size={14} />
                          <span>{community.recentActivity.activeMembers} active</span>
                        </div>
                      </div>

                      <Button
                        onClick={() => joinCommunity(community.id)}
                        className={`w-full ${community.isJoined ? 'bg-green-600 hover:bg-green-700 text-white' : 'owis-button-primary'}`}
                      >
                        {community.isJoined ? 'Joined' : 'Join Community'}
                      </Button>
                    </CardContent>
                  </Card>
                ))}
            </div>
          </div>

          {/* All Communities */}
          <div>
            <h2 className="text-2xl font-bold mb-4 text-owis-charcoal dark:text-owis-cream">
              All Communities ({filteredCommunities.length})
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredCommunities.map(community => (
                <Card key={community.id} className="owis-card owis-interactive">
                  <CardHeader className="p-0">
                    <div className="relative h-32 rounded-t-2xl overflow-hidden bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800">
                      <img 
                        src={community.coverImage} 
                        alt={community.name}
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute bottom-4 left-4">
                        <img 
                          src={community.avatar} 
                          alt={community.name}
                          className="w-12 h-12 rounded-full border-3 border-white shadow-lg"
                        />
                      </div>
                    </div>
                  </CardHeader>

                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="font-bold text-lg text-owis-charcoal dark:text-owis-cream">{community.name}</h3>
                        <p className="text-sm text-owis-charcoal/60 dark:text-owis-cream/60">
                          {community.memberCount.toLocaleString()} members
                        </p>
                      </div>
                      {community.isPrivate && (
                        <div className="bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 px-2 py-1 rounded-full text-xs">
                          Private
                        </div>
                      )}
                    </div>

                    <p className="text-sm text-owis-charcoal/70 dark:text-owis-cream/70 mb-3">
                      {community.description}
                    </p>

                    <div className="flex flex-wrap gap-1 mb-4">
                      {community.tags.map((tag, i) => (
                        <span key={i} className="px-2 py-1 bg-owis-cream/80 dark:bg-owis-charcoal-light/80 text-owis-charcoal dark:text-owis-cream rounded text-xs border border-owis-gold/20">
                          {tag}
                        </span>
                      ))}
                    </div>

                    <div className="flex items-center justify-between mb-4 text-sm text-owis-charcoal/60 dark:text-owis-cream/60">
                      <div className="flex items-center gap-1">
                        <MessageCircle size={14} />
                        <span>{community.recentActivity.posts} posts</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Users size={14} />
                        <span>{community.recentActivity.activeMembers} active</span>
                      </div>
                    </div>

                    <Button
                      onClick={() => joinCommunity(community.id)}
                      className={`w-full ${community.isJoined ? 'bg-green-600 hover:bg-green-700 text-white' : 'owis-button-primary'}`}
                    >
                      {community.isJoined ? 'Joined' : 'Join Community'}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Recent Community Activity */}
          {posts.length > 0 && (
            <div className="mt-12">
              <h2 className="text-2xl font-bold mb-4 text-owis-charcoal dark:text-owis-cream">Recent Activity</h2>
              <div className="space-y-4">
                {posts.map(post => (
                  <Card key={post.id} className="owis-card">
                    <CardContent className="p-4">
                      <div className="flex items-start gap-3">
                        <img 
                          src={post.user.avatar} 
                          alt={post.user.name}
                          className="w-10 h-10 rounded-full object-cover border-2 border-owis-gold/30"
                        />
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-semibold text-owis-charcoal dark:text-owis-cream">{post.user.name}</span>
                            <span className="text-owis-charcoal/60 dark:text-owis-cream/60 text-sm">{post.user.username}</span>
                            <span className="text-owis-charcoal/40 dark:text-owis-cream/40 text-sm">• {post.timestamp}</span>
                          </div>
                          <p className="text-owis-charcoal/80 dark:text-owis-cream/80 mb-3">{post.content}</p>
                          {post.image && (
                            <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800 rounded-xl mb-3 overflow-hidden">
                              <img 
                                src={post.image} 
                                alt="Post content"
                                className="w-full h-full object-cover"
                              />
                            </div>
                          )}
                          <div className="flex items-center gap-4 text-sm text-owis-charcoal/60 dark:text-owis-cream/60">
                            <button className="flex items-center gap-1 hover:text-red-500 transition-colors">
                              <Heart size={14} />
                              <span>{post.likes}</span>
                            </button>
                            <button className="flex items-center gap-1 hover:text-owis-gold transition-colors">
                              <MessageCircle size={14} />
                              <span>{post.comments}</span>
                            </button>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default StyleCommunities;
