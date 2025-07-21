
import React from 'react';
import { useUsers } from '../hooks/useUsers';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { User } from '../types/userTypes';

const AdminUserManagement = () => {
  const { users, loading, error, updateUser, deleteUser } = useUsers();

  if (loading) return <div>Loading users...</div>;
  if (error) return <div>Error fetching users: {error.message}</div>;

  const handleToggleAdmin = (user: User) => {
    updateUser(user.id.toString(), { is_admin: !user.is_admin });
  };

  const handleDeleteUser = (userId: number) => {
    deleteUser(userId.toString());
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
            <TableHead>Admin</TableHead>
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
              <TableCell>
                <Button onClick={() => handleToggleAdmin(user)}>
                  {user.is_admin ? 'Revoke Admin' : 'Make Admin'}
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
