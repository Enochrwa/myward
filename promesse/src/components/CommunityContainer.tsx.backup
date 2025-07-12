
import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useLocation, useNavigate } from 'react-router-dom';
import { Heart, Users, Camera, Trophy } from 'lucide-react';

import CommunityFeed from './CommunityFeed';
import FashionChallenges from './FashionChallenges';
import StyleCommunities from './StyleCommunities';
import Lookbook from './Lookbook';

const CommunityContainer = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(() => {
    // Get active tab from URL query parameter
    const params = new URLSearchParams(location.search);
    return params.get('tab') || 'feed';
  });

  const handleTabChange = (value: string) => {
    setActiveTab(value);
    
    // Update URL query parameter
    const searchParams = new URLSearchParams(location.search);
    searchParams.set('tab', value);
    navigate(`${location.pathname}?${searchParams.toString()}`, { replace: true });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-owis-cream to-owis-mint dark:from-owis-charcoal-dark to-owis-midnight-blue pt-20">
      <Tabs value={activeTab} onValueChange={handleTabChange} className="w-full">
        <div className="flex justify-center mb-8">
          <TabsList className="bg-white/70 dark:bg-owis-charcoal/70 backdrop-blur-md rounded-2xl p-2 shadow-lg">
            <TabsTrigger 
              value="feed"
              className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-owis-gold data-[state=active]:to-owis-bronze data-[state=active]:text-white rounded-xl px-6 py-3"
            >
              <Heart size={16} />
              Style Feed
            </TabsTrigger>
            <TabsTrigger 
              value="challenges"
              className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-owis-gold data-[state=active]:to-owis-bronze data-[state=active]:text-white rounded-xl px-6 py-3"
            >
              <Trophy size={16} />
              Challenges
            </TabsTrigger>
            <TabsTrigger 
              value="communities"
              className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-owis-gold data-[state=active]:to-owis-bronze data-[state=active]:text-white rounded-xl px-6 py-3"
            >
              <Users size={16} />
              Communities
            </TabsTrigger>
            <TabsTrigger 
              value="lookbook"
              className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-owis-gold data-[state=active]:to-owis-bronze data-[state=active]:text-white rounded-xl px-6 py-3"
            >
              <Camera size={16} />
              Lookbook
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="feed" className="animate-fade-in">
          <CommunityFeed />
        </TabsContent>
        <TabsContent value="challenges" className="animate-fade-in">
          <FashionChallenges />
        </TabsContent>
        <TabsContent value="communities" className="animate-fade-in">
          <StyleCommunities />
        </TabsContent>
        <TabsContent value="lookbook" className="animate-fade-in">
          <Lookbook />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CommunityContainer;
