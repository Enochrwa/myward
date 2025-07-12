import React, { useState, useEffect, useCallback } from 'react'; // Added useEffect, useCallback
import { Plus, Search, Filter, Grid, List, Heart, Star, Calendar, MoreVertical, Edit, Trash2, Clock, History, Users, AlertTriangle, Sparkles, Palette, Target } from 'lucide-react'; // Added ML icons
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import AddItemModal from './AddItemModal';
import EditItemModal from './EditItemModal'; // Added EditItemModal import
import apiClient, { addItem, updateItem, addItemWithML } from '@/lib/apiClient'; // Added ML functions
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
import MLAnalysisComponent from './MLAnalysisComponent'; // Added ML Analysis
import SmartRecommendationsComponent from './SmartRecommendationsComponent'; // Added Smart Recommendations
import SimilarItemsFinderComponent from './SimilarItemsFinderComponent'; // Added Similar Items Finder

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
  favorite?: boolean; // Added for consistency with backend and apiClient
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

  const VITE_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string) || '';

  // Fetch Items Function
  const fetchItems = useCallback(async () => {
    // if (!token) { // Do not fetch if user is not logged in
    //   setIsLoading(false);
    //   setError("Please login to view your wardrobe.");
    //   setItems([]);
    //   return;
    // }
    // setIsLoading(true);
    // setError(null);
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
  }, [searchTerm, selectedCategory]); // Add selectedSeason, showFavoritesOnly if filters implemented

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  // Handle Save Item (for AddItemModal)
  // Updated to accept imageFile and use the new apiClient.addItem
  const handleSaveItem = async (newItemData: Omit<WardrobeItemCreate, 'image_url'>, imageFile?: File) => {
    // if (!token) {
    //   toast({ title: "Authentication Error", description: "You must be logged in to add items.", variant: "destructive" });
    //   console.error("[WardrobeManager.handleSaveItem] Auth token missing.");
    //   return;
    // }
    // console.log("[WardrobeManager.handleSaveItem] Attempting to save item. Data:", newItemData, "Image file:", imageFile?.name);
    try {
      // Use the new addItem function from apiClient which handles FormData
      const savedItem = await addItem(newItemData, imageFile);
      console.log("[WardrobeManager.handleSaveItem] Item saved successfully by API. Response:", savedItem);

      fetchItems(); // Re-fetch to get the latest list
      setIsAddModalOpen(false);
      toast({ title: "Success", description: `${savedItem.name} added to your wardrobe.` });
    } catch (err: any) {
      console.error("[WardrobeManager.handleSaveItem] Failed to save item. Raw error object:", err);
      let errorMessage = "Could not save item. Please try again.";
      if (err.message) {
        errorMessage = err.message;
      }
      // Attempt to get more specific error details if it's an API error
      // This depends on how apiClient structures errors. Assuming it might have a 'detail' or 'data' field from the generic client.
      // The generic apiClient throws an error where error.message is already populated with detail or statusText.
      // So, err.message should be prioritized.
      
      // If err.message is generic like "Failed to fetch", check if the error object itself has more details.
      // This is heuristic, actual structure depends on how fetch errors are wrapped by apiClient or browser.
      if (err.message === "Failed to fetch" && err.cause) { // Standard way to check for underlying cause in modern fetch
        errorMessage = `Network error or server unreachable: ${err.cause}`;
      } else if (err.detail) { // Custom detail field, as seen in FastAPI
        errorMessage = err.detail;
      } else if (err.response && err.response.data && err.response.data.detail) { // Axios-like error structure
        errorMessage = err.response.data.detail;
      }
      // Ensure err.message itself is used if it's more specific than the default.
      // The initial `if (err.message)` already covers this. The toast will use `err.message` if available.

      console.error("[WardrobeManager.handleSaveItem] Displaying error to user:", errorMessage);
      // The existing toast already uses err.message, which should be good if apiClient populates it well.
      // Let's ensure the toast uses the potentially more detailed errorMessage we constructed.
      toast({ title: "Error Saving Item", description: errorMessage, variant: "destructive" });
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
    // if (!token) {
    //   toast({ title: "Authentication Error", description: "You must be logged in to update items.", variant: "destructive" });
    //   return;
    // }

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
    // if (!token) {
    //   toast({ title: "Authentication Error", description: "You must be logged in to delete items.", variant: "destructive" });
    //   return;
    // }
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
    // if (!token) {
    //   toast({ title: "Authentication Error", description: "You must be logged in to create outfits.", variant: "destructive" });
    //   console.error("[WardrobeManager.handleCreateOutfit] Auth token missing.");
    //   return;
    // }

    // Ensure item_ids are numbers, as backend expects List[int]
    // Assuming outfitData.item_ids might be string[] from the modal
    const processedOutfitData = {
      ...outfitData,
      item_ids: outfitData.item_ids.map(id => parseInt(id, 10)).filter(id => !isNaN(id)),
    };
    console.log("[WardrobeManager.handleCreateOutfit] Original outfitData:", outfitData);
    console.log("[WardrobeManager.handleCreateOutfit] Processed outfitData for API:", processedOutfitData);


    try {
      const newOutfit = await apiClient('/outfits/', {
        method: 'POST',
        body: processedOutfitData, // Send the processed data
      });
      console.log("[WardrobeManager.handleCreateOutfit] Outfit created successfully by API. Response:", newOutfit);
      toast({ title: "Success", description: `Outfit "${newOutfit.name}" created successfully.` });
      setIsCreateOutfitOpen(false);
      // Optionally, if OutfitOrganizer is also managed here or needs refresh:
      // fetchOutfits(); // Assuming fetchOutfits exists if WardrobeManager also lists outfits
    } catch (err: any) {
      console.error("[WardrobeManager.handleCreateOutfit] Failed to create outfit. Raw error object:", err);
      let errorMessage = "Could not create outfit. Please try again.";
      if (err.message) {
        errorMessage = err.message;
      }
      if (err.detail) {
        errorMessage = err.detail;
      } else if (err.data && err.data.detail) {
        errorMessage = err.data.detail;
      }
      console.error("[WardrobeManager.handleCreateOutfit] Displaying error to user:", errorMessage);
      toast({ title: "Error Creating Outfit", description: errorMessage, variant: "destructive" });
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
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-owis-charcoal">
                My Wardrobe
              </h1>
              <p className="text-owis-charcoal/70 mt-1 text-sm sm:text-base">
                Manage your fashion collection with AI-powered insights
              </p>
            </div>
            <div className="flex flex-wrap gap-2 w-full sm:w-auto">
              <Button 
                onClick={() => setIsAddModalOpen(true)}
                className="flex-1 sm:flex-none bg-gradient-to-r from-owis-purple to-owis-bronze hover:from-owis-purple-dark hover:to-owis-bronze text-owis-forest"
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
            </div>
          </div>

          {/* Main Content with Tabs */}
          <Tabs defaultValue="wardrobe" className="w-full">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="wardrobe">My Items</TabsTrigger>
              <TabsTrigger value="ml-analysis">
                <Sparkles className="h-4 w-4 mr-1" />
                AI Analysis
              </TabsTrigger>
              <TabsTrigger value="recommendations">
                <Target className="h-4 w-4 mr-1" />
                Smart Outfits
              </TabsTrigger>
              <TabsTrigger value="similar-items">
                <Palette className="h-4 w-4 mr-1" />
                Find Similar
              </TabsTrigger>
              <TabsTrigger value="tools">Tools</TabsTrigger>
            </TabsList>

            <TabsContent value="wardrobe" className="space-y-6">
              {/* Search and Filter */}
              <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
                <div className="relative flex-1 w-full">
                  <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-owis-charcoal/40" />
                  <Input
                    placeholder="Search your wardrobe..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 border-owis-sage/30 focus:border-owis-sage"
                    disabled={isLoading || !!error}
                  />
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="border-owis-sage/30 text-owis-sage hover:bg-owis-sage hover:text-white w-full sm:w-auto"
                  disabled={isLoading || !!error}
                >
                  <Filter size={16} className="mr-2" />
                  Filters
                </Button>
              </div>

              {/* Category Filter */}
              <div className="flex flex-wrap gap-2 justify-between items-center">
                <div className="flex flex-wrap gap-2">
                  {categories.map((category) => (
                    <Button
                      key={category}
                      variant="outline"
                      size="sm"
                      className={
                        selectedCategory === category
                          ? "bg-owis-sage text-white border-owis-sage"
                          : "border-owis-sage/30 text-owis-sage hover:bg-owis-sage hover:text-white"
                      }
                      onClick={() => setSelectedCategory(category)}
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

              {/* Items Grid/List */}
              {!isLoading && !error && filteredItems.length > 0 && (
                <div className={
                  viewMode === 'grid'
                    ? "grid grid-cols-1 xs:grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4"
                    : "space-y-4"
                }>
                  {filteredItems.map((item) => (
                    <Card key={item.id} className="overflow-hidden hover:shadow-lg transition-shadow duration-200 border-owis-sage/20">
                      <CardContent className="p-4">
                        <div className="space-y-3">
                          {item.image_url && (
                            <div className="aspect-square overflow-hidden rounded-md bg-owis-sage/5">
                              <img
                                src={item.image_url}
                                alt={item.name}
                                className="w-full h-full object-cover hover:scale-105 transition-transform duration-200"
                              />
                            </div>
                          )}

                          <div className="space-y-2">
                            <div className="flex items-start justify-between">
                              <h3 className="font-semibold text-owis-charcoal text-sm leading-tight line-clamp-2">
                                {item.name}
                              </h3>
                              {item.favorite && (
                                <Heart size={14} className="text-red-500 fill-current flex-shrink-0 ml-1" />
                              )}
                            </div>

                            <div className="flex flex-wrap gap-1">
                              <Badge variant="secondary" className="text-xs bg-owis-sage/10 text-owis-sage">
                                {item.category}
                              </Badge>
                              {item.brand && (
                                <Badge variant="outline" className="text-xs border-owis-bronze/30 text-owis-bronze">
                                  {item.brand}
                                </Badge>
                              )}
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
                      : "No items match your current search or filter criteria."}
                  </p>
                </div>
              )}
            </TabsContent>

            <TabsContent value="ml-analysis">
              <MLAnalysisComponent 
                onAnalysisComplete={(results) => {
                  // Handle analysis results if needed
                  console.log('ML Analysis completed:', results);
                }}
              />
            </TabsContent>

            <TabsContent value="recommendations">
              <SmartRecommendationsComponent 
                onOutfitSelect={(outfit) => {
                  // Handle outfit selection
                  console.log('Outfit selected:', outfit);
                }}
              />
            </TabsContent>

            <TabsContent value="similar-items">
              <SimilarItemsFinderComponent 
                wardrobeItems={items.map(item => ({
                  id: parseInt(item.id),
                  name: item.name,
                  category: item.category,
                  brand: item.brand,
                  image_url: item.image_url,
                  dominant_color_name: item.color
                }))}
                onItemSelect={(item) => {
                  // Handle similar item selection
                  console.log('Similar item selected:', item);
                }}
              />
            </TabsContent>

            <TabsContent value="tools" className="space-y-6">
              {/* Tools content */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Button 
                  onClick={() => setIsOccasionPlannerOpen(true)}
                  className="bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white"
                >
                  <Calendar size={16} className="mr-2" />
                  Occasion Planner
                </Button>
                <Button 
                  onClick={() => setIsStyleHistoryOpen(true)}
                  className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white"
                >
                  <History size={16} className="mr-2" />
                  Style History
                </Button>
                <Button 
                  onClick={() => setIsOutfitOrganizerOpen(true)}
                  className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white"
                >
                  <Users size={16} className="mr-2" />
                  Outfit Organizer
                </Button>
              </div>
              
              <div className="flex flex-wrap gap-2">
                <Button 
                  onClick={() => setIsPlanWeekOpen(true)}
                  variant="outline"
                  className="border-owis-sage text-owis-sage hover:bg-owis-sage hover:text-white"
                >
                  <Calendar size={16} className="mr-2" />
                  Plan Week
                </Button>
                <Button 
                  onClick={() => setShowSavedPlans(true)}
                  variant="outline"
                  className="border-owis-purple text-owis-purple hover:bg-owis-purple hover:text-owis-forest"
                >
                  <Calendar size={16} className="mr-2" />
                  Saved Plans
                </Button>
              </div>
            </TabsContent>
          </Tabs>
        </div>
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