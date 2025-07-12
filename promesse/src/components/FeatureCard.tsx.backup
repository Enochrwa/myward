
import React from 'react';
import { LucideIcon } from 'lucide-react';

interface FeatureCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  gradient?: string;
}

const FeatureCard = ({ icon: Icon, title, description, gradient = "from-owis-forest to-owis-sage" }: FeatureCardProps) => {
  return (
    <div className="group owis-card owis-hover rounded-2xl p-6 h-full">
      <div className={`w-12 h-12 bg-gradient-to-br ${gradient} rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
        <Icon className="h-6 w-6 text-white" />
      </div>
      
      <h3 className="text-xl font-heading font-semibold text-owis-charcoal mb-3">
        {title}
      </h3>
      
      <p className="text-muted-foreground leading-relaxed">
        {description}
      </p>
      
      <div className="mt-4 h-1 w-0 bg-gradient-to-r from-owis-gold to-owis-bronze rounded-full group-hover:w-full transition-all duration-500"></div>
    </div>
  );
};

export default FeatureCard;
