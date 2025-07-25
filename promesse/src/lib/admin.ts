// Admin API calls
import apiClient from './apiClient';
import { User } from '@/types/userTypes';
import { Clothe } from '@/types/clotheTypes';


// This type should align with the backend's UserUpdate schema
export interface UserUpdatePayload {
  username?: string;
  email?: string;
  full_name?: string;
  gender?: string;
  role?: string;
}

export const getAllUsers = async (): Promise<User[]> => {
  try {
    const response = await apiClient('/admin/users');
    return response;
  } catch (error) {
    console.error('Error fetching users:', error);
    throw error;
  }
};

export const getClothesByUserId = async (userId: string): Promise<Clothe[]> => {
  try {
    const response = await apiClient(`/outfit/user-clothes-admin/${userId}`);
    console.log("User Images: ", response?.data?.data)
    return response?.data;
  } catch (error) {
    console.error(`Error fetching clothes for user ${userId}:`, error);
    throw error;
  }
};

export const updateUser = async (
  userId: string,
  updates: UserUpdatePayload
): Promise<User> => {
  try {
    const response = await apiClient(`/admin/users/${userId}`, {
      method: 'PUT',
      body: updates,
    });
    return response;
  } catch (error) {
    console.error(`Error updating user ${userId}:`, error);
    throw error;
  }
};

export const deleteUser = async (userId: string): Promise<void> => {
  try {
    await apiClient(`/admin/users/${userId}`, {
      method: 'DELETE',
    });
  } catch (error) {
    console.error(`Error deleting user ${userId}:`, error);
    throw error;
  }
};
