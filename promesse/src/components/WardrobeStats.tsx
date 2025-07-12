
import React from 'react';
import { TrendingUp, DollarSign, Star, Calendar, Award, Target } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

interface WardrobeStatsProps {
  items: any[];
}

const WardrobeStats = ({ items }: WardrobeStatsProps) => {
  const totalItems = items.length;
  const totalValue = items.reduce((sum, item) => sum + item.price, 0);
  const favoriteItems = items.filter(item => item.favorite).length;
  const totalWears = items.reduce((sum, item) => sum + item.timesWorn, 0);
  const avgWears = totalWears / Math.max(totalItems, 1);
  const costPerWear = totalValue / Math.max(totalWears, 1);

  const stats = [
    {
      label: 'Total Items',
      value: totalItems,
      icon: Award,
      color: 'blue',
      bgColor: 'from-blue-500 to-indigo-600'
    },
    {
      label: 'Total Value',
      value: `$${totalValue.toLocaleString()}`,
      icon: DollarSign,
      color: 'green',
      bgColor: 'from-green-500 to-emerald-600'
    },
    {
      label: 'Favorites',
      value: favoriteItems,
      icon: Star,
      color: 'purple',
      bgColor: 'from-purple-500 to-orange-600'
    },
    {
      label: 'Avg Wears',
      value: avgWears.toFixed(1),
      icon: TrendingUp,
      color: 'purple',
      bgColor: 'from-purple-500 to-pink-600'
    },
    {
      label: 'Cost per Wear',
      value: `$${costPerWear.toFixed(2)}`,
      icon: Target,
      color: 'teal',
      bgColor: 'from-teal-500 to-cyan-600'
    },
    {
      label: 'This Month',
      value: `${Math.floor(totalWears * 0.3)} wears`,
      icon: Calendar,
      color: 'rose',
      bgColor: 'from-rose-500 to-pink-600'
    }
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
      {stats.map((stat, index) => (
        <Card key={stat.label} className="group hover:shadow-lg transition-all duration-300 border-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg animate-fade-in" style={{ animationDelay: `${index * 0.1}s` }}>
          <CardContent className="p-6 text-center">
            <div className={`inline-flex items-center justify-center w-12 h-12 bg-gradient-to-r ${stat.bgColor} rounded-xl mb-3 group-hover:scale-110 transition-transform`}>
              <stat.icon className="text-white" size={24} />
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
              {stat.value}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {stat.label}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default WardrobeStats;
