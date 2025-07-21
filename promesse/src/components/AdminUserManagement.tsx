
import React from 'react';
import { useUsers } from '../hooks/useUsers';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { User } from '../types/userTypes';
import { UserUpdatePayload } from '../lib/admin';

const AdminUserManagement = () => {
  const { users, loading, error, updateUser, deleteUser } = useUsers();

  if (loading) return <div>Loading users...</div>;
  if (error) return <div>Error fetching users: {error.message}</div>;

  
  const handleToggleAdmin = (user: User) => {
    const newRole = user.role === 'admin' ? 'user' : 'admin';
    updateUser(user.id.toString(), { role: newRole });
  };

  const handleDeleteUser = (userId: number) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      deleteUser(userId.toString());
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">User Management</h2>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>ID</TableHead>
            <TableHead>Username</TableHead>
            <TableHead>Email</TableHead>
            <TableHead>Full Name</TableHead>
            <TableHead>Gender</TableHead>
            <TableHead>Role</TableHead>
            <TableHead>Admin Actions</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {users.map((user: User) => (
            <TableRow key={user.id}>
              <TableCell>{user.id}</TableCell>
              <TableCell>{user.username}</TableCell>
              <TableCell>{user.email}</TableCell>
              <TableCell>{user.full_name}</TableCell>
              <TableCell>{user.gender}</TableCell>
              <TableCell>{user.role}</TableCell>
              <TableCell>
                <Button onClick={() => handleToggleAdmin(user)}>
                  {user.role === "admin" ? 'Revoke Admin' : 'Make Admin'}
                </Button>
              </TableCell>
              <TableCell>
                <Button variant="destructive" size="sm" onClick={() => handleDeleteUser(user.id)}>
                  Delete
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default AdminUserManagement;
