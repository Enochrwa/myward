// src/components/AdminAllClothes.tsx
import React, { useEffect, useState } from 'react';
import { getAllUsers, getClothesByUserId } from '@/lib/admin';
import { User } from '@/types/userTypes';
import { Clothe } from '@/types/clotheTypes';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Image } from 'lucide-react';

const AdminAllClothes = () => {
  const [userClothes, setUserClothes] = useState<
    { user: User; clothes: Clothe[] }[]
  >([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const users = await getAllUsers();
        const data: { user: User; clothes: Clothe[] }[] = [];

        for (const user of users) {
          const clothes = await getClothesByUserId(user.id.toString());
          if (clothes) {
            data.push({ user, clothes });
          }
        }

        setUserClothes(data);
        setError(null);
      } catch (err: any) {
        console.error(err);
        setError('Failed to load clothes data.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div className="text-center py-10">Loading clothes...</div>;
  if (error) return <div className="text-red-500 text-center py-10">{error}</div>;

  return (
    <div className="space-y-8">
      {userClothes.map(({ user, clothes }) => (
        <Card key={user.id} className="shadow-lg">
          <CardHeader>
            <CardTitle className="text-xl font-bold">
              {user.username}'s Clothes ({clothes.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            {clothes.length === 0 ? (
              <p className="text-gray-500">No clothes uploaded.</p>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {clothes.map((clothe) => (
                  <div
                    key={clothe.id}
                    className="border rounded-lg p-2 bg-white dark:bg-gray-900 shadow-md"
                  >
                    <img
                      src={clothe.image_url}
                      alt={clothe.original_name || clothe.filename}
                      className="w-full h-40 object-cover rounded-md mb-2"
                    />
                    <div className="text-sm text-gray-700 dark:text-gray-200 space-y-1">
                      <p>
                        <span className="font-semibold">Category:</span>{' '}
                        {clothe.category}
                      </p>
                      <p>
                        <span className="font-semibold">Style:</span> {clothe.style}
                      </p>
                      <p>
                        <span className="font-semibold">Occasion:</span>{' '}
                        {clothe.occasion?.replace(/["']/g, '')}
                      </p>
                      <p>
                        <span className="font-semibold">Gender:</span> {clothe.gender}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default AdminAllClothes;
