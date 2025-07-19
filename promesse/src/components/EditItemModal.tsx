import React, { useState } from 'react';
import { X, Upload, Check } from 'lucide-react';

// Mock data for demonstration
const mockFiles = [
  { name: 'shirt1.jpg', url: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop' },
  { name: 'shirt2.jpg', url: 'https://images.unsplash.com/photo-1562157873-818bc0726f68?w=400&h=400&fit=crop' },
  { name: 'shirt3.jpg', url: 'https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=400&h=400&fit=crop' },
];

const controlledVocabularies = {
  category: ['T-Shirt', 'Shirt', 'Pants', 'Dress', 'Jacket', 'Sweater'],
  color: ['Black', 'White', 'Blue', 'Red', 'Green', 'Gray', 'Navy'],
  size: ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
  material: ['Cotton', 'Polyester', 'Wool', 'Silk', 'Linen', 'Denim'],
  brand: ['Nike', 'Adidas', 'Zara', 'H&M', 'Uniqlo', 'Gap'],
  occasion: ['Casual', 'Formal', 'Business', 'Sports', 'Party', 'Beach']
};

const initialMetadata = {
  category: '',
  color: '',
  size: '',
  material: '',
  brand: '',
  occasion: '',
  temperature_range: { min: 15, max: 25 }
};

export default function ClothingModal() {
  const [isModalOpen, setIsModalOpen] = useState(true);
  const [activeImageIndex, setActiveImageIndex] = useState(0);
  const [metadata, setMetadata] = useState(
    mockFiles.map(() => ({ ...initialMetadata }))
  );

  const handleMetadataChange = (index, field, value) => {
    const newMetadata = [...metadata];
    newMetadata[index] = { ...newMetadata[index], [field]: value };
    setMetadata(newMetadata);
  };

  const applyToAll = (field, value) => {
    const newMetadata = metadata.map(item => ({ ...item, [field]: value }));
    setMetadata(newMetadata);
  };

  const uploadImages = () => {
    console.log('Uploading images with metadata:', metadata);
    setIsModalOpen(false);
  };

  if (!isModalOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={() => setIsModalOpen(false)}
      />
      
      {/* Modal */}
      <div className="relative w-full max-w-6xl h-[90vh] mx-4 bg-gray-900 rounded-2xl shadow-2xl overflow-hidden border border-gray-800">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-800 bg-gray-900/95 backdrop-blur-sm">
          <h2 className="text-2xl font-semibold text-white">Edit Clothing Details</h2>
          <button
            onClick={() => setIsModalOpen(false)}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="flex flex-1 h-[calc(90vh-140px)]">
          {/* Image Preview Section */}
          <div className="w-1/3 min-w-[300px] p-6 border-r border-gray-800 bg-gray-900/50">
            {/* Main Image */}
            <div className="w-full aspect-square rounded-xl overflow-hidden bg-gray-800 mb-4 ring-1 ring-gray-700">
              <img
                src={mockFiles[activeImageIndex]?.url}
                alt={`Preview ${activeImageIndex + 1}`}
                className="w-full h-full object-cover"
              />
            </div>

            {/* Thumbnail Grid */}
            <div className="grid grid-cols-4 gap-2">
              {mockFiles.map((file, index) => (
                <button
                  key={index}
                  onClick={() => setActiveImageIndex(index)}
                  className={`aspect-square rounded-lg overflow-hidden transition-all duration-200 ${
                    activeImageIndex === index 
                      ? 'ring-2 ring-blue-500 shadow-lg shadow-blue-500/25' 
                      : 'ring-1 ring-gray-700 hover:ring-gray-600 hover:scale-105'
                  }`}
                >
                  <img 
                    src={file.url} 
                    alt={`Thumbnail ${index + 1}`} 
                    className="w-full h-full object-cover" 
                  />
                </button>
              ))}
            </div>

            {/* Image Counter */}
            <div className="text-center mt-3 text-sm text-gray-400">
              {activeImageIndex + 1} of {mockFiles.length}
            </div>
          </div>

          {/* Form Section */}
          <div className="flex-1 p-6 overflow-y-auto bg-gray-900/30">
            <div className="max-w-2xl space-y-6">
              {/* Form Fields */}
              {Object.entries(controlledVocabularies).map(([key, options]) => (
                <div key={key} className="space-y-2">
                  <label className="block text-sm font-medium text-gray-200 capitalize">
                    {key.replace('_', ' ')}
                  </label>
                  <div className="flex gap-2 items-center">
                    <div className="flex-1">
                      <select
                        value={metadata[activeImageIndex][key] || ''}
                        onChange={(e) => handleMetadataChange(activeImageIndex, key, e.target.value)}
                        className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                      >
                        <option value="" disabled>Select {key}</option>
                        {options.map(option => (
                          <option key={option} value={option} className="bg-gray-800 text-white">
                            {option}
                          </option>
                        ))}
                      </select>
                    </div>
                    <button
                      onClick={() => applyToAll(key, metadata[activeImageIndex][key])}
                      disabled={!metadata[activeImageIndex][key]}
                      className="px-3 py-2.5 text-xs font-medium text-blue-400 hover:text-blue-300 hover:bg-gray-800 rounded-lg transition-colors disabled:text-gray-500 disabled:hover:bg-transparent whitespace-nowrap"
                    >
                      Apply to all
                    </button>
                  </div>
                </div>
              ))}

              {/* Temperature Range */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-200">
                  Temperature Range (°C)
                </label>
                <div className="flex items-center gap-2">
                  <div className="flex-1 flex items-center gap-2">
                    <input
                      type="number"
                      placeholder="Min"
                      value={metadata[activeImageIndex].temperature_range.min}
                      onChange={(e) => handleMetadataChange(activeImageIndex, 'temperature_range', {
                        ...metadata[activeImageIndex].temperature_range,
                        min: parseInt(e.target.value) || 0
                      })}
                      className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <span className="text-gray-400">to</span>
                    <input
                      type="number"
                      placeholder="Max"
                      value={metadata[activeImageIndex].temperature_range.max}
                      onChange={(e) => handleMetadataChange(activeImageIndex, 'temperature_range', {
                        ...metadata[activeImageIndex].temperature_range,
                        max: parseInt(e.target.value) || 0
                      })}
                      className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <button
                    onClick={() => applyToAll('temperature_range', metadata[activeImageIndex].temperature_range)}
                    className="px-3 py-2.5 text-xs font-medium text-blue-400 hover:text-blue-300 hover:bg-gray-800 rounded-lg transition-colors whitespace-nowrap"
                  >
                    Apply to all
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-800 bg-gray-900/95 backdrop-blur-sm">
          <button
            onClick={() => setIsModalOpen(false)}
            className="px-4 py-2 text-gray-300 hover:text-white border border-gray-700 hover:border-gray-600 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={uploadImages}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
          >
            <Upload size={16} />
            Upload {mockFiles.length} items
          </button>
        </div>
      </div>
    </div>
  );
}