
import React, { useState } from 'react';
import { Users, Settings, Shirt, BarChart2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import AdminUserManagement from './AdminUserManagement';
import AdminAllClothes from './AdminAllClothes';
import AdminAnalytics from './AdminAnalytics';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('users');

  const tabs = [
    { id: 'users', label: 'User Management', icon: Users },
    { id: 'clothes', label: 'All Clothes', icon: Shirt },
    { id: 'analytics', label: 'Analytics', icon: BarChart2 },
  
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-200 dark:from-gray-900 dark:to-black p-4 sm:p-8 transition-colors duration-500">
      <div className="max-w-8xl mx-auto">
        <header className="mb-10 text-center">
          <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-800 dark:text-white tracking-tight">
            Admin Dashboard
          </h1>
          <p className="text-md sm:text-lg text-gray-500 dark:text-gray-400 mt-2">
            Welcome back, Admin! Here's what's happening on your platform.
          </p>
        </header>

        <nav className="mb-8">
          <div className="flex flex-wrap justify-center space-x-1 sm:space-x-2 bg-white dark:bg-gray-800 p-2 rounded-xl shadow-md">
            {tabs.map((tab) => {
              const IconComponent = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 text-center py-3 px-4 rounded-lg font-semibold transition-all duration-300 flex items-center justify-center space-x-2 transform hover:scale-105 ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg'
                      : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <IconComponent size={20} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </nav>

        <main className="transition-opacity duration-500 ease-in-out">
          {activeTab === 'users' && <AdminUserManagement />}
          {activeTab === 'clothes' && <AdminAllClothes />}
          {activeTab === 'analytics' && <AdminAnalytics />}
        </main>
      </div>
    </div>
  );
};

export default AdminDashboard;
