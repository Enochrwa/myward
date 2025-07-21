import React, { useState } from 'react';
import { X, TrendingUp, Users, Calendar, Download, Filter, BarChart3, PieChart as PieChartIcon, Activity, Loader2 } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import { useWardrobeAnalytics } from '@/hooks/useWardrobeAnalytics';

interface AnalyticsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const COLORS = ['#8B5CF6', '#10B981', '#EF4444', '#3B82F6', '#F97316'];

const AdvancedAnalyticsModal = ({ isOpen, onClose }: AnalyticsModalProps) => {
  const [selectedMetric, setSelectedMetric] = useState('overview');
  const [timeRange, setTimeRange] = useState('30days');
  const { analytics, items, loading, error } = useWardrobeAnalytics();

  if (!isOpen) return null;

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <div className="bg-white dark:bg-gray-900 rounded-3xl shadow-2xl max-w-6xl w-full max-h-[90vh] flex items-center justify-center">
          <Loader2 className="w-12 h-12 text-purple-500 animate-spin" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <div className="bg-white dark:bg-gray-900 rounded-3xl shadow-2xl max-w-6xl w-full max-h-[90vh] flex flex-col items-center justify-center">
          <p className="text-red-500">{error}</p>
          <button onClick={onClose} className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg">Close</button>
        </div>
      </div>
    );
  }

  const keyMetrics = [
    {
      label: 'Total Items',
      value: analytics?.total_images.toString() || '0',
      change: '+12%',
      changeColor: 'text-green-600',
      icon: TrendingUp,
      bgColor: 'bg-gradient-to-r from-green-100 to-green-300 dark:from-green-900 dark:to-green-700'
    },
    {
        label: 'Total Size',
        value: `${analytics?.total_size_mb.toFixed(2) || '0'} MB`,
        change: '',
        changeColor: 'text-blue-600',
        icon: Users,
        bgColor: 'bg-gradient-to-r from-blue-100 to-blue-300 dark:from-blue-900 dark:to-blue-700'
      },
      {
        label: 'Avg Width',
        value: `${analytics?.average_dimensions.width.toFixed(0) || '0'} px`,
        change: '',
        changeColor: 'text-red-600',
        icon: Calendar,
        bgColor: 'bg-gradient-to-r from-red-100 to-red-300 dark:from-red-900 dark:to-red-700'
      },
      {
        label: 'Avg Height',
        value: `${analytics?.average_dimensions.height.toFixed(0) || '0'} px`,
        change: '',
        changeColor: 'text-purple-600',
        icon: TrendingUp,
        bgColor: 'bg-gradient-to-r from-purple-100 to-purple-300 dark:from-purple-900 dark:to-purple-700'
      }
  ];

  const categoryData = analytics?.category_distribution.map((item, index) => ({
    name: item.category,
    value: item.count,
    color: COLORS[index % COLORS.length]
  }));

  const styleData = analytics?.style_distribution.map((item, index) => ({
    name: item.style,
    value: item.count,
    color: COLORS[index % COLORS.length]
    }));

  const uploadTrends = analytics?.upload_trends.map(item => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    count: item.count
  })).reverse();

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
                { id: 'trends', label: 'Trends', icon: TrendingUp },
                { id: 'style', label: 'Style Analysis', icon: PieChartIcon }
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
                      <PieChart>
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
                          {categoryData?.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border dark:border-gray-700">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Upload Trends (Last 30 Days)</h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={uploadTrends}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="#8B5CF6" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            )}

            {selectedMetric === 'trends' && (
              <div className="space-y-6">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">Upload Trends</h3>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border dark:border-gray-700">
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={uploadTrends}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="count" stroke="#8B5CF6" strokeWidth={3} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {selectedMetric === 'style' && (
              <div className="space-y-6">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">Style Analysis</h3>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border dark:border-gray-700">
                  <ResponsiveContainer width="100%" height={400}>
                    <PieChart>
                      <Pie
                        data={styleData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={120}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {styleData?.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
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

export default AdvancedAnalyticsModal;
