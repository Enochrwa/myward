import React, { useState, useEffect } from 'react';
import { Loader2, BarChart, PieChart, Shirt, Palette, TrendingUp, Calendar } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Pie, Bar } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

interface AnalyticsData {
  total_images: number;
  color_distribution: { dominant_color: string; count: number }[];
  category_distribution: { category: string; count:number }[];
  style_distribution: { style: string; count: number }[];
  season_distribution: { season: string; count: number }[];
}

const ClotheAnalytics: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(false);

  const API_BASE = 'http://localhost:8000/api';

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/analytics`);
      const data = await response.json();
      setAnalytics(data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const colorChartData = {
    labels: analytics?.color_distribution.map(c => c.dominant_color),
    datasets: [
      {
        label: 'Colors',
        data: analytics?.color_distribution.map(c => c.count),
        backgroundColor: analytics?.color_distribution.map(c => c.dominant_color),
        borderColor: '#ffffff',
        borderWidth: 1,
      },
    ],
  };

  const categoryChartData = {
    labels: analytics?.category_distribution.map(c => c.category),
    datasets: [
      {
        label: 'Categories',
        data: analytics?.category_distribution.map(c => c.count),
        backgroundColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0',
          '#9966FF',
          '#FF9F40'
        ],
        borderColor: '#ffffff',
        borderWidth: 1,
      },
    ],
  };

  const styleChartData = {
    labels: analytics?.style_distribution.map(s => s.style),
    datasets: [
      {
        label: 'Styles',
        data: analytics?.style_distribution.map(s => s.count),
        backgroundColor: '#36A2EB',
      },
    ],
  };

  const seasonChartData = {
    labels: analytics?.season_distribution.map(s => s.season),
    datasets: [
      {
        label: 'Seasons',
        data: analytics?.season_distribution.map(s => s.count),
        backgroundColor: '#FFCE56',
      },
    ],
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-800 text-white">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-8 text-center">Your Wardrobe Analytics</h1>

        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
          </div>
        ) : analytics ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <Card className="bg-gray-800/50 border-gray-700">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-gray-300">Total Items</CardTitle>
                  <Shirt className="h-4 w-4 text-gray-400" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analytics.total_images}</div>
                </CardContent>
              </Card>
              {/* Add more summary cards here if needed */}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <Card className="bg-gray-800/50 border-gray-700">
                <CardHeader>
                  <CardTitle className="flex items-center"><Palette className="mr-2" /> Color Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <div style={{ height: '300px' }}>
                    <Pie data={colorChartData} options={{ maintainAspectRatio: false, plugins: { legend: { display: false } } }} />
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-gray-800/50 border-gray-700">
                <CardHeader>
                  <CardTitle className="flex items-center"><Shirt className="mr-2" /> Category Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                    <div style={{ height: '300px' }}>
                        <Pie data={categoryChartData} options={{ maintainAspectRatio: false }} />
                    </div>
                </CardContent>
              </Card>
              <Card className="bg-gray-800/50 border-gray-700">
                <CardHeader>
                  <CardTitle className="flex items-center"><TrendingUp className="mr-2" /> Style Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                    <div style={{ height: '300px' }}>
                        <Bar data={styleChartData} options={{ maintainAspectRatio: false }} />
                    </div>
                </CardContent>
              </Card>
              <Card className="bg-gray-800/50 border-gray-700">
                <CardHeader>
                  <CardTitle className="flex items-center"><Calendar className="mr-2" /> Season Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                    <div style={{ height: '300px' }}>
                        <Bar data={seasonChartData} options={{ maintainAspectRatio: false }} />
                    </div>
                </CardContent>
              </Card>
            </div>
          </>
        ) : (
          <div className="text-center py-20">
            <p>No analytics data found.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ClotheAnalytics;