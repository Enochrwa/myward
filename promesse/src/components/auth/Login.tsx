import React, { useState, FormEvent } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { DialogFooter } from '../ui/dialog';

interface LoginProps {
  switchToRegister: () => void;
}

export const Login: React.FC<LoginProps> = ({ switchToRegister }) => {
  const { login, isLoading } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    if(username && password){
      await login({ username, password });
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <div className="grid gap-4 py-4">
        <div className="grid grid-cols-4 items-center gap-4">
          <Label htmlFor="username-login" className="text-right">
            Username
          </Label>
          <Input
            id="username-login"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
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
  );
};
