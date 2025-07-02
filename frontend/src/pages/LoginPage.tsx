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

const LoginPage = () => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [error, setError] = useState<string | string[] | null>(null);
  const navigate = useNavigate();
  const { setUserId, setRole } = useUser();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async () => {
    try {
      const res = await axios.post("http://localhost:8000/auth/login", {
        email: formData.email,
        password: formData.password,
      });

      const { user_id, role } = res.data;

      sessionStorage.setItem("user_id", user_id);
      sessionStorage.setItem("role", role);
      setUserId(user_id);
      setRole(role);

      navigate("/profile");
      setError(null);
    } catch (err: any) {
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
        <Box sx={{
          backgroundColor: 'primary.main',
          p: 2,
          borderRadius: '50%',
          mb: 2
        }}>
          <LockOutlinedIcon sx={{ color: 'white' }} />
        </Box>

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

          {error && (
            <Alert severity="error" sx={{ mt: 1, mb: 2 }}>
              {Array.isArray(error)
                ? error.map((msg, i) => <div key={i}>{msg}</div>)
                : error}
            </Alert>
          )}

          <Box sx={{ mb: 2 }}>
            <SubmitButton
              label="Sign In"
              onClick={handleSubmit}
              fullWidth
            />
          </Box>

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