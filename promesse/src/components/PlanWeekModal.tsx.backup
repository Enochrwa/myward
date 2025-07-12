import React, { useState } from 'react';
import { Calendar, Plus, Sparkles, Eye, Save, X, Zap, Star, MapPin, Cloud, Sun, CloudRain } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';

export interface PlanWeekModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface WeatherData {
  temp: string;
  condition: string;
  icon: React.ReactNode;
}

interface OutfitItem {
  id: string;
  name: string;
  image: string;
  value: number;
  category: string;
}

interface DayOutfit {
  outerwear?: OutfitItem;
  top: OutfitItem;
  bottom: OutfitItem;
  shoes: OutfitItem;
  accessories: OutfitItem[];
}

interface DayPlan {
  event: string;
  weather: WeatherData;
  outfit: DayOutfit;
  totalValue: number;
  confidence: number;
}

interface WeekPlan {
  [key: string]: DayPlan;
}

const PlanWeekModal = ({ isOpen, onClose }: PlanWeekModalProps) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [weekOf, setWeekOf] = useState(new Date().toISOString().split('T')[0]);
  const [weekPlan, setWeekPlan] = useState<WeekPlan>({});
  const [selectedDay, setSelectedDay] = useState<string | null>(null);
  const { toast } = useToast();

  // Mock wardrobe items
  const wardrobeItems: OutfitItem[] = [
    { id: '1', name: 'Navy Blazer', image: '/api/placeholder/150/150', value: 200, category: 'outerwear' },
    { id: '2', name: 'White Shirt', image: '/api/placeholder/150/150', value: 50, category: 'top' },
    { id: '3', name: 'Black Trousers', image: '/api/placeholder/150/150', value: 80, category: 'bottom' },
    { id: '4', name: 'Leather Shoes', image: '/api/placeholder/150/150', value: 150, category: 'shoes' },
    { id: '5', name: 'Gold Watch', image: '/api/placeholder/150/150', value: 300, category: 'accessories' },
    { id: '6', name: 'Silk Dress', image: '/api/placeholder/150/150', value: 180, category: 'top' },
    { id: '7', name: 'Denim Jacket', image: '/api/placeholder/150/150', value: 90, category: 'outerwear' },
    { id: '8', name: 'Sneakers', image: '/api/placeholder/150/150', value: 120, category: 'shoes' }
  ];

  const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  const getWeatherIcon = (condition: string) => {
    switch (condition.toLowerCase()) {
      case 'sunny': return <Sun className="w-3 h-3 xs:w-4 xs:h-4 text-yellow-500" />;
      case 'cloudy': return <Cloud className="w-3 h-3 xs:w-4 xs:h-4 text-gray-500" />;
      case 'rainy': return <CloudRain className="w-3 h-3 xs:w-4 xs:h-4 text-blue-500" />;
      default: return <Sun className="w-3 h-3 xs:w-4 xs:h-4 text-yellow-500" />;
    }
  };

  const generateRecommendations = () => {
    const events = ['Work Meeting', 'Casual Day', 'Date Night', 'Business Lunch', 'Weekend Outing', 'Formal Event', 'Gym Session'];
    const weathers: WeatherData[] = [
      { temp: '22°C', condition: 'Sunny', icon: getWeatherIcon('sunny') },
      { temp: '18°C', condition: 'Cloudy', icon: getWeatherIcon('cloudy') },
      { temp: '15°C', condition: 'Rainy', icon: getWeatherIcon('rainy') }
    ];

    const newWeekPlan: WeekPlan = {};

    daysOfWeek.forEach((day, index) => {
      const event = events[index % events.length];
      const weather = weathers[index % weathers.length];
      
      // Smart outfit selection based on event and weather
      let selectedItems: DayOutfit;
      
      if (event.includes('Work') || event.includes('Business')) {
        selectedItems = {
          outerwear: wardrobeItems.find(item => item.name.includes('Blazer')),
          top: wardrobeItems.find(item => item.name.includes('Shirt'))!,
          bottom: wardrobeItems.find(item => item.name.includes('Trousers'))!,
          shoes: wardrobeItems.find(item => item.name.includes('Leather'))!,
          accessories: [wardrobeItems.find(item => item.name.includes('Watch'))!]
        };
      } else if (event.includes('Casual') || event.includes('Weekend')) {
        selectedItems = {
          outerwear: wardrobeItems.find(item => item.name.includes('Denim')),
          top: wardrobeItems.find(item => item.name.includes('Shirt'))!,
          bottom: wardrobeItems.find(item => item.name.includes('Trousers'))!,
          shoes: wardrobeItems.find(item => item.name.includes('Sneakers'))!,
          accessories: []
        };
      } else {
        selectedItems = {
          top: wardrobeItems.find(item => item.name.includes('Dress'))!,
          bottom: wardrobeItems.find(item => item.name.includes('Trousers'))!,
          shoes: wardrobeItems.find(item => item.name.includes('Leather'))!,
          accessories: [wardrobeItems.find(item => item.name.includes('Watch'))!]
        };
      }

      // Calculate total value
      const totalValue = [
        selectedItems.outerwear?.value || 0,
        selectedItems.top?.value || 0,
        selectedItems.bottom?.value || 0,
        selectedItems.shoes?.value || 0,
        ...(selectedItems.accessories?.map(acc => acc.value) || [])
      ].reduce((sum, val) => sum + val, 0);

      newWeekPlan[day] = {
        event,
        weather,
        outfit: selectedItems,
        totalValue,
        confidence: Math.floor(Math.random() * 20) + 80 // 80-100% confidence
      };
    });

    setWeekPlan(newWeekPlan);
    setCurrentStep(2);
  };

  const saveWeeklyPlan = () => {
    const savedPlans = JSON.parse(localStorage.getItem('weeklyPlans') || '[]');
    const newPlan = {
      weekOf,
      plan: weekPlan,
      createdAt: new Date().toISOString()
    };
    
    savedPlans.push(newPlan);
    localStorage.setItem('weeklyPlans', JSON.stringify(savedPlans));
    
    toast({
      title: "Weekly Plan Saved!",
      description: "Your outfit schedule has been saved successfully.",
    });
    
    onClose();
  };

  const renderOutfitPreview = (outfit: DayOutfit) => {
    const allItems = [
      outfit.outerwear,
      outfit.top,
      outfit.bottom,
      outfit.shoes,
      ...(outfit.accessories || [])
    ].filter(Boolean) as OutfitItem[];

    return (
      <div className="grid grid-cols-3 gap-1 xs:gap-2">
        {allItems.slice(0, 6).map((item, index) => (
          <div key={index} className="relative group">
            <img 
              src={item.image} 
              alt={item.name}
              className="w-full h-12 xs:h-16 object-cover rounded border-2 border-white shadow-sm"
            />
            <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity rounded flex items-center justify-center">
              <span className="text-white text-xs font-medium text-center px-1">
                {item.name}
              </span>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderDetailedOutfit = (outfit: DayOutfit) => {
    return (
      <div className="space-y-2 xs:space-y-4">
        {outfit.outerwear && (
          <div className="flex items-center gap-2 xs:gap-3 p-2 xs:p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
            <img src={outfit.outerwear.image} alt={outfit.outerwear.name} className="w-8 h-8 xs:w-12 xs:h-12 object-cover rounded" />
            <div>
              <h4 className="font-medium text-purple-800 dark:text-purple-200 text-xs xs:text-sm">{outfit.outerwear.name}</h4>
              <p className="text-xs text-purple-600 dark:text-purple-300">${outfit.outerwear.value}</p>
            </div>
          </div>
        )}
        
        <div className="flex items-center gap-2 xs:gap-3 p-2 xs:p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <img src={outfit.top.image} alt={outfit.top.name} className="w-8 h-8 xs:w-12 xs:h-12 object-cover rounded" />
          <div>
            <h4 className="font-medium text-blue-800 dark:text-blue-200 text-xs xs:text-sm">{outfit.top.name}</h4>
            <p className="text-xs text-blue-600 dark:text-blue-300">${outfit.top.value}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2 xs:gap-3 p-2 xs:p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <img src={outfit.bottom.image} alt={outfit.bottom.name} className="w-8 h-8 xs:w-12 xs:h-12 object-cover rounded" />
          <div>
            <h4 className="font-medium text-green-800 dark:text-green-200 text-xs xs:text-sm">{outfit.bottom.name}</h4>
            <p className="text-xs text-green-600 dark:text-green-300">${outfit.bottom.value}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2 xs:gap-3 p-2 xs:p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
          <img src={outfit.shoes.image} alt={outfit.shoes.name} className="w-8 h-8 xs:w-12 xs:h-12 object-cover rounded" />
          <div>
            <h4 className="font-medium text-orange-800 dark:text-orange-200 text-xs xs:text-sm">{outfit.shoes.name}</h4>
            <p className="text-xs text-orange-600 dark:text-orange-300">${outfit.shoes.value}</p>
          </div>
        </div>

        {outfit.accessories && outfit.accessories.length > 0 && (
          <div className="space-y-1 xs:space-y-2">
            <h4 className="font-medium text-gray-700 dark:text-gray-300 text-xs xs:text-sm">Accessories</h4>
            {outfit.accessories.map((accessory, index) => (
              <div key={index} className="flex items-center gap-2 xs:gap-3 p-2 xs:p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <img src={accessory.image} alt={accessory.name} className="w-8 h-8 xs:w-12 xs:h-12 object-cover rounded" />
                <div>
                  <h5 className="font-medium text-gray-800 dark:text-gray-200 text-xs xs:text-sm">{accessory.name}</h5>
                  <p className="text-xs text-gray-600 dark:text-gray-400">${accessory.value}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-2 xs:p-3 sm:p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl xs:rounded-3xl w-full max-w-xs xs:max-w-sm sm:max-w-2xl md:max-w-4xl lg:max-w-6xl max-h-[95vh] xs:max-h-[90vh] overflow-y-auto">
        <div className="p-3 xs:p-4 sm:p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div>
            <h2 className="text-lg xs:text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">Plan Your Week</h2>
            <p className="text-xs xs:text-sm text-gray-600 dark:text-gray-400">AI-powered outfit recommendations for the entire week</p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose} className="p-1 xs:p-2">
            <X size={16} className="xs:w-5 xs:h-5" />
          </Button>
        </div>

        <div className="p-3 xs:p-4 sm:p-6">
          {currentStep === 1 && (
            <div className="space-y-4 xs:space-y-6">
              <div>
                <label className="block text-xs xs:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 xs:mb-2">
                  Week Starting
                </label>
                <input
                  type="date"
                  value={weekOf}
                  onChange={(e) => setWeekOf(e.target.value)}
                  className="w-full p-2 xs:p-3 text-sm xs:text-base border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white h-10 xs:h-11"
                />
              </div>

              <div className="text-center">
                <Button
                  onClick={generateRecommendations}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 xs:px-8 py-2 xs:py-3 rounded-xl text-sm xs:text-base h-10 xs:h-12"
                >
                  <Sparkles className="w-4 h-4 xs:w-5 xs:h-5 mr-1 xs:mr-2" />
                  Generate AI Recommendations
                </Button>
              </div>
            </div>
          )}

          {currentStep === 2 && (
            <div className="space-y-4 xs:space-y-6">
              <div className="flex flex-col xs:flex-row items-start xs:items-center justify-between gap-2 xs:gap-0">
                <h3 className="text-lg xs:text-xl font-semibold text-gray-900 dark:text-white">
                  Week of {new Date(weekOf).toLocaleDateString()}
                </h3>
                <div className="flex gap-2 w-full xs:w-auto">
                  <Button variant="outline" onClick={() => setCurrentStep(1)} className="flex-1 xs:flex-none text-xs xs:text-sm h-8 xs:h-9">
                    Back
                  </Button>
                  <Button onClick={saveWeeklyPlan} className="flex-1 xs:flex-none bg-green-600 hover:bg-green-700 text-white text-xs xs:text-sm h-8 xs:h-9">
                    <Save className="w-3 h-3 xs:w-4 xs:h-4 mr-1 xs:mr-2" />
                    Save Plan
                  </Button>
                </div>
              </div>

              {/* Week Overview */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2 xs:gap-3 sm:gap-4">
                {daysOfWeek.map((day) => {
                  const dayPlan = weekPlan[day];
                  if (!dayPlan) return null;

                  return (
                    <Card 
                      key={day} 
                      className={`cursor-pointer transition-all hover:shadow-lg ${
                        selectedDay === day ? 'ring-2 ring-blue-500' : ''
                      }`}
                      onClick={() => setSelectedDay(selectedDay === day ? null : day)}
                    >
                      <CardHeader className="pb-2 xs:pb-3 p-2 xs:p-4">
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-sm xs:text-lg">{day}</CardTitle>
                          <Button size="sm" variant="ghost" className="p-1">
                            <Eye size={12} className="xs:w-4 xs:h-4" />
                          </Button>
                        </div>
                        <div className="flex items-center gap-1 xs:gap-2 text-xs text-gray-600 dark:text-gray-400">
                          {dayPlan.weather.icon}
                          <span>{dayPlan.weather.temp}</span>
                          <span>•</span>
                          <span>{dayPlan.weather.condition}</span>
                        </div>
                      </CardHeader>
                      
                      <CardContent className="space-y-2 xs:space-y-3 p-2 xs:p-4 pt-0">
                        <div>
                          <div className="flex items-center gap-1 xs:gap-2 mb-1 xs:mb-2">
                            <MapPin size={10} className="xs:w-3 xs:h-3 text-gray-500" />
                            <span className="text-xs font-medium text-gray-900 dark:text-white">
                              {dayPlan.event}
                            </span>
                          </div>
                          
                          {renderOutfitPreview(dayPlan.outfit)}
                        </div>
                        
                        <div className="flex items-center justify-between text-xs">
                          <div className="flex items-center gap-1">
                            <Star size={10} className="xs:w-3 xs:h-3 text-yellow-500" />
                            <span className="text-gray-600 dark:text-gray-400">
                              {dayPlan.confidence}%
                            </span>
                          </div>
                          <div className="font-semibold text-green-600">
                            ${dayPlan.totalValue.toFixed(0)}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>

              {/* Detailed View - Responsive for small screens */}
              {selectedDay && weekPlan[selectedDay] && (
                <Card className="mt-4 xs:mt-6">
                  <CardHeader className="p-3 xs:p-6">
                    <CardTitle className="flex items-center gap-1 xs:gap-2 text-sm xs:text-lg">
                      <Calendar size={16} className="xs:w-5 xs:h-5" />
                      {selectedDay} - Detailed Outfit
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-3 xs:p-6 pt-0">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 xs:gap-6">
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2 xs:mb-3 text-sm xs:text-base">Event & Weather</h4>
                        <div className="space-y-1 xs:space-y-2">
                          <div className="flex items-center gap-1 xs:gap-2 text-xs xs:text-sm">
                            <MapPin size={12} className="xs:w-4 xs:h-4 text-blue-500" />
                            <span>{weekPlan[selectedDay].event}</span>
                          </div>
                          <div className="flex items-center gap-1 xs:gap-2 text-xs xs:text-sm">
                            {weekPlan[selectedDay].weather.icon}
                            <span>{weekPlan[selectedDay].weather.temp} • {weekPlan[selectedDay].weather.condition}</span>
                          </div>
                          <div className="flex items-center gap-1 xs:gap-2 text-xs xs:text-sm">
                            <Star size={12} className="xs:w-4 xs:h-4 text-yellow-500" />
                            <span>{weekPlan[selectedDay].confidence}% Style Match</span>
                          </div>
                          <div className="flex items-center gap-1 xs:gap-2 text-xs xs:text-sm">
                            <Zap size={12} className="xs:w-4 xs:h-4 text-green-500" />
                            <span>Total Value: ${weekPlan[selectedDay].totalValue.toFixed(0)}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-2 xs:mb-3 text-sm xs:text-base">Outfit Details</h4>
                        {renderDetailedOutfit(weekPlan[selectedDay].outfit)}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Weekly Summary - Mobile responsive */}
              <Card>
                <CardHeader className="p-3 xs:p-6">
                  <CardTitle className="text-sm xs:text-lg">Weekly Summary</CardTitle>
                </CardHeader>
                <CardContent className="p-3 xs:p-6 pt-0">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 xs:gap-4">
                    <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-2 xs:p-4 text-center">
                      <div className="text-lg xs:text-2xl font-bold text-blue-600">
                        {Object.values(weekPlan).reduce((sum, day) => sum + day.totalValue, 0).toFixed(0)}
                      </div>
                      <div className="text-xs text-blue-700 dark:text-blue-300">Total Value</div>
                    </div>
                    <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-2 xs:p-4 text-center">
                      <div className="text-lg xs:text-2xl font-bold text-green-600">
                        {Math.round(Object.values(weekPlan).reduce((sum, day) => sum + day.confidence, 0) / Object.values(weekPlan).length)}%
                      </div>
                      <div className="text-xs text-green-700 dark:text-green-300">Avg Match</div>
                    </div>
                    <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-2 xs:p-4 text-center">
                      <div className="text-lg xs:text-2xl font-bold text-purple-600">
                        {Object.values(weekPlan).reduce((sum, day) => {
                          const outfitItems = [
                            day.outfit.outerwear,
                            day.outfit.top,
                            day.outfit.bottom,
                            day.outfit.shoes,
                            ...(day.outfit.accessories || [])
                          ].filter(Boolean);
                          return sum + outfitItems.length;
                        }, 0)}
                      </div>
                      <div className="text-xs text-purple-700 dark:text-purple-300">Total Items</div>
                    </div>
                    <div className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-2 xs:p-4 text-center">
                      <div className="text-lg xs:text-2xl font-bold text-orange-600">7</div>
                      <div className="text-xs text-orange-700 dark:text-orange-300">Days Planned</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PlanWeekModal;
