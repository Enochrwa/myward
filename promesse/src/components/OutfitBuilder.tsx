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
  const [{ isOver }, drop] = useDrop(() => ({
    accept: acceptedTypes,
    drop: (item) => onDrop(item),
    collect: (monitor) => ({
      isOver: !!monitor.isOver(),
    }),
  }));

  return (
    <div
      ref={drop}
      className={`border-2 border-dashed rounded-lg flex items-center justify-center transition-colors ${
        isOver ? 'bg-accent' : ''
      } dark:border-gray-600 ${className}`}
    >
      {items.length > 0 ? (
        items.map((item) => (
          <div key={item.id} className="relative group h-full w-full">
            <img
              src={item.image_url}
              alt={item.name}
              className="h-full w-full object-contain rounded-lg"
            />
            <div className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <Button
                variant="destructive"
                size="icon"
                className="h-6 w-6"
                onClick={() => onRemoveItem(item.id)}
              >
                <X className="h-4 w-4" />
              </Button>
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="outline" size="icon" className="h-6 w-6">
                    Crop
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Crop Image</DialogTitle>
                  </DialogHeader>
                  <CroppableImage src={item.image_url} onCropComplete={(croppedImage) => onCrop(item.id, croppedImage)} />
                </DialogContent>
              </Dialog>
            </div>
          </div>
        ))
      ) : (
        <p className="text-muted-foreground">{title}</p>
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
  });

  const handleDrop = (item, category) => {
    setPlayground((prev) => {
      const newCategoryItems = ['accessory', 'shoes'].includes(category) ? [...prev[category], item] : [item];
      return {
        ...prev,
        [category]: newCategoryItems,
      };
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
        if (['accessory', 'shoes'].includes(category)) {
          clothing_parts[category] = items.map((i) => i.id);
        } else {
          clothing_parts[category] = items[0].id;
        }
        clothing_items.push(...items.map((i) => i.id));
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
      setPlayground({
        top: [],
        bottom: [],
        outerwear: [],
        accessory: [],
        shoes: [],
      });
    } catch (err) {
      toast({ title: "Error", description: "Could not save outfit.", variant: "destructive" });
    }
  };

  return (
    <div className="w-full h-full p-4 md:p-6 bg-background text-foreground">
      <Card className="bg-card h-full flex flex-col">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Outfit Playground</CardTitle>
        </CardHeader>
        <CardContent className="flex-grow grid grid-cols-2 md:grid-cols-3 grid-rows-3 md:grid-rows-2 gap-4">
          <div className="md:col-start-2 md:row-start-1 h-48 md:h-full">
            <DropZone
              onDrop={(item) => handleDrop(item, 'top')}
              items={playground.top}
              title="Top"
              acceptedTypes={['top']}
              onRemoveItem={() => handleRemoveItem('top', playground.top[0]?.id)}
              onCrop={(itemId, croppedImageUrl) => handleCrop(itemId, croppedImageUrl)}
              className="h-full"
            />
          </div>
          <div className="md:col-start-2 md:row-start-2 h-48 md:h-full">
            <DropZone
              onDrop={(item) => handleDrop(item, 'bottom')}
              items={playground.bottom}
              title="Bottom"
              acceptedTypes={['bottom']}
              onRemoveItem={() => handleRemoveItem('bottom', playground.bottom[0]?.id)}
              onCrop={(itemId, croppedImageUrl) => handleCrop(itemId, croppedImageUrl)}
              className="h-full"
            />
          </div>
          <div className="md:col-start-1 md:row-start-1 md:row-span-2 h-48 md:h-full">
            <DropZone
              onDrop={(item) => handleDrop(item, 'outerwear')}
              items={playground.outerwear}
              title="Outerwear"
              acceptedTypes={['outerwear']}
              onRemoveItem={() => handleRemoveItem('outerwear', playground.outerwear[0]?.id)}
              onCrop={(itemId, croppedImageUrl) => handleCrop(itemId, croppedImageUrl)}
              className="h-full"
            />
          </div>
          <div className="col-span-2 md:col-span-1 md:col-start-3 md:row-start-1 h-48 md:h-full">
            <DropZone
              onDrop={(item) => handleDrop(item, 'accessory')}
              items={playground.accessory}
              title="Accessories"
              acceptedTypes={['accessory']}
              onRemoveItem={(itemId) => handleRemoveItem('accessory', itemId)}
              onCrop={(itemId, croppedImageUrl) => handleCrop(itemId, croppedImageUrl)}
              className="h-full"
            />
          </div>
          <div className="col-span-2 md:col-span-1 md:col-start-3 md:row-start-2 h-48 md:h-full">
            <DropZone
              onDrop={(item) => handleDrop(item, 'shoes')}
              items={playground.shoes}
              title="Shoes"
              acceptedTypes={['shoes']}
              onRemoveItem={(itemId) => handleRemoveItem('shoes', itemId)}
              onCrop={(itemId, croppedImageUrl) => handleCrop(itemId, croppedImageUrl)}
              className="h-full"
            />
          </div>
        </CardContent>
        <div className="p-6 flex justify-end">
          <Button onClick={handleSaveOutfit} size="lg">
            <Save size={20} className="mr-2" />
            Save Outfit
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default OutfitBuilder;
