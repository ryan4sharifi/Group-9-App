import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Alert,
  Typography,
  Paper,
  Container,
  Link,
  Divider,
} from "@mui/material";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import InputField from "../components/inputs/InputField";
import SubmitButton from "../components/buttons/SubmitButton";
import { useUser } from "../context/UserContext";

// Login page component
const LoginPage = () => {
  // Manage form state
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  // Track error messages
  const [error, setError] = useState<string | string[] | null>(null);

  const navigate = useNavigate(); // Hook for navigation
  const { setUserId, setRole } = useUser(); // Context to store user session

  // Handle input changes for email and password
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  // Handle login form submission
  const handleSubmit = async () => {
    try {
      const res = await axios.post("http://localhost:8000/auth/login", {
        email: formData.email,
        password: formData.password,
      });

      // Extract user_id and role from response
      const { user_id, role } = res.data;

      // Save session info in sessionStorage and global context
      sessionStorage.setItem("user_id", user_id);
      sessionStorage.setItem("role", role);
      setUserId(user_id);
      setRole(role);

      // Redirect to profile page on success
      navigate("/profile");
      setError(null);
    } catch (err: any) {
      // Extract error details and display
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail.map((e: any) => e.msg) : detail || "Login failed");
    }
  };

  return (
    <Container maxWidth="sm">
      <Paper
        elevation={3}
        sx={{
          p: 4,
          mt: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          borderRadius: 2
        }}
      >
        {/* Lock icon at the top of the login card */}
        <Box sx={{
          backgroundColor: 'primary.main',
          p: 2,
          borderRadius: '50%',
          mb: 2
        }}>
          <LockOutlinedIcon sx={{ color: 'white' }} />
        </Box>

        {/* Title and subtitle */}
        <Typography
          variant="h4"
          fontWeight="500"
          mb={1}
          color="primary.main"
        >
          Welcome Back
        </Typography>

        <Typography
          variant="body2"
          color="text.secondary"
          mb={3}
        >
          Enter your credentials to access your account
        </Typography>

        {/* Form fields */}
        <Box sx={{ width: '100%' }}>
          <Box sx={{ mb: 2 }}>
            <InputField
              name="email"
              label="Email Address"
              type="email"
              value={formData.email}
              onChange={handleChange}
              fullWidth
            />
          </Box>

          <Box sx={{ mb: 2 }}>
            <InputField
              name="password"
              label="Password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              fullWidth
            />
          </Box>

          {/* Error display */}
          {error && (
            <Alert severity="error" sx={{ mt: 1, mb: 2 }}>
              {Array.isArray(error)
                ? error.map((msg, i) => <div key={i}>{msg}</div>)
                : error}
            </Alert>
          )}

          {/* Submit button */}
          <Box sx={{ mb: 2 }}>
            <SubmitButton
              label="Sign In"
              onClick={handleSubmit}
              fullWidth
            />
          </Box>

          {/* Divider and signup link */}
          <Divider sx={{ my: 2 }}>
            <Typography variant="body2" color="text.secondary">
              OR
            </Typography>
          </Divider>

          <Box textAlign="center" mt={1}>
            <Typography variant="body2" color="text.secondary">
              Don't have an account?{" "}
              <Link href="/register" underline="hover" fontWeight="medium">
                Sign up
              </Link>
            </Typography>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default LoginPage;