import React, { useState, useEffect, useCallback } from 'react'; // Added useEffect, useCallback
import { Plus, Search, Filter, Grid, List, Heart, Star, Calendar, MoreVertical, Edit, Trash2, Clock, History, Users, AlertTriangle } from 'lucide-react'; // Added AlertTriangle
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import AddItemModal from './AddItemModal';
import EditItemModal from './EditItemModal'; // Added EditItemModal import
import apiClient from '@/lib/apiClient'; // Added apiClient
import { useAuth } from '@/hooks/useAuth'; // Added useAuth
import { useToast } from "@/components/ui/use-toast"; // Added useToast
import  LoadingSpinner  from '@/components/ui/loading'; // Added LoadingSpinner
import CreateOutfitModal from './CreateOutfitModal';
import { OutfitCreate } from '../types/outfitTypes'; // Added OutfitCreate import
import PlanWeekModal from './PlanWeekModal';
import SavedWeeklyPlans from './SavedWeeklyPlans';
import OccasionPlanner from './OccasionPlanner';
import StyleHistory from './StyleHistory';
import OutfitOrganizer from './OutfitOrganizer';

// Updated WardrobeItem interface
export interface WardrobeItem {
  id: string;
  name: string;
  brand: string;
  category: string;
  size: string;
  price: number;
  material: string;
  season: string;
  image_url: string; // Changed from image
  tags: string[];
  favorite: boolean;
  times_worn: number; // Changed from timesWorn
  date_added: string; // Ensure format matches backend
  color?: string; // Optional field
  notes?: string; // Optional field
}

// For data sent to backend (POST request) - used by AddItemModal and handleSaveItem
export interface WardrobeItemCreate {
  name: string;
  brand: string;
  category: string;
  size: string;
  price: number;
  material: string;
  season: string;
  image_url?: string; // Optional, backend might handle upload separately or auto-generate
  tags: string[];
  color?: string;
  notes?: string;
}


