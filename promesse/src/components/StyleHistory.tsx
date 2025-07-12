
import React, { useState, useEffect, useCallback } from 'react';
import { Calendar, Search, Clock, AlertTriangle, Info } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import  apiClient  from '@/lib/apiClient';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ui/use-toast';
import  LoadingSpinner  from '@/components/ui/loading'; // Assuming this exists

interface StyleHistoryProps {
  isOpen: boolean;
  onClose: () => void;
}

interface OutfitInfo {
  id: number;
  name: string;
  image_url?: string;
  // Add other fields like items list if provided by backend and needed
}

interface ItemInfo {
  id: number;
  name: string;
  image_url?: string;
}

interface StyleHistoryEntry {
  id: number;
  date_worn: string; // ISO date string
  notes?: string;
  item_id?: number;
  outfit_id?: number;
  item_worn?: ItemInfo;
  outfit_worn?: OutfitInfo;
  // Fields like occasion, rating, mood, tags are removed as they are not in the base StyleHistory backend model.
  // They could be added later if the backend model is extended.
}

const StyleHistory = ({ isOpen, onClose }: StyleHistoryProps) => {
  const [styleHistory, setStyleHistory] = useState<StyleHistoryEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('date_worn_desc'); // Default sort

  const { token } = useAuth();
  const { toast } = useToast(); // Available for future use (e.g., delete entry)

  const fetchStyleHistory = useCallback(async () => {
    if (!token) {
      setError("Please login to view your style history.");
      setIsLoading(false);
      setStyleHistory([]);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiClient<StyleHistoryEntry[]>('/style-history/', { token });
      setStyleHistory(data || []);
    } catch (err: any) {
      console.error("Fetch Style History Error:", err);
      setError(err.message || 'Failed to fetch style history.');
      setStyleHistory([]);
      toast({
        title: "Error",
        description: err.message || 'Failed to fetch style history.',
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }, [token, toast]);

  useEffect(() => {
    if (isOpen && token) {
      fetchStyleHistory();
    } else if (isOpen && !token) {
        setError("Please login to view your style history.");
        setIsLoading(false);
        setStyleHistory([]);
    }
  }, [isOpen, token, fetchStyleHistory]);

  const filteredHistory = styleHistory.filter(entry => {
    const searchTermLower = searchTerm.toLowerCase();
    const matchesSearch =
      (entry.notes && entry.notes.toLowerCase().includes(searchTermLower)) ||
      (entry.outfit_worn && entry.outfit_worn.name.toLowerCase().includes(searchTermLower)) ||
      (entry.item_worn && entry.item_worn.name.toLowerCase().includes(searchTermLower));
    return matchesSearch;
  });

  const sortedHistory = [...filteredHistory].sort((a, b) => {
    switch (sortBy) {
      case 'date_worn_asc':
        return new Date(a.date_worn).getTime() - new Date(b.date_worn).getTime();
      case 'date_worn_desc':
      default:
        return new Date(b.date_worn).getTime() - new Date(a.date_worn).getTime();
    }
  });

  const VITE_BASE_URL = import.meta.env.VITE_BASE_URL || '';

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-3xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Style History</h2>
            <p className="text-gray-600 dark:text-gray-400">Your fashion journey and style evolution.</p>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close style history">
            <span className="text-2xl">&times;</span>
          </Button>
        </div>

        <div className="p-6 space-y-6 flex-grow overflow-y-auto">
          {/* Filters and Sorting */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <Input
                  placeholder="Search in notes, outfit or item names..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="flex gap-2">
              <select 
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-owis-purple focus:border-owis-purple"
              >
                <option value="date_worn_desc">Sort by Date (Newest First)</option>
                <option value="date_worn_asc">Sort by Date (Oldest First)</option>
              </select>
            </div>
          </div>

          {isLoading && (
            <div className="flex justify-center items-center h-64">
              <LoadingSpinner size={64} />
            </div>
          )}

          {error && (
            <div className="text-center py-12 bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-red-700 dark:text-red-300 mb-2">Error Fetching History</h3>
              <p className="text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}

          {!isLoading && !error && sortedHistory.length === 0 && (
            <div className="text-center py-12">
              <Clock className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No Style History Found</h3>
              <p className="text-gray-600 dark:text-gray-400">
                {searchTerm ? "No entries match your search." : "Start wearing and logging your outfits to build your style timeline!"}
              </p>
            </div>
          )}

          {!isLoading && !error && sortedHistory.length > 0 && (
            <div className="space-y-6">
              {sortedHistory.map((entry) => {
                const displayImage = entry.outfit_worn?.image_url || entry.item_worn?.image_url;
                const displayName = entry.outfit_worn?.name || entry.item_worn?.name || "Entry";
                const imageUrl = displayImage && displayImage.startsWith('http') ? displayImage : displayImage ? `${VITE_BASE_URL}${displayImage}` : 'https://via.placeholder.com/300x300?text=No+Image';


                return (
                  <Card key={entry.id} className="overflow-hidden hover:shadow-lg transition-all duration-300 dark:border-gray-700">
                    <div className="flex flex-col lg:flex-row">
                      <div className="lg:w-56 aspect-w-1 aspect-h-1 lg:aspect-none">
                        <img
                          src={imageUrl}
                          alt={displayName}
                          className="w-full h-full object-cover object-center"
                        />
                      </div>
                      
                      <div className="flex-1 p-6">
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <h3 className="text-xl font-semibold text-gray-900 dark:text-white">{displayName}</h3>
                            {entry.outfit_worn && entry.item_worn && (
                               <p className="text-sm text-gray-500 dark:text-gray-400">Outfit containing: {entry.item_worn.name}</p>
                            )}
                          </div>
                          {/* Removed rating stars as rating is not in the base model */}
                        </div>

                        <div className="space-y-3">
                           <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                              <Calendar size={16} />
                              <span>{new Date(entry.date_worn).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}</span>
                            </div>

                          {entry.notes && (
                            <div>
                              <h4 className="font-medium text-gray-900 dark:text-white mb-1">Notes:</h4>
                              <p className="text-gray-600 dark:text-gray-400 text-sm italic">"{entry.notes}"</p>
                            </div>
                          )}

                          {(entry.outfit_worn || entry.item_worn) && (
                            <Badge variant="outline" className="text-xs">
                              {entry.outfit_id ? `Outfit ID: ${entry.outfit_id}` : `Item ID: ${entry.item_id}`}
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                  </Card>
                );
              })}
            </div>
          )}
        </div>

        {/* Stats Overview - Simplified or could be removed if not meaningful */}
        {!isLoading && !error && styleHistory.length > 0 && (
          <div className="p-6 border-t border-gray-200 dark:border-gray-700">
            <Card className="bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-900/30 dark:to-blue-800/30">
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-300">{styleHistory.length}</div>
                <div className="text-sm text-blue-700 dark:text-blue-400">Total History Entries</div>
              </CardContent>
            </Card>
          </div>
        )}
         {!isLoading && !error && styleHistory.length === 0 && !searchTerm && (
           <div className="p-6 border-t border-gray-200 dark:border-gray-700 text-center">
             <Info size={20} className="inline mr-2 text-gray-500" />
             <p className="text-sm text-gray-500 dark:text-gray-400 inline">
                Log your outfits to see your style journey grow!
             </p>
           </div>
        )}


      </div>
    </div>
  );
};

export default StyleHistory;
