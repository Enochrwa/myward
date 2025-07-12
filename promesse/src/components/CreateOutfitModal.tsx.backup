
import React, { useState, useEffect } from 'react'; // Added useEffect
import { X, Plus, Save, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast'; // Corrected path
import { WardrobeItem } from './WardrobeManager'; // Import full WardrobeItem type
import { OutfitCreate } from '../types/outfitTypes'; // Import OutfitCreate type

export interface CreateOutfitModalProps {
  isOpen: boolean;
  onClose: () => void;
  wardrobeItems: WardrobeItem[];
  onSave: (outfitData: OutfitCreate) => void; // Added onSave prop
}

const CreateOutfitModal = ({ isOpen, onClose, wardrobeItems, onSave }: CreateOutfitModalProps) => {
  const [outfitName, setOutfitName] = useState('');
  const [selectedItems, setSelectedItems] = useState<WardrobeItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState(''); // Added for filtering available items
  const { toast } = useToast();


  // Reset state when modal opens/closes or items change (e.g. parent re-fetches)
  useEffect(() => {
    if (isOpen) {
      setOutfitName('');
      setSelectedItems([]);
      setSelectedCategory('all');
      setSearchTerm('');
    }
  }, [isOpen]);


  const categories = ['all', ...Array.from(new Set(wardrobeItems.map(item => item.category)))];

  const filteredItems = wardrobeItems.filter(item => {
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
    const matchesSearch = !searchTerm ||
                          item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          item.brand.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const toggleItemSelection = (item: WardrobeItem) => {
    setSelectedItems(prev => {
      const isSelected = prev.some(selected => selected.id === item.id);
      if (isSelected) {
        return prev.filter(selected => selected.id !== item.id);
      } else {
        return [...prev, item];
      }
    });
  };

  const handleSaveOutfit = () => {
    if (!outfitName.trim() || selectedItems.length === 0) {
      toast({
        title: "Missing Information",
        description: "Please provide an outfit name and select at least one item.",
        variant: "destructive",
      });
      return;
    }

    const outfitToSave: OutfitCreate = {
      name: outfitName.trim(),
      item_ids: selectedItems.map(item => item.id), // item.id is now string from WardrobeItem
      tags: [], // Placeholder for now, UI can be added
      // image_url: '', // Placeholder for now, UI can be added for this
    };
    
    onSave(outfitToSave); // Call the onSave prop passed from WardrobeManager
    // Parent (WardrobeManager) will handle closing the modal and showing toast on success/failure of API call.
    // Resetting state here might be premature if API call fails, but for now, let's keep it simple.
    // If parent needs to control reset, these lines can be removed or made conditional.
    // setOutfitName('');
    // setSelectedItems([]);
    // onClose(); // Parent will call onClose.
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-2 xs:p-3 sm:p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl xs:rounded-3xl w-full max-w-xs xs:max-w-sm sm:max-w-2xl md:max-w-4xl lg:max-w-6xl max-h-[95vh] xs:max-h-[90vh] overflow-y-auto">
      <div className="bg-white dark:bg-gray-800 rounded-2xl xs:rounded-3xl w-full max-w-xs xs:max-w-sm sm:max-w-2xl md:max-w-4xl lg:max-w-6xl max-h-[95vh] xs:max-h-[90vh] flex flex-col"> {/* Added flex flex-col */}
        <div className="p-3 xs:p-4 sm:p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between shrink-0"> {/* Added shrink-0 */}
          <div>
            <h2 className="text-lg xs:text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">Create Outfit</h2>
            <p className="text-xs xs:text-sm text-gray-600 dark:text-gray-400">Select items to create a perfect outfit</p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose} className="p-1 xs:p-2">
            <X size={16} className="xs:w-5 xs:h-5" />
          </Button>
        </div>

        <div className="p-3 xs:p-4 sm:p-6 space-y-4 xs:space-y-6 overflow-y-auto flex-grow"> {/* Added flex-grow and overflow-y-auto */}
          <div>
            <label htmlFor="outfitName" className="block text-xs xs:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 xs:mb-2">
              Outfit Name *
            </label>
            <input
              id="outfitName"
              type="text"
              value={outfitName}
              onChange={(e) => setOutfitName(e.target.value)}
              placeholder="e.g., Summer Date Night, Business Meeting"
              className="w-full p-2 xs:p-3 text-sm xs:text-base border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white h-10 xs:h-11"
            />
          </div>

          {/* TODO: Add UI for outfit tags and image_url if needed */}

          <div className="sticky top-0 bg-white dark:bg-gray-800 py-2 z-10"> {/* Made filter section sticky */}
            <input
                type="text"
                placeholder="Search available items..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full p-2 mb-2 text-sm border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700"
            />
            <div className="flex flex-wrap gap-1 xs:gap-2">
                {categories.map(category => (
                <Button
                    key={category}
                    variant={selectedCategory === category ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSelectedCategory(category)}
                    className={`text-xs xs:text-sm h-8 xs:h-9 px-2 xs:px-3 ${selectedCategory === category
                    ? "bg-owis-gold text-owis-forest"
                    : "border-owis-sage/30 text-owis-sage hover:bg-owis-sage hover:text-white"
                    }`}
                >
                    {category.charAt(0).toUpperCase() + category.slice(1)}
                </Button>
                ))}
            </div>
          </div>


          {selectedItems.length > 0 && (
            <div className="bg-owis-mint/20 dark:bg-owis-mint/10 rounded-lg p-3 xs:p-4">
              <h3 className="font-semibold text-owis-forest dark:text-owis-mint-light mb-2 xs:mb-3 text-sm xs:text-base">Selected Items ({selectedItems.length})</h3>
              <div className="grid grid-cols-3 xs:grid-cols-4 sm:grid-cols-6 lg:grid-cols-8 gap-2 xs:gap-3">
                {selectedItems.map(item => (
                  <div key={item.id} className="relative group">
                    <img
                      src={item.image_url} // Use image_url from WardrobeItem
                      alt={item.name}
                      className="w-full h-16 xs:h-20 object-cover rounded-lg border-2 border-owis-gold"
                    />
                    <Button
                      variant="destructive"
                      size="icon" // Changed to icon
                      onClick={() => toggleItemSelection(item)}
                      className="absolute -top-2 -right-2 w-5 h-5 xs:w-6 xs:h-6 rounded-full p-0 text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <X size={12}/>
                    </Button>
                    <p className="text-xs text-center mt-1 text-owis-charcoal dark:text-owis-cream truncate">{item.name}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2 xs:mb-3 text-sm xs:text-base">Available Items ({filteredItems.length})</h3>
            <div className="grid grid-cols-2 xs:grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-7 2xl:grid-cols-8 gap-2 xs:gap-3 max-h-60 xs:max-h-72 sm:max-h-80 overflow-y-auto"> {/* Adjusted grid and max-h */}
              {filteredItems.map(item => {
                const isSelected = selectedItems.some(selected => selected.id === item.id);
                return (
                  <div 
                    key={item.id} 
                    className={`cursor-pointer rounded-lg border-2 p-1 xs:p-2 transition-all hover:shadow-lg ${
                      isSelected 
                        ? 'border-owis-gold bg-owis-gold/10 dark:bg-owis-gold/20'
                        : 'border-gray-200 dark:border-gray-600 hover:border-owis-sage dark:hover:border-owis-mint'
                    }`}
                    onClick={() => toggleItemSelection(item)}
                  >
                    <img
                      src={item.image_url} // Use image_url from WardrobeItem
                      alt={item.name}
                      className="w-full h-16 xs:h-20 object-cover rounded-lg mb-1 xs:mb-2"
                    />
                    <h4 className="font-medium text-xs text-gray-900 dark:text-white truncate">{item.name}</h4>
                    <p className="text-xs text-gray-600 dark:text-gray-400 truncate">{item.brand}</p>
                    <p className="text-xs text-owis-sage dark:text-owis-mint-light">{item.category}</p>
                  </div>
                );
              })}
             {filteredItems.length === 0 && <p className="col-span-full text-center text-gray-500 dark:text-gray-400 py-4">No items match your search or filter.</p>}
            </div>
          </div>
        </div>

        <div className="p-3 xs:p-4 sm:p-6 border-t border-gray-200 dark:border-gray-700 flex flex-col xs:flex-row gap-2 xs:gap-3 shrink-0"> {/* Added shrink-0 */}
          <Button variant="outline" onClick={onClose} className="flex-1 h-10 xs:h-11 text-sm xs:text-base">
            Cancel
          </Button>
          <Button onClick={handleSaveOutfit} className="flex-1 h-10 xs:h-11 text-sm xs:text-base bg-owis-gold hover:bg-owis-gold-dark text-owis-forest">
            <Save size={14} className="xs:w-4 xs:h-4 mr-1 xs:mr-2" />
            Save Outfit
          </Button>
        </div>
      </div>
      </div>
      </div>
  );
};

export default CreateOutfitModal;
