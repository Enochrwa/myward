import React, { useState } from 'react';
import { useDrop } from 'react-dnd';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Save, X } from 'lucide-react';
import { useToast } from "@/components/ui/use-toast";
import * as apiClient from '@/lib/apiClient';
import CroppableImage from './CroppableImage';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

const DropZone = ({ onDrop, items, title, acceptedTypes, onRemoveItem, onCrop, className = '' }) => {
  const [isCropOpen, setCropOpen] = useState(false);
  const [{ isOver }, drop] = useDrop(() => ({
    accept: acceptedTypes,
    drop: (item) => onDrop(item),
    collect: (monitor) => ({ isOver: !!monitor.isOver() }),
  }));

  return (
    <div
      ref={drop}
      className={`border-2 border-dashed rounded-lg flex items-center justify-center transition-colors relative group ${
        isOver ? 'bg-purple-100 dark:bg-purple-900' : 'bg-gray-100/50 dark:bg-gray-800/50'
      } hover:border-purple-400 dark:hover:border-purple-600 ${className}`}
    >
      {items.length > 0 ? (
        items.map((item) => (
          <div key={item.id} className="h-full w-full">
            <img
              src={item.image_url}
              alt={item.name || 'clothing item'}
              className="h-full w-full object-contain rounded-lg"
            />
            <div className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
              <Button
                variant="destructive"
                size="icon"
                className="h-7 w-7 bg-red-500/80 hover:bg-red-600"
                onClick={() => onRemoveItem(item.id)}
              >
                <X className="h-4 w-4" />
              </Button>
              <Dialog open={isCropOpen} onOpenChange={setCropOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline" size="icon" className="h-7 w-7 bg-white/80 hover:bg-white">
                    {/* <CropIcon className="h-4 w-4 text-gray-700" /> */}
                    Crop
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle className="text-2xl font-bold text-center">Crop Your Image</DialogTitle>
                  </DialogHeader>
                  <CroppableImage 
                    src={item.image_url} 
                    onCropComplete={(croppedImage) => onCrop(item.id, croppedImage)}
                    onClose={() => setCropOpen(false)}
                  />
                </DialogContent>
              </Dialog>
            </div>
          </div>
        ))
      ) : (
        <p className="text-gray-400 dark:text-gray-500 text-sm font-semibold">{title}</p>
      )}
    </div>
  );
};

const OutfitBuilder = ({ onSave }) => {
  const { toast } = useToast();
  const [playground, setPlayground] = useState({
    top: [],
    bottom: [],
    outerwear: [],
    accessory: [],
    shoes: [],
    full_body: [],
  });

  const handleDrop = (item, category) => {
    setPlayground((prev) => {
      const isMulti = ['accessory', 'shoes'].includes(category);
      const newItems = isMulti ? [...prev[category], item] : [item];
      
      let updates = { [category]: newItems };

      if (category === 'full_body') {
        updates = { ...updates, top: [], bottom: [], outerwear: [] };
      } else if (['top', 'bottom', 'outerwear'].includes(category)) {
        updates = { ...updates, full_body: [] };
      }

      return { ...prev, ...updates };
    });
  };

  const handleRemoveItem = (category, itemId) => {
    setPlayground((prev) => ({
      ...prev,
      [category]: prev[category].filter((item) => item.id !== itemId),
    }));
  };

  const handleCrop = (itemId, croppedImageUrl) => {
    setPlayground((prev) => {
      const newPlayground = { ...prev };
      for (const category in newPlayground) {
        newPlayground[category] = newPlayground[category].map((item) => {
          if (item.id === itemId) {
            return { ...item, image_url: croppedImageUrl };
          }
          return item;
        });
      }
      return newPlayground;
    });
  };

  const handleSaveOutfit = async () => {
    const clothing_parts = {};
    const clothing_items = [];

    for (const category in playground) {
      const items = playground[category];
      if (items.length > 0) {
        clothing_parts[category] = items.map(i => i.id);
        clothing_items.push(...items.map(i => i.id));
      }
    }

    if (clothing_items.length === 0) {
      toast({ title: "Empty Outfit", description: "Add some items to the playground first.", variant: "destructive" });
      return;
    }

    const outfitData = {
      name: 'My Custom Outfit',
      gender: 'unisex',
      clothing_parts,
      clothing_items,
    };

    try {
      await apiClient.saveOutfit(outfitData);
      toast({ title: "Success", description: "Outfit saved." });
      onSave(outfitData);
      setPlayground({ top: [], bottom: [], outerwear: [], accessory: [], shoes: [], full_body: [] });
    } catch (err) {
      toast({ title: "Error", description: "Could not save outfit.", variant: "destructive" });
    }
  };
  
  const isFullBodyView = playground.full_body.length > 0;

  return (
    <div className="w-full h-full p-4 md:p-6 bg-gradient-to-br from-gray-50 to-gray-200 dark:from-gray-900 dark:to-gray-800 text-foreground">
      <Card className="bg-white/80 dark:bg-gray-950/80 backdrop-blur-sm h-full flex flex-col shadow-2xl rounded-3xl">
        <CardHeader className="border-b border-gray-200 dark:border-gray-800">
          <CardTitle className="text-3xl font-bold text-center text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
            Outfit Playground
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-grow p-4 md:p-8">
          <div className="h-full w-full max-w-4xl mx-auto grid grid-cols-3 grid-rows-4 gap-4 relative">
            
            {/* Accessories */}
            <div className="col-span-3 row-start-1 flex justify-center items-center gap-4">
              <DropZone
                onDrop={(item) => handleDrop(item, 'accessory')}
                items={playground.accessory.slice(0, 2)}
                title="Accessories"
                acceptedTypes={['accessory']}
                onRemoveItem={(itemId) => handleRemoveItem('accessory', itemId)}
                onCrop={handleCrop}
                className="w-24 h-24 rounded-full"
              />
            </div>

            {isFullBodyView ? (
              <div className="col-span-3 row-start-2 row-span-2">
                <DropZone
                  onDrop={(item) => handleDrop(item, 'full_body')}
                  items={playground.full_body}
                  title="Full Body"
                  acceptedTypes={['full_body']}
                  onRemoveItem={() => handleRemoveItem('full_body', playground.full_body[0]?.id)}
                  onCrop={handleCrop}
                  className="h-full"
                />
              </div>
            ) : (
              <>
                <div className="col-start-2 row-start-2 row-span-2 grid grid-rows-2 gap-4">
                  <DropZone
                    onDrop={(item) => handleDrop(item, 'top')}
                    items={playground.top}
                    title="Top"
                    acceptedTypes={['top']}
                    onRemoveItem={() => handleRemoveItem('top', playground.top[0]?.id)}
                    onCrop={handleCrop}
                    className="h-full"
                  />
                  <DropZone
                    onDrop={(item) => handleDrop(item, 'bottom')}
                    items={playground.bottom}
                    title="Bottom"
                    acceptedTypes={['bottom']}
                    onRemoveItem={() => handleRemoveItem('bottom', playground.bottom[0]?.id)}
                    onCrop={handleCrop}
                    className="h-full"
                  />
                </div>
                <div className="col-start-1 row-start-2 row-span-2">
                  <DropZone
                    onDrop={(item) => handleDrop(item, 'outerwear')}
                    items={playground.outerwear}
                    title="Outerwear"
                    acceptedTypes={['outerwear']}
                    onRemoveItem={() => handleRemoveItem('outerwear', playground.outerwear[0]?.id)}
                    onCrop={handleCrop}
                    className="h-full"
                  />
                </div>
              </>
            )}
            
            {/* Shoes */}
            <div className="col-span-3 row-start-4 flex justify-center items-center gap-4">
              <DropZone
                onDrop={(item) => handleDrop(item, 'shoes')}
                items={playground.shoes}
                title="Shoes"
                acceptedTypes={['shoes']}
                onRemoveItem={(itemId) => handleRemoveItem('shoes', itemId)}
                onCrop={handleCrop}
                className="w-48 h-24"
              />
            </div>
          </div>
        </CardContent>
        <div className="p-6 flex justify-center border-t border-gray-200 dark:border-gray-800">
          <Button onClick={handleSaveOutfit} size="lg" className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-bold py-3 px-8 rounded-full shadow-lg transform hover:scale-105 transition-transform">
            <Save size={20} className="mr-2" />
            Save Outfit
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default OutfitBuilder;
