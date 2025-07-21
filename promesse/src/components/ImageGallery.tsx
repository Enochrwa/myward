import React, { useState, useEffect, useRef } from 'react';
import { Upload, Eye, Trash2, BarChart3, Image as ImageIcon, Palette, Activity, Loader2 } from 'lucide-react';
import apiClient from '@/lib/apiClient';
interface ImageMetadata {
  id: string;
  filename: string;
  original_name: string;
  file_size: number;
  image_width: number;
  image_height: number;
  dominant_color: string;
  color_palette: string[];
  resnet_features?: number[];
  opencv_features?: any;
  upload_date: string;
  image_url: string;
  batch_id?: string;
}

interface BatchUploadResponse {
  message: string;
  total_images: number;
  successful_uploads: number;
  failed_uploads: number;
  batch_id: string;
  results: Array<{
    success: boolean;
    image_id?: string;
    filename?: string;
    image_url?: string;
    file_size?: number;
    dimensions?: string;
    dominant_color?: string;
    error?: string;
  }>;
  processing_time: number;
}

interface Analytics {
  total_images: number;
  total_size_mb: number;
  average_dimensions: {
    width: number;
    height: number;
  };
  color_distribution: Array<{
    dominant_color: string;
    count: number;
  }>;
  batch_statistics: {
    total_batches: number;
    average_processing_time: number;
    average_batch_size: number;
  };
  recent_batches: Array<{
    batch_id: string;
    total_images: number;
    successful_images: number;
    failed_images: number;
    upload_date: string;
    processing_time: number;
  }>;
  upload_trends: Array<{
    date: string;
    count: number;
  }>;
}

