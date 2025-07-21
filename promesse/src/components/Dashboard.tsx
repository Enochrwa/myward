
import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import apiClient from '@/lib/apiClient';
import { 
  Shirt, 
  Calendar, 
  TrendingUp, 
  Sparkles, 
  Eye,
  Upload,
  Loader2,
  X
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import ClotheAnalytics from './ClotheAnalytics';
import WeeklyPlanner from './WeeklyPlanner';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogClose } from '@/components/ui/dialog';
import AdvancedAnalyticsModal from './AdvancedAnalyticsModal';

const controlledVocabularies = {
  style: [
    "Smart Casual", "Business Casual", "Formal", "Black Tie", "Sporty", "Athleisure",
    "Vintage", "Bohemian", "Minimalist", "Streetwear", "Preppy", "Punk",
    "Grunge", "Gothic", "Y2K", "Avant-Garde", "Artsy", "Loungewear", "Workwear"
  ],
  occasion: [
    "Business", "Everyday", "Work", "Interview", "Wedding", "Party", "Formal Event",
    "Casual Date", "Outdoor", "Travel", "Vacation", "Festival", "Religious Ceremony",
    "Fitness", "Beach", "Club", "Concert", "Dinner", "Homewear","Church",
  ],
  season: [
    "Spring", "Summer", "Autumn", "Winter", "All Season", "Rainy Season", "Transitional"
  ],
  gender: [
    "Male", "Female", "Unisex", "Non-Binary", "Genderfluid"
  ],
  pattern: [
    "Solid", "Striped", "Plaid", "Floral", "Polka Dot", "Houndstooth", "Geometric",
    "Animal Print", "Camouflage", "Tie-Dye", "Abstract", "Paisley", "Checkered", "Chevron"
  ],
  material: [
    "Cotton", "Wool", "Polyester", "Silk", "Linen", "Denim", "Leather", "Suede",
    "Velvet", "Satin", "Nylon", "Rayon", "Acrylic", "Spandex", "Bamboo", "Cashmere",
    "Jersey", "Corduroy", "Tweed", "Chiffon"
  ],
  color: [
    "Black", "White", "Grey", "Beige", "Brown", "Navy", "Blue", "Sky Blue", "Teal", "Green",
    "Olive", "Mint", "Yellow", "Mustard", "Orange", "Coral", "Red", "Burgundy", "Pink",
    "Blush", "Purple", "Lavender", "Violet", "Gold", "Silver", "Bronze", "Multicolor"
  ],
  fit: [
    "Slim Fit", "Regular Fit", "Relaxed Fit", "Oversized", "Tailored", "Loose Fit", "Skinny Fit",
    "Bodycon", "Boxy"
  ],
  length: [
    "Crop", "Hip Length", "Waist Length", "Knee Length", "Midi", "Maxi", "Ankle Length",
    "Full Length", "Short", "Above Knee"
  ],
  sleeveType: [
    "Sleeveless", "Cap Sleeve", "Short Sleeve", "3/4 Sleeve", "Long Sleeve",
    "Bell Sleeve", "Bishop Sleeve", "Puff Sleeve", "Raglan Sleeve", "Dolman Sleeve",
    "Kimono Sleeve"
  ],
  neckline: [
    "Crew Neck", "V-Neck", "Round Neck", "Square Neck", "Scoop Neck", "Halter Neck",
    "Off-Shoulder", "Boat Neck", "Turtleneck", "Cowl Neck", "Sweetheart", "Keyhole"
  ],
  accessoryType: [
    "Hat", "Scarf", "Belt", "Gloves", "Watch", "Bracelet", "Necklace", "Earrings",
    "Rings", "Brooch", "Bag", "Wallet", "Sunglasses", "Hair Accessories", "Tie",
    "Bow Tie", "Suspenders"
  ],
  footwearType: [
    "Sneakers", "Sandals", "Loafers", "Oxfords", "Derby", "Brogues", "Boots",
    "Chelsea Boots", "Chukka Boots", "Hiking Boots", "Heels", "Pumps", "Stilettos",
    "Flats", "Ballet Flats", "Mules", "Clogs", "Espadrilles", "Flip-Flops", "Slides",
    "Wedges"
  ]
};


interface ImageMetadata {
  style: string;
  occasion: string[];
  season: string[];
  temperature_range: { min: number; max: number };
  gender: string;
  material: string;
  pattern: string;
}

