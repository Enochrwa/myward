import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { getAllUsers, getClothesByUserId } from '@/lib/admin';
import { User } from '@/types/userTypes';
import { Clothe } from '@/types/clotheTypes';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface AnalyticsData {
  totalUsers: number;
  totalClothes: number;
  clothesPerUser: { username: string; count: number }[];
  topCategories: { name: string; value: number }[];
  topOccasions: { name: string; value: number }[];
  topStyles: { name: string; value: number }[];
}

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#0088FE', '#00C49F'];

const AdminAnalytics = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      try {
        const users = await getAllUsers();
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
        })).sort((a, b) => b.count - a.count).slice(0, 10);

        const countByKey = (items: Clothe[], key: keyof Clothe) =>
          items.reduce((acc: Record<string, number>, item) => {
            const raw = item[key];
            const val = typeof raw === 'string' ? raw.replace(/['"]+/g, '').trim() : 'Unknown';
            acc[val] = (acc[val] || 0) + 1;
            return acc;
          }, {});

        const getTopN = (data: Record<string, number>, n: number) =>
          Object.entries(data)
            .sort(([, a], [, b]) => b - a)
            .slice(0, n)
            .map(([name, value]) => ({ name, value }));

        const topCategories = getTopN(countByKey(allClothes, 'category'), 5);
        const topOccasions = getTopN(countByKey(allClothes, 'occasion'), 5);
        const topStyles = getTopN(countByKey(allClothes, 'style'), 5);

        setAnalytics({
          totalUsers,
          totalClothes,
          clothesPerUser,
          topCategories,
          topOccasions,
          topStyles,
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
      <Card className="dark:bg-gray-800">
        <CardHeader>
          <CardTitle className="dark:text-white">Total Users</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-4xl font-bold dark:text-white">{analytics.totalUsers}</p>
        </CardContent>
      </Card>

      <Card className="dark:bg-gray-800">
        <CardHeader>
          <CardTitle className="dark:text-white">Total Clothes</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-4xl font-bold dark:text-white">{analytics.totalClothes}</p>
        </CardContent>
      </Card>

      <Card className="md:col-span-2 lg:col-span-4 dark:bg-gray-800">
        <CardHeader>
          <CardTitle className="dark:text-white">Top 10 Users by Clothes Count</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={analytics.clothesPerUser}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="username" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card className="md:col-span-2 dark:bg-gray-800">
        <CardHeader>
          <CardTitle className="dark:text-white">Top 5 Categories</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={analytics.topCategories} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} fill="#82ca9d" label>
                {analytics.topCategories.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card className="md:col-span-1 dark:bg-gray-800">
        <CardHeader>
          <CardTitle className="dark:text-white">Top 5 Styles</CardTitle>
        </CardHeader>
        <CardContent>
        <ResponsiveContainer width="100%" height={300}>
            <BarChart data={analytics.topStyles}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#ffc658" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card className="md:col-span-1 dark:bg-gray-800">
        <CardHeader>
          <CardTitle className="dark:text-white">Top 5 Occasions</CardTitle>
        </CardHeader>
        <CardContent>
        <ResponsiveContainer width="100%" height={300}>
            <BarChart data={analytics.topOccasions}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#ff8042" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminAnalytics;
