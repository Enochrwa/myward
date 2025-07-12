
import React from 'react';
import { Heart, Share2, MessageCircle, Users, Sparkles } from 'lucide-react';

const CommunityHub = () => {
  const posts = [
    { id: 1, user: 'Sarah Chen', outfit: 'Autumn Elegance', likes: 42, comments: 8, image: '/placeholder.svg' },
    { id: 2, user: 'Emma Wilson', outfit: 'Office Chic', likes: 35, comments: 12, image: '/placeholder.svg' },
    { id: 3, user: 'Maya Patel', outfit: 'Weekend Vibes', likes: 28, comments: 6, image: '/placeholder.svg' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-owis-cream to-owis-mint dark:from-owis-charcoal-dark to-owis-midnight-blue pt-20 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="owis-card rounded-3xl p-8 mb-8 animate-fade-in">
          <h1 className="text-4xl font-heading font-bold gradient-text mb-2">
            Fashion Community
          </h1>
          <p className="text-owis-charcoal/70 dark:text-owis-cream/70 text-lg">
            Share, discover, and get inspired by fellow fashion enthusiasts
          </p>
        </div>

        <div className="space-y-6">
          {posts.map((post) => (
            <div key={post.id} className="owis-card owis-interactive rounded-2xl p-6">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-owis-purple to-owis-bronze rounded-full flex items-center justify-center">
                  <Users className="text-white" size={20} />
                </div>
                <div>
                  <h3 className="font-semibold text-owis-charcoal dark:text-owis-cream">{post.user}</h3>
                  <p className="text-sm text-owis-charcoal/60 dark:text-owis-cream/60">{post.outfit}</p>
                </div>
              </div>
              
              <div className="aspect-square bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800 rounded-xl mb-4 flex items-center justify-center">
                <Sparkles className="text-owis-charcoal/30 dark:text-owis-cream/30" size={48} />
              </div>

              <div className="flex items-center gap-6">
                <button className="flex items-center gap-2 text-owis-charcoal dark:text-owis-cream hover:text-owis-purple transition-colors">
                  <Heart size={20} />
                  <span>{post.likes}</span>
                </button>
                <button className="flex items-center gap-2 text-owis-charcoal dark:text-owis-cream hover:text-owis-purple transition-colors">
                  <MessageCircle size={20} />
                  <span>{post.comments}</span>
                </button>
                <button className="flex items-center gap-2 text-owis-charcoal dark:text-owis-cream hover:text-owis-purple transition-colors">
                  <Share2 size={20} />
                  <span>Share</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CommunityHub;
