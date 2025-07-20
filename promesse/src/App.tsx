
import React, { useEffect } from 'react';
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
import UploadForm from './components/UploadForm';
import RenderRecommendations from './components/Recommendations';
import AIStudioPage from './pages/AIStudioPage';
import OutfitBuilderPage from "./pages/OutfitBuilderPage"
import ImageGallery from "./components/ImageGallery"
import axios from 'axios'
import ClotheClassifier from './components/ClotheClassifier';
import OutfitRecommendations from './components/test/OutfitRecommendations';
import OutfitPage from "./pages/OutfitPage"
import WardrobeTestPage from './pages/WardrobeTestPaget';




function App() {



  return (
    <ThemeProvider>
      <AuthProvider> {/* Added AuthProvider wrapper */}
        <Router>
          <div className="min-h-screen bg-background">
            <Header />
          <main className="pt-16">
            <Routes>
              <Route path="/" element={<IndexPage />}/>
              <Route path="/outfit-builder/:imageId" element={<OutfitBuilderPage />} />
              <Route path='/classifier' element={<ClotheClassifier/>} />
              <Route path='/test' element={<WardrobeTestPage/>} />
              <Route path="/upload" element={<UploadForm />} />
              <Route path="/outfit" element={<OutfitPage/>} />
              <Route path="/gallery" element={<OutfitRecommendations/>} />
              <Route path='/recommendations' element={<RenderRecommendations/>}/>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/wardrobe" element={<WardrobePage />} />
              <Route path="/ai-studio/*" element={<AIStudioPage />} />
              <Route path="/community" element={<CommunityPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/admin" element={<AdminPage />} />
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