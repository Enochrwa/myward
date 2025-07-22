import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Calendar } from 'lucide-react';

type OutfitItem = {
  id: number;
  image_url: string;
  category: string;
};

type Outfit = {
  id: number;
  name: string;
  items: OutfitItem[];
};

type Day = {
  id: number;
  day_of_week: string;
  date: string;
  occasion: string;
  outfit: Outfit | null;
  weather_forecast: any;
};

type WeeklyPlan = {
  id: number;
  name: string;
  start_date: string;
  end_date: string;
  days: Day[];
};

interface SavedPlanCardProps {
  plan: WeeklyPlan;
}

const SavedPlanCard: React.FC<SavedPlanCardProps> = ({ plan }) => {
  return (
    <Card className="w-full mx-auto my-4 shadow-md">
      <CardHeader className="bg-gray-50">
        <CardTitle className="flex items-center text-xl font-bold text-gray-700">
          <Calendar className="mr-3 text-indigo-500" />
          {plan.name}
        </CardTitle>
        <p className="text-sm text-gray-500">
          {plan.start_date} - {plan.end_date}
        </p>
      </CardHeader>
      <CardContent className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-7 gap-2">
          {plan.days.map((day) => (
            <div key={day.id} className="p-2 border rounded-lg">
              <h4 className="font-semibold text-sm">{day.day_of_week}</h4>
              <p className="text-xs text-gray-500 mb-2">{day.date}</p>
              {day.outfit ? (
                <div className="flex flex-wrap gap-1">
                  {day.outfit.items.map((item) => (
                    <div
                      key={item.id}
                      className="h-16 w-16 rounded-md overflow-hidden shadow-sm transition-transform duration-200 hover:scale-105"
                    >
                      <img
                        src={item.image_url}
                        alt={item.category}
                        className="h-full w-full object-cover"
                      />
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-400">No outfit</p>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default SavedPlanCard;
