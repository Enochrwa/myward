import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { getAllUsers, getClothesByUserId } from '@/lib/admin';
import { User } from '@/types/userTypes';
import { Clothe } from '@/types/clotheTypes';

interface AnalyticsData {
  totalUsers: number;
  totalClothes: number;
  clothesPerUser: { username: string; count: number }[];
  topCategories: { category: string; count: number }[];
  topOccasions: { occasion: string; count: number }[];
  topStyles: { style: string; count: number }[];
}

const AdminAnalytics = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      try {
        const users = await getAllUsers();
        // console.log("All users: ", users);
        let allClothes: Clothe[] = [];

        for (const user of users) {
          const userClothes = await getClothesByUserId(user.id.toString());
          
          if (userClothes) {
            allClothes = [...allClothes, ...userClothes];
          }
        }

        const totalUsers = users.length;
        const totalClothes = allClothes.length;

        const clothesPerUser = users.map((user) => ({
          username: user.username,
          count: allClothes.filter((clothe) => clothe.user_id.toString() === user.id.toString()).length,
        }));

        const countByKey = (
          items: Clothe[],
          key: keyof Clothe,
          topN: number = 5
        ): { [key: string]: number } =>
          items.reduce((acc: Record<string, number>, item) => {
            const raw = item[key];
            const val = typeof raw === 'string' ? raw.replace(/['"]+/g, '').trim() : 'Unknown';
            acc[val] = (acc[val] || 0) + 1;
            return acc;
          }, {});

        const top = (obj: Record<string, number>) =>
          Object.entries(obj)
            .map(([key, count]) => ({ [key]: count }))
            .flat()
            .sort((a, b) => Object.values(b)[0] - Object.values(a)[0])
            .slice(0, 5);

        const topCategories = top(countByKey(allClothes, 'category'));
        const topOccasions = top(countByKey(allClothes, 'occasion'));
        const topStyles = top(countByKey(allClothes, 'style'));

        setAnalytics({
          totalUsers,
          totalClothes,
          clothesPerUser,
          topCategories: topCategories.map((entry) => ({
            category: Object.keys(entry)[0],
            count: Object.values(entry)[0],
          })),
          topOccasions: topOccasions.map((entry) => ({
            occasion: Object.keys(entry)[0],
            count: Object.values(entry)[0],
          })),
          topStyles: topStyles.map((entry) => ({
            style: Object.keys(entry)[0],
            count: Object.values(entry)[0],
          })),
        });
        setError(null);
      } catch (err: any) {
        console.error(err);
        setError('Failed to load analytics data.');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (loading) return <div className="text-center py-10">Loading analytics...</div>;
  if (error) return <div className="text-red-500 text-center py-10">{error}</div>;
  if (!analytics) return <div className="text-center py-10">No analytics data found.</div>;

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader>
          <CardTitle>Total Users</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-4xl font-bold">{analytics.totalUsers}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Total Clothes</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-4xl font-bold">{analytics.totalClothes}</p>
        </CardContent>
      </Card>

      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>Clothes Per User</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            {analytics.clothesPerUser.map((user) => (
              <li key={user.username} className="flex justify-between">
                <span>{user.username}</span>
                <span className="font-semibold">{user.count}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>Top 5 Categories</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            {analytics.topCategories.map((c) => (
              <li key={c.category} className="flex justify-between">
                <span>{c.category}</span>
                <span className="font-semibold">{c.count}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Top Styles</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            {analytics.topStyles.map((s) => (
              <li key={s.style} className="flex justify-between">
                <span>{s.style}</span>
                <span className="font-semibold">{s.count}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Top Occasions</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            {analytics.topOccasions.map((o) => (
              <li key={o.occasion} className="flex justify-between">
                <span>{o.occasion}</span>
                <span className="font-semibold">{o.count}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminAnalytics;
