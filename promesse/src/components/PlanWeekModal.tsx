import React, { useState, useCallback } from 'react';
import { Calendar, Sparkles, Eye, Save, X, PackageOpen, AlertTriangle, Info } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import  apiClient  from '@/lib/apiClient';
import { useAuth } from '@/hooks/useAuth';
import  LoadingSpinner  from '@/components/ui/loading'; // Assuming this exists

// Simplified WardrobeItem type for this component's props
export interface WardrobeItem {
  id: number; // Or string, depending on your backend
  name: string;
  image_url?: string;
  // Add other relevant fields if needed for display or logic within this modal
}

export interface PlanWeekModalProps {
  isOpen: boolean;
  onClose: () => void;
  wardrobeItems: WardrobeItem[]; // Pass wardrobe items as a prop
}

// Matches backend WeeklyPlanCreate Pydantic schema
interface WeeklyPlanCreate {
  name: string;
  start_date: string; // ISO date string "YYYY-MM-DD"
  end_date: string;   // ISO date string "YYYY-MM-DD"
  daily_outfits: Record<string, number | null>; // day_name (e.g. "monday") -> outfit_id
}

// Expected response from AI plan generation
type AIPlanResponse = Record<string, number | null>; // day_name -> outfit_id


const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const dayKeys = daysOfWeek.map(day => day.toLowerCase());


