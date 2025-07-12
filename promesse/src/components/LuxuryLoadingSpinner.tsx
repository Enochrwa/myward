
import React from 'react';

interface LuxuryLoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

const LuxuryLoadingSpinner = ({ size = 'md', text }: LuxuryLoadingSpinnerProps) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16'
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative">
        <div className={`${sizeClasses[size]} rounded-full border-4 border-owis-purple/30 border-t-owis-purple animate-spin`}></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className={`rounded-full bg-white ${
            size === 'sm' ? 'w-3 h-3' : size === 'md' ? 'w-4 h-4' : 'w-5 h-5'
          }`}></div>
        </div>
      </div>
      
      {text && (
        <div className="text-center space-y-1">
          <p className="text-gray-700 dark:text-gray-300 font-medium">{text}</p>
          <div className="flex justify-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-owis-purple animate-pulse"></div>
            <div className="w-2 h-2 rounded-full bg-owis-purple animate-pulse delay-150"></div>
            <div className="w-2 h-2 rounded-full bg-owis-purple animate-pulse delay-300"></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LuxuryLoadingSpinner;
