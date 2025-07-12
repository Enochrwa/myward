
import React from 'react';

const PremiumEffects = () => {
  return (
    <>
      {/* Background gradient effects */}
      <div className="fixed inset-0 z-0">
        {/* Top right glow */}
        <div className="absolute top-0 right-0 w-[30rem] h-[30rem] bg-gradient-to-bl from-purple-600/30 via-pink-600/20 to-transparent rounded-full blur-3xl"></div>
        
        {/* Bottom left glow */}
        <div className="absolute bottom-0 left-0 w-[30rem] h-[30rem] bg-gradient-to-tr from-indigo-600/30 via-blue-600/20 to-transparent rounded-full blur-3xl"></div>
        
        {/* Center subtle glow */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[40rem] h-[40rem] bg-gradient-to-r from-purple-400/10 via-pink-500/10 to-indigo-500/10 rounded-full blur-3xl"></div>
      </div>
      
      {/* Particles/floating elements - subtle luxury elements */}
      <div className="fixed inset-0 z-0 overflow-hidden">
        {Array.from({ length: 15 }).map((_, i) => (
          <div 
            key={i}
            className={`absolute bg-white/50 dark:bg-white/20 rounded-full blur-sm animate-float-slow`}
            style={{
              top: `${Math.random() * 100}%`,
              left: `${Math.random() * 100}%`,
              width: `${Math.random() * 10 + 5}px`,
              height: `${Math.random() * 10 + 5}px`,
              animationDelay: `${i * 0.5}s`,
              animationDuration: `${Math.random() * 15 + 15}s`,
              opacity: Math.random() * 0.5 + 0.1
            }}
          ></div>
        ))}
      </div>
      
      {/* Subtle grid overlay */}
      <div className="fixed inset-0 z-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_110%)]"></div>
    </>
  );
};

export default PremiumEffects;
