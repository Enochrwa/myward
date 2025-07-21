
import React, { useState, useEffect } from 'react';
import { Menu, X, User, Settings, LogOut, Sparkles, Heart, Calendar, BarChart3, Wand2, Eye, Brain, LogIn } from 'lucide-react'; // Added LogIn
import { Link, useLocation } from 'react-router-dom';
import ThemeToggle from './ThemeToggle';
import { useAuth } from '../hooks/useAuth'; // Added useAuth
import { AuthModal } from './auth'; // Added AuthModal
import { Button } from './ui/button'; // Added Button
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "@/components/ui/navigation-menu";
import { cn } from "@/lib/utils";

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false); // Added AuthModal state
  const location = useLocation();
  const { user, logout } = useAuth(); // Consumed AuthContext

  

  const baseNavigation = [
    { name: 'Home', href: '/', icon: Sparkles },
      { name: 'Dashboard', href: '/dashboard', icon: BarChart3 },
      { name: 'Wardrobe', href: '/wardrobe', icon: Heart },
  ];

  const adminNavigation = user && (user.role === 'admin' || user.role === 'superadmin')
      ? [{ name: 'Admin', href: '/admin', icon: Settings }]
      : [];

  const navigation = [...baseNavigation, ...adminNavigation];

    const wardrobeFeatures = [
      { name: 'My Closet', href: '/wardrobe', description: 'Browse and organize your clothing items', icon: Heart },
  
      { name: 'Plan Week', href: '/wardrobe?action=plan-week', description: 'Weekly outfit planning calendar', icon: Calendar },
      
    ];

  
  

  // Close mobile menu when route changes
  useEffect(() => {
    setIsMenuOpen(false);
    setIsProfileOpen(false);
  }, [location]);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (!target.closest('.profile-dropdown')) {
        setIsProfileOpen(false);
      }
      if (!target.closest('.mobile-menu') && !target.closest('.mobile-menu-button')) {
        setIsMenuOpen(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/95 dark:bg-gray-900/95 backdrop-blur-md border-b border-gray-200/50 dark:border-gray-700/50 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-600 via-pink-600 to-blue-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-105">
              <span className="text-white font-bold text-lg">O</span>
            </div>
            <span className="font-heading font-bold text-xl bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent">DWS</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center">
            <NavigationMenu>
              <NavigationMenuList className="space-x-2">
                {navigation.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.href || 
                    (item.href === '/ai-studio' && location.pathname.startsWith('/ai-studio'));
                  
                  if (item.name === 'Wardrobe') {
                    return (
                      <NavigationMenuItem key={item.name}>
                        <NavigationMenuTrigger className={cn(
                          "bg-transparent hover:bg-gradient-to-r hover:from-purple-50 hover:to-pink-50 dark:hover:from-purple-900/20 dark:hover:to-pink-900/20 transition-all duration-300",
                          isActive && "bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/40 dark:to-pink-900/40 text-purple-700 dark:text-purple-300"
                        )}>
                          <Icon size={16} className="mr-2" />
                          {item.name}
                        </NavigationMenuTrigger>
                        <NavigationMenuContent>
                          <div className="w-[420px] p-4 bg-white/95 dark:bg-gray-800/95 backdrop-blur-lg border border-white/50 dark:border-gray-700/50">
                            <div className="mb-4">
                              <h4 className="text-lg font-semibold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                                Digital Wardrobe
                              </h4>
                              <p className="text-sm text-gray-600 dark:text-gray-400">
                                Your personal fashion assistant
                              </p>
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                              {wardrobeFeatures.map((feature) => (
                                <NavigationMenuLink key={feature.name} asChild>
                                  <Link
                                    to={feature.href}
                                    className="block p-3 rounded-lg hover:bg-gradient-to-r hover:from-purple-50 hover:to-pink-50 dark:hover:from-purple-900/20 dark:hover:to-pink-900/20 transition-all duration-200 group"
                                  >
                                    <div className="flex items-center gap-2 mb-1">
                                      <feature.icon size={14} className="text-purple-600 dark:text-purple-400" />
                                      <div className="font-medium text-gray-900 dark:text-gray-100 group-hover:text-purple-700 dark:group-hover:text-purple-300">
                                        {feature.name}
                                      </div>
                                    </div>
                                    <div className="text-xs text-gray-500 dark:text-gray-400">
                                      {feature.description}
                                    </div>
                                  </Link>
                                </NavigationMenuLink>
                              ))}
                            </div>
                          </div>
                        </NavigationMenuContent>
                      </NavigationMenuItem>
                    );
                  }

                  return (
                    <NavigationMenuItem key={item.name}>
                      <NavigationMenuLink asChild>
                        <Link
                          to={item.href}
                          className={cn(
                            "flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 hover:bg-gradient-to-r hover:from-gray-50 hover:to-gray-100 dark:hover:from-gray-800 dark:hover:to-gray-700",
                            isActive
                              ? "bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-700 text-gray-900 dark:text-gray-100"
                              : "text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100"
                          )}
                        >
                          <Icon size={16} className="mr-2" />
                          {item.name}
                        </Link>
                      </NavigationMenuLink>
                    </NavigationMenuItem>
                  );
                })}
              </NavigationMenuList>
            </NavigationMenu>
          </div>

          {/* Right Section */}
          <div className="flex items-center space-x-4">
            {/* <ThemeToggle /> */}
            
            {/* Profile Dropdown / Login Button */}
            {user ? (
              <div className="relative profile-dropdown">
                <button
                  onClick={() => setIsProfileOpen(!isProfileOpen)}
                  className="flex items-center space-x-2 p-2 rounded-xl bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 hover:from-purple-200 hover:to-pink-200 dark:hover:from-purple-900/50 dark:hover:to-pink-900/50 transition-all duration-200 shadow-md hover:shadow-lg"
                >
                  <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center shadow-inner">
                    {/* Optionally display user initial or avatar here */}
                    <User size={16} className="text-white" />
                  </div>
                  {/* <span className="hidden sm:inline text-sm font-medium text-gray-700 dark:text-gray-200">{user.username}</span> */}
                </button>

                {isProfileOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white/95 dark:bg-gray-800/95 rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 py-2 animate-fade-in backdrop-blur-md">
                    <div className="px-4 py-2 border-b border-gray-200/50 dark:border-gray-700/50">
                      <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{user.username}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user.email}</p>
                    </div>
                    <Link
                      to="/profile"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gradient-to-r hover:from-purple-50 hover:to-pink-50 dark:hover:from-purple-900/20 dark:hover:to-pink-900/20 transition-all duration-200"
                      onClick={() => setIsProfileOpen(false)}
                    >
                      <User size={16} className="mr-3" />
                      Profile
                    </Link>
                    <Link
                      to="/settings"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gradient-to-r hover:from-blue-50 hover:to-cyan-50 dark:hover:from-blue-900/20 dark:hover:to-cyan-900/20 transition-all duration-200"
                      onClick={() => setIsProfileOpen(false)}
                    >
                      <Settings size={16} className="mr-3" />
                      Settings
                    </Link>
                    <button
                      onClick={() => {
                        logout();
                        setIsProfileOpen(false);
                      }}
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gradient-to-r hover:from-red-50 hover:to-orange-50 dark:hover:from-red-900/20 dark:hover:to-orange-900/20 transition-all duration-200"
                    >
                      <LogOut size={16} className="mr-3" />
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <Button
                onClick={() => setIsAuthModalOpen(true)}
                variant="outline"
                className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold py-2 px-4 rounded-lg shadow-md hover:shadow-lg transition-all duration-300 ease-in-out transform hover:scale-105 flex items-center space-x-2"
              >
                <LogIn size={16} className="mr-1" />
                Login / Register
              </Button>
            )}

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 rounded-xl bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-700 hover:from-gray-200 hover:to-gray-300 dark:hover:from-gray-700 dark:hover:to-gray-600 transition-all duration-200 mobile-menu-button shadow-md"
            >
              {isMenuOpen ? <X size={20} className="text-gray-700 dark:text-gray-300" /> : <Menu size={20} className="text-gray-700 dark:text-gray-300" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-4 animate-fade-in mobile-menu">
            <nav className="space-y-2">
              {/* Add Login/Register to mobile menu if not logged in? For now, focus on desktop */}
              {navigation.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.href || 
                  (item.href === '/ai-studio' && location.pathname.startsWith('/ai-studio'));
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={cn(
                      "flex items-center px-4 py-3 rounded-xl transition-all duration-200",
                      isActive
                        ? "bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/40 dark:to-pink-900/40 text-purple-700 dark:text-purple-300"
                        : "text-gray-600 dark:text-gray-300 hover:bg-gradient-to-r hover:from-gray-50 hover:to-gray-100 dark:hover:from-gray-800 dark:hover:to-gray-700"
                    )}
                    onClick={() => setIsMenuOpen(false)}
                  >
                    <Icon size={20} className="mr-3" />
                    {item.name}
                  </Link>
                );
              })}
            </nav>
          </div>
        )}
      </div>
      <AuthModal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} />
    </header>
  );
};

export default Header;
