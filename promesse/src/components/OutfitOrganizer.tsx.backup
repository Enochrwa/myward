
import React, { useState, useEffect, useCallback } from 'react'; // Added useEffect, useCallback
import { Grid, List, Filter, Star, Calendar, Tag, Search, Plus, Eye, Edit, Trash2, AlertTriangle } from 'lucide-react'; // Added AlertTriangle
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Outfit, OutfitCreate } from '@/types/outfitTypes'; // Import Outfit & OutfitCreate interface
import { WardrobeItem } from './WardrobeManager'; // Import WardrobeItem for props
import apiClient from '@/lib/apiClient';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ui/use-toast';
import  LoadingSpinner  from '@/components/ui/loading';
import EditOutfitModal from './EditOutfitModal'; // Import EditOutfitModal

interface OutfitOrganizerProps {
  isOpen: boolean;
  onClose: () => void;
  wardrobeItemsForOutfitCreation: WardrobeItem[]; // For EditOutfitModal
}

// Mock data removed, will fetch from backend

const OutfitOrganizer = ({ isOpen, onClose, wardrobeItemsForOutfitCreation }: OutfitOrganizerProps) => {
  const [outfits, setOutfits] = useState<Outfit[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuth(); // Get token for API calls
  const { toast } = useToast();

  // State for Edit Modal
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [currentEditingOutfit, setCurrentEditingOutfit] = useState<Outfit | null>(null);

  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchTerm, setSearchTerm] = useState('');
  // Simplified filters based on backend Outfit model
  const [sortBy, setSortBy] = useState('name'); // 'name', 'created_at' (if available)

  const fetchOutfits = useCallback(async () => {
    if (!token) {
      setError("Please login to view your outfits.");
      setIsLoading(false);
      setOutfits([]);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiClient('/outfits/');
      setOutfits(data || []);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch outfits.');
      setOutfits([]);
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (isOpen) { // Fetch outfits when modal is opened and token is available
      fetchOutfits();
    }
  }, [isOpen, fetchOutfits]);

  // client-side filtering and sorting
  const processedOutfits = outfits
    .filter(outfit => {
      const searchLower = searchTerm.toLowerCase();
      const nameMatch = outfit.name.toLowerCase().includes(searchLower);
      const tagsMatch = outfit.tags && outfit.tags.some(tag => tag.toLowerCase().includes(searchLower));
      return nameMatch || tagsMatch;
    })
    .sort((a, b) => {
      if (sortBy === 'name') {
        return a.name.localeCompare(b.name);
      } else if (sortBy === 'created_at' && a.created_at && b.created_at) {
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      }
      // Add more sorting options if needed
      return 0;
    });

  // Favorite toggle for outfits - to be implemented if backend supports it
  // const toggleOutfitFavorite = async (outfitId: string, currentStatus: boolean) => { ... }

  const handleDeleteOutfit = async (outfitId: string) => {
    if (!token) {
      toast({ title: "Authentication Error", description: "Please login to delete outfits.", variant: "destructive" });
      return;
    }
    // Optional: Add confirmation dialog here
    // if (!window.confirm("Are you sure you want to delete this outfit?")) return;
    try {
      await apiClient(`/outfits/${outfitId}`, { method: 'DELETE' });
      setOutfits(prev => prev.filter(o => o.id !== outfitId));
      toast({ title: "Success", description: "Outfit deleted." });
    } catch (err: any) {
      toast({ title: "Error", description: err.message || "Could not delete outfit.", variant: "destructive" });
    }
  };

  const handleUpdateOutfit = async (outfitId: string, data: Partial<OutfitCreate>) => {
    if (!token) {
      toast({ title: "Authentication Error", description: "Please login to update outfits.", variant: "destructive" });
      return;
    }
    try {
      const updatedOutfit = await apiClient(`/outfits/${outfitId}`, {
        method: 'PUT',
        body: data,
      });
      // If PUT returns the full updated outfit, merge it. Otherwise, re-fetch.
      setOutfits(prev => prev.map(o => o.id === outfitId ? { ...o, ...updatedOutfit } : o));
      // Or for simplicity and consistency if backend response varies:
      // fetchOutfits();
      setIsEditModalOpen(false);
      toast({ title: "Success", description: "Outfit updated." });
    } catch (err: any) {
      toast({ title: "Error", description: err.message || "Could not update outfit.", variant: "destructive" });
    }
  };

  const openEditOutfitModal = (outfit: Outfit) => {
    setCurrentEditingOutfit(outfit);
    setIsEditModalOpen(true);
  };


  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[70] flex items-center justify-center p-4"> {/* Increased z-index */}
      <div className="bg-white dark:bg-gray-800 rounded-3xl max-w-7xl w-full max-h-[90vh] flex flex-col">
        <EditOutfitModal
            isOpen={isEditModalOpen}
            onClose={() => { setIsEditModalOpen(false); setCurrentEditingOutfit(null); }}
            onUpdate={handleUpdateOutfit}
            outfitToEdit={currentEditingOutfit}
            allWardrobeItems={wardrobeItemsForOutfitCreation}
        />
        <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between shrink-0">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Outfit Organizer</h2>
            <p className="text-gray-600 dark:text-gray-400">Organize and manage your complete outfit collections</p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose} className="p-2">
            <X size={20}/>
          </Button>
        </div>

        <div className="p-6 space-y-6 overflow-y-auto flex-grow">
          {/* Controls */}
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <Input
                  placeholder="Search outfits by name or tags..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600"
                  disabled={isLoading || !!error}
                />
              </div>
            </div>
            
            <div className="flex flex-wrap gap-2">
              {/* Removed category and occasion filters as they are not in backend Outfit model */}
              <select 
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                disabled={isLoading || !!error}
              >
                <option value="name">Sort by Name</option>
                {/* Add other sort options if applicable, e.g., by date_created if available */}
                 <option value="created_at">Sort by Date Created</option>
              </select>

              <div className="flex gap-1">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setViewMode('grid')}
                  className={viewMode === 'grid' ? 'bg-owis-sage text-white' : 'dark:text-gray-300 dark:border-gray-600'}
                  disabled={isLoading || !!error}
                >
                  <Grid size={16} />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setViewMode('list')}
                  className={viewMode === 'list' ? 'bg-owis-sage text-white' : 'dark:text-gray-300 dark:border-gray-600'}
                  disabled={isLoading || !!error}
                >
                  <List size={16} />
                </Button>
              </div>
            </div>
          </div>

          {/* Loading and Error States */}
          {isLoading && (
            <div className="flex justify-center items-center py-12">
              <LoadingSpinner size="lg" />
              <p className="ml-4 text-gray-600 dark:text-gray-400">Loading outfits...</p>
            </div>
          )}
          {!isLoading && error && (
            <div className="text-center py-12 bg-red-50 dark:bg-red-900/20 p-6 rounded-lg shadow-md">
              <AlertTriangle size={48} className="text-red-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-red-700 dark:text-red-400 mb-2">Failed to Load Outfits</h3>
              <p className="text-red-600 dark:text-red-300">{error}</p>
              <Button onClick={fetchOutfits} className="mt-4">Try Again</Button>
            </div>
          )}

          {/* Outfits Display */}
          {!isLoading && !error && processedOutfits.length > 0 && (
            <div className={
              viewMode === 'grid'
                ? "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
                : "space-y-4"
            }>
              {processedOutfits.map((outfit) => (
                <Card
                  key={outfit.id}
                  className={`group hover:shadow-xl transition-all duration-300 bg-white dark:bg-gray-800/50 ${
                    viewMode === 'list' ? 'flex flex-row items-center' : ''
                  }`}
                >
                  <div className={viewMode === 'list' ? 'w-32 h-32 flex-shrink-0' : 'aspect-[3/4]'}>
                    <img
                      src={outfit.image_url || 'https://via.placeholder.com/300x400.png?text=No+Image'} // Use placeholder if no image_url
                      alt={outfit.name}
                      className="w-full h-full object-cover rounded-t-lg md:rounded-l-lg md:rounded-t-none group-hover:opacity-90 transition-opacity duration-300"
                    />
                  </div>

                  <CardContent className={`p-4 flex flex-col justify-between ${viewMode === 'list' ? 'flex-1' : 'h-full'}`}>
                    <div>
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-semibold text-gray-900 dark:text-white truncate group-hover:text-owis-gold transition-colors">{outfit.name}</h3>
                        {/* Favorite button (functionality to be added if backend supports) */}
                        {/* <Button variant="ghost" size="icon" className="ml-2 p-1 h-7 w-7 text-gray-400 hover:text-yellow-500">
                          <Star size={16} />
                        </Button> */}
                      </div>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                        {outfit.item_ids?.length || 0} item{outfit.item_ids?.length === 1 ? '' : 's'}
                      </p>
                      {outfit.tags && outfit.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mb-3">
                          {outfit.tags.slice(0, 3).map((tag, i) => (
                            <Badge key={i} variant="secondary" className="text-xs bg-owis-tag-background text-owis-tag-text">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Display created_at if available and in list view */}
                    {viewMode === 'list' && outfit.created_at && (
                        <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
                            Created: {new Date(outfit.created_at).toLocaleDateString()}
                        </p>
                    )}

                    <div className="flex justify-end gap-2 mt-auto pt-3">
                       {/* Placeholder for View button if needed */}
                       {/* <Button variant="outline" size="icon" className="h-7 w-7" onClick={() => {}} disabled={isLoading}><Eye size={12} /></Button> */}
                       <Button variant="outline" size="icon" className="h-7 w-7" onClick={() => openEditOutfitModal(outfit)} disabled={isLoading}>
                            <Edit size={12} />
                       </Button>
                       <Button variant="destructiveOutline" size="icon" className="h-7 w-7" onClick={() => handleDeleteOutfit(outfit.id)} disabled={isLoading}>
                            <Trash2 size={12} />
                       </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {!isLoading && !error && processedOutfits.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-600 dark:text-gray-400 text-lg">
                {outfits.length === 0 ? "You haven't created any outfits yet." : "No outfits found matching your criteria."}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OutfitOrganizer;
