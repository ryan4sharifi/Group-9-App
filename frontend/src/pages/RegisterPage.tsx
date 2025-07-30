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
  SelectChangeEvent,
  Paper,
  Container,
  Divider,
  Stack,
} from "@mui/material";
import InputField from "../components/inputs/InputField";
import SubmitButton from "../components/buttons/SubmitButton";
import { useUser } from "../context/UserContext";

<<<<<<< HEAD
// Register page component
const RegisterPage = () => {
  // Form state for email, password, and user role
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    role: "volunteer", // default role
  });

  const [error, setError] = useState<string | string[] | null>(null);
=======
interface FormData {
  email: string;
  password: string;
  confirmPassword: string;
  role: string;
}

interface FormErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
  role?: string;
}

const RegisterPage = () => {
  const [formData, setFormData] = useState<FormData>({
    email: "",
    password: "",
    confirmPassword: "",
    role: "volunteer",
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [apiError, setApiError] = useState<string | string[] | null>(null);
>>>>>>> c7755f350084cea77c4aa9a597b23aaaaf0a615a
  const navigate = useNavigate();
  const { setUserId, setRole } = useUser(); // Context setters for session

  // Handle text input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    setErrors((prev) => ({ ...prev, [name]: undefined }));
    setApiError(null);
  };

  // Handle role dropdown change
  const handleRoleChange = (e: SelectChangeEvent<string>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    setErrors((prev) => ({ ...prev, [name]: undefined }));
    setApiError(null);
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};
    const { email, password, confirmPassword, role } = formData;

    if (!email) {
      newErrors.email = "Email is required.";
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = "Invalid email format.";
    }

    if (!password) {
      newErrors.password = "Password is required.";
    } else if (password.length < 6) {
      newErrors.password = "Password must be at least 6 characters long.";
    }

    if (!confirmPassword) {
      newErrors.confirmPassword = "Confirm password is required.";
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match.";
    }

    if (!role) {
      newErrors.role = "Role is required.";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async () => {
    setApiError(null);

    if (!validateForm()) {
      setApiError("Please correct the errors in the form.");
      return;
    }

    try {
      // Register user with backend
      const res = await axios.post("http://localhost:8000/auth/register", {
        email: formData.email,
        password: formData.password,
        role: formData.role,
      });

      const userId = res.data.id;
      const role = res.data.role;

      // Store user info in sessionStorage and global context
      sessionStorage.setItem("user_id", userId);
      sessionStorage.setItem("role", role);
      setUserId(userId);
      setRole(role);

<<<<<<< HEAD
      // Create empty profile after registration
      await axios.post(`http://localhost:8000/api/profile/${userId}`, {});

      setError(null);
      navigate("/profile"); // Redirect to profile page
=======
      // --- UPDATED: Send the required 'skills' field as an empty array ---
      await axios.post(`http://localhost:8000/api/profile/${userId}`, { skills: [] });
      // --- END UPDATE ---

      navigate("/profile");
>>>>>>> c7755f350084cea77c4aa9a597b23aaaaf0a615a
    } catch (err: any) {
      const detail = err.response?.data?.detail;

      // Show field-specific or general error
      if (Array.isArray(detail)) {
        const messages = detail.map((e: any) => {
          if (e.loc?.includes("password") && e.msg.includes("at least 6 characters")) {
            return "Password should have at least 6 characters";
          }
          if (e.loc && e.loc.length > 1 && typeof e.loc[1] === 'string') {
              const fieldName = e.loc[1] as keyof FormErrors;
              setErrors(prev => ({ ...prev, [fieldName]: e.msg }));
          }
          return e.msg || "Validation error";
        });
        setApiError(messages);
      } else {
        setApiError(detail || "Registration failed");
      }
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 8, mb: 8 }}>
      <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
        {/* Title and subtitle */}
        <Typography variant="h4" fontWeight="500" color="primary" align="center" gutterBottom>
          Create Account
        </Typography>
        <Typography variant="body2" color="text.secondary" align="center" mb={3}>
          Join our community and start making a difference
        </Typography>
        <Divider sx={{ mb: 4 }} />

        {/* Form fields */}
        <Stack spacing={3}>
          <InputField
            name="email"
            label="Email Address"
            type="email"
            value={formData.email}
            onChange={handleInputChange}
<<<<<<< HEAD
=======
            error={!!errors.email}
            helperText={errors.email}
            required
>>>>>>> c7755f350084cea77c4aa9a597b23aaaaf0a615a
          />

          <InputField
            name="password"
            label="Password"
            type="password"
            value={formData.password}
            onChange={handleInputChange}
<<<<<<< HEAD
          />

          {/* Role selection */}
          <FormControl fullWidth>
            <InputLabel id="role-label">Select Role</InputLabel>
=======
            error={!!errors.password}
            helperText={errors.password}
            required
          />

          <InputField
            name="confirmPassword"
            label="Confirm Password"
            type="password"
            value={formData.confirmPassword}
            onChange={handleInputChange}
            error={!!errors.confirmPassword}
            helperText={errors.confirmPassword}
            required
          />

          <FormControl fullWidth error={!!errors.role}>
            <InputLabel id="role-label" required>Select Role</InputLabel>
>>>>>>> c7755f350084cea77c4aa9a597b23aaaaf0a615a
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
<<<<<<< HEAD
          </FormControl>

          {/* Error messages */}
          {error && (
            <Alert severity="error" variant="filled">
              {Array.isArray(error)
                ? error.map((msg, i) => <div key={i}>{msg}</div>)
                : error}
            </Alert>
          )}

          {/* Submit button */}
=======
            {errors.role && <Typography color="error" variant="caption" sx={{ ml: 2, mt: 0.5 }}>{errors.role}</Typography>}
          </FormControl>

          {apiError && (
            <Alert severity="error" variant="filled">
              {Array.isArray(apiError)
                ? apiError.map((msg, i) => <div key={i}>{msg}</div>)
                : apiError}
            </Alert>
          )}

>>>>>>> c7755f350084cea77c4aa9a597b23aaaaf0a615a
          <Box mt={2}>
            <SubmitButton
              label="Register"
              onClick={handleSubmit}
              fullWidth
            />
          </Box>

          {/* Login redirect */}
          <Typography variant="body2" color="text.secondary" align="center">
            Already have an account?{" "}
            <span
              style={{ color: '#1976d2', cursor: 'pointer' }}
              onClick={() => navigate('/login')}
            >
              Sign in
            </span>
          </Typography>
        </Stack>
      </Paper>
    </Container>
  );
};

export default RegisterPage;