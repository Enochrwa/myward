
import React, { useState } from 'react';
import { Server, Database, Zap, Globe, AlertTriangle, CheckCircle, Clock, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface SystemComponent {
  id: string;
  name: string;
  status: 'healthy' | 'warning' | 'critical';
  uptime: string;
  lastCheck: string;
  responseTime: string;
  description: string;
  icon: any;
}

const AdminSystemHealth = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const systemComponents: SystemComponent[] = [
    {
      id: 'api',
      name: 'API Services',
      status: 'healthy',
      uptime: '99.97%',
      lastCheck: '2 minutes ago',
      responseTime: '145ms',
      description: 'Core API endpoints and services',
      icon: Server
    },
    {
      id: 'database',
      name: 'Database Cluster',
      status: 'healthy',
      uptime: '99.99%',
      lastCheck: '1 minute ago',
      responseTime: '23ms',
      description: 'Primary and replica databases',
      icon: Database
    },
    {
      id: 'ai',
      name: 'AI Recommendation Engine',
      status: 'warning',
      uptime: '98.12%',
      lastCheck: '5 minutes ago',
      responseTime: '2.3s',
      description: 'Machine learning and AI processing',
      icon: Zap
    },
    {
      id: 'cdn',
      name: 'Content Delivery Network',
      status: 'healthy',
      uptime: '99.89%',
      lastCheck: '1 minute ago',
      responseTime: '89ms',
      description: 'Global image and asset delivery',
      icon: Globe
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'critical': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return CheckCircle;
      case 'warning': return AlertTriangle;
      case 'critical': return AlertTriangle;
      default: return Clock;
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsRefreshing(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">System Health</h2>
          <p className="text-gray-600 dark:text-gray-400">Monitor system performance and status</p>
        </div>
        <Button 
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
        >
          <RefreshCw size={16} className={`mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
          Refresh Status
        </Button>
      </div>

      {/* Overall Status */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-4 h-4 bg-green-500 rounded-full animate-pulse"></div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">All Systems Operational</h3>
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* System Components */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {systemComponents.map((component) => {
          const StatusIcon = getStatusIcon(component.status);
          return (
            <div key={component.id} className="bg-white dark:bg-gray-800 rounded-xl p-6 border dark:border-gray-700">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">
                    <component.icon size={24} className="text-gray-600 dark:text-gray-300" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white">{component.name}</h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{component.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 ${getStatusColor(component.status)} rounded-full`}></div>
                  <StatusIcon size={16} className={
                    component.status === 'healthy' ? 'text-green-600' :
                    component.status === 'warning' ? 'text-yellow-600' : 'text-red-600'
                  } />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">Uptime</div>
                  <div className="font-semibold text-gray-900 dark:text-white">{component.uptime}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">Response Time</div>
                  <div className="font-semibold text-gray-900 dark:text-white">{component.responseTime}</div>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Last check: {component.lastCheck}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Performance Metrics */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Performance Metrics</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">99.8%</div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Overall Uptime</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">156ms</div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Avg Response</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">2.4K</div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Requests/min</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">12MB</div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Memory Usage</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminSystemHealth;
