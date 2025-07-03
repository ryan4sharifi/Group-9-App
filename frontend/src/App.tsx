import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import HomePage from './pages/HomePage';
import EventsPage from './pages/EventsPage';
import ReportPage from './pages/ReportPage';
import AboutPage from './pages/AboutPage';
import ContactPage from './pages/ContactPage';
import Navbar from './components/layout/Navbar';
import NotificationsPage from './pages/NotificationsPage';
import VolunteerHistoryPage from './pages/VolunteerHistoryPage';

import { UserProvider, useUser } from './context/UserContext';

const AppRoutes = () => {
  const { userId, setUserId } = useUser();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedId = sessionStorage.getItem("user_id");
    if (storedId) {
      setUserId(storedId);
    }
    setLoading(false);
  }, [setUserId]);

  const isLoggedIn = !!userId;

  if (loading) return null;
  
  //retrict access to certain pages based on login status and authority,didnt add so we dont have to log in everytime
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/events" element={<EventsPage />} /> 
        <Route path="/report" element={<ReportPage />}/>
        <Route path="/about" element={<AboutPage />} />
        <Route path="/contact" element={<ContactPage />} />
        <Route path="/history" element={isLoggedIn ? <VolunteerHistoryPage /> : <Navigate to="/login" />} />
        <Route path="/notifications" element={isLoggedIn ? <NotificationsPage /> : <Navigate to="/login" />} />
        {/* Protected routes */}
        <Route path="/profile" element={isLoggedIn ? <ProfilePage /> : <Navigate to="/login" />} />
      </Routes>
    </>
  );
};

function App() {
  return (
    <UserProvider>
      <Router>
        <AppRoutes />
      </Router>
    </UserProvider>
  );
}

export default App;