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

export const GeneratedOutfitsPanel = ({ recommendedOutfits }: { recommendedOutfits: any }) => {
  if (!recommendedOutfits) {
    return <div>Loading...</div>;
  }

  const { outfit } = recommendedOutfits;

  return (
    <div style={{ width: '30%' }}>
      <h2>Recommended Outfits</h2>
      {Object.entries(outfit).map(([category, item]: [string, any]) => (
        <div key={category}>
          <h3>{category}</h3>
          <DraggableImage item={item} type={category} />
        </div>
      ))}
    </div>
  );
};
