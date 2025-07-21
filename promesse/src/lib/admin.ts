// Admin API calls
import apiClient from './apiClient';
import { User } from '@/types/userTypes';

export const getAllUsers = async (): Promise<User[]> => {
  return apiClient('/admin/users');
};

export const updateUser = async (userId: string, role: string): Promise<User> => {
  return apiClient(`/admin/users/${userId}`, {
    method: 'PUT',
    body: { role },  // send { role: "admin" }
  });
};

export const deleteUser = async (userId: string): Promise<void> => {
  return apiClient(`/admin/users/${userId}`, {
    method: 'DELETE',
  });
};
