
import React from 'react';
import { Link } from 'react-router-dom';
import { Home, ArrowLeft } from 'lucide-react';
import ThemeToggle from '@/components/ThemeToggle';

const NotFoundPage = () => {
  return (
    <>
      <div className="fixed top-6 right-6 z-50 no-print">
        <ThemeToggle />
      </div>
      <div className="min-h-screen bg-gradient-to-br from-owis-cream to-owis-mint dark:from-owis-charcoal-dark to-owis-midnight-blue flex items-center justify-center p-6">
        <div className="owis-card rounded-3xl p-8 max-w-md text-center animate-fade-in">
          <div className="w-24 h-24 bg-gradient-to-br from-owis-gold to-owis-bronze rounded-full flex items-center justify-center mx-auto mb-6">
            <span className="text-4xl font-bold text-white">404</span>
          </div>
          
          <h1 className="text-3xl font-heading font-bold gradient-text mb-2">
            Page Not Found
          </h1>
          
          <p className="text-owis-charcoal/70 dark:text-owis-cream/70 mb-8">
            The page you're looking for doesn't exist or has been moved.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/"
              className="owis-button-primary px-6 py-3 rounded-xl flex items-center gap-2 justify-center"
            >
              <Home size={16} />
              Go Home
            </Link>
            
            <button
              onClick={() => window.history.back()}
              className="px-6 py-3 rounded-xl border border-owis-gold text-owis-gold hover:bg-owis-gold hover:text-owis-forest transition-all duration-300 flex items-center gap-2 justify-center"
            >
              <ArrowLeft size={16} />
              Go Back
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default NotFoundPage;
