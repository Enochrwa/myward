
import React from 'react';
import { Plus, Sparkles, Calendar, BarChart3, Shuffle, Heart, Zap, Crown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

interface QuickActionsProps {
  onAddItem: () => void;
  onCreateOutfit: () => void;
  onPlanWeek: () => void;
  onShowAnalytics: () => void;
  onGenerateRandomOutfit: () => void;
  onShowFavorites: () => void;
  selectedItemsCount: number;
}

const QuickActions = ({
  onAddItem,
  onCreateOutfit,
  onPlanWeek,
  onShowAnalytics,
  onGenerateRandomOutfit,
  onShowFavorites,
  selectedItemsCount
}: QuickActionsProps) => {
  const actions = [
    {
      label: 'Add Item',
      icon: Plus,
      onClick: onAddItem,
      color: 'from-purple-600 to-pink-600',
      description: 'Add new piece to wardrobe'
    },
    {
      label: 'Create Outfit',
      icon: Sparkles,
      onClick: onCreateOutfit,
      color: 'from-indigo-600 to-purple-600',
      description: `${selectedItemsCount ? `Use ${selectedItemsCount} selected` : 'Design new look'}`
    },
    {
      label: 'Plan Week',
      icon: Calendar,
      onClick: onPlanWeek,
      color: 'from-green-600 to-teal-600',
      description: 'AI weekly outfit planning'
    },
    {
      label: 'Analytics',
      icon: BarChart3,
      onClick: onShowAnalytics,
      color: 'from-blue-600 to-indigo-600',
      description: 'Wardrobe insights & stats'
    },
    {
      label: 'Random Mix',
      icon: Shuffle,
      onClick: onGenerateRandomOutfit,
      color: 'from-orange-500 to-red-600',
      description: 'Surprise outfit combo'
    },
    {
      label: 'Favorites',
      icon: Heart,
      onClick: onShowFavorites,
      color: 'from-pink-500 to-rose-600',
      description: 'Show loved pieces'
    }
  ];

  return (
    <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg shadow-2xl border border-white/50 rounded-3xl">
      <CardContent className="p-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-xl">
            <Zap className="text-white" size={20} />
          </div>
          <h3 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
            Quick Actions
          </h3>
          <div className="p-1 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg">
            <Crown className="text-white" size={16} />
          </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {actions.map((action, index) => (
            <Button
              key={action.label}
              onClick={action.onClick}
              className={`h-auto p-6 flex flex-col items-center gap-3 bg-gradient-to-r ${action.color} hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-xl text-white border-0 rounded-2xl animate-fade-in`}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <action.icon size={24} />
              <div className="text-center">
                <div className="font-bold text-sm">{action.label}</div>
                <div className="text-xs opacity-90 mt-1">{action.description}</div>
              </div>
              {action.label === 'Create Outfit' && selectedItemsCount > 0 && (
                <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center font-bold">
                  {selectedItemsCount}
                </div>
              )}
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default QuickActions;
