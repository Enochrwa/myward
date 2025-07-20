import React from 'react';
import { useDrag } from 'react-dnd';

const DraggableImage = ({ item, type }: { item: any; type: string }) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type,
    item: { ...item, type },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  }));

  return (
    <img
      ref={drag}
      src={item.image_url}
      alt={item.category}
      style={{
        width: '100px',
        height: '100px',
        opacity: isDragging ? 0.5 : 1,
        cursor: 'move',
      }}
    />
  );
};

const CATEGORY_PART_MAPPING: { [key: string]: string } = {
  "Overcoat": "outerwear", "bag": "accessory", "blazers": "outerwear", "blouse": "top", "coats": "outerwear",
  "croptop": "top", "dress": "full_body", "hat": "accessory", "hoodie": "outerwear", "jacket": "outerwear",
  "jeans": "bottom", "outwear": "outerwear", "shirt": "top", "shoes": "accessory", "shorts": "bottom",
  "skirt": "bottom", "suit": "full_body", "sunglasses": "accessory", "sweater": "top", "trousers": "bottom", "tshirt": "top"
};

export const GeneratedOutfitsPanel = ({ recommendedOutfits }: { recommendedOutfits: any }) => {
  if (!recommendedOutfits) {
    return (
      <div className="w-96 p-6 bg-white dark:bg-gray-900 shadow-lg rounded-2xl flex flex-col">
        <h2 className="text-2xl font-bold mb-4 text-gray-800 dark:text-white">Discover Looks</h2>
        <div className="animate-pulse flex-grow">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="w-24 h-24 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const { outfit } = recommendedOutfits;

  const groupedOutfits: { [key: string]: any[] } = {
    top: [],
    bottom: [],
    outerwear: [],
    accessory: [],
    full_body: [],
    shoes: [],
  };

  Object.values(outfit).forEach((item: any) => {
    const part = CATEGORY_PART_MAPPING[item.category];
    if (part && groupedOutfits[part]) {
      groupedOutfits[part].push(item);
    }
  });

  return (
    <div className="w-96 p-6 bg-white dark:bg-gray-900 shadow-lg rounded-2xl flex flex-col">
      <h2 className="text-3xl font-bold mb-6 text-gray-800 dark:text-white text-center">Discover Looks</h2>
      <div className="space-y-6 overflow-y-auto flex-grow">
        {Object.entries(groupedOutfits).map(([part, items]) => (
          items.length > 0 && (
            <div key={part}>
              <h3 className="text-xl font-semibold mb-3 text-gray-700 dark:text-gray-300 capitalize">{part.replace('_', ' ')}</h3>
              <div className="grid grid-cols-3 gap-4">
                {items.map((item: any) => (
                  <DraggableImage key={item.id} item={item} type={part} />
                ))}
              </div>
            </div>
          )
        ))}
      </div>
    </div>
  );
};
