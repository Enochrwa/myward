
import React from 'react';
import { Moon, Sun, Monitor } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';

const ThemeToggle = () => {
  const { theme, setTheme } = useTheme();

  const themes = [
    { key: 'light' as const, icon: Sun, label: 'Light' },
    { key: 'dark' as const, icon: Moon, label: 'Dark' },
    { key: 'auto' as const, icon: Monitor, label: 'Auto' },
  ];

  return (
    <div className="flex items-center bg-white/10 dark:bg-black/20 backdrop-blur-md rounded-2xl p-1 border border-white/20 dark:border-white/10">
      {themes.map(({ key, icon: Icon, label }) => (
        <button
          key={key}
          onClick={() => setTheme(key)}
          className={`
            relative flex items-center justify-center w-10 h-10 rounded-xl transition-all duration-300
            ${theme === key 
              ? 'bg-owis-purple text-owis-forest shadow-lg scale-110' 
              : 'text-owis-charcoal/70 dark:text-owis-cream/70 hover:text-owis-purple hover:bg-white/20 dark:hover:bg-white/10'
            }
          `}
          title={label}
        >
          <Icon size={18} />
          {theme === key && (
            <div className="absolute inset-0 bg-owis-purple/20 rounded-xl animate-pulse-glow"></div>
          )}
        </button>
      ))}
    </div>
  );
};

export default ThemeToggle;
