
import React, { useState } from 'react';
import { Bell, Shield, Palette, Globe, User, Moon, Sun } from 'lucide-react';

const AppSettings = () => {
  const [notifications, setNotifications] = useState({
    outfitSuggestions: true,
    communityUpdates: false,
    weeklyReports: true,
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-owis-cream to-owis-mint dark:from-owis-charcoal-dark to-owis-midnight-blue pt-20 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="owis-card rounded-3xl p-8 mb-8 animate-fade-in">
          <h1 className="text-4xl font-heading font-bold gradient-text mb-2">
            Settings
          </h1>
          <p className="text-owis-charcoal/70 dark:text-owis-cream/70 text-lg">
            Customize your OWIS experience
          </p>
        </div>

        <div className="space-y-6">
          {/* Notifications */}
          <div className="owis-card rounded-2xl p-6">
            <h2 className="text-xl font-semibold text-owis-charcoal dark:text-owis-cream mb-4 flex items-center gap-3">
              <Bell className="text-owis-gold" size={24} />
              Notifications
            </h2>
            <div className="space-y-4">
              {Object.entries(notifications).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between">
                  <span className="text-owis-charcoal dark:text-owis-cream capitalize">
                    {key.replace(/([A-Z])/g, ' $1').trim()}
                  </span>
                  <button
                    onClick={() => setNotifications(prev => ({ ...prev, [key]: !value }))}
                    className={`w-12 h-6 rounded-full transition-colors ${
                      value ? 'bg-owis-gold' : 'bg-gray-300 dark:bg-gray-600'
                    }`}
                  >
                    <div className={`w-4 h-4 bg-white rounded-full transition-transform ${
                      value ? 'translate-x-7' : 'translate-x-1'
                    }`} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Privacy */}
          <div className="owis-card rounded-2xl p-6">
            <h2 className="text-xl font-semibold text-owis-charcoal dark:text-owis-cream mb-4 flex items-center gap-3">
              <Shield className="text-owis-sage" size={24} />
              Privacy & Security
            </h2>
            <div className="space-y-4">
              <button className="w-full text-left p-4 bg-white/50 dark:bg-black/20 rounded-xl hover:bg-owis-gold/20 transition-colors">
                <div className="flex items-center justify-between">
                  <span className="text-owis-charcoal dark:text-owis-cream">Profile Visibility</span>
                  <span className="text-sm text-owis-charcoal/60 dark:text-owis-cream/60">Public</span>
                </div>
              </button>
              <button className="w-full text-left p-4 bg-white/50 dark:bg-black/20 rounded-xl hover:bg-owis-gold/20 transition-colors">
                <div className="flex items-center justify-between">
                  <span className="text-owis-charcoal dark:text-owis-cream">Data Sharing</span>
                  <span className="text-sm text-owis-charcoal/60 dark:text-owis-cream/60">Limited</span>
                </div>
              </button>
            </div>
          </div>

          {/* Appearance */}
          <div className="owis-card rounded-2xl p-6">
            <h2 className="text-xl font-semibold text-owis-charcoal dark:text-owis-cream mb-4 flex items-center gap-3">
              <Palette className="text-owis-bronze" size={24} />
              Appearance
            </h2>
            <div className="grid grid-cols-3 gap-4">
              <button className="p-4 bg-white border-2 border-owis-gold rounded-xl">
                <Sun className="mx-auto mb-2 text-owis-gold" size={24} />
                <span className="text-sm text-owis-charcoal">Light</span>
              </button>
              <button className="p-4 bg-gray-800 border-2 border-transparent rounded-xl">
                <Moon className="mx-auto mb-2 text-white" size={24} />
                <span className="text-sm text-white">Dark</span>
              </button>
              <button className="p-4 bg-gradient-to-br from-white to-gray-800 border-2 border-transparent rounded-xl">
                <div className="mx-auto mb-2 w-6 h-6 bg-gradient-to-br from-owis-gold to-owis-sage rounded-full" />
                <span className="text-sm text-owis-charcoal dark:text-owis-cream">Auto</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AppSettings;
