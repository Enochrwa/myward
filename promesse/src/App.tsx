
import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { AuthProvider } from '@/contexts/AuthContext'; // Added AuthProvider import
import IndexPage from './pages/IndexPage';
import DashboardPage from './pages/DashboardPage';
import WardrobePage from './pages/WardrobePage';
import CommunityPage from './pages/CommunityPage';
import ProfilePage from './pages/ProfilePage';
import SettingsPage from './pages/SettingsPage';
import AdminPage from './pages/AdminPage';
import NotFoundPage from './pages/NotFoundPage';
import Header from './components/Header';
import PrivateRoute from './components/auth/PrivateRoute';
import UploadForm from './components/UploadForm';
import RenderRecommendations from './components/Recommendations';
import AIStudioPage from './pages/AIStudioPage';
import OutfitBuilderPage from "./pages/OutfitBuilderPage"
import ImageGallery from "./components/ImageGallery"
import axios from 'axios'
import ClotheClassifier from './components/ClotheClassifier';
import OutfitRecommendations from './components/test/OutfitRecommendations';
import OutfitPage from "./pages/OutfitPage"
import WardrobeAnalytics from './components/WardrobeAnalytics';
import WardrobeAndOutfits from './components/WardrobeAndOutfits';
import DisplayClothes from "./components/DisplayClothes"
import WeatherOccasionRecommender from './components/WeatherOccasionRecommender';
import WeeklyPlanner from './components/WeeklyPlanner';
import apiClient from './lib/apiClient';
import LoginPage from './pages/LoginPage';

function App() {

  const [items, setItems] = useState<[]>([]);
  // const [isAuthModalOpen, setIsAuthModalOpen] = useState(true);
  const [ isOpen, setOpen] = useState(false);

  const onClose = () =>{
    setOpen(false)
  }


    // API returns direct array of items



    useEffect(() => {
      (async () => {
        try {
          const token = localStorage.getItem("token"); // or use the exact key you stored the token with

          const allItems = await axios.get("http://127.0.0.1:8000/api/outfit/user-items", {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });

          setItems(allItems?.data)
        } catch (error) {
          console.error("Error fetching images", error);
        }
      })();
    }, []);


    const getAuthToken = () => localStorage.getItem("token");
    const token = getAuthToken();


    console.log("Token:", token); // inside apiClient



  
    // const fetchImages = async () => {
      
    //   try {
    //     const response = await apiClient('/images/?limit=50');
      
    //     setItems(response?.data?.images || []);
    //     console.log("occasion: ", response?.data)
    //   } catch (error) {
    //     console.error('Error fetching images:', error);
    //   } finally {
    //     console.log("Fetching ready")
    //   }
    // };
  
    // useEffect(() => {
    //   fetchImages();
    // }, []);

 

  return (
    <ThemeProvider>
      <AuthProvider> {/* Added AuthProvider wrapper */}
        <Router>
          <div className="min-h-screen bg-background">
            <Header />
          <main className="pt-16">
            <Routes>
              <Route path="/" element={<IndexPage />}/>
              <Route path='/clothes' element={<DisplayClothes/>}  />
              <Route path='/login' element={<LoginPage isOpen={ isOpen} onClose={onClose}/>} />
              <Route path="/outfit-builder/:imageId" element={<OutfitBuilderPage />} />
              <Route path='/weather' element={<WeatherOccasionRecommender wardrobeItems={items || []} />} />
              <Route path='/classifier' element={<ClotheClassifier/>} />
              <Route path='/weekly' element={<WeeklyPlanner/>} />
              <Route path='/saved-outfits' element={<WardrobeAndOutfits/>} />
              <Route path="/upload" element={<UploadForm />} />
              <Route path="/outfit" element={<OutfitPage/>} />
              <Route path="/gallery" element={<OutfitRecommendations/>} />
              <Route path='/recommendations' element={<RenderRecommendations/>}/>
              <Route element={<PrivateRoute roles={['user', 'admin', 'superadmin']} />}>
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/wardrobe" element={<WardrobePage />} />
                <Route path="/ai-studio/*" element={<AIStudioPage />} />
                <Route path="/community" element={<CommunityPage />} />
                <Route path="/profile" element={<ProfilePage />} />
                <Route path="/settings" element={<SettingsPage />} />
              </Route>
              <Route element={<PrivateRoute roles={['admin', 'superadmin']} />}>
                <Route path="/admin" element={<AdminPage />} />
              </Route>
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </main>
        </div>
      </Router>
      </AuthProvider> {/* Closed AuthProvider wrapper */}
    </ThemeProvider>
  );
}

export default App;