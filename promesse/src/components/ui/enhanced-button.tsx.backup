
import React from 'react';
import { cn } from '@/lib/utils';

interface EnhancedButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'luxury' | 'premium' | 'elegant' | 'minimal';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  glow?: boolean;
  children: React.ReactNode;
}

const EnhancedButton: React.FC<EnhancedButtonProps> = ({
  variant = 'luxury',
  size = 'md',
  glow = false,
  className,
  children,
  ...props
}) => {
  const baseClasses = "relative overflow-hidden font-semibold transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-owis-gold/30";
  
  const variants = {
    luxury: "bg-gradient-to-r from-owis-gold to-owis-bronze text-owis-forest hover:from-owis-gold-light hover:to-owis-bronze-light transform hover:scale-105 shadow-lg hover:shadow-xl",
    premium: "bg-gradient-to-r from-owis-forest to-owis-sage text-white hover:from-owis-forest-light hover:to-owis-sage-light transform hover:scale-105 shadow-lg hover:shadow-xl",
    elegant: "bg-white/10 backdrop-blur-lg border border-white/20 text-owis-charcoal dark:text-white hover:bg-white/20 shadow-soft hover:shadow-medium",
    minimal: "bg-transparent border-2 border-owis-gold text-owis-gold hover:bg-owis-gold hover:text-owis-forest"
  };

  const sizes = {
    sm: "px-4 py-2 text-sm rounded-lg",
    md: "px-6 py-3 text-base rounded-xl", 
    lg: "px-8 py-4 text-lg rounded-2xl",
    xl: "px-12 py-6 text-xl rounded-3xl"
  };

  const glowEffect = glow ? "shadow-glow hover:shadow-glow-lg" : "";

  return (
    <button
      className={cn(
        baseClasses,
        variants[variant],
        sizes[size],
        glowEffect,
        className
      )}
      {...props}
    >
      {/* Shine Effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full hover:translate-x-full transition-transform duration-700"></div>
      
      {/* Content */}
      <span className="relative z-10">{children}</span>
    </button>
  );
};

export default EnhancedButton;
