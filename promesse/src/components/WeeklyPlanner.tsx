import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Calendar, Loader2 } from 'lucide-react';
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
      setWardrobeItems(response?.data);
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
      acc[day.date] = { occasion: day.occasion };
      return acc;
    }, {});

    try {
      const response = await fetch('http://localhost:8000/api/outfit/weekly-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ location, weekly_plan, wardrobe_items: wardrobeItems })
      });
      console.log("Weekly plan: ", response)
      if (response.ok) {
        const data = await response.json();
        setRecommendations(data);
      }
    } catch (error) {
      console.error('Error fetching weekly plan:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-6xl mx-auto my-8">
      <CardHeader>
        <CardTitle className="flex items-center">
          <Calendar className="mr-2" /> Weekly Outfit Planner
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex gap-4 mb-6">
          <Input 
            placeholder="Enter City" 
            value={location} 
            onChange={(e) => setLocation(e.target.value)}
            className="max-w-xs"
          />
          <Button onClick={handlePlanWeek} disabled={loading}>
            {loading ? <Loader2 className="animate-spin mr-2" /> : null}
            Plan My Week
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-7 gap-4">
          {weekDays.map(day => (
            <Card key={day.date} className="p-4">
              <h3 className="font-semibold">{day.day}</h3>
              <p className="text-sm text-gray-500 mb-2">{day.date}</p>
              <Select onValueChange={(value) => handleOccasionChange(day.date, value)} defaultValue={day.occasion}>
                <SelectTrigger>
                  <SelectValue placeholder="Occasion" />
                </SelectTrigger>
                <SelectContent>
                  {occasionOptions.map(opt => <SelectItem key={opt} value={opt}>{opt}</SelectItem>)}
                </SelectContent>
              </Select>

              {recommendations[day.date] && (
                <div className="mt-4">
                  <h4 className="font-semibold text-sm">Outfit:</h4>
                  {recommendations[day.date][0] ? (
                    <div className="flex gap-2 mt-2">
                      {recommendations[day.date][0].items.map((item: any) => (
                        <img key={item.id} src={item.image_url} alt={item.category} className="h-16 w-16 rounded shadow" />
                      ))}
                    </div>
                  ) : <p className="text-xs text-gray-500">No outfit found.</p>}
                </div>
              )}
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default WeeklyPlanner;
