import React, { useState } from 'react';
import { useDrop } from 'react-dnd';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Save, Trash2, X } from 'lucide-react';
import { useToast } from "@/components/ui/use-toast";
import * as apiClient from '@/lib/apiClient';

const DropZone = ({ onDrop, items, title, acceptedTypes, onRemoveItem }) => {
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
      className={`h-48 border-2 border-dashed rounded-lg flex items-center justify-center transition-colors ${
        isOver ? 'bg-accent' : ''
      } dark:border-gray-600`}
    >
      {items.length > 0 ? (
        items.map((item) => (
          <div key={item.id} className="relative group">
            <img
              src={item.image_url}
              alt={item.name}
              className="max-h-full rounded-lg"
            />
            <Button
              variant="destructive"
              size="icon"
              className="absolute top-1 right-1 h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
              onClick={() => onRemoveItem(item.id)}
            >
              <X className="h-4 w-4" />
            </Button>
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
  });

  const handleDrop = (item, category) => {
    setPlayground((prev) => {
      const newCategoryItems = category === 'accessory' ? [...prev[category], item] : [item];
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

  const handleSaveOutfit = async () => {
    const clothing_parts = {};
    const clothing_items = [];

    for (const category in playground) {
      const items = playground[category];
      if (items.length > 0) {
        if (category === 'accessory') {
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
      // Clear playground after saving
      setPlayground({
        top: [],
        bottom: [],
        outerwear: [],
        accessory: [],
      });
    } catch (err) {
      toast({ title: "Error", description: "Could not save outfit.", variant: "destructive" });
    }
  };

  return (
    <div className="w-full p-6 bg-background text-foreground">
      <Card className="bg-card">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Outfit Playground</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-6">
            <DropZone
              onDrop={(item) => handleDrop(item, 'top')}
              items={playground.top}
              title="Top"
              acceptedTypes={['top']}
              onRemoveItem={(itemId) => handleRemoveItem('top', itemId)}
            />
            <DropZone
              onDrop={(item) => handleDrop(item, 'bottom')}
              items={playground.bottom}
              title="Bottom"
              acceptedTypes={['bottom']}
              onRemoveItem={(itemId) => handleRemoveItem('bottom', itemId)}
            />
            <DropZone
              onDrop={(item) => handleDrop(item, 'outerwear')}
              items={playground.outerwear}
              title="Outerwear"
              acceptedTypes={['outerwear']}
              onRemoveItem={(itemId) => handleRemoveItem('outerwear', itemId)}
            />
            <DropZone
              onDrop={(item) => handleDrop(item, 'accessory')}
              items={playground.accessory}
              title="Accessories"
              acceptedTypes={['accessory']}
              onRemoveItem={(itemId) => handleRemoveItem('accessory', itemId)}
            />
          </div>
          <div className="mt-6 flex justify-end">
            <Button onClick={handleSaveOutfit} size="lg">
              <Save size={20} className="mr-2" />
              Save Outfit
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default OutfitBuilder;
