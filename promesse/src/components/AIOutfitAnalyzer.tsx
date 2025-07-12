
import React, { useState, useRef, useCallback } from 'react';
import { Upload, Camera, Sparkles, Brain, Palette, TrendingUp, Image as ImageIcon, Download, Share, Zap, Target, Eye, Trash2, RotateCcw, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import apiClient from '@/lib/apiClient'; // Added apiClient import

interface AnalysisResult {
  style: string;
  colors: string[];
  occasion: string;
  season: string;
  confidence: number;
  recommendations: string[];
  colorPalette: { color: string; name: string; percentage: number }[];
  styleInsights: { category: string; score: number; description: string }[];
}

const AIOutfitAnalyzer = () => {
  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult | null>(null);
  const [currentStep, setCurrentStep] = useState(1);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Only set isDragging to false if we're leaving the drop zone completely
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX;
    const y = e.clientY;
    
    if (x < rect.left || x >= rect.right || y < rect.top || y >= rect.bottom) {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files).filter(file => 
      file.type.startsWith('image/')
    );
    
    if (files.length > 0) {
      setSelectedImages(prev => [...prev, ...files]);
      toast({
        title: "✨ Images Added",
        description: `${files.length} image(s) ready for AI analysis`,
      });
    } else {
      toast({
        title: "Invalid Files",
        description: "Please drop image files only (JPG, PNG, WebP)",
        variant: "destructive"
      });
    }
  }, [toast]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      setSelectedImages(prev => [...prev, ...files]);
      toast({
        title: "📸 Images Selected",
        description: `${files.length} image(s) added to analysis queue`,
      });
    }
  };

  const removeImage = (index: number) => {
    setSelectedImages(prev => prev.filter((_, i) => i !== index));
    toast({
      title: "Image Removed",
      description: "Image has been removed from analysis queue",
    });
  };

  const analyzeOutfit = async () => {
    if (selectedImages.length === 0) {
      toast({
        title: "⚠️ No Images",
        description: "Please add images to analyze",
        variant: "destructive"
      });
      return;
    }

    setIsAnalyzing(true);
    setCurrentStep(1);

    try {
      // Prepare form data for API call
      const formData = new FormData();
      formData.append('file', selectedImages[0]); // Use first image for now

      // Call the backend AI analysis API using apiClient
      // apiClient handles token and will throw an error for non-ok responses.
      const apiResults = await apiClient('/ai/analyze-outfit/', {
        method: 'POST',
        body: formData,
        // No need to set Content-Type for FormData, browser does it.
        // No need to set Authorization header, apiClient handles it.
      });

      // Transform API response to match frontend interface
      const transformedResults: AnalysisResult = {
        style: apiResults.style || "Contemporary Style",
        colors: apiResults.dominantColors || ["#2563EB", "#DC2626", "#059669", "#8B5CF6"],
        occasion: apiResults.occasionSuitability || "Versatile for multiple occasions",
        season: "All Seasons", // Could be enhanced based on analysis
        confidence: Math.round((apiResults.confidenceScore || 0.65) * 100),
        recommendations: apiResults.recommendations || ["Upload an image to get personalized recommendations"],
        colorPalette: apiResults.colorPalette || [
          { color: "#2563EB", name: "Royal Blue", percentage: 35 },
          { color: "#DC2626", name: "Classic Red", percentage: 25 },
          { color: "#059669", name: "Emerald Green", percentage: 20 },
          { color: "#8B5CF6", name: "Royal Purple", percentage: 20 }
        ],
        styleInsights: apiResults.styleInsights || [
          { category: "Style Analysis", score: 75, description: "AI-powered style analysis completed" }
        ]
      };

      setAnalysisResults(transformedResults);
      
      toast({
        title: "🎉 Analysis Complete",
        description: "Your outfit analysis is ready!",
      });

    } catch (error) {
      console.error('AI Analysis Error:', error); // Keep for debugging
      // The error message from apiClient might be more user-friendly.
      // Consider using err.message in the toast.
      
      // Fallback to mock data if API fails
      const fallbackResults: AnalysisResult = {
        style: "Modern Casual",
        colors: ["#2563EB", "#DC2626", "#059669", "#8B5CF6"],
        occasion: "Business Casual",
        season: "Spring/Summer",
        confidence: 92,
        recommendations: [
          "Consider adding a statement accessory to elevate the look",
          "The color combination works well for professional settings",
          "Try incorporating more neutral tones for versatility",
          "This style suits both casual and semi-formal occasions"
        ],
        colorPalette: [
          { color: "#2563EB", name: "Royal Blue", percentage: 35 },
          { color: "#DC2626", name: "Classic Red", percentage: 25 },
          { color: "#059669", name: "Emerald Green", percentage: 20 },
          { color: "#8B5CF6", name: "Royal Purple", percentage: 20 }
        ],
        styleInsights: [
          { category: "Elegance", score: 88, description: "Sophisticated and refined appearance" },
          { category: "Comfort", score: 95, description: "High comfort factor for daily wear" },
          { category: "Versatility", score: 82, description: "Suitable for multiple occasions" },
          { category: "Trend Factor", score: 90, description: "Aligns with current fashion trends" }
        ]
      };

      setAnalysisResults(fallbackResults);
      
      toast({
        title: "⚠️ Analysis Error",
        description: "Could not connect to the AI analysis service. Showing example results instead. Please try again later.",
        variant: "destructive"
      });
    }

    setIsAnalyzing(false);
  };

  const resetAnalysis = () => {
    setSelectedImages([]);
    setAnalysisResults(null);
    setCurrentStep(1);
    toast({
      title: "Reset Complete",
      description: "Ready for a new analysis",
    });
  };

  const exportResults = () => {
    if (!analysisResults) return;
    
    const dataStr = JSON.stringify(analysisResults, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'outfit-analysis.json';
    link.click();
    
    toast({
      title: "📊 Export Complete",
      description: "Analysis report downloaded successfully!",
    });
  };

  const shareResults = () => {
    if (!analysisResults) return;
    
    if (navigator.share) {
      navigator.share({
        title: 'My Outfit Analysis',
        text: `Style: ${analysisResults.style}, Confidence: ${analysisResults.confidence}%`,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(`My outfit analysis: ${analysisResults.style} style with ${analysisResults.confidence}% confidence`);
      toast({
        title: "📤 Copied to Clipboard",
        description: "Analysis summary copied for sharing!",
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50 dark:from-gray-900 dark:via-purple-900 dark:to-pink-900 p-4 lg:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-4">
            <div className="p-3 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl">
              <Brain className="text-white" size={32} />
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              AI Photo Analysis Studio
            </h1>
          </div>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Upload your outfit photos and get instant AI-powered style analysis, color insights, and personalized recommendations
          </p>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          {/* Upload Section */}
          <div className="xl:col-span-2 space-y-6">
            {/* Enhanced Drag & Drop Zone */}
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-3xl p-6 border-2 border-dashed border-gray-300 dark:border-gray-600 shadow-xl">
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`relative transition-all duration-300 rounded-2xl p-12 text-center border-2 border-dashed cursor-pointer ${
                  isDragging 
                    ? 'bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/50 dark:to-pink-900/50 border-purple-400 scale-102 shadow-lg' 
                    : 'hover:bg-gray-50 dark:hover:bg-gray-700/50 border-gray-300 dark:border-gray-600 hover:border-purple-400 hover:scale-101'
                }`}
                onClick={() => fileInputRef.current?.click()}
              >
                {isDragging && (
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-2xl animate-pulse" />
                )}
                
                <div className="relative z-10">
                  <div className="mb-6">
                    <div className={`mx-auto w-24 h-24 rounded-full flex items-center justify-center mb-4 transition-all duration-300 ${
                      isDragging 
                        ? 'bg-gradient-to-r from-purple-600 to-pink-600 scale-110' 
                        : 'bg-gradient-to-r from-purple-600 to-pink-600'
                    }`}>
                      {isDragging ? (
                        <Sparkles className="text-white animate-spin" size={40} />
                      ) : (
                        <Upload className="text-white" size={40} />
                      )}
                    </div>
                    <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                      {isDragging ? 'Drop Your Photos Here!' : 'Upload Outfit Photos'}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-300">
                      {isDragging 
                        ? 'Release to add images for analysis' 
                        : 'Drag & drop images or click to browse • Supports JPG, PNG, WebP'
                      }
                    </p>
                  </div>

                  {!isDragging && (
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                      <Button 
                        onClick={(e) => {
                          e.stopPropagation();
                          fileInputRef.current?.click();
                        }}
                        className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-8 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all"
                      >
                        <ImageIcon size={20} className="mr-2" />
                        Choose Files
                      </Button>
                      <Button 
                        variant="outline"
                        onClick={(e) => e.stopPropagation()}
                        className="border-2 border-purple-300 text-purple-600 hover:bg-purple-50 dark:border-purple-600 dark:text-purple-400 px-8 py-3 rounded-xl"
                      >
                        <Camera size={20} className="mr-2" />
                        Take Photo
                      </Button>
                    </div>
                  )}
                </div>

                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="hidden"
                />
              </div>
            </div>

            {/* Selected Images with Enhanced Preview */}
            {selectedImages.length > 0 && (
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                    Selected Images ({selectedImages.length})
                  </h3>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSelectedImages([])}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 size={16} className="mr-1" />
                    Clear All
                  </Button>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-6">
                  {selectedImages.map((file, index) => (
                    <div key={index} className="relative group">
                      <div className="aspect-square bg-gray-100 dark:bg-gray-700 rounded-xl overflow-hidden shadow-md hover:shadow-lg transition-shadow">
                        <img
                          src={URL.createObjectURL(file)}
                          alt={`Upload ${index + 1}`}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        />
                      </div>
                      <button
                        onClick={() => removeImage(index)}
                        className="absolute -top-2 -right-2 bg-red-500 hover:bg-red-600 text-white rounded-full p-1.5 opacity-0 group-hover:opacity-100 transition-all duration-200 shadow-lg"
                      >
                        <Trash2 size={14} />
                      </button>
                      <div className="absolute bottom-2 left-2 right-2 bg-black/50 backdrop-blur-sm rounded-lg p-1">
                        <p className="text-white text-xs truncate">{file.name}</p>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="flex flex-col sm:flex-row gap-4">
                  <Button 
                    onClick={analyzeOutfit}
                    disabled={isAnalyzing}
                    className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white py-3 rounded-xl shadow-lg hover:shadow-xl transition-all"
                  >
                    {isAnalyzing ? (
                      <>
                        <Sparkles size={20} className="mr-2 animate-spin" />
                        Analyzing... (Step {currentStep}/5)
                      </>
                    ) : (
                      <>
                        <Zap size={20} className="mr-2" />
                        Start AI Analysis
                      </>
                    )}
                  </Button>
                  <Button 
                    onClick={resetAnalysis}
                    variant="outline"
                    className="border-2 border-gray-300 px-6 py-3 rounded-xl hover:bg-gray-50"
                  >
                    <RotateCcw size={20} className="mr-2" />
                    Reset
                  </Button>
                </div>
              </div>
            )}
          </div>

          {/* Analysis Results */}
          <div className="space-y-6">
            {analysisResults ? (
              <>
                {/* Analysis Summary */}
                <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white">Analysis Results</h3>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                      <span className="text-sm text-green-600 font-medium">{analysisResults.confidence}% Confident</span>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-gradient-to-r from-blue-100 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-xl p-4">
                        <div className="text-sm text-gray-600 dark:text-gray-400">Style</div>
                        <div className="font-bold text-gray-900 dark:text-white">{analysisResults.style}</div>
                      </div>
                      <div className="bg-gradient-to-r from-green-100 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/30 rounded-xl p-4">
                        <div className="text-sm text-gray-600 dark:text-gray-400">Occasion</div>
                        <div className="font-bold text-gray-900 dark:text-white">{analysisResults.occasion}</div>
                      </div>
                    </div>

                    <div className="bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 rounded-xl p-4">
                      <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">Dominant Colors</div>
                      <div className="flex gap-2">
                        {analysisResults.colors.map((color, index) => (
                          <div
                            key={index}
                            className="w-8 h-8 rounded-full border-2 border-white shadow-md hover:scale-110 transition-transform"
                            style={{ backgroundColor: color }}
                            title={analysisResults.colorPalette[index]?.name || color}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Style Insights */}
                <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Style Insights</h3>
                  <div className="space-y-3">
                    {analysisResults.styleInsights.map((insight, index) => (
                      <div key={index} className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="font-medium text-gray-900 dark:text-white">{insight.category}</span>
                          <span className="text-sm text-gray-600 dark:text-gray-400">{insight.score}%</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div 
                            className="bg-gradient-to-r from-purple-600 to-pink-600 h-2 rounded-full transition-all duration-1000"
                            style={{ width: `${insight.score}%` }}
                          />
                        </div>
                        <p className="text-xs text-gray-600 dark:text-gray-400">{insight.description}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Color Palette */}
                <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Color Analysis</h3>
                  <div className="space-y-3">
                    {analysisResults.colorPalette.map((colorInfo, index) => (
                      <div key={index} className="flex items-center gap-3">
                        <div
                          className="w-6 h-6 rounded-full border-2 border-white shadow-md"
                          style={{ backgroundColor: colorInfo.color }}
                        />
                        <div className="flex-1">
                          <div className="text-sm font-medium text-gray-900 dark:text-white">{colorInfo.name}</div>
                          <div className="text-xs text-gray-600 dark:text-gray-400">{colorInfo.percentage}%</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Actions */}
                <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Export & Share</h3>
                  <div className="space-y-3">
                    <Button 
                      onClick={exportResults}
                      className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white py-3 rounded-xl"
                    >
                      <Download size={20} className="mr-2" />
                      Export Full Report
                    </Button>
                    <Button 
                      onClick={shareResults}
                      variant="outline"
                      className="w-full border-2 border-purple-300 text-purple-600 hover:bg-purple-50 dark:border-purple-600 dark:text-purple-400 py-3 rounded-xl"
                    >
                      <Share size={20} className="mr-2" />
                      Share Analysis
                    </Button>
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl text-center">
                <div className="mb-4">
                  <Eye className="mx-auto text-gray-400" size={48} />
                </div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Ready for Analysis</h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Upload your outfit photos to get started with AI-powered style analysis
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Recommendations */}
        {analysisResults && (
          <div className="mt-8 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl">
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">AI Recommendations</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analysisResults.recommendations.map((recommendation, index) => (
                <div key={index} className="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-600 rounded-xl p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg">
                      <Target size={16} className="text-white" />
                    </div>
                    <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed">{recommendation}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIOutfitAnalyzer;
