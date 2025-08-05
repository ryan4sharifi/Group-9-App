import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Stack,
  Paper,
  IconButton,
  Snackbar,
  Alert,
  Container,
  Chip,
  Divider,
  useTheme,
  useMediaQuery,
  Autocomplete, // Import Autocomplete
  TextField, // Import TextField (used by Autocomplete)
} from "@mui/material";
import { Delete, Edit, LocationOn, DateRange, Flag } from "@mui/icons-material";
import axios from "axios";
import { useUser } from "../context/UserContext";
import InputField from "../components/inputs/InputField";
import MultiInputField from "../components/inputs/MultiInputField";
import DropdownField from "../components/inputs/SelectDropdown";
import DatePickerField from "../components/inputs/DatePickerField";
import SubmitButton from "../components/buttons/SubmitButton";
import { SelectChangeEvent } from "@mui/material";

// Import usStates data
import usStates from '../data/usStates.json'; // Adjust path if your data directory is different


// --- CHANGE 1: UPDATED INTERFACE TO MATCH BACKEND ROUTE ---
interface EventData {
  id?: string;
  name: string;
  description: string;
  address1: string;
  address2?: string;
  city: string;
  state: string;
  zip_code?: string;
  required_skills: string[];
  urgency: string;
  event_date: Date | null;
}

interface FormErrors {
  name?: string;
  description?: string;
  address1?: string;
  address2?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  required_skills?: string;
  urgency?: string;
  event_date?: string;
}

const defaultEvent: EventData = {
  name: "",
  description: "",
  address1: "",
  address2: "",
  city: "",
  state: "",
  zip_code: "",
  required_skills: [],
  urgency: "",
  event_date: null,
};

const urgencyOptions = [
  { label: "Low", value: "Low" },
  { label: "Medium", value: "Medium" },
  { label: "High", value: "High" },
];

