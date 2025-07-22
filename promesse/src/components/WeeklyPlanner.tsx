import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Calendar, Loader2, Lock, Unlock, RefreshCw, Save, Trash2 } from 'lucide-react';
import axios from 'axios';
import { Slider } from './ui/slider';
import { Label } from './ui/label';

type DailyPlan = {
  occasion: string;
  weather_override?: any;
};

type WeatherData = {
  temp_max: number;
  temp_min: number;
  weather: string;
  description: string;
};

type WardrobeItem = { id: string; [key: string]: any };

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

type OutfitRecommendation = {
  score: number;
  items: OutfitItem[];
};

const occasionOptions = [
  'work',
  'leisure',
  'formal',
  'outdoor',
  'party',
  'sport',
  'smart_casual'
];

const WeeklyPlanner: React.FC = () => {
  const [weekDays, setWeekDays] = useState<
    { date: string; day: string; occasion: string }[]
  >([]);
  const [location, setLocation] = useState('Kigali');
  const [creativity, setCreativity] = useState(0.5);
  const [recommendations, setRecommendations] = useState<
    Record<string, OutfitRecommendation[]>
  >({});
  const [weather, setWeather] = useState<Record<string, WeatherData>>({});
  const [loading, setLoading] = useState(false);
  const [wardrobeItems, setWardrobeItems] = useState<WardrobeItem[]>([]);
  const [lockedOutfits, setLockedOutfits] = useState<Record<string, OutfitRecommendation>>(
    {}
  );
  const [savedPlans, setSavedPlans] = useState<WeeklyPlan[]>([]);
  const [currentPlanId, setCurrentPlanId] = useState<number | null>(null);
  const [planName, setPlanName] = useState('My Weekly Plan');

  useEffect(() => {
    fetchSavedPlans();
    fetchWardrobeItems();
    initializeWeekDays();
  }, []);

  const initializeWeekDays = () => {
    const today = new Date();
    const days = Array.from({ length: 7 }, (_, i) => {
      const d = new Date(today);
      d.setDate(today.getDate() + i);
      return {
        date: d.toISOString().slice(0, 10),
        day: d.toLocaleDateString('en-US', { weekday: 'long' }),
        occasion: 'leisure'
      };
    });
    setWeekDays(days);
  };

  const fetchWardrobeItems = async () => {
    try {
      const token = localStorage.getItem('token');
      const resp = await axios.get<WardrobeItem[]>(
        'http://127.0.0.1:8000/api/outfit/user-clothes',
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setWardrobeItems(resp.data || []);
    } catch (err) {
      console.error('Error fetching wardrobe items:', err);
    }
  };

  const fetchSavedPlans = async () => {
    try {
      const token = localStorage.getItem('token');
      const resp = await axios.get<WeeklyPlan[]>(
        'http://127.0.0.1:8000/api/weekly-plan/',
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setSavedPlans(resp.data);
    } catch (err) {
      console.error('Error fetching saved plans:', err);
    }
  };

  const handleOccasionChange = (date: string, occasion: string) => {
    setWeekDays((days) =>
      days.map((d) =>
        d.date === date
          ? {
              ...d,
              occasion
            }
          : d
      )
    );
  };

  const handlePlanWeek = async (singleDate?: string) => {
    setLoading(true);
    const plan: Record<string, DailyPlan> = {};
    (singleDate ? [singleDate] : weekDays.map((d) => d.date)).forEach((date) => {
      if (!lockedOutfits[date]) {
        const day = weekDays.find((d) => d.date === date);
        plan[date] = { occasion: day!.occasion };
      }
    });

    try {
      const token = localStorage.getItem('token');
      const resp = await axios.post(
        'http://127.0.0.1:8000/api/weekly-plan/recommendations',
        {
          location,
          weekly_plan: plan,
          wardrobe_items: wardrobeItems,
          creativity
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      const { recommendations: newRecs, weather: newWeather } = resp.data;
      setRecommendations((prev) => ({ ...prev, ...newRecs }));
      setWeather((prev) => ({ ...prev, ...newWeather }));
    } catch (err) {
      console.error('Error planning week:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleLockOutfit = (date: string) => {
    setLockedOutfits((prev) => {
      const copy = { ...prev };
      if (copy[date]) {
        delete copy[date];
      } else if (recommendations[date]?.[0]) {
        copy[date] = recommendations[date][0];
      }
      return copy;
    });
  };

  const handleSavePlan = async () => {
    const token = localStorage.getItem('token');
    const planData = {
      name: planName,
      start_date: weekDays[0].date,
      end_date: weekDays[weekDays.length - 1].date,
      days: weekDays.map((day) => ({
        date: day.date,
        day_of_week: day.day,
        occasion: day.occasion,
        outfit_id: lockedOutfits[day.date] ? (lockedOutfits[day.date] as any).id : null,
      })),
    };

    try {
      if (currentPlanId) {
        await axios.put(
          `http://127.0.0.1:8000/api/weekly-plan/${currentPlanId}`,
          planData,
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } else {
        const response = await axios.post(
          'http://127.0.0.1:8000/api/weekly-plan/',
          planData,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setCurrentPlanId(response.data.id);
      }
      fetchSavedPlans();
    } catch (error) {
      console.error('Error saving plan:', error);
    }
  };

  const handleDeletePlan = async () => {
    if (!currentPlanId) return;
    const token = localStorage.getItem('token');
    try {
      await axios.delete(`http://127.0.0.1:8000/api/weekly-plan/${currentPlanId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCurrentPlanId(null);
      setPlanName('My Weekly Plan');
      initializeWeekDays();
      setRecommendations({});
      setLockedOutfits({});
      fetchSavedPlans();
    } catch (error) {
      console.error('Error deleting plan:', error);
    }
  };

  const handleLoadPlan = (plan: WeeklyPlan) => {
    setCurrentPlanId(plan.id);
    setPlanName(plan.name);
    const loadedWeekDays = plan.days.map((day) => ({
      date: day.date,
      day: day.day_of_week,
      occasion: day.occasion,
    }));
    setWeekDays(loadedWeekDays);

    const newRecommendations: Record<string, OutfitRecommendation[]> = {};
    const newLockedOutfits: Record<string, OutfitRecommendation> = {};

    plan.days.forEach((day) => {
      if (day.outfit) {
        const outfitAsRecommendation = {
          score: 0, // Score is not available in the saved plan
          ...day.outfit,
        };
        newRecommendations[day.date] = [outfitAsRecommendation];
        newLockedOutfits[day.date] = outfitAsRecommendation;
      }
    });

    setRecommendations(newRecommendations);
    setLockedOutfits(newLockedOutfits);
  };

  return (
    <Card className="max-w-7xl mx-auto my-8 shadow-lg">
      <CardHeader className="bg-gray-50">
        <div className="flex justify-between items-center">
          <CardTitle className="flex items-center text-2xl font-bold text-gray-700">
            <Calendar className="mr-3 text-indigo-500" />
            <Input
              value={planName}
              onChange={(e) => setPlanName(e.target.value)}
              className="text-2xl font-bold"
            />
          </CardTitle>
          <div className="flex items-center space-x-2">
            <Select onValueChange={(planId) => handleLoadPlan(savedPlans.find(p => p.id === parseInt(planId))!)}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Load a plan" />
              </SelectTrigger>
              <SelectContent>
                {savedPlans.map(plan => (
                  <SelectItem key={plan.id} value={String(plan.id)}>{plan.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button onClick={handleSavePlan} size="sm">
              <Save className="h-4 w-4 mr-2" />
              Save Plan
            </Button>
            {currentPlanId && (
              <Button onClick={handleDeletePlan} size="sm" variant="destructive">
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-6">
        <div className="flex flex-wrap gap-6 mb-8 items-end">
          <div className="flex-grow max-w-xs">
            <Label htmlFor="city">City</Label>
            <Input
              id="city"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="mt-1"
            />
          </div>

          <div className="flex items-center space-x-4">
            <div>
              <Label>Creativity</Label>
              <Slider
                min={0}
                max={1}
                step={0.1}
                value={[creativity]}
                onValueChange={(v) => setCreativity(v[0])}
                className="mt-2"
              />
              <p className="text-xs text-gray-500 mt-1 text-center">
                {creativity < 0.3
                  ? 'Classic'
                  : creativity > 0.7
                  ? 'Adventurous'
                  : 'Balanced'}
              </p>
            </div>

            <Button
              onClick={() => handlePlanWeek()}
              disabled={loading}
              className="bg-indigo-600 hover:bg-indigo-700"
            >
              {loading && <Loader2 className="animate-spin mr-2" />}
              Plan My Week
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-7 gap-4">
          {weekDays.map((day) => {
            const recs = recommendations[day.date] || [];
            const locked = lockedOutfits[day.date];
            const topRec = locked || recs[0];

            return (
              <Card
                key={day.date}
                className={`p-4 flex flex-col transition-colors ${
                  locked ? 'bg-indigo-50' : 'bg-white'
                }`}
              >
                <div className="flex-grow">
                  <h3 className="font-semibold">{day.day}</h3>
                  <p className="text-sm text-gray-500 mb-3">{day.date}</p>

                  <Select
                    value={day.occasion}
                    onValueChange={(v) => handleOccasionChange(day.date, v)}
                  >
                    <SelectTrigger>
                      <SelectValue>{day.occasion}</SelectValue>
                    </SelectTrigger>
                    <SelectContent>
                      {occasionOptions.map((opt) => (
                        <SelectItem key={opt} value={opt}>
                          {opt.replace(/_/g, ' ')}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  <div className="mt-4 text-sm">
                    <h4 className="font-semibold text-gray-600">Weather</h4>
                    {weather[day.date] ? (
                      <div className="text-xs">
                        <p>
                          {weather[day.date].temp_min.toFixed(0)}°C -{' '}
                          {weather[day.date].temp_max.toFixed(0)}°C
                        </p>
                        <p className="capitalize">
                          {weather[day.date].description}
                        </p>
                      </div>
                    ) : (
                      <p className="text-xs text-gray-400">No forecast</p>
                    )}
                  </div>

                  <div className="mt-4">
                    <h4 className="font-semibold mb-2 text-gray-700">
                      Recommended:
                    </h4>
                    {topRec ? (
                      <div className="flex flex-wrap gap-2">
                        {topRec.items.map((item) => (
                          <div
                            key={item.id}
                            className="h-20 w-20 rounded-lg shadow-md overflow-hidden"
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
                      <p className="text-xs text-gray-500">
                        No recommendation yet
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between mt-4">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => toggleLockOutfit(day.date)}
                    disabled={!recs[0]}
                  >
                    {locked ? (
                      <Lock className="h-4 w-4 text-indigo-600" />
                    ) : (
                      <Unlock className="h-4 w-4" />
                    )}
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handlePlanWeek(day.date)}
                    disabled={loading || locked}
                  >
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default WeeklyPlanner;