const WardrobeManager = () => {
  const { token } = useAuth(); // Get token to ensure user is authenticated before actions
  const { toast } = useToast();

  const [items, setItems] = useState<WardrobeItem[]>([]); // Changed from wardrobeItems and mockWardrobeItems
  const [isLoading, setIsLoading] = useState(true); // Added isLoading state
  const [error, setError] = useState<string | null>(null); // Added error state

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  // const [selectedSeason, setSelectedSeason] = useState('all'); // Example for future filter
  // const [showFavoritesOnly, setShowFavoritesOnly] = useState(false); // Example for future filter

  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isCreateOutfitOpen, setIsCreateOutfitOpen] = useState(false);
  const [isPlanWeekOpen, setIsPlanWeekOpen] = useState(false);
  const [showSavedPlans, setShowSavedPlans] = useState(false);
  const [isOccasionPlannerOpen, setIsOccasionPlannerOpen] = useState(false);
  const [isStyleHistoryOpen, setIsStyleHistoryOpen] = useState(false);
  const [isOutfitOrganizerOpen, setIsOutfitOrganizerOpen] = useState(false);

  // State for Edit Modal
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<WardrobeItem | null>(null);

  // Fetch Items Function
  const fetchItems = useCallback(async () => {
    if (!token) { // Do not fetch if user is not logged in
      setIsLoading(false);
      setError("Please login to view your wardrobe.");
      setItems([]);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (selectedCategory && selectedCategory !== 'all') params.append('category', selectedCategory);
      // if (selectedSeason && selectedSeason !== 'all') params.append('season', selectedSeason);
      // if (showFavoritesOnly) params.append('favorite', 'true');

      const data = await apiClient(`/wardrobe/items/?${params.toString()}`);
      setItems(data || []);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch wardrobe items.');
      setItems([]);
    } finally {
      setIsLoading(false);
    }
  }, [searchTerm, selectedCategory, token]); // Add selectedSeason, showFavoritesOnly if filters implemented

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  // Handle Save Item (for AddItemModal)
  // Updated to accept imageFile and use the new apiClient.addItem
  const handleSaveItem = async (newItemData: Omit<WardrobeItemCreate, 'image_url'>, imageFile?: File) => {
    if (!token) {
      toast({ title: "Authentication Error", description: "You must be logged in to add items.", variant: "destructive" });
      return;
    }
    try {
      // Use the new addItem function from apiClient which handles FormData
      const savedItem = await apiClient.addItem(newItemData, imageFile);

      fetchItems(); // Re-fetch to get the latest list
      setIsAddModalOpen(false);
      toast({ title: "Success", description: `${savedItem.name} added to your wardrobe.` });
    } catch (err: any) {
      console.error("Failed to save item:", err);
      toast({ title: "Error", description: err.message || "Could not save item.", variant: "destructive" });
    }
  };

  // Handle Update Item
  // Updated to accept imageFile, removeCurrentImage and use apiClient.updateItem
  const handleUpdateItem = async (
    itemId: string,
    updatedData: Partial<Omit<WardrobeItemCreate, 'image_url'>>,
    imageFile?: File,
    removeCurrentImage?: boolean
  ) => {
    if (!token) {
      toast({ title: "Authentication Error", description: "You must be logged in to update items.", variant: "destructive" });
      return;
    }

    // Note: Optimistic update for image changes is tricky as the image_url is generated by the backend.
    // For simplicity, we'll re-fetch items after successful update to show image changes.
    // A more advanced optimistic update would involve creating a temporary local URL for the new image.

    try {
      // Construct the data payload for the API.
      // If removeCurrentImage is true and no new imageFile, send image_url: null.
      // If imageFile is present, backend handles it, image_url in updatedData might be ignored or used as fallback.
      const dataForApi = { ...updatedData };
      if (removeCurrentImage && !imageFile) {
        (dataForApi as any).image_url = null;
      }

      await apiClient.updateItem(itemId, dataForApi, imageFile);

      toast({ title: "Success", description: "Item updated successfully." });
      fetchItems(); // Re-fetch items to reflect changes, especially for image_url
      setIsEditModalOpen(false); // Close modal on successful update
    } catch (err: any) {
      // No optimistic update to revert here for simplicity with images,
      // but if you had one for non-image fields, revert it.
      toast({ title: "Error", description: err.message || "Could not update item.", variant: "destructive" });
      // fetchItems(); // Optionally re-fetch to ensure UI consistency even after error
    }
  };

  // Handle Delete Item
  const handleDeleteItem = async (itemId: string) => {
    if (!token) {
      toast({ title: "Authentication Error", description: "You must be logged in to delete items.", variant: "destructive" });
      return;
    }
    // Optional: Add a confirmation dialog here if desired
    // For example, using window.confirm or a custom dialog component
    // if (!window.confirm("Are you sure you want to delete this item? This action cannot be undone.")) {
    //   return;
    // }

    try {
      await apiClient(`/wardrobe/items/${itemId}`, {
        method: 'DELETE',
      });
      setItems(prevItems => prevItems.filter(item => item.id !== itemId));
      toast({ title: "Success", description: "Item deleted successfully." });
    } catch (err: any) {
      toast({ title: "Error", description: err.message || "Could not delete item.", variant: "destructive" });
    }
  };

  // Handle Create Outfit
  const handleCreateOutfit = async (outfitData: OutfitCreate) => {
    if (!token) {
      toast({ title: "Authentication Error", description: "You must be logged in to create outfits.", variant: "destructive" });
      return;
    }
    try {
      const newOutfit = await apiClient('/outfits/', {
        method: 'POST',
        body: outfitData,
      });
      toast({ title: "Success", description: `Outfit "${newOutfit.name}" created successfully.` });
      setIsCreateOutfitOpen(false);
      // Optionally, if OutfitOrganizer is also managed here or needs refresh:
      // fetchOutfits(); // Assuming fetchOutfits exists if WardrobeManager also lists outfits
    } catch (err: any) {
      toast({ title: "Error", description: err.message || "Could not create outfit.", variant: "destructive" });
    }
  };

  const filteredItems = items.filter(item => { // Changed from wardrobeItems to items
    const matchesSearch = item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.brand.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (item.tags && item.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase())));
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
    // const matchesSeason = selectedSeason === 'all' || item.season === selectedSeason;
    // const matchesFavorite = !showFavoritesOnly || item.favorite;
    return matchesSearch && matchesCategory; // && matchesSeason && matchesFavorite;
  });

  const categories = ['all', ...Array.from(new Set(items.map(item => item.category)))]; // Changed from wardrobeItems

  // Updated toggleFavorite to use handleUpdateItem
  const toggleFavorite = (id: string, currentFavoriteStatus: boolean) => {
    handleUpdateItem(id, { favorite: !currentFavoriteStatus });
  };

  const openEditModal = (item: WardrobeItem) => {
    setEditingItem(item);
    setIsEditModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-owis-cream via-white to-owis-mint p-2 sm:p-4 lg:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header - Responsive */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6 lg:mb-8">
          <div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-owis-forest to-owis-sage bg-clip-text text-transparent">
              My Wardrobe
            </h1>
            <p className="text-owis-charcoal/70 mt-1 text-sm sm:text-base">
              Manage your fashion collection
            </p>
          </div>
          <div className="flex flex-wrap gap-2 w-full sm:w-auto">
            <Button 
              onClick={() => setIsAddModalOpen(true)}
              className="flex-1 sm:flex-none bg-gradient-to-r from-owis-gold to-owis-bronze hover:from-owis-gold-dark hover:to-owis-bronze text-owis-forest"
            >
              <Plus size={16} className="mr-2" />
              <span className="hidden xs:inline">Add Item</span>
              <span className="xs:hidden">Add</span>
            </Button>
            <Button 
              onClick={() => setIsCreateOutfitOpen(true)}
              variant="outline"
              className="flex-1 sm:flex-none border-owis-forest text-owis-forest hover:bg-owis-forest hover:text-white"
            >
              <Star size={16} className="mr-2" />
              <span className="hidden xs:inline">Create Outfit</span>
              <span className="xs:hidden">Outfit</span>
            </Button>
            <Button 
              onClick={() => setIsPlanWeekOpen(true)}
              variant="outline"
              className="flex-1 sm:flex-none border-owis-sage text-owis-sage hover:bg-owis-sage hover:text-white"
            >
              <Calendar size={16} className="mr-2" />
              <span className="hidden xs:inline">Plan Week</span>
              <span className="xs:hidden">Plan</span>
            </Button>
            <Button 
              onClick={() => setShowSavedPlans(true)}
              variant="outline"
              className="flex-1 sm:flex-none border-owis-gold text-owis-gold hover:bg-owis-gold hover:text-owis-forest"
            >
              <Calendar size={16} className="mr-2" />
              <span className="hidden sm:inline">Saved Plans</span>
              <span className="sm:hidden">Plans</span>
            </Button>
          </div>
        </div>

        {/* New Occasion & Style Tools */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
          <Button 
            onClick={() => setIsOccasionPlannerOpen(true)}
            className="bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white"
          >
            <Users size={16} className="mr-2" />
            <span className="hidden sm:inline">Occasion Planner</span>
            <span className="sm:hidden">Occasions</span>
          </Button>
          <Button 
            onClick={() => setIsStyleHistoryOpen(true)}
            variant="outline"
            className="border-blue-500 text-blue-500 hover:bg-blue-500 hover:text-white"
          >
            <History size={16} className="mr-2" />
            <span className="hidden sm:inline">Style History</span>
            <span className="sm:hidden">History</span>
          </Button>
          <Button 
            onClick={() => setIsOutfitOrganizerOpen(true)}
            variant="outline"
            className="border-green-500 text-green-500 hover:bg-green-500 hover:text-white"
          >
            <Grid size={16} className="mr-2" />
            <span className="hidden sm:inline">Outfit Organizer</span>
            <span className="sm:hidden">Organize</span>
          </Button>
        </div>

        {/* Filters - Responsive */}
        <div className="flex flex-col lg:flex-row gap-4 mb-6">
          <div className="flex-1">
            {/* TODO: Add selectors for season, favorites if implemented */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-owis-charcoal/40" size={20} />
              <Input
                placeholder="Search items by name, brand, tags..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-white/80 border-owis-sage/30 focus:border-owis-gold"
                disabled={isLoading || !!error}
              />
            </div>
          </div>
          
          <div className="flex flex-wrap gap-2">
            {categories.map(category => (
              <Button
                key={category}
                variant={selectedCategory === category ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedCategory(category)}
                className={selectedCategory === category 
                  ? "bg-owis-gold text-owis-forest hover:bg-owis-gold-dark" 
                  : "border-owis-sage/30 text-owis-sage hover:bg-owis-sage hover:text-white"
                }
                disabled={isLoading || !!error}
              >
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </Button>
            ))}
          </div>

          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setViewMode('grid')}
              className={viewMode === 'grid' ? "bg-owis-sage text-white" : "border-owis-sage/30 text-owis-sage"}
              disabled={isLoading || !!error}
            >
              <Grid size={16} />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setViewMode('list')}
              className={viewMode === 'list' ? "bg-owis-sage text-white" : "border-owis-sage/30 text-owis-sage"}
              disabled={isLoading || !!error}
            >
              <List size={16} />
            </Button>
          </div>
        </div>

        {/* Loading and Error States */}
        {isLoading && (
          <div className="flex justify-center items-center py-12">
            <LoadingSpinner size="lg" />
            <p className="ml-4 text-owis-charcoal/70">Loading wardrobe items...</p>
          </div>
        )}

        {!isLoading && error && (
          <div className="text-center py-12 bg-red-50 dark:bg-red-900/20 p-6 rounded-lg shadow-md">
            <AlertTriangle size={48} className="text-red-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-red-700 dark:text-red-400 mb-2">Oops! Something went wrong.</h3>
            <p className="text-red-600 dark:text-red-300">{error}</p>
            <Button onClick={fetchItems} className="mt-4">Try Again</Button>
          </div>
        )}

        {/* Items Grid/List - Extremely Responsive */}
        {!isLoading && !error && filteredItems.length > 0 && (
          <div className={
            viewMode === 'grid'
              ? "grid grid-cols-1 xs:grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-7 gap-3 sm:gap-4 lg:gap-6"
              : "space-y-3 sm:space-y-4"
          }>
            {filteredItems.map((item) => (
              <Card
                key={item.id}
                className={`group hover:shadow-lg transition-all duration-300 bg-white/90 backdrop-blur-sm border-white/30 hover:border-owis-gold/50 ${
                  viewMode === 'list' ? 'flex flex-row' : ''
                }`}
              >
                <div className={viewMode === 'list' ? 'w-20 sm:w-24 lg:w-32 flex-shrink-0' : 'aspect-square'}>
                  <img
                    src={item.image_url ? `http://localhost:8000${item.image_url}` : "https://via.placeholder.com/150?text=No+Image"} // Added base URL and placeholder
                    alt={item.name}
                    className="w-full h-full object-cover rounded-t-lg group-hover:scale-105 transition-transform duration-300"
                  />
                </div>

                <CardContent className={`p-3 sm:p-4 ${viewMode === 'list' ? 'flex-1 flex flex-col justify-between' : ''}`}>
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-owis-charcoal text-sm sm:text-base truncate">
                        {item.name}
                      </h3>
                      <p className="text-xs sm:text-sm text-owis-charcoal/60 truncate">
                        {item.brand}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon" // Changed for consistency with other action buttons
                      onClick={() => toggleFavorite(item.id, item.favorite)}
                      className="ml-2 p-1 h-auto w-auto" // Adjusted padding and size
                      disabled={isLoading}
                    >
                      <Heart
                        size={16}
                        className={item.favorite ? "fill-red-500 text-red-500" : "text-owis-charcoal/40 hover:text-red-400"}
                      />
                    </Button>
                  </div>

                  <div className="space-y-2">
                    <div className="flex flex-wrap gap-1">
                      <Badge variant="secondary" className="text-xs bg-owis-sage/10 text-owis-sage border-owis-sage/20">
                        {item.category}
                      </Badge>
                      <Badge variant="outline" className="text-xs border-owis-gold/30 text-owis-gold">
                        ${item.price.toFixed(2)}
                      </Badge>
                    </div>

                    {viewMode === 'grid' && (
                      <>
                        <div className="text-xs text-owis-charcoal/50 space-y-1 pt-1">
                          <p>Worn: {item.times_worn} times</p>
                          <p>Size: {item.size}</p>
                        </div>
                        <div className="flex justify-end gap-1 pt-2">
                          <Button variant="outline" size="icon" className="h-7 w-7" onClick={() => openEditModal(item)} disabled={isLoading}>
                            <Edit size={12} />
                          </Button>
                          <Button variant="destructiveOutline" size="icon" className="h-7 w-7" onClick={() => handleDeleteItem(item.id)} disabled={isLoading}>
                            <Trash2 size={12} />
                          </Button>
                        </div>
                      </>
                    )}

                    {viewMode === 'list' && (
                      <>
                        <div className="grid grid-cols-2 gap-2 text-xs text-owis-charcoal/60">
                          <p>Size: {item.size}</p>
                          <p>Worn: {item.times_worn}x</p>
                          <p>Material: {item.material}</p>
                          <p>Season: {item.season}</p>
                        </div>
                        <div className="flex justify-end gap-1 pt-2">
                           <Button variant="outline" size="icon" className="h-7 w-7" onClick={() => openEditModal(item)} disabled={isLoading}>
                            <Edit size={12} />
                          </Button>
                          <Button variant="destructiveOutline" size="icon" className="h-7 w-7" onClick={() => handleDeleteItem(item.id)} disabled={isLoading}>
                            <Trash2 size={12} />
                          </Button>
                        </div>
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {!isLoading && !error && filteredItems.length === 0 && (
          <div className="text-center py-12">
            <p className="text-owis-charcoal/60 text-lg">
              {items.length === 0 && !searchTerm && selectedCategory === 'all'
                ? "Your wardrobe is empty. Add some items to get started!"
                : "No items found matching your criteria."}
            </p>
          </div>
        )}
      </div>

      {/* Modals */}
      <AddItemModal 
        isOpen={isAddModalOpen} 
        onClose={() => setIsAddModalOpen(false)}
        onSave={handleSaveItem}
      />
      <EditItemModal
        isOpen={isEditModalOpen}
        onClose={() => { setIsEditModalOpen(false); setEditingItem(null); }}
        item={editingItem}
        onUpdate={handleUpdateItem}
      />

      <CreateOutfitModal
        isOpen={isCreateOutfitOpen}
        onClose={() => setIsCreateOutfitOpen(false)}
        wardrobeItems={items}
        onSave={handleCreateOutfit} // Passed handleCreateOutfit
      />

      <PlanWeekModal
        isOpen={isPlanWeekOpen}
        onClose={() => setIsPlanWeekOpen(false)}
      />

      <SavedWeeklyPlans
        isOpen={showSavedPlans}
        onClose={() => setShowSavedPlans(false)}
      />

      <OccasionPlanner
        isOpen={isOccasionPlannerOpen}
        onClose={() => setIsOccasionPlannerOpen(false)}
      />

      <StyleHistory
        isOpen={isStyleHistoryOpen}
        onClose={() => setIsStyleHistoryOpen(false)}
      />

      <OutfitOrganizer
        isOpen={isOutfitOrganizerOpen}
        onClose={() => setIsOutfitOrganizerOpen(false)}
        wardrobeItemsForOutfitCreation={items} // Pass wardrobe items here
      />
    </div>
  );
};

export default WardrobeManager;
