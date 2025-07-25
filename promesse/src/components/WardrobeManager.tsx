import React, { useState, useEffect, useCallback } from 'react';
import { Plus, Search, Filter, Grid, List, Heart, Star, Calendar, Edit, Trash2, AlertTriangle, Sparkles, Palette, Target, UploadCloud, CheckSquare, XSquare, Clock, Shuffle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardTitle, CardFooter, CardHeader } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/hooks/useAuth';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import { Link } from 'react-router-dom';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import AddItemModal from './AddItemModal';
import EditItemModal from './EditItemModal';
import * as apiClient from '@/lib/apiClient';
import { useToast } from "@/components/ui/use-toast";
import LoadingSpinner from '@/components/ui/loading';
import CreateOutfitModal from './CreateOutfitModal';
import { OutfitCreate } from '../types/outfitTypes';
import PlanWeekModal from './PlanWeekModal';
import SavedWeeklyPlans from './SavedWeeklyPlans';
import OccasionPlanner from './OccasionPlanner';
import StyleHistory from './StyleHistory';
import OutfitOrganizer from './OutfitOrganizer';
import MLAnalysisComponent from './MLAnalysisComponent';
import SimilarItemsFinderComponent from './SimilarItemsFinderComponent';
import { WardrobeItemResponse, WardrobeItemCreate, WardrobeItemUpdate, Outfit } from '@/lib/apiClient';
import SingleGridWardrobe from './CategorizedWardrobe';
import OutfitBuilder from './OutfitBuilder';
import SmartOutFits from '@/components/SmartOutFits';
import WeeklyPlanner from './WeeklyPlanner';

