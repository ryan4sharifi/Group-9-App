import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Alert,
  Typography,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  type SelectChangeEvent,
  Paper,
  Container,
  Divider,
  Stack,
} from "@mui/material";
import InputField from "../components/inputs/InputField";
import SubmitButton from "../components/buttons/SubmitButton";
import FormWrapper from "../components/form/FormWrapper";
import { useUser } from "../context/UserContext";

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    role: "volunteer",
  });
  const [error, setError] = useState<string | string[] | null>(null);
  const navigate = useNavigate();
  const { setUserId, setRole } = useUser();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRoleChange = (e: SelectChangeEvent<string>) => {
    setFormData({ ...formData, role: e.target.value });
  };

  const handleSubmit = async () => {
    try {
      const res = await axios.post("http://localhost:8000/auth/register", {
        email: formData.email,
        password: formData.password,
        role: formData.role,
      });

      const userId = res.data.id;
      const role = res.data.role;

      sessionStorage.setItem("user_id", userId);
      sessionStorage.setItem("role", role);
      setUserId(userId);
      setRole(role);

      await axios.post(`http://localhost:8000/api/profile/${userId}`, {});

      setError(null);
      navigate("/profile");
    } catch (err: any) {
      const detail = err.response?.data?.detail;

      if (Array.isArray(detail)) {
        const messages = detail.map((e: any) => {
          if (e.loc?.includes("password") && e.msg.includes("at least 6 characters")) {
            return "Password should have at least 6 characters";
          }
          return e.msg || "Validation error";
        });
        setError(messages);
      } else {
        setError(detail || "Registration failed");
      }
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 8, mb: 8 }}>
      <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
        <Typography variant="h4" fontWeight="500" color="primary" align="center" gutterBottom>
          Create Account
        </Typography>
        <Typography variant="body2" color="text.secondary" align="center" mb={3}>
          Join our community and start making a difference
        </Typography>
        <Divider sx={{ mb: 4 }} />

        <Stack spacing={3}>
      <InputField
        name="email"
            label="Email Address"
        type="email"
        value={formData.email}
        onChange={handleInputChange}
      />

      <InputField
        name="password"
        label="Password"
        type="password"
        value={formData.password}
        onChange={handleInputChange}
      />

          <FormControl fullWidth>
            <InputLabel id="role-label">Select Role</InputLabel>
        <Select
          labelId="role-label"
          name="role"
          value={formData.role}
              label="Select Role"
          onChange={handleRoleChange}
        >
          <MenuItem value="volunteer">Volunteer</MenuItem>
              <MenuItem value="admin">Administrator</MenuItem>
        </Select>
      </FormControl>

      {error && (
            <Alert severity="error" variant="filled">
          {Array.isArray(error)
            ? error.map((msg, i) => <div key={i}>{msg}</div>)
            : error}
        </Alert>
      )}

      <Box mt={2}>
            <SubmitButton
              label="Register"
              onClick={handleSubmit}
              fullWidth
            />
      </Box>

          <Typography variant="body2" color="text.secondary" align="center">
            Already have an account? <span style={{ color: '#1976d2', cursor: 'pointer' }} onClick={() => navigate('/login')}>Sign in</span>
          </Typography>
        </Stack>
      </Paper>
    </Container>
  );
};

export default RegisterPage;