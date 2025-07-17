import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface WardrobeAnalyticsProps {
  items: any[];
}

const WardrobeAnalytics: React.FC<WardrobeAnalyticsProps> = ({ items }) => {
  const totalItems = items.length;
  const favoriteItems = items.filter(item => item.favorite).length;
  const totalWorn = items.reduce((acc, item) => acc + item.times_worn, 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Wardrobe Analytics</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold">{totalItems}</p>
            <p className="text-sm text-gray-500">Total Items</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold">{favoriteItems}</p>
            <p className="text-sm text-gray-500">Favorites</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold">{totalWorn}</p>
            <p className="text-sm text-gray-500">Total Wears</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default WardrobeAnalytics;
