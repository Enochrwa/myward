import React, { useState, useEffect } from 'react';
import apiClient from '@/lib/apiClient';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface Clothe {
  id: string;
  filename: string;
  image_url: string;
  category: string;
  user_id: string;
  dominant_color: string;
}

const AdminAllClothes = () => {
  const [clothes, setClothes] = useState<Clothe[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUser, setSelectedUser] = useState<string | null>(null);

  useEffect(() => {
    const fetchClothes = async () => {
      try {
        setLoading(true);
        const response = await apiClient('/outfit/user-clothes');
        setClothes(response);
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch clothes');
      } finally {
        setLoading(false);
      }
    };

    fetchClothes();
  }, []);

  const users = Array.from(new Set(clothes.map((clothe) => clothe.user_id)));

  const filteredClothes = clothes
    .filter((clothe) =>
      clothe.category.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .filter((clothe) => !selectedUser || clothe.user_id === selectedUser);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>All Users' Clothes</CardTitle>
        <div className="flex space-x-4">
          <Input
            placeholder="Search by category..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="max-w-sm"
          />
          {
            users?.length > 0 &&
            <Select onValueChange={setSelectedUser} value={selectedUser || ''}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by user" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Users</SelectItem>
              {users.map((user) => (
                <SelectItem key={user} value={user}>
                  {user}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          }
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {filteredClothes.map((clothe) => (
            <div key={clothe.id} className="border rounded-lg p-2">
              <img
                src={clothe.image_url}
                alt={clothe.filename}
                className="w-full h-48 object-cover rounded-md"
              />
              <div className="mt-2">
                <p className="text-sm font-semibold">{clothe.category}</p>
                <p className="text-xs text-gray-500">User: {clothe.user_id}</p>
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
      </CardContent>
    </Card>
  );
};

export default AdminAllClothes;
