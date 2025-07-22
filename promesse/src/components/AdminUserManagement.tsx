
import React, { useState } from 'react';
import { useUsers } from '../hooks/useUsers';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { User } from '../types/userTypes';
import apiClient from '@/lib/apiClient';
import { Clothe } from '@/types/clotheTypes';
import { getClothesByUserId } from '@/lib/admin';

import { ChevronDown, ChevronUp } from 'lucide-react';

const UserClothes = ({ userId, clothes }: { userId: string; clothes: Clothe[] | null }) => {
  if (!clothes) {
    return (
      <TableRow>
        <TableCell colSpan={8} className="text-center">
          Loading clothes...
        </TableCell>
      </TableRow>
    );
  }

  if (clothes.length === 0) {
    return (
      <TableRow>
        <TableCell colSpan={8} className="text-center">
          This user has no clothes.
        </TableCell>
      </TableRow>
    );
  }

  return (
    <TableRow>
      <TableCell colSpan={8}>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 p-4">
          {clothes.map((clothe) => (
            <div key={clothe.id} className="border rounded-lg p-2">
              <img
                src={clothe.image_url}
                alt={clothe.filename}
                className="w-full h-48 object-cover rounded-md"
              />
              <div className="mt-2">
                <p className="text-sm font-semibold">{clothe.category}</p>
                <div className="flex items-center mt-1">
                  <div
                    className="w-4 h-4 rounded-full mr-2"
                    style={{ backgroundColor: clothe.dominant_color }}
                  />
                  <p className="text-xs">{clothe.dominant_color}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </TableCell>
    </TableRow>
  );
};

const AdminUserManagement = () => {
  const { users, loading, error, updateUser, deleteUser } = useUsers();
  const [visibleClothes, setVisibleClothes] = useState<Record<string, Clothe[] | null>>({});

  const toggleClothesVisibility = async (userId: string) => {
    if (visibleClothes[userId]) {
      setVisibleClothes((prev) => ({ ...prev, [userId]: undefined }));
    } else {
      setVisibleClothes((prev) => ({ ...prev, [userId]: null }));
      try {
        const clothes = await apiClient(`/outfit/user-clothes/${userId}`);
        console.log("User Items: ", clothes)
        setVisibleClothes((prev) => ({ ...prev, [userId]: clothes }));
      } catch (error) {
        console.error('Failed to fetch clothes for user', userId, error);
        setVisibleClothes((prev) => ({ ...prev, [userId]: [] }));
      }
    }
  };

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


  // console.log("All users: ", users);
  // const userItems = getClothesByUserId("5");
  // console.log("All User Items: ", userItems);

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">User Management</h2>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead />
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
            <React.Fragment key={user.id}>
              <TableRow>
                <TableCell>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => toggleClothesVisibility(user.id.toString())}
                  >
                    {visibleClothes[user.id.toString()] ? (
                      <ChevronUp size={16} />
                    ) : (
                      <ChevronDown size={16} />
                    )}
                  </Button>
                </TableCell>
                <TableCell>{user.id}</TableCell>
                <TableCell>{user.username}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>{user.full_name}</TableCell>
                <TableCell>{user.gender}</TableCell>
                <TableCell>{user.role}</TableCell>
                <TableCell>
                  <Button onClick={() => handleToggleAdmin(user)}>
                    {user.role === 'admin' ? 'Revoke Admin' : 'Make Admin'}
                  </Button>
                </TableCell>
                <TableCell>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => handleDeleteUser(user.id)}
                  >
                    Delete
                  </Button>
                </TableCell>
              </TableRow>
              {visibleClothes[user.id.toString()] !== undefined && (
                <UserClothes userId={user.id.toString()} clothes={visibleClothes[user.id.toString()]} />
              )}
            </React.Fragment>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default AdminUserManagement;