const Dashboard = () => {
  const [greeting, setGreeting] = useState('');
  const [currentTime, setCurrentTime] = useState(new Date());
  const [uploading, setUploading] = useState(false);
  const [batchProgress, setBatchProgress] = useState<{ total: number; completed: number; failed: number } | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isAnalyticsModalOpen, setIsAnalyticsModalOpen] = useState(false);
  const [metadata, setMetadata] = useState<ImageMetadata[]>([]);
  const [activeImageIndex, setActiveImageIndex] = useState(0);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good Morning');
    else if (hour < 18) setGreeting('Good Afternoon');
    else setGreeting('Good Evening');

    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      const fileList = Array.from(files);
      setSelectedFiles(fileList);
      setMetadata(fileList.map(() => ({
        style: '',
        occasion: [],
        season: [],
        temperature_range: { min: 0, max: 30 },
        gender: '',
        material: '',
        pattern: ''
      })));
      setActiveImageIndex(0);
      setIsModalOpen(true);
    }
  };

  const handleMetadataChange = (index: number, field: keyof ImageMetadata, value: any) => {
    const newMetadata = [...metadata];
    newMetadata[index] = { ...newMetadata[index], [field]: value };
    setMetadata(newMetadata);
  };
  
  const applyToAll = (field: keyof ImageMetadata, value: any) => {
    const newMetadata = metadata.map(meta => ({ ...meta, [field]: value }));
    setMetadata(newMetadata);
  };

  const uploadImages = async () => {
    setIsModalOpen(false);
    setUploading(true);
    setBatchProgress({
      total: selectedFiles.length,
      completed: 0,
      failed: 0
    });

    const formData = new FormData();
    selectedFiles.forEach(file => {
      formData.append('files', file);
    });
    formData.append('metadatas', JSON.stringify(metadata));

    try {
      const data = await apiClient('/upload-images/', {
        method: 'POST',
        body: formData,  // FormData is passed as-is, no need for JSON.stringify
      });

      setBatchProgress({
        total: data.total_images,
        completed: data.successful_uploads,
        failed: data.failed_uploads,
      });
      navigate("/wardrobe");
    } catch (error) {
      console.error('Error uploading images:', error);
    } finally {
      setUploading(false);
      setTimeout(() => setBatchProgress(null), 5000);
      setSelectedFiles([]);
      setMetadata([]);
    }
  };

  const quickActions = [
    {
      title: 'Create Outfit',
      description: 'Generate AI-powered outfit combinations',
      icon: Sparkles,
      href: '/wardrobe?action=create-outfit',
      gradient: 'from-purple-500 to-pink-600',
      bgGradient: 'from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20'
    },
    {
      title: 'View Analytics',
      description: 'Insights into your style patterns',
      icon: TrendingUp,
      onClick: () => setIsAnalyticsModalOpen(true),
      gradient: 'from-orange-500 to-red-600',
      bgGradient: 'from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-blue-900/20 dark:to-purple-900/20 pt-20 pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent">
                {greeting}, Fashionista! ✨
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                Ready to create some amazing outfits today? Your style journey awaits.
              </p>
            </div>
            <div className="hidden md:block text-right">
              <div className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                {currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {currentTime.toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' })}
              </div>
            </div>
          </div>
        </div>

        {/* Upload and Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Upload Area */}
          <Card 
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center bg-white hover:border-blue-400 transition-colors cursor-pointer"
            onClick={() => !uploading && fileInputRef.current?.click()}
          >
            {uploading ? (
              <div className="space-y-4">
                <Loader2 className="w-12 h-12 text-blue-600 mx-auto animate-spin" />
                <p className="text-lg text-gray-600">
                  Processing {batchProgress?.completed || 0} of {batchProgress?.total || 0} clothes
                </p>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div
                    className="bg-blue-600 h-2.5 rounded-full"
                    style={{
                      width: `${((batchProgress?.completed || 0) / (batchProgress?.total || 1)) * 100}%`
                    }}
                  />
                </div>
                <p className="text-sm text-gray-500">
                  {batchProgress?.failed || 0} failed uploads
                </p>
              </div>
            ) : (
              <>
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">Upload Your Clothes</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Drop images here or click to browse. They'll be automatically categorized.
                </p>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileSelect}
                  accept="image/*"
                  multiple
                  className="hidden"
                />
              </>
            )}
          </Card>
          
          {/* Quick Actions simplified */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {quickActions.map((action, index) => {
              const Icon = action.icon;
              const CardComponent = action.href ? Link : 'div';
              return (
                <CardComponent key={index} to={action.href} onClick={action.onClick}>
                  <Card className={`h-full hover:shadow-xl transition-all duration-300 hover:scale-105 bg-gradient-to-br ${action.bgGradient} border-0 shadow-lg cursor-pointer`}>
                    <CardContent className="p-6 flex flex-col items-center justify-center text-center h-full">
                      <div className={`w-12 h-12 bg-gradient-to-br ${action.gradient} rounded-xl flex items-center justify-center mb-4 shadow-lg`}>
                        <Icon size={24} className="text-white" />
                      </div>
                      <h3 className="font-semibold text-gray-800 dark:text-gray-200">{action.title}</h3>
                    </CardContent>
                  </Card>
                </CardComponent>
              );
            })}
          </div>
        </div>

        {new URLSearchParams(window.location.search).get('action') === 'plan-week' ? (
          <WeeklyPlanner />
        ) : (
          <Card className="shadow-lg border-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-2xl text-gray-800 dark:text-gray-200">Your Wardrobe</CardTitle>
              <CardDescription>All your clothes, automatically categorized by AI.</CardDescription>
            </CardHeader>
            <CardContent>
              <ClotheAnalytics />
            </CardContent>
          </Card>
        )}

        <AdvancedAnalyticsModal isOpen={isAnalyticsModalOpen} onClose={() => setIsAnalyticsModalOpen(false)} />

        {/* Call to Action */}
        <div className="mt-12 text-center">
          <Card className="bg-gradient-to-r from-purple-500 via-pink-500 to-blue-500 border-0 shadow-2xl">
            <CardContent className="p-8">
              <div className="text-white">
                <h2 className="text-3xl font-bold mb-4">Ready to Elevate Your Style?</h2>
                <p className="text-lg mb-6 text-purple-100">
                  Discover new outfits, plan your week, and connect with fashion enthusiasts worldwide.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Button size="lg" variant="secondary" className="bg-white text-purple-600 hover:bg-gray-100">
                    <Sparkles size={20} className="mr-2" />
                    Create Outfit
                  </Button>
                  <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10" asChild>
                    <Link to="/wardrobe">
                      <Eye size={20} className="mr-2" />
                      Browse Wardrobe
                    </Link>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Metadata Editing Modal */}
      {/* Metadata Editing Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="max-w-4xl h-4/5 pb-5 flex flex-col bg-gray-900 text-white border-gray-700">
          <DialogHeader>
            <DialogTitle>Edit Clothing Details</DialogTitle>
            <DialogClose className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground">
              <X className="h-4 w-4" />
              <span className="sr-only">Close</span>
            </DialogClose>
          </DialogHeader>

          <div className="flex-grow overflow-hidden grid grid-cols-3 gap-6">
            {/* Image Preview Column */}
            <div className="col-span-1 flex flex-col gap-4">
              <div className="w-full aspect-square rounded-lg overflow-hidden bg-gray-800">
                {selectedFiles[activeImageIndex] && (
                  <img
                    src={URL.createObjectURL(selectedFiles[activeImageIndex])}
                    alt={`Preview ${activeImageIndex + 1}`}
                    className="w-full h-full object-contain"
                  />
                )}
              </div>
              <div className="flex-shrink-0 grid grid-cols-4 gap-2">
                {selectedFiles.map((file, index) => (
                  <button
                    key={index}
                    onClick={() => setActiveImageIndex(index)}
                    className={`aspect-square rounded-md overflow-hidden transition-all ${
                      activeImageIndex === index ? 'ring-2 ring-blue-500' : 'hover:opacity-80'
                    }`}
                  >
                    <img src={URL.createObjectURL(file)} alt={`Thumbnail ${index + 1}`} className="w-full h-full object-cover" />
                  </button>
                ))}
              </div>
            </div>

            {/* Metadata Form Column */}
            <div className="col-span-2 overflow-y-auto pr-4">
              {metadata[activeImageIndex] && (
                <div className="space-y-6">
                  <div className="grid grid-cols-2 gap-4">
                    {Object.entries(controlledVocabularies).map(([key, options]) => (
                      <div key={key}>
                        <label className="block text-sm font-medium text-gray-300 capitalize">{key.replace(/([A-Z])/g, ' $1')}</label>
                        <Select
                          value={metadata[activeImageIndex][key as keyof ImageMetadata] as string}
                          onValueChange={(value) => handleMetadataChange(activeImageIndex, key as keyof ImageMetadata, value)}
                        >
                          <SelectTrigger className="bg-gray-800 border-gray-600 text-white">
                            <SelectValue placeholder={`Select ${key}`} />
                          </SelectTrigger>
                          <SelectContent className="bg-gray-800 border-gray-600 text-white">
                            {options.map(option => (
                              <SelectItem key={option} value={option}>{option}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <Button variant="link" size="sm" onClick={() => applyToAll(key as keyof ImageMetadata, metadata[activeImageIndex][key as keyof ImageMetadata])} className="text-blue-400">
                          Apply to all
                        </Button>
                      </div>
                    ))}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300">Temperature Range (°C)</label>
                    <div className="flex items-center gap-2">
                      <Input
                        type="number"
                        placeholder="Min"
                        value={metadata[activeImageIndex].temperature_range.min}
                        onChange={(e) => handleMetadataChange(activeImageIndex, 'temperature_range', { ...metadata[activeImageIndex].temperature_range, min: parseInt(e.target.value) || 0 })}
                        className="bg-gray-800 border-gray-600 text-white"
                      />
                      <Input
                        type="number"
                        placeholder="Max"
                        value={metadata[activeImageIndex].temperature_range.max}
                        onChange={(e) => handleMetadataChange(activeImageIndex, 'temperature_range', { ...metadata[activeImageIndex].temperature_range, max: parseInt(e.target.value) || 0 })}
                        className="bg-gray-800 border-gray-600 text-white"
                      />
                      <Button variant="link" size="sm" onClick={() => applyToAll('temperature_range', metadata[activeImageIndex].temperature_range)} className="text-blue-400">
                        Apply to all
                      </Button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          <DialogFooter className="border-t border-gray-700 pt-4">
            <Button variant="outline" onClick={() => setIsModalOpen(false)} className="text-white border-gray-600 hover:bg-gray-700">Cancel</Button>
            <Button onClick={uploadImages} className="bg-blue-600 hover:bg-blue-700">Upload {selectedFiles.length} items</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

          </div>
  );
};

export default Dashboard;