const WardrobeManager = () => {
    // const { token } = useAuth();
    const { toast } = useToast();

    const [items, setItems] = useState<WardrobeItemResponse[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [editingItem, setEditingItem] = useState<WardrobeItemResponse | null>(null);
    const [selectedItems, setSelectedItems] = useState<number[]>([]);

    // Modals states
    // const [isCreateOutfitOpen, setIsCreateOutfitOpen] = useState(false);
    const [isPlanWeekOpen, setIsPlanWeekOpen] = useState(false);
    const [showSavedPlans, setShowSavedPlans] = useState(false);
    const [isOccasionPlannerOpen, setIsOccasionPlannerOpen] = useState(false);
    const [isStyleHistoryOpen, setIsStyleHistoryOpen] = useState(false);
    const [isOutfitOrganizerOpen, setIsOutfitOrganizerOpen] = useState(false);
    const [outfit, setOutfit] = useState<Outfit | null>(null);
    const [savedOutfits, setSavedOutfits] = useState<any[]>([]);

    const { user } = useAuth();
    const fetchSavedOutfits = async () => {
        if (!user) return;
        try {
            const outfits = await apiClient.getUserOutfits();
            setSavedOutfits(outfits);
        } catch (err) {
            console.error(err);
        }
    };

    useEffect(() => {
        fetchSavedOutfits();
    }, []);

    const handleSaveOutfit = async (outfitData: any) => {
        try {
            await apiClient.saveOutfit(outfitData);
            fetchSavedOutfits();
        } catch (err: any) {
            console.error(err);
            throw err;
        }
    };

    const handleDeleteOutfit = async (outfitId: string) => {
        try {
            await apiClient.deleteOutfit(outfitId);
            fetchSavedOutfits();
        } catch (err) {
            console.error(err);
        }
    };

    const generateOutfit = useCallback(async () => {
        if (items.length === 0) {
            setError('You need to add items to your wardrobe first.');
            return;
        }
        setIsLoading(true);
        setError(null);
        try {
            const randomItem = items[Math.floor(Math.random() * items.length)];
            const recommendedOutfit = await apiClient.recommendOutfit(randomItem.id);
            setOutfit(recommendedOutfit);
        } catch (err: any) {
            setError(err.message || 'Failed to generate outfit.');
        } finally {
            setIsLoading(false);
        }
    }, [items]);

    const renderOutfit = () => {
        if (!outfit) return null;

        const outfitCategories = {
            outerwear: [] as any[],
            tops: [] as any[],
            bottoms: [] as any[],
            footwear: [] as any[],
            accessories: [] as any[],
        };

        for (const key in outfit) {
            const item = outfit[key as keyof Outfit];
            if (item && typeof item === 'object' && 'category' in item) {
                const category = item.category?.toLowerCase();
                if (category?.includes('coat') || category?.includes('jacket') || category?.includes('blazer') || category?.includes('cardigan')) {
                    outfitCategories.outerwear.push(item);
                } else if (category?.includes('t-shirt') || category?.includes('blouse') || category?.includes('top') || category?.includes('shirt')) {
                    outfitCategories.tops.push(item);
                } else if (category?.includes('pants') || category?.includes('jeans') || category?.includes('skirt') || category?.includes('shorts')) {
                    outfitCategories.bottoms.push(item);
                } else if (category?.includes('shoes') || category?.includes('boots') || category?.includes('sneakers') || category?.includes('sandals')) {
                    outfitCategories.footwear.push(item);
                } else {
                    outfitCategories.accessories.push(item);
                }
            }
        }

        return (
            <Card>
                <CardHeader>
                    <CardTitle>Your Smart Outfit</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    {Object.entries(outfitCategories).map(([category, items]) => (
                        items.length > 0 && (
                            <div key={category}>
                                <h4 className="text-lg font-semibold mb-2 capitalize">{category}</h4>
                                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                                    {items.map((item: any) => (
                                        <Card key={item.id}>
                                            <CardContent className="p-0">
                                                <img src={item.image_url} alt={item.name} className="w-full h-48 object-cover rounded-t-lg" />
                                                <div className="p-4">
                                                    <h5 className="font-semibold">{item.name}</h5>
                                                    <p className="text-sm text-gray-500">{item.category}</p>
                                                </div>
                                            </CardContent>
                                        </Card>
                                    ))}
                                </div>
                            </div>
                        )
                    ))}
                </CardContent>
            </Card>
        );
    };

    const fetchItems = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const params = new URLSearchParams();
            if (searchTerm) params.append('search', searchTerm);
            if (selectedCategory && selectedCategory !== 'all') params.append('category', selectedCategory);
            
            const data = await apiClient.getAllItems(params);
            setItems(data || []);
        } catch (err: any) {
            setError(err.message || 'Failed to fetch wardrobe items.');
            setItems([]);
        } finally {
            setIsLoading(false);
        }
    }, [searchTerm, selectedCategory]);

    useEffect(() => {
        fetchItems();
    }, []);

    const handleSaveItem = async (newItemData: WardrobeItemCreate, imageFile?: File) => {
        try {
            const savedItem = await apiClient.createWardrobeItem(newItemData, imageFile);
            toast({ title: "Success", description: `${savedItem.name} added.` });
            fetchItems();
            setIsAddModalOpen(false);
        } catch (err: any) {
            toast({ title: "Error", description: err.message, variant: "destructive" });
        }
    };

    const handleUpdateItem = async (itemId: number, updatedData: WardrobeItemUpdate, imageFile?: File) => {
        try {
            const updatedItem = await apiClient.updateItem(itemId, updatedData);
            if (imageFile && updatedItem.id) {
                await apiClient.uploadItemImage(updatedItem.id, imageFile);
            }
            toast({ title: "Success", description: "Item updated." });
            fetchItems();
            setIsEditModalOpen(false);
        } catch (err: any) {
            toast({ title: "Error", description: err.message, variant: "destructive" });
        }
    };

    const handleDeleteItem = async (itemId: number) => {
        try {
            await apiClient.deleteItem(itemId);
            toast({ title: "Success", description: "Item deleted." });
            fetchItems();
        } catch (err: any) {
            toast({ title: "Error", description: err.message, variant: "destructive" });
        }
    };

    const handleToggleFavorite = async (item: WardrobeItemResponse) => {
        try {
            await apiClient.toggleFavorite(item.id);
            setItems(items.map(i => i.id === item.id ? { ...i, favorite: !i.favorite } : i));
        } catch (err: any) {
            toast({ title: "Error", description: "Could not update favorite status.", variant: "destructive" });
        }
    };
    
    const handleMarkAsWorn = async (item: WardrobeItemResponse) => {
        try {
            const result = await apiClient.markAsWorn(item.id);
            setItems(items.map(i => i.id === item.id ? { ...i, times_worn: result.times_worn, last_worn: result.last_worn } : i));
            toast({ title: "Success", description: `${item.name} marked as worn.`});
        } catch (err: any) {
            toast({ title: "Error", description: "Could not mark as worn.", variant: "destructive" });
        }
    };

    const handleSelectItem = (itemId: number, isSelected: boolean) => {
        if (isSelected) {
            setSelectedItems([...selectedItems, itemId]);
        } else {
            setSelectedItems(selectedItems.filter(id => id !== itemId));
        }
    };

    const handleBulkDelete = async () => {
        if (selectedItems.length === 0) return;
        try {
            await apiClient.bulkDeleteItems(selectedItems);
            toast({ title: "Success", description: `${selectedItems.length} items deleted.` });
            setSelectedItems([]);
            fetchItems();
        } catch (err: any) {
            toast({ title: "Error", description: "Could not delete items.", variant: "destructive" });
        }
    };

    const openEditModal = (item: WardrobeItemResponse) => {
        setEditingItem(item);
        setIsEditModalOpen(true);
    };

    const filteredItems = items.filter(item => {
        const name = item.name ?? '';
        const brand = item.brand ?? '';
        const tags = Array.isArray(item.tags) ? item.tags : [];
        const matchesSearch = name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                             brand.toLowerCase().includes(searchTerm.toLowerCase()) ||
                             tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
        const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
        return matchesSearch && matchesCategory;
    });

    const categories = ['all', ...Array.from(new Set(items.map(item => item.category as string).filter(c => c)))];
    return (
    <div className="min-h-screen bg-gradient-to-br from-owis-cream via-white to-owis-mint p-2 sm:p-4 lg:p-6">
      <div className="max-w-7xl mx-auto">
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-owis-charcoal">My Wardrobe</h1>
              <p className="text-owis-charcoal/70 mt-1 text-sm sm:text-base">
                Manage your fashion collection with AI-powered insights
              </p>
            </div>
            <div className="flex flex-wrap gap-2 w-full sm:w-auto">
              <Button className="flex-1 sm:flex-none bg-gradient-to-r from-owis-purple to-owis-bronze hover:from-owis-purple-dark hover:to-owis-bronze text-owis-forest">
                
                  <Link to={"/dashboard"}>
                     Add Item
                  </Link>
              </Button>
              {/* <Button onClick={() => setIsCreateOutfitOpen(true)} variant="outline" className="flex-1 sm:flex-none border-owis-forest text-owis-forest hover:bg-owis-forest hover:text-white">
                <Star size={16} className="mr-2" /> Create Outfit
              </Button> */}
              {/* <Button
                onClick={async () => {
                  try {
                    await apiClient.clusterImages();
                    toast({ title: 'Success', description: 'Clustering process started.' });
                  } catch (err: any) {
                    toast({ title: 'Error', description: 'Could not start clustering.', variant: 'destructive' });
                  }
                }}
                variant="outline"
                className="flex-1 sm:flex-none border-owis-forest text-owis-forest hover:bg-owis-forest hover:text-white"
              >
                <Sparkles size={16} className="mr-2" /> Cluster Items
              </Button> */}
            </div>
          </div>

          <Tabs defaultValue="wardrobe" className="w-full">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="wardrobe">My Items</TabsTrigger>
              {/* <TabsTrigger value="ml-analysis"><Sparkles className="h-4 w-4 mr-1" /> AI Analysis</TabsTrigger> */}
              <TabsTrigger value="recommendations"><Target className="h-4 w-4 mr-1" /> Smart Outfits</TabsTrigger>
              <TabsTrigger value="weekly-planner"><Calendar className="h-4 w-4 mr-1" /> Weekly Planner</TabsTrigger>
              {/* <TabsTrigger value="outfit-builder"><Palette className="h-4 w-4 mr-1" /> Outfit Builder</TabsTrigger> */}
              <TabsTrigger value="similar-items"><Palette className="h-4 w-4 mr-1" /> Find Similar</TabsTrigger>
              {/* <TabsTrigger value="tools">Tools</TabsTrigger> */}
            </TabsList>

            <TabsContent value="wardrobe" className="space-y-6">
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
                <Button variant="outline" size="sm" className="border-owis-sage/30 text-owis-sage hover:bg-owis-sage hover:text-white w-full sm:w-auto" disabled={isLoading || !!error}>
                  <Filter size={16} className="mr-2" /> Filters
                </Button>
                 {selectedItems.length > 0 && (
                    <Button variant="destructive" size="sm" onClick={handleBulkDelete} className="w-full sm:w-auto">
                        <Trash2 size={16} className="mr-2" /> Delete ({selectedItems.length})
                    </Button>
                )}
              </div>

              <div className="flex flex-wrap gap-2 justify-between items-center">
                <div className="flex flex-wrap gap-2">
                  {categories.map((category) => (
                    <Button
                      key={category}
                      variant={selectedCategory === category ? "default" : "outline"}
                      size="sm"
                      onClick={() => setSelectedCategory(category)}
                      disabled={isLoading || !!error}
                    >
                      {category.charAt(0).toUpperCase() + category.slice(1)}
                    </Button>
                  ))}
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => setViewMode('grid')} className={viewMode === 'grid' ? "bg-owis-sage text-white" : "border-owis-sage/30 text-owis-sage"} disabled={isLoading || !!error}>
                    <Grid size={16} />
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => setViewMode('list')} className={viewMode === 'list' ? "bg-owis-sage text-white" : "border-owis-sage/30 text-owis-sage"} disabled={isLoading || !!error}>
                    <List size={16} />
                  </Button>
                </div>
              </div>

              {isLoading && <div className="flex justify-center items-center py-12"><LoadingSpinner size="lg" /><p className="ml-4 text-owis-charcoal/70">Loading items...</p></div>}
              {!isLoading && error && (
                <div className="text-center py-12 bg-red-50 p-6 rounded-lg">
                  <AlertTriangle size={48} className="text-red-500 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-red-700">Error</h3>
                  <p className="text-red-600">{error}</p>
                  <Button onClick={fetchItems} className="mt-4">Try Again</Button>
                </div>
              )}

              
              <SingleGridWardrobe/>
              {!isLoading && !error && filteredItems.length === 0 && <div className="text-center py-12"><p>No items found.</p></div>}
            </TabsContent>
            
            {/* Other Tabs Content */}
            {/* <TabsContent value="ml-analysis"><MLAnalysisComponent onAnalysisComplete={() => {}} /></TabsContent> */}
            <TabsContent value="recommendations">
              <SmartOutFits/>
            </TabsContent>
            <TabsContent value="weekly-planner">
              <WeeklyPlanner />
            </TabsContent>
            {/* <TabsContent value="outfit-builder">
              <OutfitBuilder items={items} onSave={handleSaveOutfit} />
            </TabsContent> */}
            <TabsContent value="similar-items"><SimilarItemsFinderComponent/></TabsContent>
            {/* <TabsContent value="tools"><div>Tools placeholder</div></TabsContent> */}
          </Tabs>
        </div>
      </div>

      <AddItemModal isOpen={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} onSave={handleSaveItem} />
      {editingItem && <EditItemModal isOpen={isEditModalOpen} onClose={() => setIsEditModalOpen(false)} item={editingItem} onUpdate={(id, data, file) => handleUpdateItem(id, data, file)} />}
      {/* <CreateOutfitModal isOpen={isCreateOutfitOpen} onClose={() => setIsCreateOutfitOpen(false)} onSave={handleSaveOutfit} items={items} /> */}
    </div>
  );
};

export default WardrobeManager;