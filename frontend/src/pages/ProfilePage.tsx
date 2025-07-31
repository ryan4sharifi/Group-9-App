// src/pages/ProfilePage.tsx - FINAL Refactored Version with warning fixes
import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";
import {
  Box, Typography, Alert, Container, Snackbar,
  useMediaQuery, useTheme, CircularProgress,
  Card, CardContent,
} from "@mui/material";
import {
  Person as PersonIcon,
} from "@mui/icons-material";

import AccountInfoCard from '../components/common/AccountInfoCard';
import ProfileActions from '../components/common/ProfileActions';
import ConfirmDialog from "../components/common/ConfirmDialog";

import VolunteerDetailsForm from '../components/profile/VolunteerDetailsForm';
import AdminDetailsForm from '../components/profile/AdminDetailsForm';

import { FormData, FormErrors } from '../interfaces/profile';

import { useUser } from "../context/UserContext";

import usStates from '../data/usStates.json';


const ProfilePage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const { userId, setUserId, role: userRole } = useUser();

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
  const [errors, setErrors] = useState<FormErrors>({});


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

  const fetchProfile = useCallback(async () => {
    if (!userId || userId === "undefined") return;
    setStatus(prev => ({ ...prev, loading: true }));
    try {
      const profileRes = await axios.get(`http://localhost:8000/api/profile/${userId}`);
      const skillsData = Array.isArray(profileRes.data.skills) ? profileRes.data.skills : [];
      setFormData(prev => ({ ...prev, ...profileRes.data, skills: skillsData }));
      if (profileRes.data.updated_at) {
        setLastUpdated(new Date(profileRes.data.updated_at).toLocaleDateString());
      }
    } catch (profileError) {
      console.error("Failed to load user profile:", profileError);
      try {
        const credsRes = await axios.get(`http://localhost:8000/auth/user/${userId}`);
        setFormData(prev => ({
          ...prev,
          email: prev.email || credsRes.data.email,
        }));
      } catch (credsError) {
        console.error("Failed to load user email:", credsError);
        setStatus(prev => ({ ...prev, error: "Failed to load user email or profile." }));
      }
    } finally {
      setStatus(prev => ({ ...prev, loading: false }));
    }
  }, [userId]); // Removed setUserId from dependency array

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);


  // Handle string field updates
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setErrors(prev => ({ ...prev, [name]: undefined }));
  };

  const handleStateChange = (event: React.SyntheticEvent, value: { label: string; value: string } | null) => {
    setFormData(prev => ({ ...prev, state: value ? value.value : "" }));
    setErrors(prev => ({ ...prev, state: undefined }));
  };

  // Handle multi-input updates (e.g. skills)
  const handleArrayChange = (name: string, values: string[]) => {
    setFormData(prev => ({ ...prev, [name]: values }));
    setErrors(prev => ({ ...prev, [name]: undefined }));
  };

  const handleDateChange = (date: Date | null) => {
    setFormData(prev => ({ ...prev, availability: date ? date.toISOString().split('T')[0] : "" }));
    setErrors(prev => ({ ...prev, availability: undefined }));
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (userRole === 'volunteer') {
      if (!formData.skills || formData.skills.length === 0) {
        newErrors.skills = "At least one skill is required.";
      }
      if (formData.state && !usStates.some(state => state.value === formData.state)) {
          newErrors.state = "Please select a valid state from the list.";
      }
      if (formData.zip_code && !/^\d{5}(-\d{4})?$/.test(formData.zip_code)) {
        newErrors.zip_code = "Invalid zip code format (e.g., 12345 or 12345-6789).";
      }
      if (formData.availability) {
        const selectedDate = new Date(formData.availability);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        if (selectedDate < today) {
          newErrors.availability = "Availability date cannot be in the past.";
        }
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Save profile to backend
  const handleSubmit = async () => {
    setStatus(prev => ({ ...prev, error: "", success: "" }));
    setErrors({});

    if (!validateForm()) {
      setStatus({ loading: false, error: "Please correct the errors in the form.", success: "" });
      setOpenSnackbar(true);
      return;
    }

    setStatus(prev => ({ ...prev, loading: true }));
    try {
      const { email, ...rest } = formData;

      const postData: { [key: string]: any } = {};

      if (rest.full_name !== undefined && rest.full_name !== "") postData.full_name = rest.full_name;
      else postData.full_name = null;

      if (rest.preferences !== undefined && rest.preferences !== "") postData.preferences = rest.preferences;
      else postData.preferences = null;


      if (userRole === 'volunteer') {
        postData.skills = rest.skills;

        if (rest.address1 !== undefined && rest.address1 !== "") postData.address1 = rest.address1; else postData.address1 = null;
        if (rest.address2 !== undefined && rest.address2 !== "") postData.address2 = rest.address2; else postData.address2 = null;
        if (rest.city !== undefined && rest.city !== "") postData.city = rest.city; else postData.city = null;
        if (rest.zip_code !== undefined && rest.zip_code !== "") postData.zip_code = rest.zip_code; else postData.zip_code = null;
        
        postData.state = rest.state !== undefined && rest.state !== "" ? rest.state : null;

        postData.availability = rest.availability ? new Date(rest.availability as string).toISOString().split('T')[0] : null;

      } else {
        postData.skills = [];
      }

      console.log("Sending profile data:", postData);


      const res = await axios.post(`http://localhost:8000/api/profile/${userId}`, postData);
      setLastUpdated(new Date().toLocaleDateString());
      setStatus({ loading: false, error: "", success: res.data.message || "Profile updated successfully" });
      setOpenSnackbar(true);
    } catch (apiError: any) {
      console.error("Profile update failed:", apiError);
      const detail = apiError.response?.data?.detail;

      if (apiError.response && apiError.response.status === 422) {
        let errorMessages: string[] = ["Validation Error:"];
        if (Array.isArray(detail)) {
          detail.forEach((e: any) => {
            if (e.loc && e.loc.length > 1 && typeof e.loc[1] === 'string') {
              const fieldName = e.loc[1] as keyof FormErrors;
              const errorMessage = `${(fieldName as string).replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase())}: ${e.msg}`;
              errorMessages.push(errorMessage);
              setErrors(prev => ({ ...prev, [fieldName]: e.msg }));
            } else {
              errorMessages.push(e.msg || "An unknown validation error occurred.");
            }
          });
        } else if (typeof detail === 'string') {
          errorMessages.push(detail);
        } else {
          errorMessages.push("Unexpected validation error format.");
        }
        setStatus({ loading: false, error: errorMessages.join(" "), success: "" });
      } else {
        setStatus({ loading: false, error: detail || "Failed to update profile", success: "" });
      }
      setOpenSnackbar(true);
    } finally {
      setStatus(prev => ({ ...prev, loading: false }));
    }
  };

  // Trigger confirmation for profile deletion
  const handleDelete = () => setDeleteConfirmOpen(true);

  // Confirm and delete profile
  const confirmDelete = async () => {
    setDeleteConfirmOpen(false);
    setStatus(prev => ({ ...prev, loading: true }));
    try {
      await axios.delete(`http://localhost:8000/auth/delete_account/${userId}`);
      sessionStorage.clear();
      setUserId(null);
      setStatus({ loading: false, error: "", success: "Your account has been successfully deleted." });
      setTimeout(() => (window.location.href = "/login"), 2000);
    } catch (deleteError: any) {
      console.error("Account deletion failed:", deleteError);
      const detail = deleteError.response?.data?.detail;
      setStatus({ loading: false, error: detail || "Failed to delete account. Please try again.", success: "" });
    } finally {
      setOpenSnackbar(true);
      setStatus(prev => ({ ...prev, loading: false }));
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
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <AccountInfoCard
            email={formData.email}
            lastUpdated={lastUpdated}
            userRole={userRole}
          />

          <Card elevation={3} sx={{ borderRadius: 2, overflow: 'hidden' }}>
            <Box sx={{ bgcolor: theme.palette.primary.main, color: 'white', py: 2, px: 3 }}>
              <Typography variant="h6">Personal Details</Typography>
            </Box>
            <CardContent sx={{ p: 3 }}>
              {userRole === 'volunteer' ? (
                <VolunteerDetailsForm
                  formData={formData}
                  errors={errors}
                  handleChange={handleChange}
                  handleArrayChange={handleArrayChange}
                  handleStateChange={handleStateChange}
                  handleDateChange={handleDateChange}
                  isMobile={isMobile}
                />
              ) : (
                <AdminDetailsForm
                  formData={formData}
                  errors={errors}
                  handleChange={handleChange}
                  handleArrayChange={handleArrayChange}
                  handleStateChange={handleStateChange}
                  handleDateChange={handleDateChange}
                  isMobile={isMobile}
                />
              )}

              <ProfileActions
                isSaving={status.loading}
                onSave={handleSubmit}
                onDelete={handleDelete}
              />
            </CardContent>
          </Card>
        </Box>
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
        title="Delete Your Account"
        description="Are you sure you want to permanently delete your account? This action cannot be undone and will remove all associated data."
        onClose={() => setDeleteConfirmOpen(false)}
        onConfirm={confirmDelete}
      />
    </Container>
  );
};

export default ProfilePage;