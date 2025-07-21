import React, { useState, FormEvent, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription, DialogClose } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Calculator, Upload, X, CloudSun, Calendar, Thermometer, MapPin } from 'lucide-react';

// React Leaflet imports
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialView?: 'login' | 'register';
}

interface BMICalculatorProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (bmi: number, height: string, weight: string) => void;
}

interface Location {
  lat: number;
  lng: number;
  address?: string;
}

const LocationPicker: React.FC<{
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

const BMICalculator: React.FC<BMICalculatorProps> = ({ isOpen, onClose, onSave }) => {
  const [height, setHeight] = useState('');
  const [weight, setWeight] = useState('');
  const [heightUnit, setHeightUnit] = useState<'cm' | 'ft'>('cm');
  const [weightUnit, setWeightUnit] = useState<'kg' | 'lbs'>('kg');
  const [feet, setFeet] = useState('');
  const [inches, setInches] = useState('');

  const calculateBMI = () => {
    let heightInMeters = 0;
    let weightInKg = 0;

    if (heightUnit === 'cm') {
      heightInMeters = parseFloat(height) / 100;
    } else {
      const totalInches = parseFloat(feet) * 12 + parseFloat(inches);
      heightInMeters = totalInches * 0.0254;
    }

    if (weightUnit === 'kg') {
      weightInKg = parseFloat(weight);
    } else {
      weightInKg = parseFloat(weight) * 0.453592;
    }

    const bmi = weightInKg / (heightInMeters * heightInMeters);
    const heightStr = heightUnit === 'cm' ? `${height}cm` : `${feet}'${inches}"`;
    const weightStr = `${weight}${weightUnit}`;

    onSave(Math.round(bmi * 10) / 10, heightStr, weightStr);
    onClose();
  };

  const isValid = () => {
    if (heightUnit === 'cm') {
      return height && parseFloat(height) > 0 && weight && parseFloat(weight) > 0;
    } else {
      return feet && inches && parseFloat(feet) > 0 && parseFloat(inches) >= 0 && weight && parseFloat(weight) > 0;
    }
  };


  return (
    <Dialog open={isOpen} onOpenChange={(open) => { if (!open) onClose(); }}>
      <DialogContent className="sm:max-w-[400px] bg-gray-950">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Calculator className="h-5 w-5" />
            BMI Calculator
          </DialogTitle>
          <DialogDescription>
            Calculate your Body Mass Index automatically
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label>Height</Label>
            <div className="flex gap-2">
              <Select value={heightUnit} onValueChange={(value: 'cm' | 'ft') => setHeightUnit(value)}>
                <SelectTrigger className="w-20 bg-gray-700">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cm">cm</SelectItem>
                  <SelectItem value="ft">ft</SelectItem>
                </SelectContent>
              </Select>
              {heightUnit === 'cm' ? (
                <Input placeholder="170" value={height} onChange={(e) => setHeight(e.target.value)} className="bg-gray-700" type="number" />
              ) : (
                <div className="flex gap-1 flex-1">
                  <Input placeholder="5" value={feet} onChange={(e) => setFeet(e.target.value)} className="bg-gray-700" type="number" />
                  <span className="self-center text-sm">ft</span>
                  <Input placeholder="8" value={inches} onChange={(e) => setInches(e.target.value)} className="bg-gray-700" type="number" />
                  <span className="self-center text-sm">in</span>
                </div>
              )}
            </div>
          </div>
          <div className="grid gap-2">
            <Label>Weight</Label>
            <div className="flex gap-2">
              <Select value={weightUnit} onValueChange={(value: 'kg' | 'lbs') => setWeightUnit(value)}>
                <SelectTrigger className="w-20 bg-gray-700">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="kg">kg</SelectItem>
                  <SelectItem value="lbs">lbs</SelectItem>
                </SelectContent>
              </Select>
              <Input placeholder={weightUnit === 'kg' ? '70' : '154'} value={weight} onChange={(e) => setWeight(e.target.value)} className="bg-gray-700 flex-1" type="number" />
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="button" onClick={calculateBMI} disabled={!isValid()}>
            Calculate BMI
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

const LoginPage: React.FC<AuthModalProps> = ({onClose, isOpen, initialView = 'login' }) => {
  const [view, setView] = useState<'login' | 'register'>(initialView);
  const { login, register, error, isLoading, user } = useAuth();

  // Login fields
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  // Registration fields
  const [regEmail, setRegEmail] = useState('');
  const [regUsername, setRegUsername] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');
  const [height, setHeight] = useState('');
  const [weight, setWeight] = useState('');
  const [bmi, setBmi] = useState('');
  const [bodyType, setBodyType] = useState('');
  const [skinTone, setSkinTone] = useState('');
  const [location, setLocation] = useState<Location | null>(null);
  const [timezone, setTimezone] = useState('');
  const [lifestyle, setLifestyle] = useState('');
  const [budgetRange, setBudgetRange] = useState('');
  const [stylePreferences, setStylePreferences] = useState('');
  const [colorPreferences, setColorPreferences] = useState('');
  const [favoriteColors, setFavoriteColors] = useState('');
  const [avoidColors, setAvoidColors] = useState('');
  const [allergies, setAllergies] = useState('');
  const [disabilities, setDisabilities] = useState('');
  const [profilePhoto, setProfilePhoto] = useState<File | null>(null);
  const [bodyPhotos, setBodyPhotos] = useState<File[]>([]);
  
  // Weather preferences
  const [weatherPreferences, setWeatherPreferences] = useState<string[]>([]);
  const [temperatureRange, setTemperatureRange] = useState<[string, string]>(['10', '30']);
  
  // Occasion preferences
  const [occasionPreferences, setOccasionPreferences] = useState<string[]>([]);
  
  const [showBMICalculator, setShowBMICalculator] = useState(false);

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    await login({ username, password });
  };

  const handleRegister = async (e: FormEvent) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('username', regUsername);
    formData.append('email', regEmail);
    formData.append('password', regPassword);
    formData.append('fullName', fullName);
    formData.append('age', age);
    formData.append('gender', gender);
    formData.append('height', height);
    formData.append('weight', weight);
    formData.append('bmi', bmi);
    formData.append('bodyType', bodyType);
    formData.append('skinTone', skinTone);
    formData.append('location', location ? JSON.stringify(location) : '');
    formData.append('timezone', timezone);
    formData.append('lifestyle', lifestyle);
    formData.append('budgetRange', budgetRange);
    formData.append('stylePreferences', stylePreferences);
    formData.append('colorPreferences', colorPreferences);
    formData.append('favoriteColors', favoriteColors);
    formData.append('avoidColors', avoidColors);
    formData.append('allergies', allergies);
    formData.append('disabilities', disabilities);
    formData.append('weatherPreferences', JSON.stringify(weatherPreferences));
    formData.append('temperatureRange', JSON.stringify(temperatureRange));
    formData.append('occasionPreferences', JSON.stringify(occasionPreferences));

    if (profilePhoto) {
      formData.append('profilePhoto', profilePhoto);
    }

    bodyPhotos.forEach((photo, index) => {
      formData.append(`bodyPhoto${index}`, photo);
    });

    await register(formData);
  };

  const handleBMISave = (calculatedBMI: number, calculatedHeight: string, calculatedWeight: string) => {
    setBmi(calculatedBMI.toString());
    setHeight(calculatedHeight);
    setWeight(calculatedWeight);
  };

  const handleProfilePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setProfilePhoto(e.target.files[0]);
    }
  };

  const handleBodyPhotosChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setBodyPhotos(Array.from(e.target.files));
    }
  };

  const removeBodyPhoto = (index: number) => {
    setBodyPhotos(bodyPhotos.filter((_, i) => i !== index));
  };

  const toggleWeatherPreference = (preference: string) => {
    setWeatherPreferences(prev =>
      prev.includes(preference)
        ? prev.filter(p => p !== preference)
        : [...prev, preference]
    );
  };

  const toggleOccasionPreference = (occasion: string) => {
    setOccasionPreferences(prev =>
      prev.includes(occasion)
        ? prev.filter(o => o !== occasion)
        : [...prev, occasion]
    );
  };

  const resetLoginForm = () => {
    setUsername('');
    setPassword('');
  };

  const resetRegisterForm = () => {
    setRegEmail('');
    setRegUsername('');
    setRegPassword('');
    setFullName('');
    setAge('');
    setGender('');
    setHeight('');
    setWeight('');
    setBmi('');
    setBodyType('');
    setSkinTone('');
    setLocation(null);
    setTimezone('');
    setLifestyle('');
    setBudgetRange('');
    setStylePreferences('');
    setColorPreferences('');
    setFavoriteColors('');
    setAvoidColors('');
    setAllergies('');
    setDisabilities('');
    setProfilePhoto(null);
    setBodyPhotos([]);
    setWeatherPreferences([]);
    setOccasionPreferences([]);
  };

  const switchToRegister = () => {
    setView('register');
    resetLoginForm();
  };

  const switchToLogin = () => {
    setView('login');
    resetRegisterForm();
  };

  React.useEffect(() => {
    if (isOpen) {
      setView(initialView);
      resetLoginForm();
      resetRegisterForm();
    }
  }, [isOpen, initialView]);

  React.useEffect(() => {
    if (user && !isLoading && !error && isOpen) {
      onClose();
      resetLoginForm();
      resetRegisterForm();
    }
  }, [user, isLoading, error, isOpen, onClose]);

  return (
    <>
      <BMICalculator 
        isOpen={showBMICalculator} 
        onClose={() => setShowBMICalculator(false)} 
        onSave={handleBMISave} 
      />
      
      <Dialog open={isOpen} onOpenChange={(open) => { if (!open) onClose(); }}>
        <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto bg-gray-950">
          <DialogHeader>
            <DialogTitle>{view === 'login' ? 'Login' : 'Create Your Digital Wardrobe Profile'}</DialogTitle>
            <DialogDescription>
              {view === 'login' ? 'Enter your credentials to access your digital wardrobe.' : 'Tell us about yourself to get personalized outfit recommendations based on weather, occasion, and your style.'}
            </DialogDescription>
          </DialogHeader>

          {error && <p className="text-red-500 text-sm text-center py-2">{error}</p>}
          
          {view === 'login' ? (
            <form onSubmit={handleLogin}>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="username-login" className="text-right">
                    Username
                  </Label>
                  <Input
                    id="username-login"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="col-span-3 bg-gray-700"
                    required
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="password-login" className="text-right">
                    Password
                  </Label>
                  <Input
                    id="password-login"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="col-span-3 bg-gray-700"
                    required
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="link" onClick={switchToRegister}>
                  Create an account
                </Button>
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? 'Logging in...' : 'Login'}
                </Button>
              </DialogFooter>
            </form>
          ) : (
            <form onSubmit={handleRegister} className="space-y-6">
              {/* Basic Information */}
              <Card className="bg-gray-900 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-lg">Basic Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="fullName">Full Name</Label>
                      <Input
                        id="fullName"
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        className="bg-gray-700"
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="age">Age</Label>
                      <Input
                        id="age"
                        type="number"
                        value={age}
                        onChange={(e) => setAge(e.target.value)}
                        className="bg-gray-700"
                        required
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="regUsername">Username</Label>
                      <Input
                        id="regUsername"
                        value={regUsername}
                        onChange={(e) => setRegUsername(e.target.value)}
                        className="bg-gray-700"
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="regEmail">Email</Label>
                      <Input
                        id="regEmail"
                        type="email"
                        value={regEmail}
                        onChange={(e) => setRegEmail(e.target.value)}
                        className="bg-gray-700"
                        required
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="regPassword">Password</Label>
                    <Input
                      id="regPassword"
                      type="password"
                      value={regPassword}
                      onChange={(e) => setRegPassword(e.target.value)}
                      className="bg-gray-700"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="gender">Gender</Label>
                    <Select value={gender} onValueChange={setGender}>
                      <SelectTrigger className="bg-gray-700">
                        <SelectValue placeholder="Select gender" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="male">Male</SelectItem>
                        <SelectItem value="female">Female</SelectItem>
                        <SelectItem value="non-binary">Non-binary</SelectItem>
                        <SelectItem value="prefer-not-to-say">Prefer not to say</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>

              {/* Physical Characteristics */}
              <Card className="bg-gray-900 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-lg">Physical Characteristics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="height">Height</Label>
                      <Input
                        id="height"
                        placeholder="e.g., 170cm or 5'8&quot;"
                        value={height}
                        onChange={(e) => setHeight(e.target.value)}
                        className="bg-gray-700"
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="weight">Weight</Label>
                      <Input
                        id="weight"
                        placeholder="e.g., 70kg or 154lbs"
                        value={weight}
                        onChange={(e) => setWeight(e.target.value)}
                        className="bg-gray-700"
                        required
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <Label htmlFor="bmi">BMI (optional)</Label>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => setShowBMICalculator(true)}
                        >
                          <Calculator className="h-4 w-4" />
                          Calculate
                        </Button>
                      </div>
                      <Input
                        id="bmi"
                        placeholder="e.g., 22.5"
                        value={bmi}
                        onChange={(e) => setBmi(e.target.value)}
                        className="bg-gray-700"
                        type="number"
                        step="0.1"
                      />
                    </div>
                    <div>
                      <Label htmlFor="bodyType">Body Type</Label>
                      <Select value={bodyType} onValueChange={setBodyType}>
                        <SelectTrigger className="bg-gray-700">
                          <SelectValue placeholder="Select body type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="ectomorph">Ectomorph (Lean)</SelectItem>
                          <SelectItem value="mesomorph">Mesomorph (Athletic)</SelectItem>
                          <SelectItem value="endomorph">Endomorph (Curvy)</SelectItem>
                          <SelectItem value="apple">Apple Shape</SelectItem>
                          <SelectItem value="pear">Pear Shape</SelectItem>
                          <SelectItem value="hourglass">Hourglass</SelectItem>
                          <SelectItem value="rectangle">Rectangle</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="skinTone">Skin Tone</Label>
                    <Select value={skinTone} onValueChange={setSkinTone}>
                      <SelectTrigger className="bg-gray-700">
                        <SelectValue placeholder="Select skin tone" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="fair">Fair</SelectItem>
                        <SelectItem value="light">Light</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="olive">Olive</SelectItem>
                        <SelectItem value="tan">Tan</SelectItem>
                        <SelectItem value="dark">Dark</SelectItem>
                        <SelectItem value="deep">Deep</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>

              {/* Photos */}
              <Card className="bg-gray-900 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-lg">Photos</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="profilePhoto">Profile Photo</Label>
                    <Input
                      id="profilePhoto"
                      type="file"
                      accept="image/*"
                      onChange={handleProfilePhotoChange}
                      className="bg-gray-700"
                    />
                  </div>
                  <div>
                    <Label htmlFor="bodyPhotos">Body Photos (for better fit recommendations)</Label>
                    <Input
                      id="bodyPhotos"
                      type="file"
                      accept="image/*"
                      multiple
                      onChange={handleBodyPhotosChange}
                      className="bg-gray-700"
                    />
                    {bodyPhotos.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-2">
                        {bodyPhotos.map((photo, index) => (
                          <div key={index} className="relative">
                            <img
                              src={URL.createObjectURL(photo)}
                              alt={`Body photo ${index + 1}`}
                              className="h-16 w-16 object-cover rounded border"
                            />
                            <button
                              type="button"
                              onClick={() => removeBodyPhoto(index)}
                              className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1"
                            >
                              <X className="h-3 w-3" />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Location & Lifestyle */}
              <Card className="bg-gray-900 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-lg">Location & Lifestyle</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Location (for weather-based recommendations)</Label>
                    <LocationPicker 
                      location={location} 
                      onLocationChange={(loc) => setLocation(loc)} 
                    />
                  </div>
                  <div>
                    <Label htmlFor="timezone">Timezone</Label>
                    <Select value={timezone} onValueChange={setTimezone}>
                      <SelectTrigger className="bg-gray-700">
                        <SelectValue placeholder="Select timezone" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="UTC-12">UTC-12</SelectItem>
                        <SelectItem value="UTC-11">UTC-11</SelectItem>
                        <SelectItem value="UTC-10">UTC-10</SelectItem>
                        <SelectItem value="UTC-9">UTC-9</SelectItem>
                        <SelectItem value="UTC-8">UTC-8</SelectItem>
                        <SelectItem value="UTC-7">UTC-7</SelectItem>
                        <SelectItem value="UTC-6">UTC-6</SelectItem>
                        <SelectItem value="UTC-5">UTC-5</SelectItem>
                        <SelectItem value="UTC-4">UTC-4</SelectItem>
                        <SelectItem value="UTC-3">UTC-3</SelectItem>
                        <SelectItem value="UTC-2">UTC-2</SelectItem>
                        <SelectItem value="UTC-1">UTC-1</SelectItem>
                        <SelectItem value="UTC+0">UTC+0</SelectItem>
                        <SelectItem value="UTC+1">UTC+1</SelectItem>
                        <SelectItem value="UTC+2">UTC+2</SelectItem>
                        <SelectItem value="UTC+3">UTC+3</SelectItem>
                        <SelectItem value="UTC+4">UTC+4</SelectItem>
                        <SelectItem value="UTC+5">UTC+5</SelectItem>
                        <SelectItem value="UTC+6">UTC+6</SelectItem>
                        <SelectItem value="UTC+7">UTC+7</SelectItem>
                        <SelectItem value="UTC+8">UTC+8</SelectItem>
                        <SelectItem value="UTC+9">UTC+9</SelectItem>
                        <SelectItem value="UTC+10">UTC+10</SelectItem>
                        <SelectItem value="UTC+11">UTC+11</SelectItem>
                        <SelectItem value="UTC+12">UTC+12</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="lifestyle">Lifestyle</Label>
                    <Select value={lifestyle} onValueChange={setLifestyle}>
                      <SelectTrigger className="bg-gray-700">
                        <SelectValue placeholder="Select lifestyle" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="professional">Professional/Corporate</SelectItem>
                        <SelectItem value="casual">Casual/Relaxed</SelectItem>
                        <SelectItem value="student">Student</SelectItem>
                        <SelectItem value="active">Active/Sporty</SelectItem>
                        <SelectItem value="creative">Creative/Artistic</SelectItem>
                        <SelectItem value="social">Social/Party</SelectItem>
                        <SelectItem value="travel">Travel/Adventure</SelectItem>
                        <SelectItem value="home">Work from Home</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="budgetRange">Budget Range</Label>
                    <Select value={budgetRange} onValueChange={setBudgetRange}>
                      <SelectTrigger className="bg-gray-700">
                        <SelectValue placeholder="Select budget range" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="budget">Budget ($0-$50)</SelectItem>
                        <SelectItem value="moderate">Moderate ($50-$150)</SelectItem>
                        <SelectItem value="mid-range">Mid-range ($150-$300)</SelectItem>
                        <SelectItem value="high-end">High-end ($300-$500)</SelectItem>
                        <SelectItem value="luxury">Luxury ($500+)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>

              {/* Weather Preferences */}
              <Card className="bg-gray-900 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <CloudSun className="h-5 w-5" />
                    Weather Preferences
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Select Weather Conditions You Experience</Label>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {['Sunny', 'Rainy', 'Snowy', 'Windy', 'Humid', 'Dry', 'Cloudy', 'Foggy'].map(condition => (
                        <Button
                          key={condition}
                          type="button"
                          variant={weatherPreferences.includes(condition) ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => toggleWeatherPreference(condition)}
                        >
                          {condition}
                        </Button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <Label className="flex items-center gap-2">
                      <Thermometer className="h-4 w-4" />
                      Comfortable Temperature Range (°C)
                    </Label>
                    <div className="flex items-center gap-4">
                      <div className="flex-1">
                        <Label htmlFor="minTemp">Min</Label>
                        <Input
                          id="minTemp"
                          type="number"
                          value={temperatureRange[0]}
                          onChange={(e) => setTemperatureRange([e.target.value, temperatureRange[1]])}
                          className="bg-gray-700"
                        />
                      </div>
                      <div className="flex-1">
                        <Label htmlFor="maxTemp">Max</Label>
                        <Input
                          id="maxTemp"
                          type="number"
                          value={temperatureRange[1]}
                          onChange={(e) => setTemperatureRange([temperatureRange[0], e.target.value])}
                          className="bg-gray-700"
                        />
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Occasion Preferences */}
              <Card className="bg-gray-900 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Calendar className="h-5 w-5" />
                    Occasion Preferences
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label>Select Common Occasions You Dress For</Label>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {['Work', 'Casual', 'Formal', 'Date Night', 'Wedding', 'Gym', 'Travel', 'Beach', 'Party', 'Interview'].map(occasion => (
                        <Button
                          key={occasion}
                          type="button"
                          variant={occasionPreferences.includes(occasion) ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => toggleOccasionPreference(occasion)}
                        >
                          {occasion}
                        </Button>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Style Preferences */}
              <Card className="bg-gray-900 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-lg">Style Preferences</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="stylePreferences">Style Preferences</Label>
                    <Textarea
                      id="stylePreferences"
                      placeholder="e.g., Minimalist, Bohemian, Classic, Trendy, Vintage..."
                      value={stylePreferences}
                      onChange={(e) => setStylePreferences(e.target.value)}
                      className="bg-gray-700"
                      rows={3}
                    />
                  </div>
                  <div>
                    <Label htmlFor="colorPreferences">Color Preferences</Label>
                    <Select value={colorPreferences} onValueChange={setColorPreferences}>
                      <SelectTrigger className="bg-gray-700">
                        <SelectValue placeholder="Select color preference" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="neutral">Neutral Colors</SelectItem>
                        <SelectItem value="bright">Bright Colors</SelectItem>
                        <SelectItem value="dark">Dark Colors</SelectItem>
                        <SelectItem value="pastel">Pastel Colors</SelectItem>
                        <SelectItem value="earth">Earth Tones</SelectItem>
                        <SelectItem value="monochrome">Monochrome</SelectItem>
                        <SelectItem value="mixed">Mixed/Variety</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="favoriteColors">Favorite Colors</Label>
                      <Input
                        id="favoriteColors"
                        placeholder="e.g., Blue, Green, Black"
                        value={favoriteColors}
                        onChange={(e) => setFavoriteColors(e.target.value)}
                        className="bg-gray-700"
                      />
                    </div>
                    <div>
                      <Label htmlFor="avoidColors">Colors to Avoid</Label>
                      <Input
                        id="avoidColors"
                        placeholder="e.g., Orange, Pink, Yellow"
                        value={avoidColors}
                        onChange={(e) => setAvoidColors(e.target.value)}
                        className="bg-gray-700"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Additional Information */}
              <Card className="bg-gray-900 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-lg">Additional Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="allergies">Allergies/Sensitivities</Label>
                    <Textarea
                      id="allergies"
                      placeholder="e.g., Wool, Latex, Synthetic fabrics..."
                      value={allergies}
                      onChange={(e) => setAllergies(e.target.value)}
                      className="bg-gray-700"
                      rows={2}
                    />
                  </div>
                  <div>
                    <Label htmlFor="disabilities">Accessibility Needs</Label>
                    <Textarea
                      id="disabilities"
                      placeholder="e.g., Mobility limitations, Visual impairments, Dexterity issues..."
                      value={disabilities}
                      onChange={(e) => setDisabilities(e.target.value)}
                      className="bg-gray-700"
                      rows={2}
                    />
                  </div>
                </CardContent>
              </Card>

              <DialogFooter>
                <Button type="button" variant="link" onClick={switchToLogin}>
                  Already have an account? Login
                </Button>
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? 'Creating account...' : 'Create Account'}
                </Button>
              </DialogFooter>
            </form>
          )}
          <DialogClose asChild />
        </DialogContent>
      </Dialog>
    </>
  );
};

export default LoginPage