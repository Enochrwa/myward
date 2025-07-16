import React, { useState, useEffect, useCallback } from 'react';
import apiClient from '@/lib/apiClient';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from "@/components/ui/use-toast";
import LoadingSpinner from '@/components/ui/loading';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Plus, Edit, Trash2 } from 'lucide-react';
import CreateOutfitModal from './CreateOutfitModal';
import { OutfitCreate } from '../types/outfitTypes';
import { WardrobeItem } from './WardrobeManager';

export interface Outfit {
  id: number;
  name: string;
  description?: string;
  season?: string;
  image_url?: string;
  tags?: string[];
  item_ids: number[];
}

const OutfitManager = () => {
  const { token } = useAuth();
  const { toast } = useToast();
  const [outfits, setOutfits] = useState<Outfit[]>([]);
  const [wardrobeItems, setWardrobeItems] = useState<WardrobeItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreateModalOpen, setCreateModalOpen] = useState(false);
  const [isEditModalOpen, setEditModalOpen] = useState(false);
  const [editingOutfit, setEditingOutfit] = useState<Outfit | null>(null);

  const fetchOutfits = useCallback(async () => {
    // if (!token) {
    //   setIsLoading(false);
    //   setError("Please login to view your outfits.");
    //   setOutfits([]);
    //   return;
    // }
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiClient('/outfit/outfits/');
      setOutfits(data || []);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch outfits.');
      setOutfits([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchWardrobeItems = useCallback(async () => {
    // if (!token) return;
    try {
      const data = await apiClient('/wardrobe/wardrobe-items/');
      setWardrobeItems(data || []);
    } catch (err: any) {
      toast({
        title: "Error",
        description: "Could not fetch wardrobe items.",
        variant: "destructive",
      });
    }
  }, [ toast]);

  useEffect(() => {
    fetchOutfits();
    fetchWardrobeItems();
  }, [fetchOutfits, fetchWardrobeItems]);

  const handleCreateOutfit = async (outfitData: OutfitCreate) => {
    try {
      const newOutfit = await apiClient('/outfit/outfits/', {
        method: 'POST',
        body: outfitData,
      });
      fetchOutfits();
      setCreateModalOpen(false);
      toast({ title: "Success", description: "Outfit created." });
    } catch (err: any) {
      toast({ title: "Error", description: err.message, variant: "destructive" });
    }
  };

  const handleUpdateOutfit = async (outfitData: OutfitCreate) => {
    if (!editingOutfit) return;
    try {
      const updatedOutfit = await apiClient(`/outfit/outfits/${editingOutfit.id}`, {
        method: 'PUT',
        body: outfitData,
      });
      fetchOutfits();
      setEditModalOpen(false);
      setEditingOutfit(null);
      toast({ title: "Success", description: "Outfit updated." });
    } catch (err: any) {
      toast({ title: "Error", description: err.message, variant: "destructive" });
    }
  };

  const handleDeleteOutfit = async (outfitId: number) => {
    try {
      await apiClient(`/outfit/outfits/${outfitId}`, { method: 'DELETE' });
      setOutfits((prev) => prev.filter((o) => o.id !== outfitId));
      toast({ title: "Success", description: "Outfit deleted." });
    } catch (err: any) {
      toast({ title: "Error", description: err.message, variant: "destructive" });
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return <div className="text-red-500 text-center">{error}</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">My Outfits</h1>
        <Button onClick={() => setCreateModalOpen(true)}>
          <Plus size={16} className="mr-2" />
          Create Outfit
        </Button>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {outfits.map((outfit) => {
          const itemsInOutfit = outfit.item_ids.map(id => wardrobeItems.find(item => item.id === id)).filter(Boolean) as WardrobeItem[];
          return (
            <Card key={outfit.id}>
              <CardHeader>
                <CardTitle>{outfit.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {itemsInOutfit.map(item => (
                    <img key={item.id} src={item.image_url} alt={item.name} className="w-16 h-16 object-cover rounded-md" />
                  ))}
                </div>
              </CardContent>
              <CardFooter className="flex justify-end gap-2">
                <Button variant="outline" size="icon" onClick={() => { setEditingOutfit(outfit); setEditModalOpen(true); }}>
                  <Edit size={16} />
                </Button>
                <Button variant="destructive" size="icon" onClick={() => handleDeleteOutfit(outfit.id)}>
                  <Trash2 size={16} />
                </Button>
              </CardFooter>
            </Card>
          )
        })}
      </div>
      <CreateOutfitModal
        isOpen={isCreateModalOpen}
        onClose={() => setCreateModalOpen(false)}
        wardrobeItems={wardrobeItems}
        onSave={handleCreateOutfit}
      />
      {editingOutfit && (
        <CreateOutfitModal
          isOpen={isEditModalOpen}
          onClose={() => { setEditModalOpen(false); setEditingOutfit(null); }}
          wardrobeItems={wardrobeItems}
          onSave={handleUpdateOutfit}
          outfit={editingOutfit}
        />
      )}
    </div>
  );
};

export default OutfitManager;
