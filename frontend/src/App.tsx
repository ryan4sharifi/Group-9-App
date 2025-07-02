import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import HomePage from './pages/HomePage';
import EventsPage from './pages/EventsPage';
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

  if (loading) return null;

  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/events" element={<EventsPage />} /> {/* chane this to admin only later when roles are added*/}
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