import React, { useState, FormEvent } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Textarea } from '../ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Calculator, Upload, X, CloudSun, Calendar, Thermometer, MapPin } from 'lucide-react';
import { Location, LocationPicker } from './LocationPicker';
import { BMICalculator } from './BMICalculator';
import { DialogFooter } from '../ui/dialog';

interface RegistrationProps {
  switchToLogin: () => void;
}

export const Registration: React.FC<RegistrationProps> = ({ switchToLogin }) => {
  const { register, isLoading } = useAuth();
  const [step, setStep] = useState(1);

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
    window.location.reload()

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

  const nextStep = () => setStep(prev => prev + 1);
  const prevStep = () => setStep(prev => prev - 1);

  return (
    <>
      <BMICalculator
        isOpen={showBMICalculator}
        onClose={() => setShowBMICalculator(false)}
        onSave={handleBMISave}
      />
      <form onSubmit={handleRegister} className="space-y-6">
        {step === 1 && (
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
        )}

        {step === 2 && (
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
        )}

        {step === 3 && (
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
        )}

        {step === 4 && (
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
        )}

        {step === 5 && (
          <>
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
          </>
        )}

        {step === 6 && (
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
        )}

        {step === 7 && (
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
        )}

        <DialogFooter>
          <div className="flex justify-between w-full">
            <Button type="button" variant="link" onClick={switchToLogin}>
              Already have an account? Login
            </Button>
            <div className="flex gap-2">
              {step > 1 && <Button type="button" variant="outline" onClick={prevStep}>Previous</Button>}
              {step < 7 && <Button type="button" onClick={nextStep}>Next</Button>}
              {step === 7 && (
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? 'Creating account...' : 'Create Account'}
                </Button>
              )}
            </div>
          </div>
        </DialogFooter>
      </form>
    </>
  );
};