const PlanWeekModal = ({ isOpen, onClose, wardrobeItems }: PlanWeekModalProps) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [weekOf, setWeekOf] = useState(new Date().toISOString().split('T')[0]);

  // weekPlan now stores outfit IDs per day
  const [weekPlan, setWeekPlan] = useState<Record<string, number | null>>({});

  const [selectedDay, setSelectedDay] = useState<string | null>(null);
  const [isLoadingAiPlan, setIsLoadingAiPlan] = useState(false);
  const [isSavingPlan, setIsSavingPlan] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);

  const { toast } = useToast();
  const { token } = useAuth();

  const VITE_BASE_URL = import.meta.env.VITE_BASE_URL || '';


  const handleGenerateAIPlan = useCallback(async () => {
    if (!token) {
      toast({ title: "Authentication Error", description: "Please log in to generate a plan.", variant: "destructive" });
      return;
    }
    setIsLoadingAiPlan(true);
    setAiError(null);
    try {
      // const response = await apiClient<AIPlanResponse>('/weekly-plans/generate-ai-plan', {
      //   method: 'POST',
      //   token,
      //   body: JSON.stringify({ start_date: weekOf }),
      // });
      // setWeekPlan(response || {});
      // setCurrentStep(2);

      // TEMP: Simulating AI response until endpoint is ready
      // This creates a plan with null outfit IDs, user has to fill them manually.
      // Or, if you have outfit IDs from wardrobeItems, you could randomly assign a few.
      console.warn("AI Plan Generation: Using placeholder. Integrate with actual /api/weekly-plans/generate-ai-plan");
      const placeholderPlan: AIPlanResponse = dayKeys.reduce((acc, day) => {
        acc[day] = null; // Or pick a random outfit ID from wardrobeItems if available and desired
        return acc;
      }, {} as AIPlanResponse);
      setWeekPlan(placeholderPlan);
      // Example: assign first outfit to Monday if wardrobeItems exist
      // if (wardrobeItems.length > 0 && placeholderPlan.monday === null) {
      //    const firstOutfitCandidate = wardrobeItems.find(item => item.category === 'outfit'); // This assumes wardrobeItems can be outfits
      //    if(firstOutfitCandidate) placeholderPlan.monday = firstOutfitCandidate.id;
      // }
      setCurrentStep(2);
      toast({ title: "Manual Plan Created", description: "AI endpoint placeholder: Please assign outfits manually.", variant: "default" });


    } catch (error: any) {
      console.error("AI Plan Generation Error:", error);
      setAiError(error.message || "Failed to generate AI plan. Please try creating a blank plan or try again later.");
      toast({ title: "AI Plan Error", description: error.message || "Could not generate plan.", variant: "destructive" });
    } finally {
      setIsLoadingAiPlan(false);
    }
  }, [token, weekOf, toast/*, wardrobeItems*/]); // Add wardrobeItems if used in placeholder

  const createBlankPlan = () => {
    const blankPlan: Record<string, number | null> = dayKeys.reduce((acc, day) => {
      acc[day.toLowerCase()] = null;
      return acc;
    }, {});
    setWeekPlan(blankPlan);
    setCurrentStep(2);
    toast({ title: "Blank Plan Created", description: "You can now assign outfits to each day.", variant: "default"});
  };


  const saveWeeklyPlan = async () => {
    if (!token) {
      toast({ title: "Authentication Error", description: "Please log in to save the plan.", variant: "destructive" });
      return;
    }
    setIsSavingPlan(true);

    const startDate = new Date(weekOf);
    const endDate = new Date(startDate);
    endDate.setDate(startDate.getDate() + 6);

    const planToSave: WeeklyPlanCreate = {
      name: `Plan for week of ${startDate.toLocaleDateString()}`,
      start_date: weekOf,
      end_date: endDate.toISOString().split('T')[0],
      daily_outfits: weekPlan,
    };

    try {
      await apiClient('/weekly-plans/', {
        method: 'POST',
        token,
        body: JSON.stringify(planToSave),
      });
      toast({
        title: "Weekly Plan Saved!",
        description: "Your outfit schedule has been saved successfully.",
        variant: "success",
      });
      onClose(); // Close modal on successful save
      // Optionally reset state here if modal can be reopened without remounting
      setCurrentStep(1);
      setWeekPlan({});
      setWeekOf(new Date().toISOString().split('T')[0]);
    } catch (error: any) {
      console.error("Save Weekly Plan Error:", error);
      toast({
        title: "Error Saving Plan",
        description: error.message || "Could not save the plan.",
        variant: "destructive",
      });
    } finally {
      setIsSavingPlan(false);
    }
  };

  // Simplified: Renders outfit ID or a placeholder.
  // Needs wardrobeItems prop to find and display outfit image/name.
  const renderOutfitPreview = (outfitId: number | null, dayKey: string) => {
    // This is tricky: weekly plan stores outfit_id, but wardrobeItems are individual items.
    // For a proper preview, you'd need a list of all user *Outfits* (not just WardrobeItems)
    // and then find the outfit by outfitId.
    // For now, we'll just show the ID or a placeholder if we can't find a matching item.
    // This part highlights a potential mismatch if `wardrobeItems` is just clothing items
    // and not pre-defined outfits.

    // Placeholder logic: try to find an item (if wardrobeItems were outfits)
    // const outfitDetails = wardrobeItems.find(item => item.id === outfitId && item.category === 'outfit'); // Requires outfits in wardrobeItems

    if (outfitId === null) {
      return (
        <div className="text-xs text-gray-500 dark:text-gray-400 italic text-center py-4">
          No outfit assigned
        </div>
      );
    }

    // If we had outfit details (e.g. from a prop `userOutfits: Outfit[]`)
    // const outfitDetails = userOutfits.find(o => o.id === outfitId);
    // if (outfitDetails && outfitDetails.image_url) {
    //   return <img src={outfitDetails.image_url} alt={outfitDetails.name} className="w-full h-20 object-cover rounded" />;
    // }

    return (
      <div className="text-center py-4">
        <PackageOpen size={24} className="mx-auto text-gray-400 mb-1" />
        <p className="text-xs font-medium text-gray-700 dark:text-gray-300">Outfit ID: {outfitId}</p>
        <Button variant="link" size="xs" className="text-xs mt-1" onClick={() => {/* TODO: Open outfit selection for this day */}}>
          Change
        </Button>
      </div>
    );
  };


  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-2 xs:p-3 sm:p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl xs:rounded-3xl w-full max-w-xs xs:max-w-sm sm:max-w-2xl md:max-w-4xl lg:max-w-6xl max-h-[95vh] xs:max-h-[90vh] flex flex-col">
        <div className="p-3 xs:p-4 sm:p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div>
            <h2 className="text-lg xs:text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">Plan Your Week</h2>
            <p className="text-xs xs:text-sm text-gray-600 dark:text-gray-400">Create or generate an outfit schedule.</p>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} className="p-1 xs:p-2" aria-label="Close plan week modal">
            <X size={20} className="xs:w-5 xs:h-5" />
          </Button>
        </div>

        <div className="p-3 xs:p-4 sm:p-6 flex-grow overflow-y-auto">
          {currentStep === 1 && (
            <div className="space-y-4 xs:space-y-6">
              <div>
                <label htmlFor="weekStartDate" className="block text-xs xs:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 xs:mb-2">
                  Week Starting
                </label>
                <input
                  type="date"
                  id="weekStartDate"
                  value={weekOf}
                  onChange={(e) => setWeekOf(e.target.value)}
                  className="w-full p-2 xs:p-3 text-sm xs:text-base border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white h-10 xs:h-11 focus:ring-owis-purple focus:border-owis-purple"
                />
              </div>

              <div className="text-center space-y-3">
                 <Button
                  onClick={handleGenerateAIPlan}
                  disabled={isLoadingAiPlan}
                  className="w-full sm:w-auto bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 xs:px-8 py-2 xs:py-3 rounded-xl text-sm xs:text-base h-10 xs:h-12"
                >
                  {isLoadingAiPlan ? <LoadingSpinner size={20} className="mr-2" /> : <Sparkles className="w-4 h-4 xs:w-5 xs:h-5 mr-1 xs:mr-2" />}
                  Generate AI Recommendations
                </Button>
                <p className="text-xs text-gray-500 dark:text-gray-400">Alternatively</p>
                 <Button
                  onClick={createBlankPlan}
                  variant="outline"
                  className="w-full sm:w-auto text-sm xs:text-base h-10 xs:h-12"
                >
                  Create Blank Plan
                </Button>
              </div>
              {aiError && (
                <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-md text-center">
                    <AlertTriangle className="w-5 h-5 text-red-500 mx-auto mb-1" />
                    <p className="text-xs text-red-600 dark:text-red-400">{aiError}</p>
                </div>
              )}
            </div>
          )}

          {currentStep === 2 && (
            <div className="space-y-4 xs:space-y-6">
              <div className="flex flex-col xs:flex-row items-start xs:items-center justify-between gap-2 xs:gap-0">
                <h3 className="text-lg xs:text-xl font-semibold text-gray-900 dark:text-white">
                  Week of {new Date(weekOf).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}
                </h3>
                <div className="flex gap-2 w-full xs:w-auto">
                  <Button variant="outline" onClick={() => { setCurrentStep(1); setAiError(null); /* Do not clear weekPlan */ }} className="flex-1 xs:flex-none text-xs xs:text-sm h-8 xs:h-9">
                    Back
                  </Button>
                  <Button
                    onClick={saveWeeklyPlan}
                    disabled={isSavingPlan}
                    className="flex-1 xs:flex-none bg-green-600 hover:bg-green-700 text-white text-xs xs:text-sm h-8 xs:h-9"
                  >
                    {isSavingPlan ? <LoadingSpinner size={16} className="mr-2" /> : <Save className="w-3 h-3 xs:w-4 xs:h-4 mr-1 xs:mr-2" />}
                    Save Plan
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 xs:gap-3 sm:gap-4">
                {daysOfWeek.map((dayName) => {
                  const dayKey = dayName.toLowerCase();
                  const outfitId = weekPlan[dayKey];
                  // Calculate actual date for the day card
                  const planStartDate = new Date(weekOf);
                  const dayIndex = daysOfWeek.findIndex(d => d.toLowerCase() === dayKey);
                  const currentDate = new Date(planStartDate);
                  currentDate.setDate(planStartDate.getDate() + dayIndex);
                  const displayDate = currentDate.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });


                  return (
                    <Card 
                      key={dayKey}
                      className={`transition-all hover:shadow-lg dark:border-gray-700 ${
                        selectedDay === dayKey ? 'ring-2 ring-blue-500 dark:ring-blue-400' : ''
                      }`}
                      // onClick={() => setSelectedDay(selectedDay === dayKey ? null : dayKey)} // Simplified, no detailed view for now
                    >
                      <CardHeader className="pb-2 xs:pb-3 p-2 xs:p-4">
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-sm xs:text-base capitalize">{dayName}</CardTitle>
                           <span className="text-xs text-gray-500 dark:text-gray-400">{displayDate}</span>
                          {/* <Button size="icon" variant="ghost" className="p-1 h-7 w-7" onClick={() => setSelectedDay(selectedDay === dayKey ? null : dayKey)}>
                            <Eye size={14} className="xs:w-4 xs:h-4" />
                          </Button> */}
                        </div>
                      </CardHeader>
                      
                      <CardContent className="p-2 xs:p-4 pt-0">
                        {renderOutfitPreview(outfitId, dayKey)}
                        {/* Add button to assign/change outfit */}
                        {/* <Button variant="outline" size="xs" className="w-full mt-2 text-xs" onClick={() => { console.log(`Change outfit for ${dayKey}`)}}>
                           {outfitId ? 'Change Outfit' : 'Assign Outfit'}
                        </Button> */}
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
                <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700/30 rounded-lg text-center">
                    <Info size={18} className="inline mr-2 text-gray-600 dark:text-gray-400" />
                    <p className="text-sm text-gray-600 dark:text-gray-400 inline">
                        Outfit assignment per day is a planned feature. Currently, the AI generates a basic plan structure.
                    </p>
                </div>
              {/* Simplified: Removed detailed view and weekly summary as they relied on mock data structure */}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PlanWeekModal;
