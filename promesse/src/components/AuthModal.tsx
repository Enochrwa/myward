import React, { useState, FormEvent } from 'react';
import { useAuth } from '../hooks/useAuth'; // Changed from useContext to useAuth
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription, DialogClose } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialView?: 'login' | 'register';
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, initialView = 'login' }) => {
  const [view, setView] = useState<'login' | 'register'>(initialView);
  const { login, register, error, isLoading, user } = useAuth(); // Used useAuth and added user

  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    await login({ emailOrUsername: email, password }); // Assuming backend expects emailOrUsername
    // User state will be updated by AuthContext, triggering useEffect below
  };

  const handleRegister = async (e: FormEvent) => {
    e.preventDefault();
    await register({ username, email, password });
    // User state will be updated by AuthContext, triggering useEffect below
  };

  const resetForm = () => {
    setEmail('');
    setUsername('');
    setPassword('');
  }

  const switchToRegister = () => {
    setView('register');
    resetForm();
  };

  const switchToLogin = () => {
    setView('login');
    resetForm();
  };

  // Reset view when modal is closed/opened, and close on successful login/registration
  React.useEffect(() => {
    if (isOpen) {
      setView(initialView);
      resetForm();
    }
  }, [isOpen, initialView]);

  React.useEffect(() => {
    // Close modal if login/registration was successful (user is set and no loading/error)
    if (user && !isLoading && !error && isOpen) {
      onClose();
      resetForm();
    }
  }, [user, isLoading, error, isOpen, onClose]);

  return (
    <Dialog open={isOpen} onOpenChange={(open) => { if (!open) onClose(); }}>
      <DialogContent className="sm:max-w-[425px] bg-gray-950">
        <DialogHeader>
          <DialogTitle>{view === 'login' ? 'Login' : 'Register'}</DialogTitle>
          <DialogDescription>
            {view === 'login' ? 'Enter your credentials to login.' : 'Create a new account.'}
          </DialogDescription>
        </DialogHeader>
        {error && <p className="text-red-500 text-sm text-center py-2">{error}</p>}
        {view === 'login' ? (
          <form onSubmit={handleLogin}>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="email-login" className="text-right">
                  Email or Username
                </Label>
                <Input
                  id="email-login"
                  type="text" // Allow both email and username
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="col-span-3 bg-gray-700"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="password-login" className="text-right">
                  Password
                </Label>
                <Input
                  id="password-login"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="col-span-3 bg-gray-700"
                  required
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="link" onClick={switchToRegister}>
                Create an account
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? 'Logging in...' : 'Login'}
              </Button>
            </DialogFooter>
          </form>
        ) : (
          <form onSubmit={handleRegister}>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="username-register" className="text-right">
                  Username
                </Label>
                <Input
                  id="username-register"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="col-span-3 bg-gray-700"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="email-register" className="text-right">
                  Email
                </Label>
                <Input
                  id="email-register"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="col-span-3 bg-gray-700"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="password-register" className="text-right">
                  Password
                </Label>
                <Input
                  id="password-register"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="col-span-3 bg-gray-700"
                  required
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="link" onClick={switchToLogin}>
                Already have an account? Login
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? 'Registering...' : 'Register'}
              </Button>
            </DialogFooter>
          </form>
        )}
         <DialogClose asChild>
            {/* This is an invisible button to allow Dialog's default close behavior if needed,
                but our onClose prop handles closing. We can also call onClose directly.
                Ensure this doesn't interfere with form submissions.
            */}
         </DialogClose>
      </DialogContent>
    </Dialog>
  );
};
