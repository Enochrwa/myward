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
    return <div>Loading...</div>;
  }

  const { outfit } = recommendedOutfits;

  const groupedOutfits: { [key: string]: any[] } = {
    top: [],
    bottom: [],
    outerwear: [],
    accessory: [],
    full_body: [],
  };

  Object.values(outfit).forEach((item: any) => {
    const part = CATEGORY_PART_MAPPING[item.category];
    if (part && groupedOutfits[part]) {
      groupedOutfits[part].push(item);
    }
  });

  return (
    <div style={{ width: '30%' }}>
      <h2>Recommended Outfits</h2>
      {Object.entries(groupedOutfits).map(([part, items]) => (
        <div key={part}>
          <h3>{part.charAt(0).toUpperCase() + part.slice(1)}</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap' }}>
            {items.map((item: any) => (
              <DraggableImage key={item.id} item={item} type={part} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};
