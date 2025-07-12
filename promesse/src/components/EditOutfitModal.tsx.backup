import React, { useState, useEffect } from 'react';
import { X, Save } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/use-toast';
import { Outfit, OutfitCreate } from '@/types/outfitTypes';
import { WardrobeItem } from './WardrobeManager'; // Assuming WardrobeItem is exported here

interface EditOutfitModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpdate: (outfitId: string, data: Partial<OutfitCreate>) => void;
  outfitToEdit: Outfit | null;
  allWardrobeItems: WardrobeItem[];
}

const EditOutfitModal = ({ isOpen, onClose, onUpdate, outfitToEdit, allWardrobeItems }: EditOutfitModalProps) => {
  const [outfitName, setOutfitName] = useState('');
  const [selectedItemIds, setSelectedItemIds] = useState<string[]>([]);
  const [tagsInput, setTagsInput] = useState('');
  const [imageUrlInput, setImageUrlInput] = useState('');

  const [itemSearchTerm, setItemSearchTerm] = useState('');
  const [itemCategoryFilter, setItemCategoryFilter] = useState('all');

  const { toast } = useToast();

  useEffect(() => {
    if (outfitToEdit && isOpen) {
      setOutfitName(outfitToEdit.name || '');
      setSelectedItemIds(outfitToEdit.item_ids || []);
      setTagsInput(outfitToEdit.tags?.join(', ') || '');
      setImageUrlInput(outfitToEdit.image_url || '');
      // Reset item filters
      setItemSearchTerm('');
      setItemCategoryFilter('all');
    }
  }, [outfitToEdit, isOpen]);

  const handleItemSelection = (itemId: string) => {
    setSelectedItemIds(prev =>
      prev.includes(itemId) ? prev.filter(id => id !== itemId) : [...prev, itemId]
    );
  };

  const handleSave = () => {
    if (!outfitToEdit) return;
    if (!outfitName.trim()) {
      toast({ title: "Validation Error", description: "Outfit name cannot be empty.", variant: "destructive" });
      return;
    }

    const outfitData: Partial<OutfitCreate> = {
      name: outfitName.trim(),
      item_ids: selectedItemIds,
      tags: tagsInput.split(',').map(tag => tag.trim()).filter(Boolean),
      image_url: imageUrlInput.trim() || undefined,
    };
    onUpdate(outfitToEdit.id, outfitData);
  };

  const availableCategories = ['all', ...Array.from(new Set(allWardrobeItems.map(item => item.category)))];

  const filteredWardrobeItems = allWardrobeItems.filter(item => {
    const matchesCategory = itemCategoryFilter === 'all' || item.category === itemCategoryFilter;
    const matchesSearch = !itemSearchTerm ||
                          item.name.toLowerCase().includes(itemSearchTerm.toLowerCase()) ||
                          item.brand.toLowerCase().includes(itemSearchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });


  if (!isOpen || !outfitToEdit) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-[80] flex items-center justify-center p-4"> {/* Higher z-index */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between shrink-0">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Edit Outfit: {outfitToEdit.name}</h2>
          <Button variant="ghost" size="icon" onClick={onClose} className="p-1">
            <X size={20} />
          </Button>
        </div>

        <div className="p-6 space-y-4 overflow-y-auto flex-grow">
          <div>
            <label htmlFor="editOutfitName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Outfit Name *</label>
            <Input id="editOutfitName" type="text" value={outfitName} onChange={(e) => setOutfitName(e.target.value)} placeholder="e.g., Casual Friday" className="h-10"/>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="editOutfitTags" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Tags (comma-separated)</label>
              <Input id="editOutfitTags" type="text" value={tagsInput} onChange={(e) => setTagsInput(e.target.value)} placeholder="e.g., summer, casual, blue" className="h-10"/>
            </div>
            <div>
              <label htmlFor="editOutfitImageUrl" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Image URL</label>
              <Input id="editOutfitImageUrl" type="text" value={imageUrlInput} onChange={(e) => setImageUrlInput(e.target.value)} placeholder="https://example.com/image.jpg" className="h-10"/>
            </div>
          </div>

          {/* Item Selection Area */}
          <div className="space-y-3 pt-2">
            <h3 className="text-md font-semibold text-gray-800 dark:text-gray-200">Select Items ({selectedItemIds.length})</h3>
            <div className="sticky top-0 bg-white dark:bg-gray-800 py-2 z-10 border-b dark:border-gray-700">
                <Input
                    type="text"
                    placeholder="Search items..."
                    value={itemSearchTerm}
                    onChange={(e) => setItemSearchTerm(e.target.value)}
                    className="w-full mb-2 h-9"
                />
                <div className="flex flex-wrap gap-2">
                    {availableCategories.map(cat => (
                        <Button key={cat} variant={itemCategoryFilter === cat ? "default" : "outline"} size="xs" onClick={() => setItemCategoryFilter(cat)}
                            className={`${itemCategoryFilter === cat ? "bg-owis-gold text-owis-forest" : "border-owis-sage/30 text-owis-sage hover:bg-owis-sage hover:text-white"}`}
                        >
                            {cat}
                        </Button>
                    ))}
                </div>
            </div>

            <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-3 max-h-60 overflow-y-auto pr-2">
              {filteredWardrobeItems.map(item => {
                const isSelected = selectedItemIds.includes(item.id);
                return (
                  <div
                    key={item.id}
                    onClick={() => handleItemSelection(item.id)}
                    className={`cursor-pointer rounded-lg border-2 p-2 transition-all hover:shadow-md ${
                      isSelected ? 'border-owis-gold bg-owis-gold/10 dark:bg-owis-gold/20' : 'border-gray-200 dark:border-gray-600 hover:border-owis-sage dark:hover:border-owis-mint'
                    }`}
                  >
                    <img src={item.image_url || 'https://via.placeholder.com/150?text=No+Image'} alt={item.name} className="w-full h-20 object-cover rounded-md mb-1.5" />
                    <p className="text-xs font-medium text-gray-700 dark:text-gray-200 truncate">{item.name}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{item.brand}</p>
                  </div>
                );
              })}
              {filteredWardrobeItems.length === 0 && <p className="col-span-full text-center text-gray-500 dark:text-gray-400 py-3">No items match filter.</p>}
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3 shrink-0">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={handleSave} className="bg-owis-gold hover:bg-owis-gold-dark text-owis-forest">
            <Save size={16} className="mr-2" />Save Changes
          </Button>
        </div>
      </div>
    </div>
  );
};

export default EditOutfitModal;
