import React, { useState } from 'react';
import { X, Save, BrainCircuit, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/use-toast';
import { WardrobeItemResponse } from '@/lib/apiClient';
import apiClient from '@/lib/apiClient';
import { OutfitCreate, SmartOutfit } from '../types/outfitTypes';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import LuxuryLoadingSpinner from './LuxuryLoadingSpinner';

export interface CreateOutfitModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (outfitData: OutfitCreate) => void;
  items: WardrobeItemResponse[];
}

const CreateOutfitModal = ({ isOpen, onClose, onSave, items }: CreateOutfitModalProps) => {
  const [name, setName] = useState('');
  const [gender, setGender] = useState('');
  const [occasion, setOccasion] = useState('Everyday');
  const [season, setSeason] = useState('All Season');
  const [selectedItems, setSelectedItems] = useState<number[]>([]);
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('manual');
  const [smartOutfits, setSmartOutfits] = useState<SmartOutfit[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleGenerateSmartOutfits = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.post('/outfits/generate-smart-outfits', {
        wardrobe_items: items,
        preferences: {
          occasion,
          season,
          gender,
        },
      });
      setSmartOutfits(response.data);
    } catch (error) {
      toast({
        title: 'Error generating outfits',
        description: 'Could not generate smart outfits. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = () => {
    if (!name || selectedItems.length === 0 || !gender) {
      toast({
        title: 'Missing Information',
        description: 'Please provide a name, gender and select at least one item.',
        variant: 'destructive',
      });
      return;
    }

    const clothing_parts = items
      .filter(item => selectedItems.includes(item.id))
      .map(item => item.category);

    onSave({
      name,
      gender,
      clothing_items: selectedItems,
      clothing_parts: clothing_parts,
    });

    setName('');
    setGender('');
    setSelectedItems([]);
    onClose();
  };

  const handleItemToggle = (itemId: number) => {
    setSelectedItems(prev =>
      prev.includes(itemId) ? prev.filter(id => id !== itemId) : [...prev, itemId]
    );
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg w-full max-w-4xl max-h-[90vh] flex flex-col">
        <div className="p-4 border-b flex items-center justify-between">
          <h2 className="text-xl font-bold">Create Outfit</h2>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X size={20} />
          </Button>
        </div>

        <div className="p-4 flex-grow overflow-y-auto">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="manual">Manual</TabsTrigger>
              <TabsTrigger value="smart">
                <BrainCircuit size={16} className="mr-2" />
                Smart Outfits
              </TabsTrigger>
            </TabsList>
            <TabsContent value="manual">
              <ScrollArea className="h-[60vh] pr-4">
                <div className="mt-4">
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Outfit Name
                    </label>
                    <Input
                      value={name}
                      onChange={e => setName(e.target.value)}
                      placeholder="e.g., Summer Casual"
                    />
                  </div>

                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Gender
                    </label>
                    <Select onValueChange={setGender} value={gender}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select gender" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="male">Male</SelectItem>
                        <SelectItem value="female">Female</SelectItem>
                        <SelectItem value="unisex">Unisex</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold mb-2">Select Items</h3>
                    {Object.entries(items.reduce((acc, item) => {
                      const category = item.category || 'Uncategorized';
                      if (!acc[category]) {
                        acc[category] = [];
                      }
                      acc[category].push(item);
                      return acc;
                    }, {} as Record<string, WardrobeItemResponse[]>)).map(([category, items]) => (
                      <div key={category} className="mb-4">
                        <h4 className="text-md font-semibold mb-2 capitalize">{category}</h4>
                        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                          {items.map(item => (
                            <div
                              key={item.id}
                              className={`cursor-pointer border-2 rounded-lg p-2 ${
                                selectedItems.includes(item.id) ? 'border-blue-500' : 'border-transparent'
                              }`}
                              onClick={() => handleItemToggle(item.id)}
                            >
                              <img src={item.image_url} alt={item.name} className="w-full h-32 object-cover rounded-md mb-2" />
                              <p className="text-sm font-medium truncate">{item.name}</p>
                              <p className="text-xs text-gray-500">{item.category}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </ScrollArea>
            </TabsContent>
            <TabsContent value="smart">
              <div className="mt-4">
                <div className="flex gap-4 mb-4">
                  <Select onValueChange={setOccasion} value={occasion}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select occasion" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Everyday">Everyday</SelectItem>
                      <SelectItem value="Work">Work</SelectItem>
                      <SelectItem value="Party">Party</SelectItem>
                      <SelectItem value="Date">Date</SelectItem>
                      <SelectItem value="Casual">Casual</SelectItem>
                      <SelectItem value="Formal">Formal</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select onValueChange={setSeason} value={season}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select season" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="All Season">All Season</SelectItem>
                      <SelectItem value="Spring">Spring</SelectItem>
                      <SelectItem value="Summer">Summer</SelectItem>
                      <SelectItem value="Fall">Fall</SelectItem>
                      <SelectItem value="Winter">Winter</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button onClick={handleGenerateSmartOutfits} disabled={isLoading}>
                    <Sparkles size={16} className="mr-2" />
                    {isLoading ? 'Generating...' : 'Generate Outfits'}
                  </Button>
                </div>

                {isLoading ? (
                  <div className="flex justify-center items-center h-64">
                    <LuxuryLoadingSpinner />
                  </div>
                ) : (
                  <ScrollArea className="h-[55vh] pr-4">
                    {smartOutfits.length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {smartOutfits.map((outfit, index) => (
                          <div key={index} className="border rounded-lg p-4">
                            <h4 className="font-semibold">{outfit.description}</h4>
                            <p className="text-sm text-gray-500 mb-2">Score: {outfit.score.toFixed(2)}</p>
                            <div className="flex flex-wrap gap-2">
                              {outfit.items.map(item => (
                                <img
                                  key={item.id}
                                  src={item.image_url}
                                  alt={item.name}
                                  className="w-16 h-16 object-cover rounded-md"
                                />
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p>No smart outfits generated yet. Select preferences and click "Generate Outfits".</p>
                    )}
                  </ScrollArea>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </div>

        <div className="p-4 border-t flex justify-end gap-2">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSave}>
            <Save size={16} className="mr-2" />
            Save Outfit
          </Button>
        </div>
      </div>
    </div>
  );
};

export default CreateOutfitModal;
