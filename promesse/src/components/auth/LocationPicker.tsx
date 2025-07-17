import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { MapPin } from 'lucide-react';

// Fix for default marker icons
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

export interface Location {
  lat: number;
  lng: number;
  address?: string;
}

export const LocationPicker: React.FC<{
  location: Location | null;
  onLocationChange: (location: Location) => void;
}> = ({ location, onLocationChange }) => {
  const [address, setAddress] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [mapCenter, setMapCenter] = useState<[number, number]>([0, 0]);
  const [userLocation, setUserLocation] = useState<Location | null>(null);
  const [watchId, setWatchId] = useState<number | null>(null);
  const [isTracking, setIsTracking] = useState(false);

  // Custom icon for live location marker
  const liveLocationIcon = new L.Icon({
    iconUrl: 'https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678111-map-marker-512.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
  });

  // Get user's current location
  const getUserLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const newLocation = {
            lat: position.coords.latitude,
            lng: position.coords.longitude
          };
          setUserLocation(newLocation);
          setMapCenter([newLocation.lat, newLocation.lng]);
          onLocationChange(newLocation);
          reverseGeocode(newLocation.lat, newLocation.lng);
        },
        (error) => {
          console.error('Error getting location:', error);
          // Default to a known location if geolocation fails
          const defaultLocation = { lat: 40.7128, lng: -74.0060 }; // New York
          setMapCenter([defaultLocation.lat, defaultLocation.lng]);
          onLocationChange(defaultLocation);
        }
      );
    } else {
      console.error('Geolocation is not supported by this browser.');
      const defaultLocation = { lat: 40.7128, lng: -74.0060 }; // New York
      setMapCenter([defaultLocation.lat, defaultLocation.lng]);
      onLocationChange(defaultLocation);
    }
  };

  // Start tracking live location
  const startLiveTracking = () => {
    if (navigator.geolocation) {
      setIsTracking(true);
      const id = navigator.geolocation.watchPosition(
        (position) => {
          const newLocation = {
            lat: position.coords.latitude,
            lng: position.coords.longitude
          };
          setUserLocation(newLocation);
          setMapCenter([newLocation.lat, newLocation.lng]);
          reverseGeocode(newLocation.lat, newLocation.lng);
        },
        (error) => {
          console.error('Error tracking location:', error);
          setIsTracking(false);
        },
        {
          enableHighAccuracy: true,
          maximumAge: 10000,
          timeout: 5000
        }
      );
      setWatchId(id);
    } else {
      console.error('Geolocation is not supported by this browser.');
    }
  };

  // Stop tracking live location
  const stopLiveTracking = () => {
    if (watchId && navigator.geolocation) {
      navigator.geolocation.clearWatch(watchId);
      setWatchId(null);
      setIsTracking(false);
    }
  };

  // Toggle live tracking
  const toggleLiveTracking = () => {
    if (isTracking) {
      stopLiveTracking();
    } else {
      startLiveTracking();
    }
  };

  // Reverse geocode coordinates to get address
  const reverseGeocode = async (lat: number, lng: number) => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`
      );
      const data = await response.json();
      if (data.display_name) {
        setAddress(data.display_name);
      }
    } catch (error) {
      console.error('Error reverse geocoding:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Geocode address to get coordinates
  const geocodeAddress = async () => {
    if (!address) return;
    setIsLoading(true);
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}`
      );
      const data = await response.json();
      if (data.length > 0) {
        const newLocation = {
          lat: parseFloat(data[0].lat),
          lng: parseFloat(data[0].lon),
          address: address
        };
        setMapCenter([newLocation.lat, newLocation.lng]);
        onLocationChange(newLocation);
      }
    } catch (error) {
      console.error('Error geocoding:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Map click handler
  const MapClickHandler = () => {
    useMapEvents({
      click: async (e) => {
        const newLocation = {
          lat: e.latlng.lat,
          lng: e.latlng.lng
        };
        onLocationChange(newLocation);
        await reverseGeocode(newLocation.lat, newLocation.lng);
      },
    });
    return null;
  };

  useEffect(() => {
    if (location) {
      setMapCenter([location.lat, location.lng]);
      if (location.address) {
        setAddress(location.address);
      } else {
        reverseGeocode(location.lat, location.lng);
      }
    } else {
      getUserLocation();
    }

    // Clean up watch position on unmount
    return () => {
      if (watchId) {
        navigator.geolocation.clearWatch(watchId);
      }
    };
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Input
          placeholder="Enter address or place"
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          className="bg-gray-700 flex-1"
        />
        <Button
          type="button"
          onClick={geocodeAddress}
          disabled={isLoading || !address}
        >
          {isLoading ? 'Searching...' : 'Search'}
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={getUserLocation}
          disabled={isLoading}
        >
          <MapPin className="h-4 w-4" />
        </Button>
        <Button
          type="button"
          variant={isTracking ? 'destructive' : 'outline'}
          onClick={toggleLiveTracking}
          disabled={isLoading}
        >
          {isTracking ? 'Stop Tracking' : 'Live Track'}
        </Button>
      </div>
      
      <div className="h-64 rounded-md overflow-hidden relative">
        <MapContainer
          center={mapCenter}
          zoom={13}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          <MapClickHandler />
          {location && (
            <Marker position={[location.lat, location.lng]}>
              <Popup>Your selected location</Popup>
            </Marker>
          )}
          {userLocation && (
            <Marker 
              position={[userLocation.lat, userLocation.lng]} 
              icon={liveLocationIcon}
            >
              <Popup>
                {isTracking ? (
                  <div>
                    <strong>Your live location</strong>
                    <p>Lat: {userLocation.lat.toFixed(6)}</p>
                    <p>Lng: {userLocation.lng.toFixed(6)}</p>
                  </div>
                ) : (
                  <div>
                    <strong>Your current location</strong>
                    <p>Lat: {userLocation.lat.toFixed(6)}</p>
                    <p>Lng: {userLocation.lng.toFixed(6)}</p>
                  </div>
                )}
              </Popup>
            </Marker>
          )}
        </MapContainer>
      </div>
      
      {userLocation && (
        <div className="text-sm text-gray-400">
          <p>Latitude: {userLocation.lat.toFixed(6)}</p>
          <p>Longitude: {userLocation.lng.toFixed(6)}</p>
          {address && <p>Address: {address}</p>}
          {isTracking && <p className="text-green-500">Live tracking active</p>}
        </div>
      )}
    </div>
  );
};
