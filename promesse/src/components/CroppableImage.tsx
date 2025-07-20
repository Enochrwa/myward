import React, { useState, useRef } from 'react';
import ReactCrop, { Crop } from 'react-image-crop';
import 'react-image-crop/dist/ReactCrop.css';
import { Button } from '@/components/ui/button';
import { ZoomIn, ZoomOut, CropIcon } from 'lucide-react';

interface CroppableImageProps {
  src: string;
  onCropComplete: (croppedImageUrl: string) => void;
}

const CroppableImage: React.FC<CroppableImageProps> = ({ src, onCropComplete }) => {
  const [crop, setCrop] = useState<Crop>();
  const [completedCrop, setCompletedCrop] = useState<Crop>();
  const [scale, setScale] = useState(1);
  const imgRef = useRef<HTMLImageElement>(null);

  const makeClientCrop = async (cropData: Crop) => {
    if (imgRef.current && cropData.width && cropData.height) {
      const croppedImageUrl = await getCroppedImg(
        imgRef.current,
        cropData,
        'newFile.jpeg'
      );
      onCropComplete(croppedImageUrl);
    }
  };

  const getCroppedImg = (image: HTMLImageElement, cropData: Crop, fileName: string): Promise<string> => {
    const canvas = document.createElement('canvas');
    const scaleX = image.naturalWidth / image.width;
    const scaleY = image.naturalHeight / image.height;
    canvas.width = cropData.width;
    canvas.height = cropData.height;
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
        cropData.width,
        cropData.height
      );
    }

    return new Promise((resolve, reject) => {
      canvas.toBlob((blob) => {
        if (!blob) {
          reject(new Error('Canvas is empty'));
          return;
        }
        const fileUrl = window.URL.createObjectURL(blob);
        resolve(fileUrl);
      }, 'image/jpeg');
    });
  };

  return (
    <div className="flex flex-col items-center">
      <ReactCrop
        crop={crop}
        onChange={(c) => setCrop(c)}
        onComplete={(c) => setCompletedCrop(c)}
      >
        <img
          ref={imgRef}
          src={src}
          style={{ transform: `scale(${scale})` }}
          alt="Crop me"
        />
      </ReactCrop>
      <div className="flex items-center space-x-2 mt-2">
        <Button onClick={() => setScale(scale + 0.1)}><ZoomIn /></Button>
        <Button onClick={() => setScale(scale - 0.1)}><ZoomOut /></Button>
        <Button onClick={() => makeClientCrop(completedCrop)}><CropIcon /></Button>
      </div>
    </div>
  );
};

export default CroppableImage;
