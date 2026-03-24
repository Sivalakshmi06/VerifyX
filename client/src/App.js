import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Import components
import Navbar from './components/Navbar';
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import TextDetection from './pages/TextDetection';
import ImageDetection from './pages/ImageDetection';
import EmotionAnalysis from './pages/EmotionAnalysis';
import NewsVerification from './pages/NewsVerification';
import AdminPanel from './pages/AdminPanel';
import { AuthProvider, useAuth } from './context/AuthContext';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div style={{ textAlign: 'center', padding: '50px' }}>Loading...</div>;
  }
  
  if (!user) {
    return <Navigate to="/login" />;
  }
  
  return children;
};

// Guest Route — accessible without login
const GuestRoute = ({ children }) => {
  const { loading } = useAuth();
  if (loading) return <div style={{ textAlign: 'center', padding: '50px' }}>Loading...</div>;
  return children;
};

function AppContent() {
  const { user } = useAuth();
  
  return (
    <Router>
      {user && <Navbar />}
      <Routes>
        <Route path="/" element={user ? <Navigate to="/dashboard" /> : <LandingPage />} />
        <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <Login />} />
        <Route path="/register" element={user ? <Navigate to="/dashboard" /> : <Register />} />
        <Route path="/detect" element={<GuestRoute><TextDetection /></GuestRoute>} />
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/text-detection" 
          element={
            <ProtectedRoute>
              <TextDetection />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/emotion-analysis" 
          element={
            <ProtectedRoute>
              <EmotionAnalysis />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/news-verification" 
          element={
            <ProtectedRoute>
              <NewsVerification />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/deepfake-detection" 
          element={
            <ProtectedRoute>
              <ImageDetection />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/admin" 
          element={
            <ProtectedRoute>
              <AdminPanel />
            </ProtectedRoute>
          } 
        />
      </Routes>
      <ToastContainer position="top-right" autoClose={3000} />
    </Router>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
