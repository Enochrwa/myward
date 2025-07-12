import React, { useState, useEffect, useCallback } from 'react';
import * as apiClient from '@/lib/apiClient';
import { Feedback, FeedbackCreate } from '@/types/outfitTypes';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input'; // For rating if not using stars
import { useToast } from '@/components/ui/use-toast';
import { Star, Trash2, Send } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth'; // To get current user ID
import LoadingSpinner from './ui/loading';

interface FeedbackSectionProps {
  outfitId: string | number; // Can be string if UUIDs are used for outfits, number if integer IDs
}

const FeedbackSection: React.FC<FeedbackSectionProps> = ({ outfitId }) => {
  const { user } = useAuth(); // Assuming useAuth() provides { user: { id: number, ... } }
  const currentUserId = user?.id;
  const { toast } = useToast();

  const [feedbackList, setFeedbackList] = useState<Feedback[]>([]);
  const [newFeedbackText, setNewFeedbackText] = useState('');
  const [newFeedbackRating, setNewFeedbackRating] = useState<number>(0); // 0 for no rating, 1-5
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFeedback = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiClient.getFeedbackForOutfit(outfitId);
      setFeedbackList(data || []);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch feedback.');
      toast({ title: 'Error fetching feedback', description: err.message, variant: 'destructive' });
    } finally {
      setIsLoading(false);
    }
  }, [outfitId, toast]);

  useEffect(() => {
    if (outfitId) {
      fetchFeedback();
    }
  }, [outfitId, fetchFeedback]);

  const handleSubmitFeedback = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFeedbackText && newFeedbackRating === 0) {
      toast({ title: 'Cannot submit empty feedback', description: 'Please add text or a rating.', variant: 'destructive' });
      return;
    }
    if (newFeedbackRating < 0 || newFeedbackRating > 5) {
        toast({ title: 'Invalid rating', description: 'Rating must be between 1 and 5.', variant: 'destructive' });
        return;
    }

    setIsSubmitting(true);
    const feedbackData: FeedbackCreate = {};
    if (newFeedbackText) feedbackData.feedback_text = newFeedbackText;
    if (newFeedbackRating > 0) feedbackData.rating = newFeedbackRating;

    try {
      const newFeedbackItem = await apiClient.addFeedbackToOutfit(outfitId, feedbackData);
      // Add new feedback to the list, ideally with commenter_username if backend returns it readily
      // For now, refetch or manually construct. Backend should return full Feedback object.
      setFeedbackList(prev => [newFeedbackItem, ...prev]);
      setNewFeedbackText('');
      setNewFeedbackRating(0);
      toast({ title: 'Success', description: 'Feedback submitted.' });
    } catch (err: any) {
      toast({ title: 'Error submitting feedback', description: err.message, variant: 'destructive' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteFeedback = async (feedbackId: number) => {
    try {
      await apiClient.deleteFeedback(feedbackId);
      setFeedbackList(prev => prev.filter(fb => fb.id !== feedbackId));
      toast({ title: 'Success', description: 'Feedback deleted.' });
    } catch (err: any) {
      toast({ title: 'Error deleting feedback', description: err.message, variant: 'destructive' });
    }
  };

  if (isLoading) {
    return <div className="flex items-center justify-center py-4"><LoadingSpinner size="sm" /><p className="ml-2">Loading feedback...</p></div>;
  }

  if (error) {
    return <div className="text-red-500 text-sm p-4">Error: {error}</div>;
  }

  return (
    <div className="space-y-6 mt-6">
      <h3 className="text-xl font-semibold">Feedback & Comments</h3>

      {/* Form for new feedback */}
      {user && (
        <form onSubmit={handleSubmitFeedback} className="space-y-3 p-4 border rounded-lg bg-gray-50 dark:bg-gray-800">
          <Textarea
            value={newFeedbackText}
            onChange={(e) => setNewFeedbackText(e.target.value)}
            placeholder="Share your thoughts on this outfit..."
            rows={3}
            className="bg-white dark:bg-gray-700"
          />
          <div className="flex items-center space-x-2">
            {[1, 2, 3, 4, 5].map((star) => (
              <Star
                key={star}
                className={`cursor-pointer ${newFeedbackRating >= star ? 'text-purple-400 fill-purple-400' : 'text-gray-300 dark:text-gray-600'}`}
                onClick={() => setNewFeedbackRating(star === newFeedbackRating ? 0 : star)} // Click again to clear rating
              />
            ))}
            <span className="text-sm text-gray-500 dark:text-gray-400">({newFeedbackRating > 0 ? `${newFeedbackRating} star${newFeedbackRating > 1 ? 's' : ''}` : 'No rating'})</span>
          </div>
          <Button type="submit" disabled={isSubmitting} size="sm">
            {isSubmitting ? <><LoadingSpinner size="xs" className="mr-2" />Submitting...</> : <><Send size={16} className="mr-2" />Submit Feedback</>}
          </Button>
        </form>
      )}
      {!user && <p className="text-sm text-gray-600 dark:text-gray-400">You must be logged in to leave feedback.</p>}

      {/* Display feedback list */}
      <div className="space-y-4">
        {feedbackList.length === 0 && <p className="text-sm text-gray-500 dark:text-gray-400">No feedback yet. Be the first to comment!</p>}
        {feedbackList.map((fb) => (
          <div key={fb.id} className="p-3 border rounded-lg bg-white dark:bg-gray-700/50 shadow-sm">
            <div className="flex items-center justify-between mb-1">
              <span className="font-semibold text-sm text-gray-800 dark:text-gray-200">{fb.commenter_username || 'Anonymous User'}</span>
              <div className="flex items-center space-x-1">
                {fb.rating && fb.rating > 0 && (
                  <div className="flex items-center">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} size={14} className={i < fb.rating! ? 'text-purple-400 fill-purple-400' : 'text-gray-300 dark:text-gray-500'} />
                    ))}
                  </div>
                )}
                {currentUserId === fb.user_id && (
                  <Button variant="ghost" size="icon" onClick={() => handleDeleteFeedback(fb.id)} className="h-6 w-6 p-0 text-red-500 hover:text-red-700">
                    <Trash2 size={14} />
                  </Button>
                )}
              </div>
            </div>
            {fb.feedback_text && <p className="text-sm text-gray-700 dark:text-gray-300 mb-1">{fb.feedback_text}</p>}
            <p className="text-xs text-gray-400 dark:text-gray-500">{new Date(fb.created_at).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FeedbackSection;
