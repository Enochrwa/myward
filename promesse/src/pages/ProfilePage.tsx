
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import UserProfile from '@/components/UserProfile';
import  LoadingSpinner  from '@/components/ui/loading'; // Assuming a loading spinner component exists

const ProfilePage = () => {
  const { user, isLoading, token } = useAuth(); // Destructure directly for convenience
  const navigate = useNavigate();

  useEffect(() => {
    // Redirect to home if not loading and no user/token is present
    // This check should be robust: might rely on token presence if user object is fetched async
    if (!isLoading && !token) {
      navigate('/');
    }
  }, [isLoading, token, navigate]);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!user) {
    // This case handles when loading is false, but user is still null (e.g. token exists but user fetch failed or is pending)
    // Or if redirect hasn't happened yet.
    // Depending on UX, could show a message or rely on the redirect.
    // For now, relying on redirect, but a message can be useful for debugging or specific scenarios.
    return (
        <div className="flex flex-col justify-center items-center h-screen">
            <p className="text-lg text-gray-600 dark:text-gray-400">Please log in to view your profile.</p>
            <p className="text-sm text-gray-500 dark:text-gray-300">Redirecting to homepage...</p>
        </div>
    );
  }

  return <UserProfile user={user} />;
};

export default ProfilePage;
