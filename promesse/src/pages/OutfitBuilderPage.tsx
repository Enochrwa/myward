import React, { useState, useEffect } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { GeneratedOutfitsPanel } from '../components/GeneratedOutfitsPanel';
import { OutfitPlayground } from '../components/OutfitPlayground';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const OutfitBuilderPage: React.FC = () => {
  const [recommendedOutfits, setRecommendedOutfits] = useState<any>(null);
  const { imageId } = useParams<{ imageId: string }>();

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/outfit/recommend/${imageId}`);
        setRecommendedOutfits(response.data);
      } catch (error) {
        console.error('Error fetching outfit recommendations:', error);
      }
    };

    if (imageId) {
      fetchRecommendations();
    }
  }, [imageId]);

  return (
    <DndProvider backend={HTML5Backend}>
      <div style={{ display: 'flex' }}>
        <GeneratedOutfitsPanel recommendedOutfits={recommendedOutfits} />
        <OutfitPlayground />
      </div>
    </DndProvider>
  );
};

export default OutfitBuilderPage;
