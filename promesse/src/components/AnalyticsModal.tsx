import React, { useState } from 'react';
import { X, TrendingUp, Users, Calendar, Download, Filter, BarChart3, PieChart, Activity } from 'lucide-react';
import { PieChart as RechartsPieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';

interface AnalyticsModalProps {
  isOpen: boolean;
  onClose: () => void;
  wardrobeItems: any[];
}

interface KeyMetric {
  label: string;
  value: string;
  change: string;
  changeColor: string;
  icon: any;
  bgColor: string;
}

interface CategoryData {
  name: string;
  value: number;
  color: string;
}

interface WeeklyUsage {
  day: string;
  outfits: number;
}

interface TrendData {
  month: string;
  outfits: number;
  items: number;
}

const AnalyticsModal = ({ isOpen, onClose, wardrobeItems }: AnalyticsModalProps) => {
  const [selectedMetric, setSelectedMetric] = useState('overview');
  const [timeRange, setTimeRange] = useState('7days');

  // Calculate real metrics from wardrobeItems
  const totalItems = wardrobeItems.length;
  const totalValue = wardrobeItems.reduce((sum, item) => sum + (item.price || 0), 0);
  const avgValue = totalItems > 0 ? totalValue / totalItems : 0;
  const mostWornItem = wardrobeItems.reduce((prev, current) => 
    ((prev?.timesWorn || 0) > (current?.timesWorn || 0)) ? prev : current, wardrobeItems[0]
  );
  const favoriteItems = wardrobeItems.filter(item => item.favorite).length;

  const keyMetrics: KeyMetric[] = [
    {
      label: 'Total Items',
      value: totalItems.toString(),
      change: '+12%',
      changeColor: 'text-green-600',
      icon: TrendingUp,
      bgColor: 'bg-gradient-to-r from-green-100 to-green-300 dark:from-green-900 dark:to-green-700'
    },
    {
      label: 'Most Worn Item',
      value: mostWornItem?.name || 'N/A',
      change: `${mostWornItem?.timesWorn || 0} times`,
      changeColor: 'text-blue-600',
      icon: Users,
      bgColor: 'bg-gradient-to-r from-blue-100 to-blue-300 dark:from-blue-900 dark:to-blue-700'
    },
    {
      label: 'Avg. Item Value',
      value: `$${avgValue.toFixed(0)}`,
      change: '-5%',
      changeColor: 'text-red-600',
      icon: Calendar,
      bgColor: 'bg-gradient-to-r from-red-100 to-red-300 dark:from-red-900 dark:to-red-700'
    },
    {
      label: 'Total Value',
      value: `$${totalValue.toFixed(0)}`,
      change: '+22%',
      changeColor: 'text-purple-600',
      icon: TrendingUp,
      bgColor: 'bg-gradient-to-r from-purple-100 to-purple-300 dark:from-purple-900 dark:to-purple-700'
    }
  ];

  // Calculate category distribution from actual data
  const categoryCount = wardrobeItems.reduce((acc, item) => {
    const category = item.category || 'other';
    acc[category] = (acc[category] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const categoryData: CategoryData[] = Object.entries(categoryCount).map(([name, value], index) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value: value as number,
    color: ['#8B5CF6', '#10B981', '#8B5CF6', '#EF4444', '#3B82F6'][index % 5]
  }));

  const weeklyUsage: WeeklyUsage[] = [
    { day: 'Mon', outfits: 12 },
    { day: 'Tue', outfits: 15 },
    { day: 'Wed', outfits: 9 },
    { day: 'Thu', outfits: 18 },
    { day: 'Fri', outfits: 22 },
    { day: 'Sat', outfits: 28 },
    { day: 'Sun', outfits: 20 },
  ];

  const trendData: TrendData[] = [
    { month: 'Jan', outfits: 50, items: 230 },
    { month: 'Feb', outfits: 65, items: 280 },
    { month: 'Mar', outfits: 80, items: 310 },
    { month: 'Apr', outfits: 60, items: 250 },
    { month: 'May', outfits: 75, items: 300 },
    { month: 'Jun', outfits: 90, items: 340 },
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-3xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-6 text-white">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">Advanced Analytics</h2>
              <p className="opacity-90">Comprehensive wardrobe insights and trends</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-xl transition-colors"
            >
              <X size={24} />
            </button>
          </div>
        </div>

        <div className="flex flex-col lg:flex-row h-[calc(90vh-120px)]">
          {/* Sidebar */}
          <div className="w-full lg:w-64 bg-gray-50 dark:bg-gray-800 p-4 border-r dark:border-gray-700">
            <div className="space-y-2">
              {[
                { id: 'overview', label: 'Overview', icon: BarChart3 },
                { id: 'usage', label: 'Usage Patterns', icon: Activity },
                { id: 'trends', label: 'Trends', icon: TrendingUp },
                { id: 'performance', label: 'Performance', icon: PieChart }
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => setSelectedMetric(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-colors ${
                    selectedMetric === item.id
                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                      : 'text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                  }`}
                >
                  <item.icon size={20} />
                  <span className="font-medium">{item.label}</span>
                </button>
              ))}
            </div>

            {/* Time Range Selector */}
            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Time Range
              </label>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg"
              >
                <option value="7days">Last 7 days</option>
                <option value="30days">Last 30 days</option>
                <option value="90days">Last 90 days</option>
                <option value="1year">Last year</option>
              </select>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 p-6 overflow-y-auto">
            {selectedMetric === 'overview' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
                  {keyMetrics.map((metric, index) => (
                    <div key={index} className="bg-white dark:bg-gray-800 rounded-xl p-6 border dark:border-gray-700">
                      <div className="flex items-center justify-between mb-4">
                        <div className={`p-3 rounded-xl ${metric.bgColor}`}>
                          <metric.icon className="text-white" size={24} />
                        </div>
                        <span className={`text-sm font-bold ${metric.changeColor}`}>
                          {metric.change}
                        </span>
                      </div>
                      <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                        {metric.value}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        {metric.label}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Charts */}
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                  <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border dark:border-gray-700">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Category Distribution</h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <RechartsPieChart>
                        <Pie
                          data={categoryData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        >
                          {categoryData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </RechartsPieChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border dark:border-gray-700">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Weekly Usage</h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={weeklyUsage}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="day" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="outfits" fill="#8B5CF6" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            )}

            {selectedMetric === 'usage' && (
              <div className="space-y-6">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">Usage Patterns</h3>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border dark:border-gray-700">
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={trendData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="outfits" stroke="#8B5CF6" strokeWidth={3} />
                      <Line type="monotone" dataKey="items" stroke="#10B981" strokeWidth={3} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {(selectedMetric === 'trends' || selectedMetric === 'performance') && (
              <div className="text-center py-12">
                <div className="text-gray-500 dark:text-gray-400">
                  {selectedMetric === 'trends' ? 'Trend analysis' : 'Performance metrics'} coming soon...
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="border-t dark:border-gray-700 p-4 bg-gray-50 dark:bg-gray-800">
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Last updated: {new Date().toLocaleDateString()}
            </div>
            <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:shadow-lg transition-all">
              <Download size={16} />
              Export Report
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsModal;
