
import React, { useState, useEffect } from 'react';
import { Calendar, Eye, Trash2, X, MapPin, Star } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';

export interface SavedWeeklyPlansProps {
  isOpen: boolean;
  onClose: () => void;
}

interface SavedPlan {
  weekOf: string;
  plan: any;
  createdAt: string;
}

const SavedWeeklyPlans = ({ isOpen, onClose }: SavedWeeklyPlansProps) => {
  const [savedPlans, setSavedPlans] = useState<SavedPlan[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<SavedPlan | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    if (isOpen) {
      const plans = JSON.parse(localStorage.getItem('weeklyPlans') || '[]');
      setSavedPlans(plans);
    }
  }, [isOpen]);

  const deletePlan = (index: number) => {
    const updatedPlans = savedPlans.filter((_, i) => i !== index);
    setSavedPlans(updatedPlans);
    localStorage.setItem('weeklyPlans', JSON.stringify(updatedPlans));
    
    toast({
      title: "Plan Deleted",
      description: "Weekly plan has been removed from your saved plans.",
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-2 xs:p-3 sm:p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl xs:rounded-3xl w-full max-w-xs xs:max-w-sm sm:max-w-2xl md:max-w-4xl lg:max-w-6xl max-h-[95vh] xs:max-h-[90vh] overflow-y-auto">
        <div className="p-3 xs:p-4 sm:p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div>
            <h2 className="text-lg xs:text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">Saved Weekly Plans</h2>
            <p className="text-xs xs:text-sm text-gray-600 dark:text-gray-400">View and manage your outfit schedules</p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose} className="p-1 xs:p-2">
            <X size={16} className="xs:w-5 xs:h-5" />
          </Button>
        </div>

        <div className="p-3 xs:p-4 sm:p-6">
          {!selectedPlan ? (
            <div className="space-y-3 xs:space-y-4">
              {savedPlans.length === 0 ? (
                <div className="text-center py-8 xs:py-12">
                  <Calendar size={36} className="xs:w-12 xs:h-12 mx-auto text-gray-400 mb-3 xs:mb-4" />
                  <h3 className="text-base xs:text-lg font-semibold text-gray-900 dark:text-white mb-1 xs:mb-2">No Saved Plans</h3>
                  <p className="text-sm xs:text-base text-gray-600 dark:text-gray-400">Create your first weekly plan to see it here.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 xs:gap-4">
                  {savedPlans.map((plan, index) => (
                    <Card key={index} className="hover:shadow-lg transition-shadow cursor-pointer">
                      <CardHeader className="pb-2 xs:pb-3 p-3 xs:p-4">
                        <CardTitle className="text-sm xs:text-lg flex items-center justify-between">
                          <span className="truncate">Week of {new Date(plan.weekOf).toLocaleDateString()}</span>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              deletePlan(index);
                            }}
                            className="text-red-500 hover:text-red-700 p-1"
                          >
                            <Trash2 size={12} className="xs:w-4 xs:h-4" />
                          </Button>
                        </CardTitle>
                        <p className="text-xs text-gray-600 dark:text-gray-400">
                          Created {new Date(plan.createdAt).toLocaleDateString()}
                        </p>
                      </CardHeader>
                      <CardContent className="p-3 xs:p-4 pt-0">
                        <div className="space-y-1 xs:space-y-2 mb-3 xs:mb-4">
                          {Object.entries(plan.plan).slice(0, 3).map(([day, dayPlan]: [string, any]) => (
                            <div key={day} className="flex items-center gap-1 xs:gap-2 text-xs">
                              <MapPin size={10} className="xs:w-3 xs:h-3 text-owis-sage" />
                              <span className="font-medium">{day}:</span>
                              <span className="text-gray-600 dark:text-gray-400 truncate">{dayPlan.event}</span>
                            </div>
                          ))}
                          {Object.keys(plan.plan).length > 3 && (
                            <p className="text-xs text-gray-500">+{Object.keys(plan.plan).length - 3} more days</p>
                          )}
                        </div>
                        <Button
                          onClick={() => setSelectedPlan(plan)}
                          className="w-full bg-owis-sage hover:bg-owis-sage-dark text-white text-xs xs:text-sm h-8 xs:h-9"
                        >
                          <Eye size={12} className="xs:w-4 xs:h-4 mr-1 xs:mr-2" />
                          View Details
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-4 xs:space-y-6">
              <div className="flex flex-col xs:flex-row items-start xs:items-center gap-2 xs:gap-3">
                <Button variant="outline" onClick={() => setSelectedPlan(null)} className="text-xs xs:text-sm h-8 xs:h-9">
                  ← Back to Plans
                </Button>
                <h3 className="text-lg xs:text-xl font-semibold text-gray-900 dark:text-white">
                  Week of {new Date(selectedPlan.weekOf).toLocaleDateString()}
                </h3>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 xs:gap-4">
                {Object.entries(selectedPlan.plan).map(([day, dayPlan]: [string, any]) => (
                  <Card key={day} className="hover:shadow-lg transition-shadow">
                    <CardHeader className="pb-2 xs:pb-3 p-3 xs:p-4">
                      <CardTitle className="text-sm xs:text-lg">{day}</CardTitle>
                      <div className="flex items-center gap-1 xs:gap-2 text-xs text-gray-600 dark:text-gray-400">
                        {dayPlan.weather?.icon}
                        <span>{dayPlan.weather?.temp}</span>
                        <span>•</span>
                        <span>{dayPlan.weather?.condition}</span>
                      </div>
                    </CardHeader>
                    
                    <CardContent className="space-y-2 xs:space-y-3 p-3 xs:p-4 pt-0">
                      <div className="flex items-center gap-1 xs:gap-2">
                        <MapPin size={10} className="xs:w-3 xs:h-3 text-owis-sage" />
                        <span className="text-xs font-medium">{dayPlan.event}</span>
                      </div>
                      
                      <div className="grid grid-cols-3 gap-1 xs:gap-2">
                        {dayPlan.outfit && [
                          dayPlan.outfit.outerwear,
                          dayPlan.outfit.top,
                          dayPlan.outfit.bottom,
                          dayPlan.outfit.shoes,
                          ...(dayPlan.outfit.accessories || [])
                        ].filter(Boolean).slice(0, 6).map((item: any, index: number) => (
                          <div key={index} className="relative group">
                            <img 
                              src={item.image} 
                              alt={item.name}
                              className="w-full h-10 xs:h-12 object-cover rounded border-2 border-white shadow-sm"
                            />
                            <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity rounded flex items-center justify-center">
                              <span className="text-white text-xs font-medium text-center px-1">
                                {item.name}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                      
                      <div className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-1">
                          <Star size={10} className="xs:w-3 xs:h-3 text-yellow-500" />
                          <span className="text-gray-600 dark:text-gray-400">
                            {dayPlan.confidence}% match
                          </span>
                        </div>
                        <div className="font-semibold text-green-600">
                          ${dayPlan.totalValue?.toFixed(0)}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SavedWeeklyPlans;
