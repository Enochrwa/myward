import React, { useState, useEffect } from 'react';
import { Trophy, Clock, Users, Camera, Star, Flame, Calendar, Award, Target, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface Challenge {
  id: string;
  title: string;
  description: string;
  theme: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  duration: string;
  prize: string;
  participants: number;
  submissions: number;
  startDate: string;
  endDate: string;
  rules: string[];
  tags: string[];
  featured: boolean;
  hostBy: string;
  status: 'upcoming' | 'active' | 'ended';
}

interface Submission {
  id: string;
  challengeId: string;
  user: {
    name: string;
    username: string;
    avatar: string;
  };
  image: string;
  caption: string;
  votes: number;
  rank: number;
  featured: boolean;
}

const FashionChallenges = () => {
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('active');
  const [selectedChallenge, setSelectedChallenge] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadChallenges();
    loadSubmissions();
  }, [selectedCategory]);

  const loadChallenges = () => {
    setIsLoading(true);
    
    setTimeout(() => {
      const mockChallenges: Challenge[] = [
        {
          id: '1',
          title: 'Sustainable Style Challenge',
          description: 'Create an amazing outfit using only sustainable and eco-friendly fashion pieces',
          theme: 'Sustainability',
          difficulty: 'intermediate',
          duration: '7 days',
          prize: '$500 Eco Fashion Voucher',
          participants: 1247,
          submissions: 893,
          startDate: '2024-01-15',
          endDate: '2024-01-22',
          rules: [
            'Use only sustainable fashion brands',
            'Include eco-friendly accessories',
            'Share the story behind your choices',
            'Tag #SustainableStyle'
          ],
          tags: ['#SustainableStyle', '#EcoFashion', '#GreenWardrobe'],
          featured: true,
          hostBy: 'EcoFashion Collective',
          status: 'active'
        },
        {
          id: '2',
          title: 'Monochrome Monday',
          description: 'Style a head-to-toe monochromatic look in your favorite color',
          theme: 'Color Theory',
          difficulty: 'beginner',
          duration: '3 days',
          prize: 'Featured on Homepage',
          participants: 2156,
          submissions: 1678,
          startDate: '2024-01-20',
          endDate: '2024-01-23',
          rules: [
            'Use only one color family',
            'Include at least 3 different textures',
            'Accessories must match the theme',
            'Tag #MonochromeMonday'
          ],
          tags: ['#MonochromeMonday', '#ColorTheory', '#OneColor'],
          featured: false,
          hostBy: 'Color Style Studio',
          status: 'active'
        },
        {
          id: '3',
          title: 'Vintage Remix Challenge',
          description: 'Modernize a vintage piece with contemporary styling',
          theme: 'Vintage Revival',
          difficulty: 'advanced',
          duration: '10 days',
          prize: '$1000 Shopping Spree',
          participants: 856,
          submissions: 634,
          startDate: '2024-01-25',
          endDate: '2024-02-04',
          rules: [
            'Include at least one vintage piece (20+ years old)',
            'Mix with modern accessories',
            'Explain your styling choices',
            'Tag #VintageRemix'
          ],
          tags: ['#VintageRemix', '#RetroStyle', '#ModernVintage'],
          featured: true,
          hostBy: 'Vintage Style Society',
          status: 'upcoming'
        }
      ];
      
      setChallenges(mockChallenges);
      setIsLoading(false);
    }, 1000);
  };

  const loadSubmissions = () => {
    const mockSubmissions: Submission[] = [
      {
        id: '1',
        challengeId: '1',
        user: {
          name: 'Maya Patel',
          username: '@mayastyle',
          avatar: '/placeholder.svg'
        },
        image: '/placeholder.svg',
        caption: 'Thrifted this amazing blazer and paired it with organic cotton basics! 🌱',
        votes: 342,
        rank: 1,
        featured: true
      },
      {
        id: '2',
        challengeId: '1',
        user: {
          name: 'Alex Thompson',
          username: '@alexeco',
          avatar: '/placeholder.svg'
        },
        image: '/placeholder.svg',
        caption: 'Sustainable fashion doesn\'t mean compromising on style! ♻️',
        votes: 298,
        rank: 2,
        featured: false
      },
      {
        id: '3',
        challengeId: '2',
        user: {
          name: 'Sophie Chen',
          username: '@sophiechic',
          avatar: '/placeholder.svg'
        },
        image: '/placeholder.svg',
        caption: 'All blue everything! From navy to powder blue 💙',
        votes: 456,
        rank: 1,
        featured: true
      }
    ];
    
    setSubmissions(mockSubmissions);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'text-emerald-600 bg-emerald-50 dark:text-emerald-400 dark:bg-emerald-900/30';
      case 'intermediate': return 'text-purple-600 bg-purple-50 dark:text-purple-400 dark:bg-purple-900/30';
      case 'advanced': return 'text-rose-600 bg-rose-50 dark:text-rose-400 dark:bg-rose-900/30';
      default: return 'text-gray-600 bg-gray-50 dark:text-gray-400 dark:bg-gray-900/30';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-50 dark:text-green-400 dark:bg-green-900/30';
      case 'upcoming': return 'text-blue-600 bg-blue-50 dark:text-blue-400 dark:bg-blue-900/30';
      case 'ended': return 'text-gray-600 bg-gray-50 dark:text-gray-400 dark:bg-gray-900/30';
      default: return 'text-gray-600 bg-gray-50 dark:text-gray-400 dark:bg-gray-900/30';
    }
  };

  const categories = [
    { id: 'active', label: 'Active Challenges', icon: Flame },
    { id: 'upcoming', label: 'Upcoming', icon: Calendar },
    { id: 'ended', label: 'Past Challenges', icon: Trophy }
  ];

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-3 mb-4">
          <div className="p-3 bg-gradient-to-r from-purple-500 to-orange-600 rounded-2xl shadow-lg">
            <Trophy className="text-white" size={32} />
          </div>
          <h1 className="text-4xl font-bold gradient-text">Fashion Challenges</h1>
        </div>
        <p className="text-owis-charcoal/70 dark:text-owis-cream/70 text-lg max-w-2xl mx-auto">
          Join exciting style challenges, showcase your creativity, and win amazing prizes
        </p>
      </div>

      {/* Category Tabs */}
      <div className="flex justify-center mb-8">
        <div className="flex gap-2 bg-white/90 dark:bg-owis-charcoal/90 backdrop-blur-md rounded-2xl p-2 shadow-lg border border-white/20 dark:border-white/10">
          {categories.map(category => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`flex items-center gap-2 px-6 py-3 rounded-xl transition-all ${
                selectedCategory === category.id
                  ? 'bg-gradient-to-r from-owis-purple to-owis-bronze text-white shadow-md transform scale-105'
                  : 'text-owis-charcoal/70 dark:text-owis-cream/70 hover:bg-white/50 dark:hover:bg-owis-charcoal-light/50'
              }`}
            >
              <category.icon size={16} />
              {category.label}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map(i => (
            <Card key={i} className="animate-pulse owis-card">
              <CardHeader>
                <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
              </CardHeader>
              <CardContent>
                <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded-xl"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {challenges
            .filter(challenge => challenge.status === selectedCategory)
            .map(challenge => (
              <Card key={challenge.id} className={`owis-card owis-interactive relative ${challenge.featured ? 'ring-2 ring-owis-purple shadow-glow' : ''}`}>
                {challenge.featured && (
                  <div className="absolute top-4 right-4 bg-gradient-to-r from-owis-purple to-owis-bronze text-white px-3 py-1 rounded-full text-sm font-medium flex items-center gap-1 shadow-md">
                    <Star size={12} />
                    Featured
                  </div>
                )}
                
                <CardHeader className="pb-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(challenge.status)}`}>
                        {challenge.status.toUpperCase()}
                      </span>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getDifficultyColor(challenge.difficulty)}`}>
                        {challenge.difficulty.toUpperCase()}
                      </span>
                    </div>
                  </div>
                  
                  <CardTitle className="text-xl mb-2 text-owis-charcoal dark:text-owis-cream">{challenge.title}</CardTitle>
                  <p className="text-owis-charcoal/70 dark:text-owis-cream/70 text-sm">
                    {challenge.description}
                  </p>
                </CardHeader>

                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex items-center gap-2 text-owis-charcoal dark:text-owis-cream">
                      <Clock size={14} className="text-owis-purple" />
                      <span>{challenge.duration}</span>
                    </div>
                    <div className="flex items-center gap-2 text-owis-charcoal dark:text-owis-cream">
                      <Users size={14} className="text-owis-purple" />
                      <span>{challenge.participants.toLocaleString()}</span>
                    </div>
                    <div className="flex items-center gap-2 text-owis-charcoal dark:text-owis-cream">
                      <Camera size={14} className="text-owis-purple" />
                      <span>{challenge.submissions.toLocaleString()}</span>
                    </div>
                    <div className="flex items-center gap-2 text-owis-charcoal dark:text-owis-cream">
                      <Award size={14} className="text-owis-purple" />
                      <span className="text-xs">{challenge.prize}</span>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-sm mb-2 text-owis-charcoal dark:text-owis-cream">Challenge Rules:</h4>
                    <div className="space-y-1">
                      {challenge.rules.slice(0, 2).map((rule, i) => (
                        <div key={i} className="text-xs text-owis-charcoal/60 dark:text-owis-cream/60">
                          • {rule}
                        </div>
                      ))}
                      {challenge.rules.length > 2 && (
                        <div className="text-xs text-owis-purple hover:text-owis-purple-light cursor-pointer">
                          +{challenge.rules.length - 2} more rules
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-1">
                    {challenge.tags.map((tag, i) => (
                      <span key={i} className="px-2 py-1 bg-owis-cream/80 dark:bg-owis-charcoal-light/80 text-owis-charcoal dark:text-owis-cream rounded text-xs border border-owis-purple/20">
                        {tag}
                      </span>
                    ))}
                  </div>

                  <div className="flex gap-2 pt-2">
                    <Button 
                      className="flex-1 owis-button-primary shadow-md hover:shadow-lg transform hover:scale-105 transition-all"
                      onClick={() => setSelectedChallenge(challenge.id)}
                    >
                      {challenge.status === 'active' ? 'Join Challenge' : 'View Details'}
                    </Button>
                    {challenge.status === 'active' && (
                      <Button variant="outline" size="sm" className="border-owis-purple text-owis-purple hover:bg-owis-purple hover:text-white">
                        <Target size={14} />
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
        </div>
      )}

      {/* Top Submissions Section */}
      {selectedCategory === 'active' && submissions.length > 0 && (
        <div className="mt-12">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold flex items-center gap-2 text-owis-charcoal dark:text-owis-cream">
              <TrendingUp className="text-owis-purple" />
              Top Submissions
            </h2>
            <Button variant="outline" className="border-owis-purple text-owis-purple hover:bg-owis-purple hover:text-white">View All</Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {submissions.slice(0, 6).map(submission => (
              <Card key={submission.id} className="owis-card owis-interactive">
                <CardContent className="p-0">
                  <div className="aspect-square rounded-t-2xl overflow-hidden bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800 relative">
                    <img 
                      src={submission.image} 
                      alt="Challenge submission"
                      className="w-full h-full object-cover"
                    />
                    {submission.featured && (
                      <div className="absolute top-3 left-3 bg-owis-purple text-white px-2 py-1 rounded-full text-xs font-medium shadow-md">
                        Featured
                      </div>
                    )}
                    <div className="absolute top-3 right-3 bg-black/50 backdrop-blur-sm text-white px-2 py-1 rounded-full text-xs font-medium">
                      #{submission.rank}
                    </div>
                  </div>
                  
                  <div className="p-4">
                    <div className="flex items-center gap-3 mb-2">
                      <img 
                        src={submission.user.avatar} 
                        alt={submission.user.name}
                        className="w-8 h-8 rounded-full object-cover border-2 border-owis-purple/30"
                      />
                      <div>
                        <p className="font-medium text-sm text-owis-charcoal dark:text-owis-cream">{submission.user.name}</p>
                        <p className="text-xs text-owis-charcoal/60 dark:text-owis-cream/60">
                          {submission.user.username}
                        </p>
                      </div>
                    </div>
                    
                    <p className="text-sm text-owis-charcoal/70 dark:text-owis-cream/70 mb-3">
                      {submission.caption}
                    </p>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1 text-red-500">
                        <Trophy size={14} />
                        <span className="text-sm font-medium">{submission.votes}</span>
                      </div>
                      <Button size="sm" variant="outline" className="text-xs border-owis-purple text-owis-purple hover:bg-owis-purple hover:text-white">
                        Vote
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default FashionChallenges;
