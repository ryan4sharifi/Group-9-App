// ProfilePage component displays and manages user profile information
import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  Box, Typography, Alert, Container, Snackbar,
  useMediaQuery, useTheme, CircularProgress,
  Card, CardContent, Paper, Divider, FormControl, InputLabel, Select, MenuItem
} from "@mui/material";
import {
  Save as SaveIcon,
  Delete as DeleteIcon,
  Person as PersonIcon,
  BusinessCenter as BusinessIcon
} from "@mui/icons-material";
import Grid from "@mui/material/Grid";
import InputField from "../components/inputs/InputField";
import MultiInputField from "../components/inputs/MultiInputField";
import SubmitButton from "../components/buttons/SubmitButton";
import ConfirmDialog from "../components/common/ConfirmDialog";
import { useUser } from "../context/UserContext";

// Define expected structure of form data
interface FormData {
  full_name?: string;
  address1?: string;
  address2?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  email?: string;
  preferences?: string;
  skills: string[];
  availability?: string;
}

const ProfilePage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const { userId, setUserId } = useUser();

  // Profile form state
  const [formData, setFormData] = useState<FormData>({
    full_name: "",
    address1: "",
    address2: "",
    city: "",
    state: "",
    zip_code: "",
    email: "",
    preferences: "",
    skills: [],
    availability: "",
  });

  const [lastUpdated, setLastUpdated] = useState<string>(new Date().toLocaleDateString());
  const [status, setStatus] = useState({ loading: false, error: "", success: "" });
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);

  // Fields that accept plain string values
  const stringFields: (keyof FormData)[] = [
    "full_name", "address1", "address2", "city", "state", "zip_code", "preferences"
  ];

  // US state dropdown options
  const stateOptions = [
    { code: 'AL', name: 'Alabama' },
    { code: 'AK', name: 'Alaska' },
    { code: 'AZ', name: 'Arizona' },
    { code: 'AR', name: 'Arkansas' },
    { code: 'CA', name: 'California' },
    { code: 'CO', name: 'Colorado' },
    { code: 'CT', name: 'Connecticut' },
    { code: 'DE', name: 'Delaware' },
    { code: 'FL', name: 'Florida' },
    { code: 'GA', name: 'Georgia' },
    { code: 'HI', name: 'Hawaii' },
    { code: 'ID', name: 'Idaho' },
    { code: 'IL', name: 'Illinois' },
    { code: 'IN', name: 'Indiana' },
    { code: 'IA', name: 'Iowa' },
    { code: 'KS', name: 'Kansas' },
    { code: 'KY', name: 'Kentucky' },
    { code: 'LA', name: 'Louisiana' },
    { code: 'ME', name: 'Maine' },
    { code: 'MD', name: 'Maryland' },
    { code: 'MA', name: 'Massachusetts' },
    { code: 'MI', name: 'Michigan' },
    { code: 'MN', name: 'Minnesota' },
    { code: 'MS', name: 'Mississippi' },
    { code: 'MO', name: 'Missouri' },
    { code: 'MT', name: 'Montana' },
    { code: 'NE', name: 'Nebraska' },
    { code: 'NV', name: 'Nevada' },
    { code: 'NH', name: 'New Hampshire' },
    { code: 'NJ', name: 'New Jersey' },
    { code: 'NM', name: 'New Mexico' },
    { code: 'NY', name: 'New York' },
    { code: 'NC', name: 'North Carolina' },
    { code: 'ND', name: 'North Dakota' },
    { code: 'OH', name: 'Ohio' },
    { code: 'OK', name: 'Oklahoma' },
    { code: 'OR', name: 'Oregon' },
    { code: 'PA', name: 'Pennsylvania' },
    { code: 'RI', name: 'Rhode Island' },
    { code: 'SC', name: 'South Carolina' },
    { code: 'SD', name: 'South Dakota' },
    { code: 'TN', name: 'Tennessee' },
    { code: 'TX', name: 'Texas' },
    { code: 'UT', name: 'Utah' },
    { code: 'VT', name: 'Vermont' },
    { code: 'VA', name: 'Virginia' },
    { code: 'WA', name: 'Washington' },
    { code: 'WV', name: 'West Virginia' },
    { code: 'WI', name: 'Wisconsin' },
    { code: 'WY', name: 'Wyoming' },
  ];

  // Restore user ID from sessionStorage if needed
  useEffect(() => {
    const storedId = sessionStorage.getItem("user_id");
    if (storedId) setUserId(storedId);
  }, [setUserId]);

  // Fetch user profile info from API
  useEffect(() => {
    if (!userId || userId === "undefined") return;

    const fetchProfile = async () => {
      setStatus(prev => ({ ...prev, loading: true }));
      try {
        const profileRes = await axios.get(`http://localhost:8000/api/profile/${userId}`);
        setFormData(prev => ({ ...prev, ...profileRes.data }));
        if (profileRes.data.updated_at) {
          setLastUpdated(new Date(profileRes.data.updated_at).toLocaleDateString());
        }
      } catch {
        // Fallback: Try to fetch just user credentials
        try {
          const credsRes = await axios.get(`http://localhost:8000/auth/user/${userId}`);
          setFormData(prev => ({
            ...prev,
            email: prev.email || credsRes.data.email,
          }));
        } catch {
          setStatus(prev => ({ ...prev, error: "Failed to load user email." }));
        }
      } finally {
        setStatus(prev => ({ ...prev, loading: false }));
      }
    };

    fetchProfile();
  }, [userId]);

  // Handle string field updates
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // Handle multi-input updates (e.g. skills)
  const handleArrayChange = (name: string, values: string[]) => {
    setFormData(prev => ({ ...prev, [name]: values }));
  };

  // Save profile to backend
  const handleSubmit = async () => {
    setStatus({ loading: true, error: "", success: "" });
    try {
      const { email, ...rest } = formData;
      const postData = Object.fromEntries(Object.entries(rest).filter(([_, v]) => v !== ""));
      const res = await axios.post(`http://localhost:8000/api/profile/${userId}`, postData);
      setLastUpdated(new Date().toLocaleDateString());
      setStatus({ loading: false, error: "", success: res.data.message || "Profile updated successfully" });
    } catch {
      setStatus({ loading: false, error: "Failed to update profile", success: "" });
    } finally {
      setOpenSnackbar(true);
    }
  };

  // Trigger confirmation for profile deletion
  const handleDelete = () => setDeleteConfirmOpen(true);

  // Confirm and delete profile
  const confirmDelete = async () => {
    setDeleteConfirmOpen(false);
    setStatus(prev => ({ ...prev, loading: true }));
    try {
      await axios.delete(`http://localhost:8000/api/profile/${userId}`);
      sessionStorage.clear();
      setUserId(null);
      setStatus({ loading: false, error: "", success: "Profile deleted" });
      setTimeout(() => (window.location.href = "/login"), 2000);
    } catch {
      setStatus({ loading: false, error: "Delete failed", success: "" });
    } finally {
      setOpenSnackbar(true);
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      {/* Page header */}
      <Box mb={4} display="flex" alignItems="center" gap={2}>
        <PersonIcon sx={{ fontSize: 40, color: theme.palette.primary.main }} />
        <Typography variant="h4" fontWeight="500" color="text.primary">Your Profile</Typography>
      </Box>

      {/* Loading spinner while fetching */}
      {status.loading && !formData.email ? (
        <Box display="flex" justifyContent="center" py={8}><CircularProgress /></Box>
      ) : (
        <Grid container spacing={3}>
          {/* Account summary card */}
          <Grid size={12}>
            <Paper elevation={2} sx={{ p: 3, borderRadius: 2, background: theme.palette.mode === 'dark' ? theme.palette.grey[800] : theme.palette.grey[50] }}>
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <BusinessIcon color="primary" />
                <Typography variant="h6" color="text.primary">Account Information</Typography>
              </Box>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography variant="subtitle2" color="text.secondary">Email Address</Typography>
                  <Typography variant="body1" fontWeight="medium" mb={1}>{formData.email || "Not available"}</Typography>
                </Grid>
                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography variant="subtitle2" color="text.secondary">Last Updated</Typography>
                  <Typography variant="body1" fontWeight="medium">{lastUpdated}</Typography>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Full editable form */}
          <Grid size={12}>
            <Card elevation={3} sx={{ borderRadius: 2, overflow: 'hidden' }}>
              <Box sx={{ bgcolor: theme.palette.primary.main, color: 'white', py: 2, px: 3 }}>
                <Typography variant="h6">Personal Details</Typography>
              </Box>
              <CardContent sx={{ p: 3 }}>
                <Grid container spacing={3}>
                  {/* Dynamic text fields */}
                  {stringFields.map((field) => (
                    <Grid size={{ xs: 12, sm: field === "preferences" ? 12 : 6 }} key={field}>
                      <InputField
                        name={field}
                        label={field.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())}
                        value={(formData[field] ?? "") as string}
                        onChange={handleChange}
                        fullWidth
                      />
                    </Grid>
                  ))}

                  {/* Skill selection */}
                  <Grid size={12}>
                    <MultiInputField
                      label="Your Skills"
                      name="skills"
                      value={formData.skills}
                      onChange={handleArrayChange}
                    />
                  </Grid>

                  {/* Date + State dropdown */}
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <InputField
                      label="Availability"
                      name="availability"
                      value={formData.availability || ""}
                      onChange={handleChange}
                      type="date"
                      fullWidth
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <FormControl fullWidth>
                      <InputLabel>State</InputLabel>
                      <Select
                        name="state"
                        value={formData.state || ""}
                        onChange={(e) => setFormData(prev => ({ ...prev, state: e.target.value }))}
                        label="State"
                        required
                      >
                        {stateOptions.map((state) => (
                          <MenuItem key={state.code} value={state.code}>
                            {state.name}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>

                {/* Save/Delete buttons */}
                <Box mt={4} display="flex" gap={2} flexDirection={isMobile ? 'column' : 'row'} justifyContent="space-between">
                  <SubmitButton
                    label="Save Profile"
                    onClick={handleSubmit}
                    disabled={status.loading}
                    startIcon={<SaveIcon />}
                    sx={{ flex: 3, py: 1.2 }}
                  />
                  <SubmitButton
                    label="Delete Profile"
                    onClick={handleDelete}
                    variant="outlined"
                    color="error"
                    startIcon={<DeleteIcon />}
                    disabled={status.loading}
                    sx={{ flex: 1, py: 1.2 }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Feedback snackbar */}
      <Snackbar
        open={openSnackbar}
        autoHideDuration={4000}
        onClose={() => setOpenSnackbar(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity={status.error ? "error" : "success"} variant="filled" sx={{ width: '100%' }}>
          {status.error || status.success}
        </Alert>
      </Snackbar>

      {/* Confirm deletion modal */}
      <ConfirmDialog
        open={deleteConfirmOpen}
        title="Delete Your Profile"
        description="Are you sure you want to permanently delete your profile? This action cannot be undone."
        onClose={() => setDeleteConfirmOpen(false)}
        onConfirm={confirmDelete}
      />
    </Container>
  );
};

export default ProfilePage;