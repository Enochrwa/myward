
import React, { useState, useEffect } from 'react';
import { Shield, Zap, Globe, Users, Award, Star, CheckCircle, TrendingUp, Lock, Sparkles } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const ProductionFeatures = () => {
  const [stats, setStats] = useState({
    users: 0,
    outfits: 0,
    satisfaction: 0,
    countries: 0
  });

  useEffect(() => {
    // Animate counter
    const timer = setTimeout(() => {
      setStats({
        users: 10500000,
        outfits: 45000000,
        satisfaction: 98,
        countries: 195
      });
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  const features = [
    {
      icon: Shield,
      title: 'Enterprise Security',
      description: 'Bank-level encryption and GDPR compliance',
      color: 'from-blue-500 to-cyan-500',
      highlights: ['256-bit encryption', 'SOC 2 certified', 'Privacy by design']
    },
    {
      icon: Zap,
      title: 'Lightning Fast AI',
      description: 'Sub-second outfit recommendations',
      color: 'from-yellow-500 to-orange-500',
      highlights: ['< 200ms response', 'Edge computing', '99.9% uptime']
    },
    {
      icon: Globe,
      title: 'Global Platform',
      description: 'Available in 195 countries',
      color: 'from-green-500 to-emerald-500',
      highlights: ['50+ languages', '24/7 support', 'Local fashion trends']
    },
    {
      icon: Users,
      title: 'Community Driven',
      description: '10M+ active fashion enthusiasts',
      color: 'from-purple-500 to-pink-500',
      highlights: ['Expert stylists', 'Peer reviews', 'Style challenges']
    }
  ];

  const awards = [
    { year: '2024', title: 'Best AI Innovation', org: 'Tech Innovation Awards' },
    { year: '2024', title: 'Sustainability Leader', org: 'Fashion Tech Council' },
    { year: '2023', title: 'Best User Experience', org: 'UX Design Awards' },
    { year: '2023', title: 'Top Fashion App', org: 'App Store Awards' }
  ];

  const testimonials = [
    {
      name: 'Sarah Chen',
      role: 'Fashion Director at Vogue',
      content: 'OWIS has revolutionized how we think about personal styling. The AI accuracy is unprecedented.',
      rating: 5
    },
    {
      name: 'Marcus Johnson',
      role: 'CEO at StyleTech',
      content: 'The platform\'s enterprise features and security make it perfect for corporate partnerships.',
      rating: 5
    },
    {
      name: 'Emma Rodriguez',
      role: 'Sustainable Fashion Advocate',
      content: 'Finally, a platform that combines style with sustainability. The wardrobe optimization is genius.',
      rating: 5
    }
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-slate-50 via-white to-blue-50 dark:from-slate-900 dark:via-blue-900 dark:to-indigo-900">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-full px-6 py-2 mb-6">
            <Award className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-semibold text-blue-700 dark:text-blue-300">Production Ready</span>
          </div>
          <h2 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
            Enterprise-Grade Fashion Platform
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            Trusted by millions worldwide with cutting-edge technology, robust security, and award-winning design.
          </p>
        </div>

        {/* Live Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
          {[
            { label: 'Active Users', value: stats.users.toLocaleString(), suffix: '+', icon: Users },
            { label: 'Outfits Created', value: stats.outfits.toLocaleString(), suffix: '+', icon: Sparkles },
            { label: 'Satisfaction Rate', value: stats.satisfaction, suffix: '%', icon: Star },
            { label: 'Countries', value: stats.countries, suffix: '', icon: Globe }
          ].map((stat, index) => (
            <Card key={index} className="text-center hover:shadow-lg transition-all duration-300 border-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm">
              <CardContent className="p-6">
                <stat.icon className="w-8 h-8 mx-auto mb-3 text-blue-600" />
                <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                  {stat.value}{stat.suffix}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Production Features */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
          {features.map((feature, index) => (
            <Card key={index} className="hover:shadow-xl transition-all duration-300 border-0 bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm group">
              <CardHeader>
                <div className="flex items-center space-x-4">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${feature.color} flex items-center justify-center group-hover:scale-110 transition-transform`}>
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-xl text-gray-900 dark:text-white">{feature.title}</CardTitle>
                    <p className="text-gray-600 dark:text-gray-400">{feature.description}</p>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {feature.highlights.map((highlight, idx) => (
                    <div key={idx} className="flex items-center space-x-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span className="text-sm text-gray-700 dark:text-gray-300">{highlight}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Awards Section */}
        <div className="mb-16">
          <h3 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-8">
            Award-Winning Platform
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {awards.map((award, index) => (
              <Card key={index} className="text-center hover:shadow-lg transition-all duration-300 border-0 bg-gradient-to-br from-yellow-50 to-amber-50 dark:from-yellow-900/20 dark:to-amber-900/20">
                <CardContent className="p-6">
                  <div className="w-12 h-12 mx-auto mb-4 bg-gradient-to-r from-yellow-400 to-amber-500 rounded-full flex items-center justify-center">
                    <Award className="w-6 h-6 text-white" />
                  </div>
                  <div className="text-lg font-bold text-gray-900 dark:text-white mb-1">{award.title}</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">{award.org}</div>
                  <div className="text-xs text-yellow-600 dark:text-yellow-400 font-semibold">{award.year}</div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Testimonials */}
        <div className="mb-16">
          <h3 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-8">
            Trusted by Industry Leaders
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="hover:shadow-lg transition-all duration-300 border-0 bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm">
                <CardContent className="p-6">
                  <div className="flex space-x-1 mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <p className="text-gray-700 dark:text-gray-300 mb-4 italic">"{testimonial.content}"</p>
                  <div>
                    <div className="font-semibold text-gray-900 dark:text-white">{testimonial.name}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">{testimonial.role}</div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Security & Compliance */}
        <Card className="bg-gradient-to-r from-blue-600 to-purple-600 text-white border-0">
          <CardContent className="p-8 text-center">
            <Lock className="w-16 h-16 mx-auto mb-4" />
            <h3 className="text-2xl font-bold mb-4">Enterprise Security & Compliance</h3>
            <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
              Your data is protected with military-grade encryption and industry-leading security protocols.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              {['SOC 2 Type II', 'GDPR Compliant', 'ISO 27001', 'CCPA Ready'].map((cert) => (
                <div key={cert} className="bg-white/20 rounded-lg px-4 py-2 text-sm font-medium">
                  {cert}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
};

export default ProductionFeatures;
