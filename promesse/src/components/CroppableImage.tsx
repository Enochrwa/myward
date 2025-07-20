import React, { useState, useRef } from 'react';
import ReactCrop, { Crop } from 'react-image-crop';
import 'react-image-crop/dist/ReactCrop.css';
import { Button } from '@/components/ui/button';
import { ZoomIn, ZoomOut, CropIcon } from 'lucide-react';

interface CroppableImageProps {
  src: string;
  onCropComplete: (croppedImageUrl: string) => void;
}

interface CroppableImageProps {
  src: string;
  onCropComplete: (croppedImageUrl: string) => void;
  onClose: () => void;
}

const CroppableImage: React.FC<CroppableImageProps> = ({ src, onCropComplete, onClose }) => {
  const [crop, setCrop] = useState<Crop>({ unit: '%', width: 50, aspect: 1 });
  const [completedCrop, setCompletedCrop] = useState<Crop>();
  const [scale, setScale] = useState(1);
  const imgRef = useRef<HTMLImageElement>(null);

  const handleCrop = async () => {
    if (imgRef.current && completedCrop?.width && completedCrop?.height) {
      const croppedImageUrl = await getCroppedImg(
        imgRef.current,
        completedCrop,
        'newFile.jpeg'
      );
      onCropComplete(croppedImageUrl);
      onClose(); // Close the dialog after applying the crop
    }
  };

  const getCroppedImg = (image: HTMLImageElement, cropData: Crop, fileName: string): Promise<string> => {
    const canvas = document.createElement('canvas');
    const scaleX = image.naturalWidth / image.width;
    const scaleY = image.naturalHeight / image.height;
    
    canvas.width = cropData.width * scaleX;
    canvas.height = cropData.height * scaleY;
    
    const ctx = canvas.getContext('2d');

    if (ctx) {
      ctx.drawImage(
        image,
        cropData.x * scaleX,
        cropData.y * scaleY,
        cropData.width * scaleX,
        cropData.height * scaleY,
        0,
        0,
        cropData.width * scaleX,
        cropData.height * scaleY
      );
    }

    return new Promise((resolve) => {
      canvas.toBlob((blob) => {
        if (blob) {
          const fileUrl = window.URL.createObjectURL(blob);
          resolve(fileUrl);
        }
      }, 'image/jpeg');
    });
  };

  return (
    <div className="flex flex-col items-center p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
      <div className="w-full max-w-md">
        <ReactCrop
          crop={crop}
          onChange={(c) => setCrop(c)}
          onComplete={(c) => setCompletedCrop(c)}
          aspect={1}
        >
          <img
            ref={imgRef}
            src={src}
            style={{ transform: `scale(${scale})`, maxHeight: "70vh" }}
            alt="Crop me"
          />
        </ReactCrop>
      </div>
      <div className="flex items-center space-x-4 mt-4 p-2 bg-white dark:bg-gray-700 rounded-full shadow-md">
        <Button variant="ghost" onClick={() => setScale(s => Math.min(s + 0.1, 3))}><ZoomIn className="text-gray-600 dark:text-gray-300" /></Button>
        <Button variant="ghost" onClick={() => setScale(s => Math.max(s - 0.1, 0.1))}><ZoomOut className="text-gray-600 dark:text-gray-300" /></Button>
        <Button onClick={handleCrop} className="bg-green-500 hover:bg-green-600 text-white rounded-full px-6 py-2 shadow-lg">
          <CropIcon className="mr-2" />
          Apply Crop
        </Button>
      </div>
    </div>
  );
};

export default CroppableImage;
