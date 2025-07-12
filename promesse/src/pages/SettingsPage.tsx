
import React from 'react';
import AppSettings from '@/components/AppSettings';
import UserProfilePreferences from '@/components/UserProfilePreferences'; // Import the new component
import { Separator } from "@/components/ui/separator"


const SettingsPage = () => {
  return (
    <div className="container mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-8">Settings</h1>

      <div className="space-y-12">
        <section>
          <h2 className="text-2xl font-semibold text-gray-700 dark:text-gray-300 mb-6">App Settings</h2>
          <AppSettings />
        </section>

        <Separator />

        <section>
          <h2 className="text-2xl font-semibold text-gray-700 dark:text-gray-300 mb-6">Fashion Preferences</h2>
          <UserProfilePreferences />
        </section>
      </div>
    </div>
  );
};

export default SettingsPage;
