import React, { useState, useEffect } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { GeneratedOutfitsPanel } from '../components/GeneratedOutfitsPanel';
import OutfitBuilder from '../components/OutfitBuilder';
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
      <div className="flex h-screen bg-gray-100 dark:bg-gray-900">
        <GeneratedOutfitsPanel recommendedOutfits={recommendedOutfits} />
        <main className="flex-1">
          <OutfitBuilder onSave={(outfit) => console.log('Outfit saved:', outfit)} />
        </main>
      </div>
    </DndProvider>
  );
};

export default OutfitBuilderPage;
