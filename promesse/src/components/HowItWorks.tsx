import React from 'react';
import { Scan, Sparkles, Calendar, Gift } from 'lucide-react';

const HowItWorks = () => {
  const steps = [
    {
      icon: Scan,
      title: "1. Digitize Your Closet",
      description: "Snap photos of your clothes, and our AI will automatically tag and organize them for you.",
    },
    {
      icon: Sparkles,
      title: "2. Get Style Suggestions",
      description: "Our AI stylist creates outfits from your clothes for any occasion, considering the weather and your style.",
    },
    {
      icon: Calendar,
      title: "3. Plan Your Week",
      description: "Use our calendar to plan your outfits for the week ahead. No more morning stress!",
    },
    {
      icon: Gift,
      title: "4. Discover New Looks",
      description: "Get inspired with new ways to wear your clothes and discover what to wear next.",
    },
  ];

  return (
    <section className="py-20 bg-white">
      <div className="container mx-auto px-4 max-w-6xl">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-heading font-bold text-owis-forest mb-6">
            How It Works
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            A simple, four-step process to a smarter wardrobe.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <div
              key={step.title}
              className="group owis-card rounded-xl p-8 text-center owis-hover"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex justify-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-br from-owis-purple to-owis-bronze rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-500 shadow-glow">
                  <step.icon className="h-8 w-8 text-white" />
                </div>
              </div>
              <h3 className="text-2xl font-display font-semibold text-owis-charcoal mb-4">
                {step.title}
              </h3>
              <p className="text-muted-foreground leading-relaxed">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
