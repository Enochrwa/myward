import React, { createContext, useState, useEffect, ReactNode } from 'react';
import apiClient from '@/lib/apiClient'; // Added apiClient import

// Interfaces
export interface User {
  id: string;
  username: string;
  email: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
}

export interface AuthContextType extends AuthState {
  login: (credentials: any) => Promise<void>;
  register: (userData: any) => Promise<void>;
  logout: () => void;
}

// Default values for context
const defaultAuthState: AuthState = {
  user: null,
  token: null,
  isLoading: false,
  error: null,
};

export const AuthContext = createContext<AuthContextType>({
  ...defaultAuthState,
  login: async () => {},
  register: async () => {},
  logout: () => {},
});

// AuthProvider component
interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      // No need to setToken here, as fetchUserData will trigger re-renders if successful
      // and setToken is implicitly called via login/register or initial load.
      // The main purpose here is to validate the token and fetch user data.
      fetchUserData();
    }
  }, []);

  const fetchUserData = async () => { // Removed currentToken parameter
    setIsLoading(true);
    // setError(null); // Clear previous error before new attempt
    try {
      // apiClient will automatically use the token from localStorage
      const userData: User = await apiClient('/users/me');
      setUser(userData);
      setError(null); // Clear error on success
    } catch (err: any) {
      setError(err.message || 'Failed to fetch user data');
      setUser(null);
      setToken(null);
      localStorage.removeItem('token');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials: any) => {
    setIsLoading(true);
    setError(null);
    try {
      const { access_token: newToken } = await apiClient('/login', {
        method: 'POST',
        body: credentials,
      });
      localStorage.setItem('token', newToken);
      setToken(newToken); // Set token state
      await fetchUserData(); // fetchUserData will use apiClient which reads from localStorage
    } catch (err: any) {
      setError(err.message || 'An error occurred during login');
      setUser(null);
      setToken(null);
      localStorage.removeItem('token');
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData: any) => {
    setIsLoading(true);
    setError(null);
    try {
      // Assuming register endpoint returns a similar token structure or user data
      const responseData = await apiClient('/register', {
        method: 'POST',
        body: userData,
      });

      // If registration immediately returns a token (auto-login)
      if (responseData && responseData.access_token) {
        localStorage.setItem('token', responseData.access_token);
        setToken(responseData.access_token);
        await fetchUserData(); // fetchUserData will use apiClient which reads from localStorage
      } else {
        // Handle cases where registration does not auto-login
        // e.g., display a success message, require manual login, or if it returns user data directly:
        // if (responseData && responseData.user) { // Hypothetical structure
        //   setUser(responseData.user);
        // }
        // For now, assume registration implies a need to login separately or returns a token.
        // If it doesn't return a token, the user remains logged out.
        // setError('Registration successful. Please log in.'); // Example message
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred during registration');
      setUser(null);
      setToken(null);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    setError(null);
    // Optionally, call backend logout if it exists
    // fetch('/api/logout', { method: 'POST' });
  };

  const authState: AuthState = { user, token, isLoading, error };

  return (
    <AuthContext.Provider value={{ ...authState, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
