import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Calendar, Loader2, Lock, Unlock } from 'lucide-react';
import apiClient from '@/lib/apiClient';

const occasionOptions = [
  "work", "leisure", "formal", "outdoor", "party", "sport", "smart_casual"
];

const WeeklyPlanner = () => {
  const [weekDays, setWeekDays] = useState<any[]>([]);
  const [location, setLocation] = useState('Kigali');
  const [recommendations, setRecommendations] = useState<any>({});
  const [loading, setLoading] = useState(false);
  const [wardrobeItems, setWardrobeItems] = useState<any[]>([]);
  const [lockedOutfits, setLockedOutfits] = useState<any>({});

  useEffect(() => {
    const today = new Date();
    const days = Array.from({ length: 7 }, (_, i) => {
      const date = new Date(today);
      date.setDate(today.getDate() + i);
      return {
        date: date.toISOString().split('T')[0],
        day: date.toLocaleDateString('en-US', { weekday: 'long' }),
        occasion: 'leisure'
      };
    });
    setWeekDays(days);
    fetchWardrobeItems();
  }, []);

  const fetchWardrobeItems = async () => {
    try {
      const response = await apiClient('/outfit/user-clothes');
      setWardrobeItems(response?.data || []);
    } catch (error) {
      console.error('Error fetching wardrobe items:', error);
    }
  };

  const handleOccasionChange = (date: string, occasion: string) => {
    setWeekDays(weekDays.map(day => day.date === date ? { ...day, occasion } : day));
  };

  const handlePlanWeek = async () => {
    setLoading(true);
    const weekly_plan = weekDays.reduce((acc, day) => {
      if (!lockedOutfits[day.date]) {
        acc[day.date] = { occasion: day.occasion };
      }
      return acc;
    }, {});

    try {
      const response = await apiClient.post('/outfit/weekly-plan', {
        location,
        weekly_plan,
        wardrobe_items: wardrobeItems,
        creativity: 0.7 // Higher creativity for more options
      });
      
      setRecommendations(prev => ({ ...prev, ...response.data }));
    } catch (error) {
      console.error('Error fetching weekly plan:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleLockOutfit = (date: string) => {
    setLockedOutfits(prev => {
      const newLocked = { ...prev };
      if (newLocked[date]) {
        delete newLocked[date];
      } else if (recommendations[date]?.[0]) {
        newLocked[date] = recommendations[date][0];
      }
      return newLocked;
    });
  };

  return (
    <Card className="w-full max-w-7xl mx-auto my-8 shadow-lg">
      <CardHeader className="bg-gray-50">
        <CardTitle className="flex items-center text-2xl font-bold text-gray-700">
          <Calendar className="mr-3 text-indigo-500" /> Weekly Outfit Planner
        </CardTitle>
      </CardHeader>
      <CardContent className="p-6">
        <div className="flex flex-wrap gap-4 mb-8 items-center">
          <Input 
            placeholder="Enter City" 
            value={location} 
            onChange={(e) => setLocation(e.target.value)}
            className="max-w-xs"
          />
          <Button onClick={handlePlanWeek} disabled={loading} className="bg-indigo-600 hover:bg-indigo-700">
            {loading ? <Loader2 className="animate-spin mr-2" /> : null}
            Plan My Week
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-7 gap-4">
          {weekDays.map(day => (
            <Card key={day.date} className={`p-4 flex flex-col ${lockedOutfits[day.date] ? 'bg-indigo-50' : ''}`}>
              <div className="flex-grow">
                <h3 className="font-semibold text-lg">{day.day}</h3>
                <p className="text-sm text-gray-500 mb-3">{day.date}</p>
                <Select onValueChange={(value) => handleOccasionChange(day.date, value)} defaultValue={day.occasion}>
                  <SelectTrigger>
                    <SelectValue placeholder="Occasion" />
                  </SelectTrigger>
                  <SelectContent>
                    {occasionOptions.map(opt => <SelectItem key={opt} value={opt}>{opt.charAt(0).toUpperCase() + opt.slice(1)}</SelectItem>)}
                  </SelectContent>
                </Select>

                <div className="mt-4">
                  <h4 className="font-semibold text-md mb-2">Recommended Outfit:</h4>
                  {recommendations[day.date]?.[0] ? (
                    <div className="flex flex-wrap gap-2">
                      {recommendations[day.date][0].items.map((item: any) => (
                        <img key={item.id} src={item.image_url} alt={item.category} className="h-20 w-20 rounded-lg shadow-md object-cover" />
                      ))}
                    </div>
                  ) : <p className="text-xs text-gray-500 mt-2">No outfit to show.</p>}
                </div>
              </div>
              
              <Button
                onClick={() => toggleLockOutfit(day.date)}
                size="sm"
                variant="ghost"
                className="mt-4 w-full flex items-center justify-center"
                disabled={!recommendations[day.date]?.[0]}
              >
                {lockedOutfits[day.date] ? <Lock className="mr-2 h-4 w-4" /> : <Unlock className="mr-2 h-4 w-4" />}
                {lockedOutfits[day.date] ? 'Locked' : 'Lock Outfit'}
              </Button>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default WeeklyPlanner;
