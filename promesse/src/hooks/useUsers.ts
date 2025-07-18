import { useState, useEffect } from 'react';
import { User } from '@/types/userTypes';
import { getAllUsers, updateUser, deleteUser } from '@/lib/admin';

export const useUsers = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const users = await getAllUsers();
        setUsers(users);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  const handleUpdateUser = async (userId: string, updates: Partial<User>) => {
    try {
      const updatedUser = await updateUser(userId, updates);
      setUsers(users.map((user) => (user.id === userId ? updatedUser : user)));
    } catch (err) {
      setError(err as Error);
    }
  };

  const handleDeleteUser = async (userId: string) => {
    try {
      await deleteUser(userId);
      setUsers(users.filter((user) => user.id !== userId));
    } catch (err) {
      setError(err as Error);
    }
  };

  return {
    users,
    loading,
    error,
    updateUser: handleUpdateUser,
    deleteUser: handleDeleteUser,
  };
};
