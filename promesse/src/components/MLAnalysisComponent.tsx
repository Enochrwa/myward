import React, { useState, useCallback } from 'react';
import { Upload, Camera, Palette, Sparkles, TrendingUp, Target } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  classifyClothingImage, 
  detectDominantColor, 
  extractColorPalette,
  ClassificationResult,
  ColorAnalysisResult,
  ColorPaletteResult
} from '@/lib/apiClient';

interface MLAnalysisProps {
  onAnalysisComplete?: (results: {
    classification?: ClassificationResult;
    colorAnalysis?: ColorAnalysisResult;
    colorPalette?: ColorPaletteResult;
  }) => void;
}

const MLAnalysisComponent: React.FC<MLAnalysisProps> = ({ onAnalysisComplete }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<{
    classification?: ClassificationResult;
    colorAnalysis?: ColorAnalysisResult;
    colorPalette?: ColorPaletteResult;
  }>({});
  const [error, setError] = useState<string | null>(null);
  const [analysisProgress, setAnalysisProgress] = useState(0);

  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      setAnalysisResults({});
      
      // Create preview URL
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  }, []);

  const runAnalysis = useCallback(async () => {
    if (!selectedFile) return;

    setIsAnalyzing(true);
    setError(null);
    setAnalysisProgress(0);
    
    try {
      const results: typeof analysisResults = {};
      
      // Step 1: Classification
      setAnalysisProgress(20);
      try {
        const classificationResult = await classifyClothingImage(selectedFile);
        results.classification = classificationResult;
        setAnalysisProgress(40);
      } catch (err) {
        console.warn('Classification failed:', err);
      }
      
      // Step 2: Color Analysis
      setAnalysisProgress(60);
      try {
        const colorResult = await detectDominantColor(selectedFile);
        results.colorAnalysis = colorResult;
        setAnalysisProgress(80);
      } catch (err) {
        console.warn('Color analysis failed:', err);
      }
      
      // Step 3: Color Palette
      try {
        const paletteResult = await extractColorPalette(selectedFile, 5);
        results.colorPalette = paletteResult;
        setAnalysisProgress(100);
      } catch (err) {
        console.warn('Color palette extraction failed:', err);
      }
      
      setAnalysisResults(results);
      onAnalysisComplete?.(results);
      
    } catch (err: any) {
      setError(err.message || 'Analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  }, [selectedFile, onAnalysisComplete]);

  const renderClassificationResults = () => {
    const { classification } = analysisResults;
    if (!classification) return null;

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Clothing Classification
          </CardTitle>
          <CardDescription>
            AI-powered clothing category detection using MobileNetV2
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="font-medium">Predicted Category:</span>
            <Badge variant="default" className="text-sm">
              {classification.predicted_category}
            </Badge>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Confidence:</span>
              <span className="text-sm font-medium">
                {(classification.confidence_score * 100).toFixed(1)}%
              </span>
            </div>
            <Progress value={classification.confidence_score * 100} className="h-2" />
          </div>
          
          <div className="space-y-2">
            <span className="text-sm font-medium">Top Predictions:</span>
            <div className="space-y-1">
              {Object.entries(classification.detailed_predictions)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 3)
                .map(([category, score]) => (
                  <div key={category} className="flex items-center justify-between text-sm">
                    <span className="capitalize">{category.replace('_', ' ')}</span>
                    <span className="text-muted-foreground">
                      {(score * 100).toFixed(1)}%
                    </span>
                  </div>
                ))}
            </div>
          </div>
          
          <div className="text-xs text-muted-foreground">
            Model: {classification.model_name}
          </div>
        </CardContent>
      </Card>
    );
  };

  const renderColorAnalysis = () => {
    const { colorAnalysis } = analysisResults;
    if (!colorAnalysis) return null;

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Palette className="h-5 w-5" />
            Color Analysis
          </CardTitle>
          <CardDescription>
            Dominant color detection and properties analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <div 
              className="w-16 h-16 rounded-lg border-2 border-border"
              style={{ backgroundColor: colorAnalysis.dominant_color_hex }}
            />
            <div className="space-y-1">
              <div className="font-medium capitalize">
                {colorAnalysis.dominant_color_name}
              </div>
              <div className="text-sm text-muted-foreground">
                {colorAnalysis.dominant_color_hex}
              </div>
              <div className="text-xs text-muted-foreground">
                RGB: {colorAnalysis.dominant_color_rgb.join(', ')}
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div className="text-center">
              <div className="font-medium">Brightness</div>
              <Badge variant="outline" className="mt-1">
                {colorAnalysis.color_properties.brightness}
              </Badge>
            </div>
            <div className="text-center">
              <div className="font-medium">Saturation</div>
              <Badge variant="outline" className="mt-1">
                {colorAnalysis.color_properties.saturation}
              </Badge>
            </div>
            <div className="text-center">
              <div className="font-medium">Temperature</div>
              <Badge variant="outline" className="mt-1">
                {colorAnalysis.color_properties.temperature}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  const renderColorPalette = () => {
    const { colorPalette } = analysisResults;
    if (!colorPalette) return null;

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Color Palette
          </CardTitle>
          <CardDescription>
            Complete color palette extracted from the image
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-5 gap-2">
            {colorPalette.palette.map((color, index) => (
              <div key={index} className="text-center">
                <div 
                  className="w-full h-12 rounded-md border-2 border-border mb-2"
                  style={{ backgroundColor: color.hex }}
                />
                <div className="text-xs font-medium capitalize">
                  {color.name}
                </div>
                <div className="text-xs text-muted-foreground">
                  {color.hex}
                </div>
              </div>
            ))}
          </div>
          
          {colorPalette.harmony_analysis && (
            <div className="space-y-2">
              <div className="text-sm font-medium">Harmony Analysis</div>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div className="text-center">
                  <div className="text-muted-foreground">Scheme</div>
                  <Badge variant="outline" className="mt-1">
                    {colorPalette.harmony_analysis.scheme}
                  </Badge>
                </div>
                <div className="text-center">
                  <div className="text-muted-foreground">Temperature</div>
                  <Badge variant="outline" className="mt-1">
                    {colorPalette.harmony_analysis.temperature}
                  </Badge>
                </div>
                <div className="text-center">
                  <div className="text-muted-foreground">Contrast</div>
                  <Badge variant="outline" className="mt-1">
                    {colorPalette.harmony_analysis.contrast}
                  </Badge>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      {/* File Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5" />
            AI-Powered Clothing Analysis
          </CardTitle>
          <CardDescription>
            Upload a clothing image to get AI-powered insights including category classification, 
            color analysis, and style recommendations.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <label htmlFor="image-upload" className="cursor-pointer">
                <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
                  <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                  <div className="text-sm font-medium">
                    {selectedFile ? selectedFile.name : 'Click to upload an image'}
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    Supports JPG, PNG, WebP (max 10MB)
                  </div>
                </div>
              </label>
              <input
                id="image-upload"
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
              />
            </div>
            
            {previewUrl && (
              <div className="w-32 h-32 rounded-lg overflow-hidden border-2 border-border">
                <img 
                  src={previewUrl} 
                  alt="Preview" 
                  className="w-full h-full object-cover"
                />
              </div>
            )}
          </div>
          
          {selectedFile && (
            <Button 
              onClick={runAnalysis} 
              disabled={isAnalyzing}
              className="w-full"
            >
              {isAnalyzing ? (
                <>
                  <Camera className="h-4 w-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 mr-2" />
                  Analyze Image
                </>
              )}
            </Button>
          )}
          
          {isAnalyzing && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Analysis Progress</span>
                <span>{analysisProgress}%</span>
              </div>
              <Progress value={analysisProgress} className="h-2" />
            </div>
          )}
          
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Results Section */}
      {(analysisResults.classification || analysisResults.colorAnalysis || analysisResults.colorPalette) && (
        <Tabs defaultValue="classification" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="classification">Classification</TabsTrigger>
            <TabsTrigger value="color">Color Analysis</TabsTrigger>
            <TabsTrigger value="palette">Color Palette</TabsTrigger>
          </TabsList>
          
          <TabsContent value="classification" className="mt-4">
            {renderClassificationResults()}
          </TabsContent>
          
          <TabsContent value="color" className="mt-4">
            {renderColorAnalysis()}
          </TabsContent>
          
          <TabsContent value="palette" className="mt-4">
            {renderColorPalette()}
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
};

export default MLAnalysisComponent;

