import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import CategorizedWardrobe from './CategorizedWardrobe';
import WeeklyPlanner from './WeeklyPlanner';
import { useLocation } from 'react-router-dom';

const WardrobePage = () => {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const initialAction = searchParams.get('action');

  const [activeView, setActiveView] = useState(initialAction === 'plan-week' ? 'planner' : 'wardrobe');

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="mb-4 flex gap-2">
        <Button 
          onClick={() => setActiveView('wardrobe')}
          variant={activeView === 'wardrobe' ? 'default' : 'outline'}
        >
          My Wardrobe
        </Button>
        <Button 
          onClick={() => setActiveView('planner')}
          variant={activeView === 'planner' ? 'default' : 'outline'}
        >
          Weekly Planner
        </Button>
      </div>

      {activeView === 'wardrobe' && <CategorizedWardrobe />}
      {activeView === 'planner' && <WeeklyPlanner />}
    </div>
  );
};

export default WardrobePage;
