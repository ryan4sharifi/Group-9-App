import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import EventFormPage from './pages/EventFormPage';
import MatchPage from './pages/MatchPage';
import NotificationPage from './pages/NotificationPage';
import HistoryPage from './pages/HistoryPage';
import ReportPage from './pages/ReportPage';
import HomePage from './pages/HomePage';
import Navbar from './components/layout/Navbar';

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

  if (loading) return null; // or a spinner if preferred

  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/profile" element={isLoggedIn ? <ProfilePage /> : <Navigate to="/login" />} />
        <Route path="/event-form" element={isLoggedIn ? <EventFormPage /> : <Navigate to="/login" />} />
        <Route path="/match" element={isLoggedIn ? <MatchPage /> : <Navigate to="/login" />} />
        <Route path="/notifications" element={isLoggedIn ? <NotificationPage /> : <Navigate to="/login" />} />
        <Route path="/history" element={isLoggedIn ? <HistoryPage /> : <Navigate to="/login" />} />
        <Route path="/reports" element={isLoggedIn ? <ReportPage /> : <Navigate to="/login" />} />
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