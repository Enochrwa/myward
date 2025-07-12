import React, { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import * as apiClient from '@/lib/apiClient';
import { UserProfile, UserProfileUpdate } from '@/types/userTypes'; // Ensure this path is correct
import LoadingSpinner from './ui/loading'; // Assuming you have a loading spinner

const UserProfilePreferences: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  // Form states
  const [preferredStyles, setPreferredStyles] = useState('');
  const [preferredColors, setPreferredColors] = useState('');
  const [avoidedColors, setAvoidedColors] = useState('');
  const [shirtSize, setShirtSize] = useState('');
  const [pantsWaistSize, setPantsWaistSize] = useState('');
  const [shoeSize, setShoeSize] = useState('');

  const mapProfileToForm = useCallback((userProfile: UserProfile | null) => {
    setPreferredStyles(userProfile?.preferred_styles?.join(', ') || '');
    setPreferredColors(userProfile?.preferred_colors?.join(', ') || '');
    setAvoidedColors(userProfile?.avoided_colors?.join(', ') || '');
    setShirtSize(userProfile?.sizes?.shirt || '');
    setPantsWaistSize(userProfile?.sizes?.pants_waist || '');
    setShoeSize(userProfile?.sizes?.shoes || '');
  }, []);

  useEffect(() => {
    const fetchProfile = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const userProfile = await apiClient.getUserProfile();
        setProfile(userProfile);
        mapProfileToForm(userProfile);
      } catch (err: any) {
        if (err.message.includes('404')) {
          // Profile not found, treat as new profile scenario
          setProfile(null); // Ensure profile is null
          mapProfileToForm(null); // Reset form fields
          setError(null); // Not an error for user, just means no profile yet
        } else {
          setError(err.message || 'Failed to fetch profile.');
          toast({ title: 'Error', description: err.message || 'Failed to fetch profile.', variant: 'destructive' });
        }
      } finally {
        setIsLoading(false);
      }
    };
    fetchProfile();
  }, [toast, mapProfileToForm]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    const sizes: Record<string, string> = {};
    if (shirtSize) sizes.shirt = shirtSize;
    if (pantsWaistSize) sizes.pants_waist = pantsWaistSize;
    if (shoeSize) sizes.shoes = shoeSize;

    const profileData: UserProfileUpdate = {
      preferred_styles: preferredStyles.split(',').map(s => s.trim()).filter(Boolean),
      preferred_colors: preferredColors.split(',').map(s => s.trim()).filter(Boolean),
      avoided_colors: avoidedColors.split(',').map(s => s.trim()).filter(Boolean),
      sizes: Object.keys(sizes).length > 0 ? sizes : undefined,
    };

    try {
      const updatedProfile = await apiClient.updateUserProfile(profileData);
      setProfile(updatedProfile);
      mapProfileToForm(updatedProfile); // Update form with data from response (e.g. updated_at)
      toast({ title: 'Success', description: 'Preferences saved successfully!' });
    } catch (err: any) {
      setError(err.message || 'Failed to save preferences.');
      toast({ title: 'Error', description: err.message || 'Failed to save preferences.', variant: 'destructive' });
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading && !profile && !error) { // Show loading only on initial fetch if no profile yet
    return <div className="flex justify-center items-center h-40"><LoadingSpinner /> <p className="ml-2">Loading preferences...</p></div>;
  }

  if (error) {
    return <div className="text-red-500 p-4">Error: {error}</div>;
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Your Fashion Preferences</CardTitle>
        <CardDescription>Help us tailor recommendations for you.</CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-6">
          <div>
            <Label htmlFor="preferredStyles">Preferred Styles (comma-separated)</Label>
            <Input
              id="preferredStyles"
              value={preferredStyles}
              onChange={(e) => setPreferredStyles(e.target.value)}
              placeholder="e.g., casual, formal, bohemian"
            />
          </div>
          <div>
            <Label htmlFor="preferredColors">Preferred Colors (comma-separated)</Label>
            <Input
              id="preferredColors"
              value={preferredColors}
              onChange={(e) => setPreferredColors(e.target.value)}
              placeholder="e.g., blue, black, red"
            />
          </div>
          <div>
            <Label htmlFor="avoidedColors">Avoided Colors (comma-separated)</Label>
            <Input
              id="avoidedColors"
              value={avoidedColors}
              onChange={(e) => setAvoidedColors(e.target.value)}
              placeholder="e.g., yellow, orange"
            />
          </div>
          <fieldset className="border p-4 rounded-md">
            <legend className="text-sm font-medium px-1">Common Sizes</legend>
            <div className="space-y-4 mt-2">
              <div>
                <Label htmlFor="shirtSize">Shirt Size</Label>
                <Input
                  id="shirtSize"
                  value={shirtSize}
                  onChange={(e) => setShirtSize(e.target.value)}
                  placeholder="e.g., M, L, XL, 40"
                />
              </div>
              <div>
                <Label htmlFor="pantsWaistSize">Pants Waist Size</Label>
                <Input
                  id="pantsWaistSize"
                  value={pantsWaistSize}
                  onChange={(e) => setPantsWaistSize(e.target.value)}
                  placeholder="e.g., 32, 34, M"
                />
              </div>
              <div>
                <Label htmlFor="shoeSize">Shoe Size</Label>
                <Input
                  id="shoeSize"
                  value={shoeSize}
                  onChange={(e) => setShoeSize(e.target.value)}
                  placeholder="e.g., 10, 42, 7.5"
                />
              </div>
            </div>
          </fieldset>
        </CardContent>
        <CardFooter>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? <><LoadingSpinner size="sm" className="mr-2" /> Saving...</> : 'Save Preferences'}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
};

export default UserProfilePreferences;
