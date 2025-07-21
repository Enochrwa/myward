import React, { useState, useEffect } from 'react';
import { Loader2, Image } from 'lucide-react';
import apiClient from '@/lib/apiClient';
import axios from 'axios';
interface ImageMetadata {
  id: string;
  filename: string;
  original_name: string;
  file_size: number;
  image_width: number;
  image_height: number;
  dominant_color: string;
  color_palette: string[];
  upload_date: string;
  batch_id?: string;
}

const ClotheAnalytics: React.FC = () => {
  const [images, setImages] = useState<ImageMetadata[]>([]);
  const [selectedImage, setSelectedImage] = useState<ImageMetadata | null>(null);
  const [loading, setLoading] = useState(false);


  const fetchImages = async () => {
    setLoading(true);
    try {
  

      const token = localStorage.getItem("token"); // or use the exact key you stored the token with

          const allItems = await axios.get("http://127.0.0.1:8000/api/images", {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });
      setImages(allItems?.data?.images);
      console.log("Fetched Images: ", allItems?.data)
    } catch (error) {
      console.error('Error fetching images:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  useEffect(() => {
    fetchImages();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-800">
      <div className="container mx-auto px-4 py-8">
        

        {/* Image Grid */}
        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6">
            {images?.map((image) => (
              <div
                key={image.id}
                className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl shadow-xl overflow-hidden hover:shadow-2xl hover:scale-[1.02] hover:border-blue-500/50 transition-all duration-300 cursor-pointer group"
                onClick={() => setSelectedImage(image)}
              >
                <div className="relative aspect-square bg-gradient-to-br from-gray-800 to-gray-700">
                  <img
                    src={`http://127.0.0.1:8000/uploads/${image?.filename}`}
                    alt={image?.category}
                    className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                    onError={(e) => {
                      e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iIzM3NDE1MSIvPgogIDx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0iY2VudHJhbCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1mYW1pbHk9Im1vbm9zcGFjZSIgZm9udC1zaXplPSIxNHB4IiBmaWxsPSIjOWNhM2FmIj5JbWFnZSBub3QgZm91bmQ8L3RleHQ+Cjwvc3ZnPgo=';
                    }}
                  />
                  {/* Dark overlay */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  
                  {/* Color indicator */}
                  <div className="absolute top-3 left-3">
                    <div
                      className="w-6 h-6 rounded-full border-2 border-white/80 shadow-lg ring-1 ring-black/20"
                      style={{ backgroundColor: image.dominant_color }}
                    />
                  </div>
                  
                  {/* Analytics badge */}
                  <div className="absolute top-3 right-3">
                    <div className="bg-blue-500/80 backdrop-blur-sm text-white text-xs px-2 py-1 rounded-full">
                      AI Analyzed
                    </div>
                  </div>
                </div>
                
                <div className="p-4 bg-gray-800/80 backdrop-blur-sm">
                  <h3 className="font-semibold text-white mb-2 truncate text-sm">
                    <span className='font-bold'>AI predicted: </span><span className='font-bold italic'>{image?.category}</span>
                  </h3>
                  
                  <div className="space-y-1 text-xs text-gray-300">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Dimensions</span>
                      <span className="text-blue-300">{image.image_width} × {image.image_height}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Size</span>
                      <span className="text-green-300">{formatFileSize(image.file_size)}</span>
                    </div>
                    {image.batch_id && (
                      <div className="flex justify-between">
                        <span className="text-gray-400">Batch</span>
                        <span className="text-purple-300 truncate max-w-20" title={image.batch_id}>
                          {image.batch_id.slice(-8)}
                        </span>
                      </div>
                    )}
                  </div>
                  
                  {/* Color palette preview */}
                  <div className="flex space-x-1 mt-3">
                    {image.color_palette.slice(0, 5).map((color, index) => (
                      <div
                        key={index}
                        className="w-3 h-3 rounded-full border border-gray-600 shadow-sm"
                        style={{ backgroundColor: color }}
                      />
                    ))}
                  </div>
                  
                  {/* Analytics indicators */}
                  <div className="flex justify-between items-center mt-3 pt-2 border-t border-gray-700">
                    <span className="text-xs text-gray-400">Added</span>
                    <span className="text-xs text-gray-300">
                      {new Date(image.upload_date).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {images.length === 0 && !loading && (
          <div className="text-center py-20">
            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-12 max-w-md mx-auto">
              <Image className="w-20 h-20 text-gray-500 mx-auto mb-6" />
              <h2 className="text-2xl font-semibold text-gray-300 mb-2">No Clothing Items Found</h2>
              <p className="text-gray-400">Your clothing inventory is empty</p>
              <p className="text-gray-500 text-sm mt-2">Upload clothing images to start analyzing</p>
            </div>
          </div>
        )}

        {/* Image Detail Modal */}
        {selectedImage && (
          <div className="fixed inset-0 bg-black/90 backdrop-blur-md flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900/95 backdrop-blur-xl border border-gray-700 rounded-2xl max-w-5xl max-h-[90vh] overflow-y-auto shadow-2xl">
              <div className="p-8">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h2 className="text-3xl font-bold text-white mb-2">
                      {selectedImage.original_name}
                    </h2>
                    <p className="text-gray-400">
                      Added to inventory on {formatDate(selectedImage.upload_date)}
                    </p>
                  </div>
                  <button
                    onClick={() => setSelectedImage(null)}
                    className="text-gray-400 hover:text-white text-3xl font-light leading-none hover:bg-gray-800 rounded-full w-10 h-10 flex items-center justify-center transition-all"
                  >
                    ×
                  </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
                  {/* Image */}
                  <div className="lg:col-span-3">
                    <div className="rounded-xl overflow-hidden shadow-2xl border border-gray-700">
                      <img
                        src={`http://127.0.0.1:8000/uploads/${selectedImage?.filename}`}
                        alt={selectedImage.original_name}
                        className="w-full h-auto max-h-[500px] object-contain bg-gray-800"
                        onError={(e) => {
                          e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgZmlsbD0iIzM3NDE1MSIvPgogIDx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0iY2VudHJhbCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1mYW1pbHk9Im1vbm9zcGFjZSIgZm9udC1zaXplPSIxNnB4IiBmaWxsPSIjOWNhM2FmIj5JbWFnZSBub3QgZm91bmQ8L3RleHQ+Cjwvc3ZnPgo=';
                        }}
                      />
                    </div>
                  </div>

                  {/* Analytics Details */}
                  <div className="lg:col-span-2 space-y-6">
                    {/* Item Properties */}
                    <div className="bg-gray-800/60 backdrop-blur-sm border border-gray-700 rounded-xl p-5">
                      <h3 className="font-semibold text-white mb-4 flex items-center">
                        <span className="w-2 h-2 bg-blue-400 rounded-full mr-2"></span>
                        Item Properties
                      </h3>
                      <div className="space-y-3 text-sm">
                        <div className="flex justify-between items-center">
                          <span className="text-gray-400">Image Dimensions</span>
                          <span className="font-medium text-blue-300">{selectedImage.image_width} × {selectedImage.image_height} px</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-400">File Size</span>
                          <span className="font-medium text-green-300">{formatFileSize(selectedImage.file_size)}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-400">Aspect Ratio</span>
                          <span className="font-medium text-purple-300">
                            {(selectedImage.image_width / selectedImage.image_height).toFixed(2)}:1
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-400">Dominant Color</span>
                          <div className="flex items-center space-x-2">
                            <div
                              className="w-5 h-5 rounded border border-gray-600 shadow-sm"
                              style={{ backgroundColor: selectedImage.dominant_color }}
                            />
                            <span className="font-medium text-xs font-mono text-yellow-300">{selectedImage.dominant_color}</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Color Analysis */}
                    <div className="bg-gray-800/60 backdrop-blur-sm border border-gray-700 rounded-xl p-5">
                      <h3 className="font-semibold text-white mb-4 flex items-center">
                        <span className="w-2 h-2 bg-purple-400 rounded-full mr-2"></span>
                        Color Analysis
                      </h3>
                      <div className="grid grid-cols-2 gap-3">
                        {selectedImage.color_palette.map((color, index) => (
                          <div key={index} className="bg-gray-700/50 rounded-lg p-3 text-center border border-gray-600">
                            <div
                              className="w-full h-8 rounded-md border border-gray-600 shadow-sm mb-2"
                              style={{ backgroundColor: color }}
                            />
                            <p className="text-xs text-gray-300 font-mono">{color}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* AI Insights */}
                    <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 backdrop-blur-sm border border-blue-500/30 rounded-xl p-5">
                      <h3 className="font-semibold text-white mb-4 flex items-center">
                        <span className="w-2 h-2 bg-cyan-400 rounded-full mr-2"></span>
                        AI Insights
                      </h3>
                      <div className="space-y-3 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-300">Analysis Status</span>
                          <span className="text-green-300 font-medium">✓ Complete</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-300">Color Complexity</span>
                          <span className="text-blue-300 font-medium">{selectedImage.color_palette.length} colors</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-300">Resolution</span>
                          <span className="text-purple-300 font-medium">
                            {selectedImage.image_width * selectedImage.image_height > 1000000 ? 'High' : 
                             selectedImage.image_width * selectedImage.image_height > 500000 ? 'Medium' : 'Standard'}
                          </span>
                        </div>
                      </div>
                    </div>

                    {selectedImage.batch_id && (
                      <div className="bg-gray-800/60 backdrop-blur-sm border border-gray-700 rounded-xl p-5">
                        <h3 className="font-semibold text-white mb-3 flex items-center">
                          <span className="w-2 h-2 bg-orange-400 rounded-full mr-2"></span>
                          Batch Information
                        </h3>
                        <div className="text-sm">
                          <div className="flex justify-between items-center">
                            <span className="text-gray-400">Batch ID</span>
                            <span className="font-mono text-xs text-orange-300 bg-orange-900/20 px-2 py-1 rounded">
                              {selectedImage.batch_id}
                            </span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ClotheAnalytics;