import { useState } from 'react';

interface Coordinates {
  lat: number;
  lon: number;
}

interface GeolocationState {
  coordinates: Coordinates | null;
  error: string | null;
  isLoading: boolean;
  getLocation: () => void;
}

const useGeolocation = (): GeolocationState => {
  const [coordinates, setCoordinates] = useState<Coordinates | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const getLocation = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setCoordinates(null);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setCoordinates({
          lat: position.coords.latitude,
          lon: position.coords.longitude,
        });
        setIsLoading(false);
      },
      (err) => {
        let errorMessage = 'Failed to retrieve location.';
        // Using direct numeric values for error codes as per GeolocationPositionError spec
        switch (err.code) {
          case 1: // PERMISSION_DENIED
            errorMessage = 'Specific: Permission Denied'; // Make it unique for debugging
            break;
          case 2: // POSITION_UNAVAILABLE
            errorMessage = 'Specific: Position Unavailable'; // Make it unique
            break;
          case 3: // TIMEOUT
            errorMessage = 'Specific: Timeout'; // Make it unique
            break;
          default:
            errorMessage = `Default: ${err.message || 'Unknown geolocation error'}`; // Ensure err.message is used
            break;
        }
        setError(errorMessage);
        setIsLoading(false);
      },
      {
        enableHighAccuracy: true, // You can adjust options as needed
        timeout: 10000, // 10 seconds
        maximumAge: 0 // Force fresh location
      }
    );
  };

  return { coordinates, error, isLoading, getLocation };
};

export default useGeolocation;
