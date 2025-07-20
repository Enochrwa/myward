import React, { useState } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, Save } from 'lucide-react';
import * as apiClient from '@/lib/apiClient';
import { useToast } from "@/components/ui/use-toast";

const OutfitBuilder = ({ items, onSave }) => {
  const { toast } = useToast();
  const [playground, setPlayground] = useState({
    top: null,
    bottom: null,
    outerwear: null,
    accessory: [],
  });

  const onDragEnd = (result) => {
    const { source, destination } = result;

    if (!destination) {
      return;
    }

    const sourceId = source.droppableId;
    const destinationId = destination.droppableId;
    const sourceIndex = source.index;
    const destinationIndex = destination.index;

    if (sourceId === destinationId && sourceIndex === destinationIndex) {
      return;
    }

    const item = items[sourceIndex];

    if (destinationId.startsWith('playground-')) {
      const category = destinationId.split('-')[1];
      setPlayground((prev) => ({
        ...prev,
        [category]: category === 'accessory' ? [...prev.accessory, item] : item,
      }));
    }
  };

  const handleSaveOutfit = async () => {
    const clothing_parts = {};
    const clothing_items = [];

    for (const category in playground) {
      const item = playground[category];
      if (item) {
        if (Array.isArray(item)) {
          clothing_parts[category] = item.map((i) => i.id);
          clothing_items.push(...item.map((i) => i.id));
        } else {
          clothing_parts[category] = item.id;
          clothing_items.push(item.id);
        }
      }
    }

    const outfitData = {
      name: 'My Custom Outfit',
      gender: 'unisex',
      clothing_parts,
      clothing_items,
    };

    try {
      await onSave(outfitData);
      toast({ title: "Success", description: "Outfit saved." });
    } catch (err) {
      toast({ title: "Error", description: "Could not save outfit.", variant: "destructive" });
    }
  };

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <div className="grid grid-cols-3 gap-4">
        <Droppable droppableId="items">
          {(provided) => (
            <div
              ref={provided.innerRef}
              {...provided.droppableProps}
              className="col-span-1"
            >
              <Card>
                <CardHeader>
                  <CardTitle>Wardrobe</CardTitle>
                </CardHeader>
                <CardContent>
                  {items.map((item, index) => (
                    <Draggable key={item.id} draggableId={item.id} index={index}>
                      {(provided) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          className="mb-2"
                        >
                          <Card>
                            <CardContent className="p-2">
                              <img src={item.image_url} alt={item.name} />
                              <p>{item.name}</p>
                            </CardContent>
                          </Card>
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </CardContent>
              </Card>
            </div>
          )}
        </Droppable>

        <div className="col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Playground</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <Droppable droppableId="playground-top">
                  {(provided) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      className="h-48 border-2 border-dashed rounded-lg flex items-center justify-center"
                    >
                      {playground.top ? (
                        <img
                          src={playground.top.image_url}
                          alt={playground.top.name}
                          className="max-h-full"
                        />
                      ) : (
                        <p>Top</p>
                      )}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
                <Droppable droppableId="playground-bottom">
                  {(provided) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      className="h-48 border-2 border-dashed rounded-lg flex items-center justify-center"
                    >
                      {playground.bottom ? (
                        <img
                          src={playground.bottom.image_url}
                          alt={playground.bottom.name}
                          className="max-h-full"
                        />
                      ) : (
                        <p>Bottom</p>
                      )}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
                <Droppable droppableId="playground-outerwear">
                  {(provided) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      className="h-48 border-2 border-dashed rounded-lg flex items-center justify-center"
                    >
                      {playground.outerwear ? (
                        <img
                          src={playground.outerwear.image_url}
                          alt={playground.outerwear.name}
                          className="max-h-full"
                        />
                      ) : (
                        <p>Outerwear</p>
                      )}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
                <Droppable droppableId="playground-accessory">
                  {(provided) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      className="h-48 border-2 border-dashed rounded-lg flex items-center justify-center"
                    >
                      {playground.accessory.length > 0 ? (
                        playground.accessory.map((item) => (
                          <img
                            key={item.id}
                            src={item.image_url}
                            alt={item.name}
                            className="max-h-16"
                          />
                        ))
                      ) : (
                        <p>Accessory</p>
                      )}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              </div>
              <Button onClick={handleSaveOutfit} className="mt-4">
                <Save size={16} className="mr-2" />
                Save Outfit
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </DragDropContext>
  );
};

export default OutfitBuilder;
