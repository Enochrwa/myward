
import React, { useState, useEffect, useCallback } from 'react';
import { Calendar, Eye, Trash2, X, PackageOpen, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import  apiClient  from '@/lib/apiClient';
import { useAuth } from '@/hooks/useAuth';
import  LoadingSpinner  from '@/components/ui/loading'; // Assuming this exists

export interface SavedWeeklyPlansProps {
  isOpen: boolean;
  onClose: () => void;
}

interface OutfitItem {
  id: number;
  image_url: string;
  category: string;
  name: string;
  brand?: string;
  material?: string;
  style?: string;
  dominant_color_name?: string;
}

interface Outfit {
  id: number;
  name: string;
  items: OutfitItem[];
}

interface Day {
  id: number;
  day_of_week: string;
  date: string;
  occasion: string;
  outfit: Outfit | null;
  weather_forecast: any;
}

interface WeeklyPlanFromAPI {
  id: number;
  name: string;
  start_date: string;
  end_date: string;
  days: Day[];
}

// Helper to format date range
const formatDateRange = (startDateStr: string, endDateStr: string) => {
  const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: 'short', day: 'numeric' };
  const startDate = new Date(startDateStr).toLocaleDateString(undefined, options);
  const endDate = new Date(endDateStr).toLocaleDateString(undefined, options);
  return `${startDate} - ${endDate}`;
};

