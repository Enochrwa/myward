import React, { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogClose } from '../ui/dialog';
import { Login } from './Login';
import { Registration } from './Registration';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialView?: 'login' | 'register';
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, initialView = 'login' }) => {
  const [view, setView] = useState<'login' | 'register'>(initialView);
  const { error, isLoading, user } = useAuth();

  const switchToRegister = () => setView('register');
  const switchToLogin = () => setView('login');

  useEffect(() => {
    if (isOpen) {
      setView(initialView);
    }
  }, [isOpen, initialView]);

  useEffect(() => {
    if (user && !isLoading && !error && isOpen) {
      onClose();
    }
  }, [user, isLoading, error, isOpen, onClose]);

  return (
    <Dialog open={isOpen} onOpenChange={(open) => { if (!open) onClose(); }}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto bg-gray-950">
        <DialogHeader>
          <DialogTitle>{view === 'login' ? 'Login' : 'Create Your Digital Wardrobe Profile'}</DialogTitle>
          <DialogDescription>
            {view === 'login' ? 'Enter your credentials to access your digital wardrobe.' : 'Tell us about yourself to get personalized outfit recommendations based on weather, occasion, and your style.'}
          </DialogDescription>
        </DialogHeader>

        {error && <p className="text-red-500 text-sm text-center py-2">{error}</p>}
        
        {view === 'login' ? (
          <Login switchToRegister={switchToRegister} />
        ) : (
          <Registration switchToLogin={switchToLogin} />
        )}
        <DialogClose asChild />
      </DialogContent>
    </Dialog>
  );
};
