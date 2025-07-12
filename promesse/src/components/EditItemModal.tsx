import React, { useState, useEffect } from 'react';
import { X, Save } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/use-toast';
import { WardrobeItem, WardrobeItemCreate } from './WardrobeManager'; // Import interfaces

import { Upload } from 'lucide-react'; // Added Upload icon

export interface EditItemModalProps {
  isOpen: boolean;
  onClose: () => void;
  // Update onUpdate to pass imageFile and removeImage flag
  onUpdate: (itemId: string, updatedData: Partial<Omit<WardrobeItemCreate, 'image_url'>>, imageFile?: File, removeCurrentImage?: boolean) => void;
  item: WardrobeItem | null;
}

const EditItemModal = ({ isOpen, onClose, onUpdate, item }: EditItemModalProps) => {
  const [formData, setFormData] = useState<Partial<Omit<WardrobeItemCreate, 'image_url' | 'tags' | 'price'>> & { tags: string[] | string; price?: number | string; image_url?: string | null }>({});
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [removeCurrentImage, setRemoveCurrentImage] = useState(false);
  const { toast } = useToast();

  const VITE_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string) || '';

  const categories = ['Shirts', 'Pants', 'Dresses', 'Shoes', 'Accessories', 'Jackets', 'Sweaters', 'Other'];
  const seasons = ['Spring', 'Summer', 'Fall', 'Winter', 'All Seasons'];

  useEffect(() => {
    if (item) {
      setFormData({
        name: item.name,
        brand: item.brand,
        category: item.category,
        size: item.size,
        price: item.price,
        material: item.material,
        season: item.season,
        image_url: item.image_url || null, // Keep existing or set to null
        tags: Array.isArray(item.tags) ? item.tags : [], // Ensure tags is an array
        color: item.color || '',
        notes: item.notes || '',
      });
      setImagePreview(item.image_url || null); // Set initial preview
      setImageFile(null); // Reset any selected file
      setRemoveCurrentImage(false); // Reset remove flag
    }
  }, [item]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleTagsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, tags: e.target.value.split(',').map(tag => tag.trim()) }));
  };

  const handlePriceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Allow empty string or valid number input
    if (value === '' || !isNaN(parseFloat(value))) {
      setFormData(prev => ({ ...prev, price: value === '' ? undefined : parseFloat(value) }));
    } else if (value === '-') { // Allow negative sign for typing negative numbers, though price shouldn't be negative
         setFormData(prev => ({ ...prev, price: 0 })); // Or handle as needed
    }
  };


  const handleSave = () => {
    if (!item || !formData.name || !formData.brand || !formData.category) {
      toast({
        title: "Missing Required Fields",
        description: "Name, Brand, and Category are required.",
        variant: "destructive",
      });
      return;
    }

    // Ensure tags are correctly formatted as an array of strings
    // Prepare data for submission
    const { image_url, ...dataToSubmit } = formData; // Exclude image_url from main data if file is handled

    const updatedItemData: Partial<Omit<WardrobeItemCreate, 'image_url'>> = {
      ...dataToSubmit,
      price: typeof formData.price === 'string' ? parseFloat(formData.price) : formData.price,
      tags: Array.isArray(formData.tags) ? formData.tags.filter(Boolean) : (typeof formData.tags === 'string' ? formData.tags.split(',').map(tag => tag.trim()).filter(Boolean) : []),
    };

    // If removeCurrentImage is true, ensure image_url is explicitly set to null in the data sent to backend
    // (if imageFile is not also being uploaded, which would override)
    if (removeCurrentImage && !imageFile) {
        (updatedItemData as any).image_url = null;
    }


    onUpdate(item.id, updatedItemData, imageFile || undefined, removeCurrentImage);
    onClose(); // Consider moving onClose to WardrobeManager after successful update
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setImageFile(file);
      setRemoveCurrentImage(false); // If new file is selected, don't remove existing one based on checkbox
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveImageClick = () => {
    setRemoveCurrentImage(true);
    setImageFile(null);
    setImagePreview(null);
    // Also update formData to reflect that image_url should be null if saved now without new file
    setFormData(prev => ({ ...prev, image_url: null }));
  };


  if (!isOpen || !item) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[60] flex items-center justify-center p-2 xs:p-3 sm:p-4"> {/* Increased z-index */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl xs:rounded-3xl w-full max-w-xs xs:max-w-sm sm:max-w-md md:max-w-lg lg:max-w-2xl max-h-[95vh] xs:max-h-[90vh] overflow-y-auto">
        <div className="p-3 xs:p-4 sm:p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h2 className="text-lg xs:text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">Edit Item</h2>
          <Button variant="ghost" size="sm" onClick={onClose} className="p-1 xs:p-2">
            <X size={16} className="xs:w-5 xs:h-5" />
          </Button>
        </div>

        <div className="p-3 xs:p-4 sm:p-6 space-y-3 xs:space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 xs:gap-4">
            <div>
              <label htmlFor="name" className="block text-xs xs:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 xs:mb-2">Item Name *</label>
              <Input id="name" name="name" value={formData.name || ''} onChange={handleChange} placeholder="e.g., Blue Cotton Shirt" className="bg-white/80 border-owis-sage/30 text-sm xs:text-base h-10 xs:h-11" />
            </div>
            <div>
              <label htmlFor="brand" className="block text-xs xs:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 xs:mb-2">Brand *</label>
              <Input id="brand" name="brand" value={formData.brand || ''} onChange={handleChange} placeholder="e.g., Zara, H&M, Nike" className="bg-white/80 border-owis-sage/30 text-sm xs:text-base h-10 xs:h-11" />
            </div>
            <div>
              <label htmlFor="category" className="block text-xs xs:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 xs:mb-2">Category *</label>
              <select id="category" name="category" value={formData.category || ''} onChange={handleChange} className="w-full p-2 xs:p-3 text-sm xs:text-base border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 h-10 xs:h-11">
                {categories.map(cat => (<option key={cat} value={cat}>{cat}</option>))}
              </select>
            </div>
            <div>
              <label htmlFor="size" className="block text-xs xs:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 xs:mb-2">Size</label>
              <Input id="size" name="size" value={formData.size || ''} onChange={handleChange} placeholder="e.g., M, 32, 9" className="bg-white/80 border-owis-sage/30 text-sm xs:text-base h-10 xs:h-11" />
            </div>
            <div>
              <label htmlFor="price" className="block text-xs xs:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 xs:mb-2">Price</label>
              <Input id="price" name="price" type="number" value={formData.price === undefined ? '' : formData.price} onChange={handlePriceChange} placeholder="0.00" className="bg-white/80 border-owis-sage/30 text-sm xs:text-base h-10 xs:h-11" />
            </div>
            <div>
              <label htmlFor="material" className="block text-xs xs:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 xs:mb-2">Material</label>
              <Input id="material" name="material" value={formData.material || ''} onChange={handleChange} placeholder="e.g., Cotton, Denim, Silk" className="bg-white/80 border-owis-sage/30 text-sm xs:text-base h-10 xs:h-11" />
            </div>
            <div>
              <label htmlFor="season" className="block text-xs xs:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 xs:mb-2">Season</label>
              <select id="season" name="season" value={formData.season || ''} onChange={handleChange} className="w-full p-2 xs:p-3 text-sm xs:text-base border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 h-10 xs:h-11">
                {seasons.map(s => (<option key={s} value={s}>{s}</option>))}
              </select>
            </div>
            {/* Image Upload Field */}
            <div className="sm:col-span-2">
              <label className="block text-xs xs:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 xs:mb-2">
                Item Image
              </label>
              <div className="mt-1 flex items-center gap-4">
                <span className="inline-block h-16 w-16 rounded-md overflow-hidden bg-gray-100 dark:bg-gray-700">
                  {imagePreview ? (
                    <img src={imagePreview.startsWith('data:') ? imagePreview : `${VITE_BASE_URL}${imagePreview}`} alt="Preview" className="h-full w-full object-cover" />
                  ) : (
                    <Upload className="h-full w-full text-gray-300 dark:text-gray-500 p-4" />
                  )}
                </span>
                <div className="flex flex-col gap-2">
                  <Input
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    className="text-sm file:mr-2 file:py-1 file:px-2 file:rounded-full file:border-0 file:text-xs file:bg-owis-mint/20 file:text-owis-forest hover:file:bg-owis-mint/40"
                  />
                  { (imagePreview || formData.image_url) && !removeCurrentImage && ( // Show remove only if there's an image to remove
                    <Button variant="link" size="sm" onClick={handleRemoveImageClick} className="text-red-500 p-0 h-auto">
                      Remove current image
                    </Button>
                  )}
                  { removeCurrentImage && <p className="text-xs text-red-500">Image will be removed upon saving.</p>}
                </div>
              </div>
            </div>
            {/* End Image Upload Field */}
            <div>
              <label htmlFor="color" className="block text-xs xs:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 xs:mb-2">Color</label>
              <Input id="color" name="color" value={formData.color || ''} onChange={handleChange} placeholder="e.g., Blue, Multi-color" className="bg-white/80 border-owis-sage/30 text-sm xs:text-base h-10 xs:h-11" />
            </div>
          </div>
          <div>
            <label htmlFor="tags" className="block text-xs xs:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 xs:mb-2">Tags (comma separated)</label>
            <Input id="tags" name="tags" value={Array.isArray(formData.tags) ? formData.tags.join(', ') : ''} onChange={handleTagsChange} placeholder="casual, summer, cotton" className="bg-white/80 border-owis-sage/30 text-sm xs:text-base h-10 xs:h-11" />
          </div>
          <div>
            <label htmlFor="notes" className="block text-xs xs:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 xs:mb-2">Notes</label>
            <textarea id="notes" name="notes" value={formData.notes || ''} onChange={handleChange} placeholder="e.g., Purchased for wedding, very comfortable" rows={2} className="w-full p-2 xs:p-3 text-sm xs:text-base border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700" />
          </div>
          <div className="flex flex-col xs:flex-row gap-2 xs:gap-3 pt-3 xs:pt-4">
            <Button variant="outline" onClick={onClose} className="flex-1 h-10 xs:h-11 text-sm xs:text-base">Cancel</Button>
            <Button onClick={handleSave} className="flex-1 h-10 xs:h-11 text-sm xs:text-base bg-owis-purple hover:bg-owis-purple-dark text-owis-forest">
              <Save size={14} className="xs:w-4 xs:h-4 mr-1 xs:mr-2" />Save Changes
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EditItemModal;