const ImageGallery: React.FC = () => {
  const [images, setImages] = useState<ImageMetadata[]>([]);
  const [selectedImage, setSelectedImage] = useState<ImageMetadata | null>(null);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [batchUploading, setBatchUploading] = useState(false);
  const [batchProgress, setBatchProgress] = useState<{
    total: number;
    completed: number;
    failed: number;
  } | null>(null);
  const [activeTab, setActiveTab] = useState<'gallery' | 'analytics' | 'batches'>('gallery');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedBatch, setSelectedBatch] = useState<string | null>(null);


  const fetchImages = async (batchId?: string) => {
    setLoading(true);
    try {
      const url = batchId 
        ? '/images/?batch_id=${batchId}&limit=100'
        : `/images/?limit=100`;
      const response = await apiClient(url)
      const data = await response?.data
      setImages(data.images || []);
    } catch (error) {
      console.error('Error fetching images:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchBatches = async () => {
    try {
      const response = await fetch(`${API_BASE}/batches/?limit=10`);
      const data = await response.json();
      return data.batches || [];
    } catch (error) {
      console.error('Error fetching batches:', error);
      return [];
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`${API_BASE}/analytics/`);
      const data = await response.json();
      setAnalytics(data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const uploadImages = async (files: FileList) => {
    setBatchUploading(true);
    setBatchProgress({
      total: files.length,
      completed: 0,
      failed: 0
    });

    const formData = new FormData();
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await fetch(`${API_BASE}/upload-images/`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data: BatchUploadResponse = await response.json();
        console.log('Batch upload successful:', data);
        
        // Update progress
        setBatchProgress({
          total: data.total_images,
          completed: data.successful_uploads,
          failed: data.failed_uploads
        });

        // Refresh data
        await Promise.all([
          fetchImages(),
          fetchAnalytics()
        ]);
      } else {
        console.error('Batch upload failed:', response.statusText);
      }
    } catch (error) {
      console.error('Error uploading images:', error);
    } finally {
      setBatchUploading(false);
      setTimeout(() => setBatchProgress(null), 3000);
    }
  };

  const deleteImage = async (imageId: string) => {
    try {
      const response = await fetch(`${API_BASE}/images/${imageId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        fetchImages(selectedBatch);
        fetchAnalytics();
        setSelectedImage(null);
      } else {
        console.error('Delete failed:', response.statusText);
      }
    } catch (error) {
      console.error('Error deleting image:', error);
    }
  };

  const deleteBatch = async (batchId: string) => {
    try {
      const response = await fetch(`${API_BASE}/batches/${batchId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        fetchImages();
        fetchAnalytics();
        if (selectedBatch === batchId) {
          setSelectedBatch(null);
        }
      } else {
        console.error('Batch delete failed:', response.statusText);
      }
    } catch (error) {
      console.error('Error deleting batch:', error);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      if (files.length === 1) {
        // Single file upload (legacy)
        uploadImage(files[0]);
      } else {
        // Batch upload
        uploadImages(files);
      }
    }
  };

  const uploadImage = async (file: File) => {
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('description', 'Uploaded from React app');

    try {
      const response = await fetch(`${API_BASE}/upload-image/`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Upload successful:', data);
        fetchImages(selectedBatch);
        fetchAnalytics();
      } else {
        console.error('Upload failed:', response.statusText);
      }
    } catch (error) {
      console.error('Error uploading image:', error);
    } finally {
      setUploading(false);
    }
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    const files = event.dataTransfer.files;
    if (files && files.length > 0) {
      if (files.length === 1 && files[0].type.startsWith('image/')) {
        uploadImage(files[0]);
      } else if (files.length > 1) {
        const imageFiles = Array.from(files).filter(file => file.type.startsWith('image/'));
        if (imageFiles.length > 0) {
          uploadImages(files);
        }
      }
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

  const formatTime = (seconds: number) => {
    return seconds > 1 ? `${seconds.toFixed(2)} seconds` : `${(seconds * 1000).toFixed(0)} ms`;
  };

  useEffect(() => {
    fetchImages(selectedBatch);
    fetchAnalytics();
  }, [selectedBatch]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">AI Image Gallery</h1>
          <p className="text-gray-600">Upload, analyze, and explore your images with AI-powered features</p>
        </div>

        {/* Navigation */}
        <div className="flex space-x-4 mb-8">
          <button
            onClick={() => {
              setActiveTab('gallery');
              setSelectedBatch(null);
            }}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === 'gallery' && !selectedBatch
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <ImageIcon className="w-5 h-5 inline mr-2" />
            Gallery
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === 'analytics'
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <BarChart3 className="w-5 h-5 inline mr-2" />
            Analytics
          </button>
          <button
            onClick={async () => {
              setActiveTab('batches');
              const batches = await fetchBatches();
              if (batches.length > 0) {
                setSelectedBatch(batches[0].batch_id);
              }
            }}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === 'batches'
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <Activity className="w-5 h-5 inline mr-2" />
            Batches
          </button>
        </div>

        {activeTab === 'gallery' && (
          <>
            {/* Upload Area */}
            <div
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center mb-8 bg-white hover:border-blue-400 transition-colors cursor-pointer"
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              {batchUploading ? (
                <div className="space-y-4">
                  <Loader2 className="w-12 h-12 text-blue-600 mx-auto animate-spin" />
                  <p className="text-lg text-gray-600">
                    Processing {batchProgress?.completed || 0} of {batchProgress?.total || 0} images
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
                  <p className="text-lg text-gray-600 mb-2">
                    {uploading ? 'Uploading and processing...' : 'Drop images here or click to browse'}
                  </p>
                  <p className="text-sm text-gray-500">
                    Supports multiple PNG, JPG, GIF files up to 10MB each
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
            </div>

            {/* Batch selector when viewing a batch */}
            {selectedBatch && (
              <div className="mb-6 flex items-center justify-between bg-blue-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <Activity className="w-5 h-5 text-blue-600 mr-2" />
                  <span className="font-medium">Viewing batch: {selectedBatch}</span>
                </div>
                <button
                  onClick={() => {
                    setSelectedBatch(null);
                    fetchImages();
                  }}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  View all images
                </button>
              </div>
            )}

            {/* Image Grid */}
            {loading ? (
              <div className="flex justify-center py-12">
                <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {images.map((image) => (
                  <div
                    key={image.id}
                    className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow cursor-pointer group"
                    onClick={() => setSelectedImage(image)}
                  >
                    <div className="relative aspect-w-1 aspect-h-1 bg-gray-200">
                      <img
                        src={`http://127.0.0.1:8000/uploads/${image?.filename}`}
                        alt={image.original_name}
                        className="w-full h-48 object-cover"
                        onError={(e) => {
                          e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2Y3ZjdmNyIvPgogIDx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0iY2VudHJhbCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1mYW1pbHk9Im1vbm9zcGFjZSIgZm9udC1zaXplPSIxNHB4IiBmaWxsPSIjOTk5Ij5JbWFnZSBub3QgZm91bmQ8L3RleHQ+Cjwvc3ZnPgo=';
                        }}
                      />
                      <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all" />
                    </div>
                    <div className="p-4">
                      <h3 className="font-medium text-gray-900 mb-2 truncate">
                        {image.original_name}
                      </h3>
                      <div className="flex items-center space-x-2 mb-2">
                        <div
                          className="w-4 h-4 rounded-full border"
                          style={{ backgroundColor: image.dominant_color }}
                        />
                        <span className="text-sm text-gray-600">
                          {image.dominant_color}
                        </span>
                      </div>
                      <p className="text-sm text-gray-500">
                        {image.image_width} × {image.image_height}
                      </p>
                      <p className="text-sm text-gray-500">
                        {formatFileSize(image.file_size)}
                      </p>
                      {image.batch_id && (
                        <p className="text-xs text-gray-400 mt-1 truncate">
                          Batch: {image.batch_id}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {images.length === 0 && !loading && (
              <div className="text-center py-12">
                <ImageIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 text-lg">
                  {selectedBatch ? 'No images in this batch' : 'No images uploaded yet'}
                </p>
                <p className="text-gray-400">
                  {selectedBatch ? 'This batch is empty' : 'Upload your first image to get started'}
                </p>
              </div>
            )}
          </>
        )}

        {activeTab === 'analytics' && analytics && (
          <div className="space-y-6">
            {/* Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center">
                  <ImageIcon className="w-8 h-8 text-blue-600 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Images</p>
                    <p className="text-2xl font-bold text-gray-900">{analytics.total_images}</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center">
                  <Activity className="w-8 h-8 text-green-600 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Size</p>
                    <p className="text-2xl font-bold text-gray-900">{analytics?.total_size_mb?.toFixed(2)} MB</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center">
                  <Palette className="w-8 h-8 text-purple-600 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-600">Avg Dimensions</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {Math.round(analytics?.average_dimensions?.width)} × {Math.round(analytics?.average_dimensions?.height)}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Batch Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center">
                  <Activity className="w-8 h-8 text-orange-600 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Batches</p>
                    <p className="text-2xl font-bold text-gray-900">{analytics?.batch_statistics?.total_batches}</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center">
                  <Activity className="w-8 h-8 text-indigo-600 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-600">Avg Batch Size</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {Math.round(analytics?.batch_statistics?.average_batch_size)}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center">
                  <Activity className="w-8 h-8 text-teal-600 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-600">Avg Process Time</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatTime(analytics?.batch_statistics?.average_processing_time)}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Color Distribution */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Color Distribution</h3>
              <div className="space-y-3">
                {analytics?.color_distribution?.map((colorData, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <div
                      className="w-6 h-6 rounded-full border-2 border-gray-200"
                      style={{ backgroundColor: colorData?.dominant_color }}
                    />
                    <div className="flex-1">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium text-gray-700">
                          {colorData?.dominant_color}
                        </span>
                        <span className="text-sm text-gray-500">
                          {colorData?.count} images
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{
                            width: `${(colorData.count / analytics.total_images) * 100}%`
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Batches */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Batches</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Batch ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Images</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Successful</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Failed</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {analytics?.recent_batches?.map((batch) => (
                      <tr key={batch?.batch_id} className="hover:bg-gray-50 cursor-pointer" onClick={() => {
                        setActiveTab('gallery');
                        setSelectedBatch(batch.batch_id);
                      }}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 truncate max-w-xs">
                          {batch?.batch_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {batch?.total_images}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">
                          {batch?.successful_images}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                          {batch?.failed_images}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatTime(batch?.processing_time)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatDate(batch?.upload_date)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'batches' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">All Batches</h3>
              {loading ? (
                <div className="flex justify-center py-12">
                  <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Batch ID</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Images</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Successful</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Failed</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {analytics?.recent_batches?.map((batch) => (
                        <tr key={batch.batch_id} className="hover:bg-gray-50">
                          <td 
                            className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600 cursor-pointer hover:underline truncate max-w-xs"
                            onClick={() => {
                              setActiveTab('gallery');
                              setSelectedBatch(batch.batch_id);
                            }}
                          >
                            {batch.batch_id}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {batch.total_images}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">
                            {batch.successful_images}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                            {batch.failed_images}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {formatTime(batch.processing_time)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {formatDate(batch.upload_date)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <button
                              onClick={() => deleteBatch(batch.batch_id)}
                              className="text-red-600 hover:text-red-800"
                              title="Delete batch"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Image Detail Modal */}
        {selectedImage && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <h2 className="text-2xl font-bold text-gray-900">
                    {selectedImage.original_name}
                  </h2>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => deleteImage(selectedImage.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => setSelectedImage(null)}
                      className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      ×
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Image */}
                  <div className="space-y-4">
                    <img
                      src={`http://127.0.0.1:8000/uploads/${selectedImage?.filename}`}
                      alt={selectedImage.original_name}
                      className="w-full rounded-lg shadow-md"
                      onError={(e) => {
                        e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgZmlsbD0iI2Y3ZjdmNyIvPgogIDx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0iY2VudHJhbCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1mYW1pbHk9Im1vbm9zcGFjZSIgZm9udC1zaXplPSIxNnB4IiBmaWxsPSIjOTk5Ij5JbWFnZSBub3QgZm91bmQ8L3RleHQ+Cjwvc3ZnPgo=';
                      }}
                    />
                    
                    {/* Color Palette */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">Color Palette</h3>
                      <div className="flex space-x-2">
                        {selectedImage.color_palette.map((color, index) => (
                          <div key={index} className="text-center">
                            <div
                              className="w-12 h-12 rounded-lg border-2 border-gray-200"
                              style={{ backgroundColor: color }}
                            />
                            <p className="text-xs text-gray-600 mt-1">{color}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Metadata */}
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">Image Details</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Dimensions:</span>
                          <span className="font-medium">{selectedImage.image_width} × {selectedImage.image_height}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">File Size:</span>
                          <span className="font-medium">{formatFileSize(selectedImage.file_size)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Dominant Color:</span>
                          <div className="flex items-center space-x-2">
                            <div
                              className="w-4 h-4 rounded-full border"
                              style={{ backgroundColor: selectedImage.dominant_color }}
                            />
                            <span className="font-medium">{selectedImage.dominant_color}</span>
                          </div>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Upload Date:</span>
                          <span className="font-medium">{formatDate(selectedImage.upload_date)}</span>
                        </div>
                        {selectedImage.batch_id && (
                          <div className="flex justify-between">
                            <span className="text-gray-600">Batch ID:</span>
                            <span className="font-medium text-blue-600 cursor-pointer hover:underline" onClick={() => {
                              setSelectedBatch(selectedImage.batch_id);
                              setActiveTab('gallery');
                              setSelectedImage(null);
                            }}>
                              {selectedImage.batch_id}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* AI Features */}
                    {selectedImage.opencv_features && (
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-3">AI Analysis</h3>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Brightness:</span>
                            <span className="font-medium">
                              {Math.round(selectedImage.opencv_features.brightness || 0)}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Contrast:</span>
                            <span className="font-medium">
                              {Math.round(selectedImage.opencv_features.contrast || 0)}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Edge Density:</span>
                            <span className="font-medium">
                              {((selectedImage.opencv_features.edge_density || 0) * 100).toFixed(2)}%
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Texture Variance:</span>
                            <span className="font-medium">
                              {Math.round(selectedImage.opencv_features.laplacian_variance || 0)}
                            </span>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* ResNet Features */}
                    {selectedImage.resnet_features && selectedImage.resnet_features.length > 0 && (
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-3">ResNet50 Features</h3>
                        <p className="text-sm text-gray-600 mb-2">
                          {selectedImage.resnet_features.length} feature dimensions extracted
                        </p>
                        <div className="bg-gray-50 rounded-lg p-3">
                          <div className="flex flex-wrap gap-1">
                            {selectedImage.resnet_features.slice(0, 20).map((feature, index) => (
                              <span
                                key={index}
                                className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded"
                              >
                                {feature.toFixed(3)}
                              </span>
                            ))}
                            {selectedImage.resnet_features.length > 20 && (
                              <span className="text-xs text-gray-500">
                                +{selectedImage.resnet_features.length - 20} more...
                              </span>
                            )}
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

        {/* Batch Upload Progress */}
        {batchProgress && (
          <div className="fixed bottom-4 right-4 bg-white rounded-lg shadow-lg p-4 max-w-sm z-50">
            <div className="flex items-center space-x-3 mb-2">
              <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
              <h3 className="font-medium text-gray-900">Batch Upload Progress</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Processed:</span>
                <span className="font-medium">
                  {batchProgress.completed} / {batchProgress.total}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{
                    width: `${(batchProgress.completed / batchProgress.total) * 100}%`
                  }}
                />
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Failed:</span>
                <span className="text-red-600 font-medium">
                  {batchProgress.failed}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImageGallery;