
import React, { useState, useEffect, useCallback } from 'react';
import { Calendar, Plus, Save, X, ArrowLeft, AlertTriangle, Info, Edit, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea'; // Assuming Textarea component exists
import { useToast } from '@/components/ui/use-toast';
import apiClient from '@/lib/apiClient';
import { useAuth } from '@/hooks/useAuth';
import  LoadingSpinner  from '@/components/ui/loading';
import { Occasion, OccasionCreate } from '@/types/occasionTypes';

interface OccasionPlannerProps {
  isOpen: boolean;
  onClose: () => void;
}

const OccasionPlanner = ({ isOpen, onClose }: OccasionPlannerProps) => {
  const [userOccasions, setUserOccasions] = useState<Occasion[]>([]);
  const [currentView, setCurrentView] = useState<'list' | 'create' | 'details'>('list');
  const [selectedOccasionDetails, setSelectedOccasionDetails] = useState<Occasion | null>(null);
  const [newOccasionData, setNewOccasionData] = useState<OccasionCreate>({ name: '', date: undefined, notes: '' });
  const [selectedOutfitForAssignment, setSelectedOutfitForAssignment] = useState<Outfit | null>(null); // New state

  const [isLoading, setIsLoading] = useState(false); // General loading
  const [isAssigningLoading, setIsAssigningLoading] = useState(false); // Specific loading for assignment
  const [error, setError] = useState<string | null>(null);

  const { token } = useAuth();
  const { toast } = useToast();

  // Import Outfit type for suggested_outfits
  // This should come from a shared types file, assuming it's available via @/types/outfitTypes
  // For this example, if it's not directly importable, we'll rely on the Occasion interface's definition
  // from occasionTypes.ts which should now correctly reference Outfit.
  // import { Outfit } from '@/types/outfitTypes';


  const fetchUserOccasions = useCallback(async () => {
    if (!token) {
      setError("Please log in to manage occasions.");
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiClient('/occasions/');
      setUserOccasions(data || []);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch occasions.');
      setUserOccasions([]);
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (isOpen && token) {
      fetchUserOccasions();
      setCurrentView('list'); // Reset to list view when opened
    }
  }, [isOpen, token, fetchUserOccasions]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setNewOccasionData(prev => ({ ...prev, [name]: value }));
  };

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Ensure date is stored as YYYY-MM-DD or null/undefined if empty
    setNewOccasionData(prev => ({ ...prev, date: e.target.value || undefined }));
  };


  const handleCreateNewOccasion = async () => {
    if (!newOccasionData.name.trim()) {
      toast({ title: "Validation Error", description: "Occasion name is required.", variant: "destructive" });
      return;
    }
    if (!token) {
      toast({ title: "Authentication Error", description: "You must be logged in.", variant: "destructive" });
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const payload: OccasionCreate = {
        ...newOccasionData,
        date: newOccasionData.date || null, // Ensure empty date is null
        notes: newOccasionData.notes || null, // Ensure empty notes is null
      };
      await apiClient('/occasions/', { method: 'POST', body: payload });
      toast({ title: "Success", description: "New occasion created." });
      fetchUserOccasions();
      setCurrentView('list');
      setNewOccasionData({ name: '', date: undefined, notes: '' });
    } catch (err: any) {
      setError(err.message || "Could not create occasion.");
      toast({ title: "Error", description: err.message || "Could not create occasion.", variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAssignOutfitToOccasion = async (occasionId: string, outfitId: string | null) => {
    if (!token) {
      toast({ title: "Authentication Error", description: "Please login to update occasion.", variant: "destructive" });
      return;
    }
    setIsAssigningLoading(true); // Use specific loading state
    try {
      const updatedOccasion = await apiClient(`/occasions/${occasionId}`, {
        method: 'PUT',
        body: { outfit_id: outfitId }, // Send null to unassign
      });
      // Update local state for the specific occasion
      setUserOccasions(prev => prev.map(occ => occ.id === occasionId ? { ...occ, ...updatedOccasion, outfit_id: outfitId } : occ));
      if (selectedOccasionDetails && selectedOccasionDetails.id === occasionId) {
        setSelectedOccasionDetails(prev => prev ? { ...prev, ...updatedOccasion, outfit_id: outfitId } : null);
      }
      toast({ title: "Success", description: outfitId ? "Outfit assigned to occasion." : "Outfit unassigned from occasion." });
      setSelectedOutfitForAssignment(null); // Clear temporary selection
    } catch (err: any) {
      toast({ title: "Error", description: err.message || "Could not update occasion.", variant: "destructive" });
    } finally {
      setIsAssigningLoading(false);
    }
  };

  const viewDetails = (occasion: Occasion) => {
    // Assuming fetchUserOccasions or initial load gets full details including suggestions
    // If not, a specific fetch for /occasions/{id} might be needed here
    setSelectedOccasionDetails(occasion);
    setCurrentView('details');
    setSelectedOutfitForAssignment(null); // Reset any temporary outfit selection
  };

  if (!isOpen) return null;

  const renderListView = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Your Occasions</h3>
        <Button onClick={() => { setCurrentView('create'); setNewOccasionData({ name: '', date: undefined, notes: '' }); }} className="bg-owis-gold hover:bg-owis-gold-dark text-owis-forest">
          <Plus size={18} className="mr-2" /> Create New
        </Button>
      </div>
      {isLoading && <div className="flex justify-center py-4"><LoadingSpinner /></div>}
      {!isLoading && error && <p className="text-red-500 dark:text-red-400 p-4 bg-red-50 dark:bg-red-900/20 rounded-md flex items-center"><AlertTriangle size={20} className="mr-2"/>{error}</p>}
      {!isLoading && !error && userOccasions.length === 0 && (
        <p className="text-gray-500 dark:text-gray-400 text-center py-6">No occasions planned yet. Get started by creating one!</p>
      )}
      {!isLoading && !error && userOccasions.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {userOccasions.map(occasion => (
            <Card key={occasion.id} className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => viewDetails(occasion)}>
              <CardContent className="p-4">
                <h4 className="font-semibold text-lg text-owis-charcoal dark:text-owis-cream truncate">{occasion.name}</h4>
                {occasion.date && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 flex items-center mt-1">
                    <Calendar size={14} className="mr-2 text-owis-sage" /> {new Date(occasion.date).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}
                  </p>
                )}
                {occasion.notes && <p className="text-xs text-gray-500 dark:text-gray-300 mt-2 line-clamp-2 italic">"{occasion.notes}"</p>}
                {/* Placeholder for outfit count or assigned outfit image if available in future */}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );

  const renderCreateView = () => (
    <div className="space-y-4">
      <Button variant="outline" onClick={() => setCurrentView('list')} className="mb-4 text-sm">
        <ArrowLeft size={16} className="mr-2" /> Back to List
      </Button>
      <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Create New Occasion</h3>
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Occasion Name *</label>
        <Input id="name" name="name" value={newOccasionData.name} onChange={handleInputChange} placeholder="e.g., Birthday Dinner, Conference Day 1" className="mt-1 h-10"/>
      </div>
      <div>
        <label htmlFor="date" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Date (Optional)</label>
        <Input id="date" name="date" type="date" value={newOccasionData.date || ''} onChange={handleDateChange} className="mt-1 h-10"/>
      </div>
      <div>
        <label htmlFor="notes" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Notes (Optional)</label>
        <Textarea id="notes" name="notes" value={newOccasionData.notes || ''} onChange={handleInputChange} placeholder="e.g., Dress code: smart casual, bring gift" className="mt-1"/>
      </div>
      <Button onClick={handleCreateNewOccasion} disabled={isLoading} className="w-full sm:w-auto bg-owis-forest hover:bg-owis-forest-dark text-white">
        {isLoading ? <LoadingSpinner size="sm" /> : <Save size={16} className="mr-2" />} Save Occasion
      </Button>
    </div>
  );

  const renderDetailsView = () => {
    if (!selectedOccasionDetails) return <p>Occasion details not found.</p>;
    return (
      <div className="space-y-4">
        <Button variant="outline" onClick={() => setCurrentView('list')} className="mb-4 text-sm">
          <ArrowLeft size={16} className="mr-2" /> Back to List
        </Button>
        <h3 className="text-2xl font-bold text-owis-charcoal dark:text-owis-cream">{selectedOccasionDetails.name}</h3>
        {selectedOccasionDetails.date && (
          <p className="text-md text-gray-700 dark:text-gray-300 flex items-center">
            <Calendar size={18} className="mr-3 text-owis-sage" />
            {new Date(selectedOccasionDetails.date).toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
        )}
        {selectedOccasionDetails.notes && (
          <div className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-md">
            <h4 className="font-semibold text-sm text-gray-600 dark:text-gray-200 mb-1 flex items-center"><Info size={14} className="mr-2 text-owis-info"/>Notes:</h4>
            <p className="text-sm text-gray-600 dark:text-gray-300 whitespace-pre-wrap">{selectedOccasionDetails.notes}</p>
          </div>
        )}
        {/* Assigned Outfit Section */}
        <div className="pt-4 border-t dark:border-gray-700">
          <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-2">Assigned Outfit</h4>
          {selectedOccasionDetails.outfit_id ? (
            (() => {
              // Try to find the full outfit details from suggested_outfits if available
              const assignedOutfitFull = selectedOccasionDetails.suggested_outfits?.find(o => o.id === selectedOccasionDetails.outfit_id);
              return (
                <div className="p-3 bg-green-50 dark:bg-green-900/30 rounded-md">
                  {assignedOutfitFull ? (
                    <div className="flex items-center gap-3">
                      <img src={assignedOutfitFull.image_url || 'https://via.placeholder.com/80?text=Outfit'} alt={assignedOutfitFull.name} className="w-16 h-20 object-cover rounded"/>
                      <div>
                        <p className="font-semibold text-green-700 dark:text-green-300">{assignedOutfitFull.name}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">ID: {assignedOutfitFull.id}</p>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-600 dark:text-gray-300">Outfit ID: {selectedOccasionDetails.outfit_id} (Details not in suggestions)</p>
                  )}
                  <Button variant="outline" size="sm" onClick={() => handleAssignOutfitToOccasion(selectedOccasionDetails!.id, null)} className="mt-2 text-xs" disabled={isAssigningLoading}>
                    {isAssigningLoading && selectedOccasionDetails.outfit_id ? <LoadingSpinner size="xs" /> : null} Unassign Outfit
                  </Button>
                </div>
              );
            })()
          ) : (
            <p className="text-sm text-gray-500 dark:text-gray-400">No outfit assigned yet.</p>
          )}
        </div>

        {/* Suggested Outfits Section */}
        <div className="pt-4 mt-4 border-t dark:border-gray-700">
          <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-3">Suggested Outfits</h4>
          {(selectedOccasionDetails.suggested_outfits && selectedOccasionDetails.suggested_outfits.length > 0) ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 max-h-96 overflow-y-auto pr-2">
              {selectedOccasionDetails.suggested_outfits.map(outfit => (
                <Card key={outfit.id} className="overflow-hidden">
                  <img src={outfit.image_url || 'https://via.placeholder.com/150x200.png?text=No+Image'} alt={outfit.name} className="w-full h-40 object-cover"/>
                  <CardContent className="p-3">
                    <h5 className="font-medium text-sm text-gray-900 dark:text-white truncate mb-1">{outfit.name}</h5>
                    {/* <p className="text-xs text-gray-500 dark:text-gray-400 mb-2 truncate">{outfit.item_ids.length} items</p> */}
                    <Button
                      size="xs"
                      className="w-full bg-owis-secondary hover:bg-owis-secondary-dark text-white"
                      onClick={() => handleAssignOutfitToOccasion(selectedOccasionDetails!.id, outfit.id)}
                      disabled={isAssigningLoading || selectedOccasionDetails.outfit_id === outfit.id}
                    >
                      {isAssigningLoading && selectedOccasionDetails.outfit_id !== outfit.id ? <LoadingSpinner size="xs" /> : (selectedOccasionDetails.outfit_id === outfit.id ? 'Assigned' : 'Select this outfit')}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500 dark:text-gray-400">No specific outfit suggestions available for this occasion yet.</p>
          )}
        </div>
         {/* <div className="flex gap-2 mt-6">
            <Button variant="outline" onClick={() => {}}><Edit size={16} className="mr-2"/> Edit Occasion</Button>
            <Button variant="destructiveOutline" onClick={() => {}}><Trash2 size={16} className="mr-2"/> Delete Occasion</Button>
        </div> */}
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-[60] flex items-center justify-center p-2 sm:p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl w-full max-w-2xl lg:max-w-3xl max-h-[90vh] flex flex-col">
        <div className="p-4 sm:p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between shrink-0">
          <h2 className="text-xl sm:text-2xl font-semibold text-gray-900 dark:text-white">Occasion Planner</h2>
          <Button variant="ghost" size="icon" onClick={onClose} className="p-1">
            <X size={20} />
          </Button>
        </div>
        <div className="p-4 sm:p-6 overflow-y-auto flex-grow">
          {currentView === 'list' && renderListView()}
          {currentView === 'create' && renderCreateView()}
          {currentView === 'details' && renderDetailsView()}
        </div>
      </div>
    </div>
  );
};

export default OccasionPlanner;
