
import React from 'react';
import { User, Settings, Camera, Award, TrendingUp, Mail } from 'lucide-react'; // Added Mail icon

// Interface for User prop based on AuthContext's User interface
interface UserProfileProps {
  user: {
    id: string; // Assuming id is string from AuthContext
    username: string;
    email: string;
    // Add other fields if present, e.g., bio, profileImageUrl
  };
}

const UserProfile = ({ user: userData }: UserProfileProps) => { // Renamed prop to userData to avoid conflict with Lucide User icon
  return (
    <div className="min-h-screen bg-gradient-to-br from-owis-cream to-owis-mint dark:from-owis-charcoal-dark to-owis-midnight-blue pt-20 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="owis-card rounded-3xl p-8 mb-8 animate-fade-in">
          <div className="flex flex-col md:flex-row items-center gap-6">
            <div className="relative">
              <div className="w-32 h-32 bg-gradient-to-br from-owis-gold to-owis-bronze rounded-full flex items-center justify-center">
                <User className="text-white" size={48} />
              </div>
              <button className="absolute bottom-0 right-0 w-10 h-10 bg-owis-sage rounded-full flex items-center justify-center border-4 border-white dark:border-gray-800">
                <Camera className="text-white" size={16} />
              </button>
            </div>
            
            <div className="text-center md:text-left">
              <h1 className="text-3xl font-heading font-bold text-owis-charcoal dark:text-owis-cream mb-1">
                {userData.username}
              </h1>
              <div className="flex items-center justify-center md:justify-start text-owis-charcoal/70 dark:text-owis-cream/70 mb-2">
                <Mail size={14} className="mr-2 text-owis-sage" />
                <span>{userData.email}</span>
              </div>
              <p className="text-owis-charcoal/70 dark:text-owis-cream/70 mb-2">
                Fashion enthusiast & sustainable style advocate {/* This can be made dynamic if a bio field is added to user model */}
              </p>
              <div className="flex items-center gap-4 justify-center md:justify-start">
                <div className="flex items-center gap-2">
                  <Award className="text-owis-gold" size={16} />
                  <span className="text-sm text-owis-charcoal dark:text-owis-cream">Style Expert</span>
                </div>
                <div className="flex items-center gap-2">
                  <TrendingUp className="text-owis-sage" size={16} />
                  <span className="text-sm text-owis-charcoal dark:text-owis-cream">Eco-Friendly</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="owis-card rounded-2xl p-6">
            <h3 className="font-semibold text-owis-charcoal dark:text-owis-cream mb-4">Statistics</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-owis-charcoal/70 dark:text-owis-cream/70">Total Items</span>
                <span className="font-medium text-owis-charcoal dark:text-owis-cream">247</span>
              </div>
              <div className="flex justify-between">
                <span className="text-owis-charcoal/70 dark:text-owis-cream/70">Outfits Created</span>
                <span className="font-medium text-owis-charcoal dark:text-owis-cream">156</span>
              </div>
              <div className="flex justify-between">
                <span className="text-owis-charcoal/70 dark:text-owis-cream/70">Community Likes</span>
                <span className="font-medium text-owis-charcoal dark:text-owis-cream">842</span>
              </div>
            </div>
          </div>

          <div className="owis-card rounded-2xl p-6">
            <h3 className="font-semibold text-owis-charcoal dark:text-owis-cream mb-4">Achievements</h3>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-owis-gold rounded-full flex items-center justify-center">
                  <Award className="text-white" size={14} />
                </div>
                <span className="text-sm text-owis-charcoal dark:text-owis-cream">Style Pioneer</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-owis-sage rounded-full flex items-center justify-center">
                  <TrendingUp className="text-white" size={14} />
                </div>
                <span className="text-sm text-owis-charcoal dark:text-owis-cream">Eco Warrior</span>
              </div>
            </div>
          </div>

          <div className="owis-card rounded-2xl p-6">
            <h3 className="font-semibold text-owis-charcoal dark:text-owis-cream mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button className="w-full text-left p-3 bg-white/50 dark:bg-black/20 rounded-xl hover:bg-owis-gold/20 transition-colors">
                <div className="flex items-center gap-3">
                  <Settings className="text-owis-charcoal dark:text-owis-cream" size={16} />
                  <span className="text-sm text-owis-charcoal dark:text-owis-cream">Edit Profile</span>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