const EventFormPage: React.FC = () => {
  const { userId } = useUser();
  const [event, setEvent] = useState<EventData>(defaultEvent);
  const [events, setEvents] = useState<EventData[]>([]);
  const [status, setStatus] = useState({ success: "", error: "" });
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const fetchEvents = async () => {
    try {
      const res = await axios.get("http://localhost:8000/api/events");
      setEvents(res.data);
    } catch (error) {
      console.error("Failed to fetch events:", error);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setEvent((prev) => ({ ...prev, [name]: value }));
    setErrors((prev) => ({ ...prev, [name]: undefined }));
  };

  // --- CHANGE 2: NEW HANDLER FOR AUTOCOMPLETE (STATE FIELD) ---
  const handleStateChange = (event: React.SyntheticEvent, value: { label: string; value: string } | null) => {
    setEvent(prev => ({ ...prev, state: value ? value.value : "" }));
    setErrors(prev => ({ ...prev, state: undefined }));
  };
  // --- END NEW HANDLER ---

  const handleDropdownChange = (e: SelectChangeEvent) => {
    const { name, value } = e.target;
    setEvent((prev) => ({ ...prev, [name]: value }));
    setErrors((prev) => ({ ...prev, [name]: undefined }));
  };

  const handleArrayChange = (name: string, values: string[]) => {
    setEvent((prev) => ({ ...prev, [name]: values }));
    setErrors((prev) => ({ ...prev, [name]: undefined }));
  };

  const handleDateChange = (date: Date | null) => {
    setEvent((prev) => ({ ...prev, event_date: date }));
    setErrors((prev) => ({ ...prev, event_date: undefined }));
  };

  // --- CHANGE 3: UPDATED VALIDATION FOR NEW ADDRESS FIELDS ---
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};
    const { name, description, address1, city, state, zip_code, required_skills, urgency, event_date } = event;

    if (!name.trim()) {
      newErrors.name = "Event Name is required.";
    }
    if (!description.trim()) {
      newErrors.description = "Description is required.";
    }
    if (!address1.trim()) {
        newErrors.address1 = "Address Line 1 is required.";
    }
    if (!city.trim()) {
        newErrors.city = "City is required.";
    }
    if (!state.trim()) {
        newErrors.state = "State is required.";
    } else if (!usStates.some(s => s.value === state)) {
        newErrors.state = "Please select a valid state from the list.";
    }
    if (zip_code && !/^\d{5}(-\d{4})?$/.test(zip_code)) {
        newErrors.zip_code = "Please enter a valid 5 or 9 digit zip code.";
    }

    if (!required_skills || required_skills.length === 0) {
      newErrors.required_skills = "At least one skill is required.";
    }
    if (!urgency.trim()) {
      newErrors.urgency = "Urgency is required.";
    }
    if (!event_date) {
      newErrors.event_date = "Event Date is required.";
    } else {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const selectedDate = new Date(event_date);
      selectedDate.setHours(0, 0, 0, 0);
      if (selectedDate < today) {
        newErrors.event_date = "Event Date cannot be in the past.";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  // --- END UPDATED VALIDATION ---

  const handleSubmit = async () => {
    if (!validateForm()) {
      setStatus({ success: "", error: "Please correct the errors in the form." });
      setSnackbarOpen(true);
      return;
    }

    try {
      if (!userId) {
        setStatus({ success: "", error: "User not logged in. Please log in to create/edit events." });
        setSnackbarOpen(true);
        return;
      }

      // --- CHANGE 4: UPDATED OBJECT TO SEND TO BACKEND ---
      const eventToSubmit = {
        ...event,
        event_date: event.event_date?.toISOString().split("T")[0] || "",
      };
      // --- END UPDATED OBJECT ---

      if (event.id) {
        await axios.put(
          `http://localhost:8000/api/events/${event.id}`,
          eventToSubmit,
          { params: { user_id: userId } }
        );
        setStatus({ success: "Event updated successfully", error: "" });
      } else {
        await axios.post("http://localhost:8000/api/events", eventToSubmit, {
          params: { user_id: userId },
        });
        setStatus({ success: "Event created successfully", error: "" });
      }

      setEvent(defaultEvent);
      fetchEvents();
    } catch (error) {
      console.error("Save failed:", error);
      setStatus({ success: "", error: "Failed to save event" });
    } finally {
      setSnackbarOpen(true);
    }
  };

  const handleEdit = (evt: EventData) => {
    const skillsToEdit = Array.isArray(evt.required_skills) ? evt.required_skills : [];
    // --- CHANGE 5: UPDATED STATE WHEN EDITING AN EVENT ---
    setEvent({
        ...evt,
        event_date: evt.event_date ? new Date(evt.event_date) : null,
        required_skills: skillsToEdit
    });
    // --- END UPDATED STATE ---
    setErrors({});
  };

  const handleDelete = async (id?: string) => {
    if (!id || !userId) {
      setStatus({ success: "", error: "Event ID or User ID is missing for deletion." });
      setSnackbarOpen(true);
      return;
    }

    try {
      await axios.delete(`http://localhost:8000/api/events/${id}`, {
        params: { user_id: userId },
      });
      setStatus({ success: "Event deleted successfully", error: "" });
      fetchEvents();
    } catch (err) {
      console.error("Delete failed:", err);
      setStatus({ success: "", error: "Delete failed" });
    } finally {
      setSnackbarOpen(true);
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'High': return 'error';
      case 'Medium': return 'warning';
      case 'Low': return 'success';
      default: return 'default';
    }
  };

  return (
    <Container maxWidth="lg">
      <Box py={4}>
        <Typography variant="h4" fontWeight="medium" color="primary.main" mb={3}>
          {event.id ? "Edit Event" : "Create Event"}
        </Typography>

        <Paper sx={{ p: 3, mb: 4, boxShadow: theme.shadows[3], borderRadius: 2 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Box sx={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: 2 }}>
              <Box sx={{ width: isMobile ? '100%' : '50%' }}>
                <InputField
                  label="Event Name"
                  name="name"
                  value={event.name}
                  onChange={handleChange}
                  error={!!errors.name}
                  helperText={errors.name}
                  required
                />
              </Box>
              <Box sx={{ width: isMobile ? '100%' : '50%' }}>
                 <InputField
                    label="Address Line 1"
                    name="address1"
                    value={event.address1}
                    onChange={handleChange}
                    error={!!errors.address1}
                    helperText={errors.address1}
                    required
                 />
              </Box>
            </Box>
            <Box sx={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: 2 }}>
                <Box sx={{ width: isMobile ? '100%' : '50%' }}>
                     <InputField
                        label="Address Line 2 (Optional)"
                        name="address2"
                        value={event.address2}
                        onChange={handleChange}
                        error={!!errors.address2}
                        helperText={errors.address2}
                    />
                </Box>
                <Box sx={{ width: isMobile ? '100%' : '50%' }}>
                    <InputField
                        label="City"
                        name="city"
                        value={event.city}
                        onChange={handleChange}
                        error={!!errors.city}
                        helperText={errors.city}
                        required
                    />
                </Box>
            </Box>
            <Box sx={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: 2 }}>
              <Box sx={{ width: isMobile ? '100%' : '50%' }}>
                {/* --- CHANGE 6: USE AUTOCOMPLETE FOR STATE --- */}
                <Autocomplete
                  options={usStates}
                  getOptionLabel={(option) => option.label}
                  value={usStates.find(s => s.value === event.state) || null}
                  onChange={handleStateChange}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="State"
                      margin="normal"
                      fullWidth
                      error={!!errors.state}
                      helperText={errors.state}
                      required
                    />
                  )}
                />
                {/* --- END CHANGE 6 --- */}
              </Box>
              <Box sx={{ width: isMobile ? '100%' : '50%' }}>
                 <InputField
                    label="Zip Code"
                    name="zip_code"
                    value={event.zip_code}
                    onChange={handleChange}
                    error={!!errors.zip_code}
                    helperText={errors.zip_code}
                 />
              </Box>
            </Box>
            <Box sx={{ width: '100%' }}>
              <InputField
                label="Description"
                name="description"
                value={event.description}
                onChange={handleChange}
                multiline
                rows={3}
                error={!!errors.description}
                helperText={errors.description}
                required
              />
            </Box>
            <Box sx={{ width: '100%' }}>
              <MultiInputField
                label="Required Skills"
                name="required_skills"
                value={event.required_skills}
                onChange={handleArrayChange}
                error={!!errors.required_skills}
                helperText={errors.required_skills}
                required
              />
            </Box>
            <Box sx={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: 2 }}>
              <Box sx={{ width: isMobile ? '100%' : '50%' }}>
                <DropdownField
                  label="Urgency"
                  name="urgency"
                  value={event.urgency}
                  onChange={handleDropdownChange}
                  options={urgencyOptions}
                  error={!!errors.urgency}
                  helperText={errors.urgency}
                  required
                />
              </Box>
              <Box sx={{ width: isMobile ? '100%' : '50%' }}>
                <DatePickerField
                  label="Event Date"
                  value={event.event_date}
                  onChange={handleDateChange}
                  error={!!errors.event_date}
                  helperText={errors.event_date}
                  required
                />
              </Box>
            </Box>
            <Box display="flex" justifyContent="flex-end" mt={2}>
              <SubmitButton
                label={event.id ? "Update Event" : "Create Event"}
                onClick={handleSubmit}
                sx={{ px: 4 }}
              />
            </Box>
          </Box>
        </Paper>

        <Box mb={4}>
          <Typography variant="h5" fontWeight="medium" color="primary.main" mb={2}>
            Your Events
          </Typography>
          <Divider sx={{ mb: 3 }} />

          {events.length === 0 ? (
            <Paper sx={{ p: 3, textAlign: "center", bgcolor: "background.default" }}>
              <Typography variant="body1" color="text.secondary">
                No events created yet. Add your first event above.
              </Typography>
            </Paper>
          ) : (
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
              {events.map((evt) => (
                <Box key={evt.id} sx={{
                  width: isMobile ? '100%' : 'calc(50% - 8px)',
                  '@media (min-width:900px)': {
                    width: 'calc(33.33% - 16px)',
                  }
                }}>
                  <Paper sx={{
                    p: 3,
                    height: "100%",
                    position: "relative",
                    borderRadius: 2,
                    transition: "all 0.2s",
                    "&:hover": { boxShadow: theme.shadows[5] }
                  }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                      <Typography variant="h6" fontWeight="medium" noWrap>{evt.name}</Typography>
                      <Box>
                        <IconButton size="small" onClick={() => handleEdit(evt)}>
                          <Edit fontSize="small" />
                        </IconButton>
                        <IconButton size="small" onClick={() => handleDelete(evt.id)}>
                          <Delete fontSize="small" color="error" />
                        </IconButton>
                      </Box>
                    </Box>

                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        mb: 2,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        display: "-webkit-box",
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: "vertical",
                      }}
                    >
                      {evt.description}
                    </Typography>

                    <Stack spacing={1}>
                      {/* --- CHANGE 7: UPDATED LOCATION DISPLAY --- */}
                      {(evt.address1 || evt.city || evt.state) && (
                        <Box display="flex" alignItems="center" gap={1}>
                          <LocationOn fontSize="small" color="action" />
                          <Typography variant="body2" color="text.secondary">
                            {evt.address1}, {evt.city}, {evt.state}
                          </Typography>
                        </Box>
                      )}
                      {/* --- END CHANGE 7 --- */}

                      {evt.event_date && (
                        <Box display="flex" alignItems="center" gap={1}>
                          <DateRange fontSize="small" color="action" />
                          <Typography variant="body2" color="text.secondary">
                            {new Date(evt.event_date).toLocaleDateString()}
                          </Typography>
                        </Box>
                      )}

                      {evt.urgency && (
                        <Box display="flex" alignItems="center" gap={1}>
                          <Flag fontSize="small" color="action" />
                          <Chip
                            label={evt.urgency}
                            size="small"
                            color={getUrgencyColor(evt.urgency) as any}
                          />
                        </Box>
                      )}
                    </Stack>

                    {evt.required_skills?.length > 0 && (
                      <Box mt={2}>
                        <Box display="flex" flexWrap="wrap" gap={0.5}>
                          {evt.required_skills.map((skill, i) => (
                            <Chip
                              key={i}
                              label={skill}
                              size="small"
                              variant="outlined"
                              sx={{ fontSize: '0.7rem' }}
                            />
                          ))}
                        </Box>
                      </Box>
                    )}
                  </Paper>
                </Box>
              ))}
            </Box>
          )}
        </Box>

        <Snackbar
          open={snackbarOpen}
          autoHideDuration={4000}
          onClose={() => setSnackbarOpen(false)}
          anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
        >
          <Alert
            severity={status.error ? "error" : "success"}
            variant="filled"
            sx={{ width: '100%' }}
          >
            {status.error || status.success}
          </Alert>
        </Snackbar>
      </Box>
    </Container>
  );
};

export default EventFormPage;