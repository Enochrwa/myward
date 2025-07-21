import React, { useState, FormEvent } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { DialogFooter } from '../ui/dialog';

interface RegistrationProps {
  switchToLogin: () => void;
}

export const Registration: React.FC<RegistrationProps> = ({ switchToLogin }) => {
  const { register, isLoading } = useAuth();

  const [regEmail, setRegEmail] = useState('');
  const [regUsername, setRegUsername] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [gender, setGender] = useState('');

  const handleRegister = async (e: FormEvent) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('username', regUsername);
    formData.append('email', regEmail);
    formData.append('password', regPassword);
    formData.append('full_name', fullName);
    formData.append('gender', gender);

    await register(formData);
    window.location.reload();
  };

  return (
    <form onSubmit={handleRegister} className="space-y-6">
      <Card className="bg-gray-900 border-gray-700">
        <CardHeader>
          <CardTitle className="text-lg">Create your account</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="fullName">Full Name</Label>
            <Input
              id="fullName"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="bg-gray-700"
              required
            />
          </div>
          <div>
            <Label htmlFor="regUsername">Username</Label>
            <Input
              id="regUsername"
              value={regUsername}
              onChange={(e) => setRegUsername(e.target.value)}
              className="bg-gray-700"
              required
            />
          </div>
          <div>
            <Label htmlFor="regEmail">Email</Label>
            <Input
              id="regEmail"
              type="email"
              value={regEmail}
              onChange={(e) => setRegEmail(e.target.value)}
              className="bg-gray-700"
              required
            />
          </div>
          <div>
            <Label htmlFor="regPassword">Password</Label>
            <Input
              id="regPassword"
              type="password"
              value={regPassword}
              onChange={(e) => setRegPassword(e.target.value)}
              className="bg-gray-700"
              required
            />
          </div>
          <div>
            <Label htmlFor="gender">Gender</Label>
            <Select value={gender} onValueChange={setGender}>
              <SelectTrigger className="bg-gray-700">
                <SelectValue placeholder="Select gender" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="male">Male</SelectItem>
                <SelectItem value="female">Female</SelectItem>
                <SelectItem value="non-binary">Non-binary</SelectItem>
                <SelectItem value="prefer-not-to-say">Prefer not to say</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <DialogFooter>
        <div className="flex justify-between w-full">
          <Button type="button" variant="link" onClick={switchToLogin}>
            Already have an account? Login
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Creating account...' : 'Create Account'}
          </Button>
        </div>
      </DialogFooter>
    </form>
  );
};
