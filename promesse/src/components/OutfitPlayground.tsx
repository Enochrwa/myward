import React, { useState } from 'react';
import { useDrop } from 'react-dnd';
import axios from 'axios';

const DropZone = ({ onDrop, items, title }: { onDrop: (item: any) => void; items: any[]; title: string }) => {
  const [{ isOver }, drop] = useDrop(() => ({
    accept: ['top', 'bottom', 'outerwear', 'accessory'],
    drop: (item) => onDrop(item),
    collect: (monitor) => ({
      isOver: !!monitor.isOver(),
    }),
  }));

  return (
    <div
      ref={drop}
      style={{
        width: '200px',
        height: '200px',
        border: '1px solid black',
        backgroundColor: isOver ? 'lightgray' : 'white',
      }}
    >
      <h3>{title}</h3>
      {items.map((item, index) => (
        <img key={index} src={item.image_url} alt={item.category} style={{ width: '100px', height: '100px' }} />
      ))}
    </div>
  );
};

export const OutfitPlayground = () => {
  const [top, setTop] = useState<any[]>([]);
  const [bottom, setBottom] = useState<any[]>([]);
  const [outerwear, setOuterwear] = useState<any[]>([]);
  const [accessories, setAccessories] = useState<any[]>([]);

  const handleDrop = (item: any) => {
    switch (item.type) {
      case 'top':
        setTop([item]);
        break;
      case 'bottom':
        setBottom([item]);
        break;
      case 'outerwear':
        setOuterwear([item]);
        break;
      case 'accessory':
        setAccessories((prev) => [...prev, item]);
        break;
      default:
        break;
    }
  };

  const handleSaveOutfit = async () => {
    const outfit = {
      name: 'My Custom Outfit',
      gender: 'Unisex',
      clothing_parts: {
        top: top.length > 0 ? top[0].id : null,
        bottom: bottom.length > 0 ? bottom[0].id : null,
        outerwear: outerwear.length > 0 ? outerwear[0].id : null,
        accessory: accessories.map((item) => item.id),
      },
      clothing_items: [...top, ...bottom, ...outerwear, ...accessories].map((item) => item.id),
    };

    try {
      await axios.post('http://127.0.0.1:8000/api/outfit/custom', outfit);
      alert('Outfit saved successfully!');
    } catch (error) {
      console.error('Error saving outfit:', error);
      alert('Failed to save outfit.');
    }
  };

  return (
    <div style={{ width: '70%' }}>
      <h2>Outfit Playground</h2>
      <div style={{ display: 'flex', justifyContent: 'space-around' }}>
        <DropZone onDrop={handleDrop} items={top} title="Top" />
        <DropZone onDrop={handleDrop} items={bottom} title="Bottom" />
        <DropZone onDrop={handleDrop} items={outerwear} title="Outerwear" />
        <DropZone onDrop={handleDrop} items={accessories} title="Accessories" />
      </div>
      <button onClick={handleSaveOutfit}>Save Outfit</button>
    </div>
  );
};
