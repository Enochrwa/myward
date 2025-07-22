
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
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-900 dark:to-black p-8">
      <div className="max-w-8xl mx-auto">
        <header className="mb-10">
          <h1 className="text-5xl font-extrabold text-gray-800 dark:text-white tracking-tight">
            Admin Dashboard
          </h1>
          <p className="text-lg text-gray-500 dark:text-gray-400 mt-2">
            Welcome back, Admin! Here's what's happening on your platform.
          </p>
        </header>

        <nav className="mb-8">
          <div className="flex space-x-2 bg-white dark:bg-gray-800 p-2 rounded-xl shadow-md">
            {tabs.map((tab) => {
              const IconComponent = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 text-center py-3 px-4 rounded-lg font-semibold transition-all duration-300 flex items-center justify-center space-x-2 ${
                    activeTab === tab.id
                      ? 'bg-blue-600 text-white shadow-lg'
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

        <main className="animate-fade-in">
          {activeTab === 'users' && <AdminUserManagement />}
          {activeTab === 'clothes' && <AdminAllClothes />}
          {activeTab === 'analytics' && <AdminAnalytics />}
          {activeTab === 'settings' && (
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="text-2xl font-bold">System Settings</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 dark:text-gray-400">
                  Advanced system configuration options will be available here.
                </p>
              </CardContent>
            </Card>
          )}
        </main>
      </div>
    </div>
  );
};

export default AdminDashboard;