const SavedWeeklyPlans = ({ isOpen, onClose }: SavedWeeklyPlansProps) => {
  const [savedPlans, setSavedPlans] = useState<WeeklyPlanFromAPI[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<WeeklyPlanFromAPI | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { toast } = useToast();
  const { token } = useAuth();

  const fetchSavedPlans = useCallback(async () => {
    if (!token) {
      setError("Please login to view saved plans.");
      setSavedPlans([]);
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiClient<WeeklyPlanFromAPI[]>('/weekly-plan/', { token });
      setSavedPlans(data || []);
    } catch (err: any) {
      console.error("Fetch Saved Plans Error:", err);
      setError(err.message || 'Failed to fetch saved plans.');
      setSavedPlans([]);
      toast({
        title: "Error",
        description: err.message || 'Failed to fetch saved plans.',
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }, [token, toast]);

  useEffect(() => {
    if (isOpen) {
      fetchSavedPlans();
    } else {
      // Reset state when closed
      setSelectedPlan(null);
    }
  }, [isOpen, fetchSavedPlans]);

  const deletePlan = async (planId: number) => {
    if (!token) {
      toast({ title: "Error", description: "Authentication required.", variant: "destructive" });
      return;
    }
    try {
      await apiClient(`/weekly-plan/${planId}/`, { method: 'DELETE', token });
      setSavedPlans(prevPlans => prevPlans.filter(p => p.id !== planId));
      if (selectedPlan?.id === planId) {
        setSelectedPlan(null); // Clear selection if deleted plan was selected
      }
      toast({
        title: "Plan Deleted",
        description: "Weekly plan has been successfully removed.",
        variant: "success",
      });
    } catch (err: any) {
      console.error("Delete Plan Error:", err);
      toast({
        title: "Error Deleting Plan",
        description: err.message || "Could not delete the plan.",
        variant: "destructive",
      });
    }
  };

  if (!isOpen) return null;

  const renderPlanList = () => (
    <div className="space-y-3 xs:space-y-4">
      {isLoading && (
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner size={48} />
        </div>
      )}
      {error && (
        <div className="text-center py-8 xs:py-12 bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-red-700 dark:text-red-300 mb-2">Error</h3>
          <p className="text-red-600 dark:text-red-400">{error}</p>
          <Button onClick={fetchSavedPlans} className="mt-4">Try Again</Button>
        </div>
      )}
      {!isLoading && !error && savedPlans.length === 0 && (
        <div className="text-center py-8 xs:py-12">
          <Calendar size={36} className="xs:w-12 xs:h-12 mx-auto text-gray-400 mb-3 xs:mb-4" />
          <h3 className="text-base xs:text-lg font-semibold text-gray-900 dark:text-white mb-1 xs:mb-2">No Saved Plans</h3>
          <p className="text-sm xs:text-base text-gray-600 dark:text-gray-400">Create your first weekly plan to see it here.</p>
        </div>
      )}
      {!isLoading && !error && savedPlans.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 xs:gap-4">
          {savedPlans.map((plan) => (
            <Card key={plan.id} className="hover:shadow-lg transition-shadow cursor-pointer flex flex-col dark:border-gray-700">
              <CardHeader className="pb-2 xs:pb-3 p-3 xs:p-4">
                <CardTitle className="text-base xs:text-lg flex items-center justify-between">
                  <span className="truncate">{plan.name}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      deletePlan(plan.id);
                    }}
                    className="text-red-500 hover:text-red-700 p-1"
                    aria-label="Delete plan"
                  >
                    <Trash2 size={12} className="xs:w-4 xs:h-4" />
                  </Button>
                </CardTitle>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  {formatDateRange(plan.start_date, plan.end_date)}
                </p>
              </CardHeader>
              <CardContent className="p-3 xs:p-4 pt-0 flex-grow flex flex-col justify-between">
                <div className="space-y-1 xs:space-y-2 mb-3 xs:mb-4">
                  {plan.days.slice(0, 3).map(day => {
                    if (day.outfit) {
                      return (
                        <div key={day.id} className="flex items-center gap-1 xs:gap-2 text-xs">
                          <PackageOpen size={10} className="xs:w-3 xs:h-3 text-owis-sage" />
                          <span className="font-medium capitalize">{day.day_of_week}:</span>
                          <span className="text-gray-600 dark:text-gray-400 truncate">
                            {day.outfit.name}
                          </span>
                        </div>
                      );
                    }
                    return null;
                  })}
                  {plan.days.filter(d => d.outfit).length > 3 && (
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      +{plan.days.filter(d => d.outfit).length - 3} more days with outfits
                    </p>
                  )}
                  {plan.days.filter(d => d.outfit).length === 0 && (
                    <p className="text-xs text-gray-500 dark:text-gray-400">No outfits assigned to this plan yet.</p>
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
  );

  const renderSelectedPlanDetails = () => {
    if (!selectedPlan) return null;

    return (
      <div className="space-y-4 xs:space-y-6">
        <div className="flex flex-col xs:flex-row items-start xs:items-center justify-between gap-2 xs:gap-3">
          <Button variant="outline" onClick={() => setSelectedPlan(null)} className="text-xs xs:text-sm h-8 xs:h-9 self-start">
            ← Back to Plans
          </Button>
          <div className="text-right">
            <h3 className="text-lg xs:text-xl font-semibold text-gray-900 dark:text-white">
              {selectedPlan.name}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {formatDateRange(selectedPlan.start_date, selectedPlan.end_date)}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 xs:gap-4">
          {selectedPlan.days.map((day) => (
            <Card key={day.id} className="hover:shadow-lg transition-shadow dark:border-gray-700">
              <CardHeader className="pb-2 xs:pb-3 p-3 xs:p-4">
                <CardTitle className="text-sm xs:text-base capitalize">{day.day_of_week}</CardTitle>
                <p className="text-xs text-gray-500 dark:text-gray-400">{day.date}</p>
              </CardHeader>
              <CardContent className="space-y-2 xs:space-y-3 p-3 xs:p-4 pt-0">
                {day.outfit ? (
                  <div className="flex flex-wrap gap-2">
                    {day.outfit.items.map((item) => (
                      <div
                        key={item.id}
                        className="h-20 w-20 rounded-lg shadow-md overflow-hidden group relative"
                      >
                        <img
                          src={item.image_url}
                          alt={item.category}
                          className="h-full w-full object-cover"
                        />
                        <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                          <div className="text-white text-xs p-1 text-center">
                            <p className="font-bold">{item.name}</p>
                            <p>{item.brand}</p>
                            <p>{item.material}</p>
                            <p>{item.style}</p>
                            <p>{item.dominant_color_name}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs xs:text-sm text-gray-500 dark:text-gray-400 italic">No outfit assigned for this day.</p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  };


  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-2 xs:p-3 sm:p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl xs:rounded-3xl w-full max-w-xs xs:max-w-sm sm:max-w-2xl md:max-w-4xl lg:max-w-6xl max-h-[95vh] xs:max-h-[90vh] flex flex-col">
        <div className="p-3 xs:p-4 sm:p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div>
            <h2 className="text-lg xs:text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">Saved Weekly Plans</h2>
            <p className="text-xs xs:text-sm text-gray-600 dark:text-gray-400">View and manage your outfit schedules</p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose} className="p-1 xs:p-2" aria-label="Close saved weekly plans">
            <X size={16} className="xs:w-5 xs:h-5" />
          </Button>
        </div>

        <div className="p-3 xs:p-4 sm:p-6 flex-grow overflow-y-auto">
          {selectedPlan ? renderSelectedPlanDetails() : renderPlanList()}
        </div>
      </div>
    </div>
  );
};

export default SavedWeeklyPlans;
