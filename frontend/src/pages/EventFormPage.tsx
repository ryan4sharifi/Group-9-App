import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Stack,
  Paper,
  IconButton,
  Snackbar,
  Alert,
  Grid,
  Container,
  Chip,
  Divider,
  useTheme,
  useMediaQuery,
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

interface EventData {
  id?: string;
  name: string;
  description: string;
  location: string;
  required_skills: string[];
  urgency: string;
  event_date: Date | null;
}

const defaultEvent: EventData = {
  name: "",
  description: "",
  location: "",
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
  };

  const handleDropdownChange = (e: SelectChangeEvent) => {
    const { name, value } = e.target;
    setEvent((prev) => ({ ...prev, [name]: value }));
  };

  const handleArrayChange = (name: string, values: string[]) => {
    setEvent((prev) => ({ ...prev, [name]: values }));
  };

  const handleDateChange = (date: Date | null) => {
    setEvent((prev) => ({ ...prev, event_date: date }));
  };

  const handleSubmit = async () => {
    try {
      if (!userId) throw new Error("User ID is missing");

      const formattedEvent = {
        ...event,
        event_date: event.event_date?.toISOString().split("T")[0] || "",
      };

      if (event.id) {
        await axios.put(
          `http://localhost:8000/api/events/${event.id}`,
          formattedEvent,
          { params: { user_id: userId } }
        );
        setStatus({ success: "Event updated successfully", error: "" });
      } else {
        await axios.post("http://localhost:8000/api/events", formattedEvent, {
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
    setEvent({ ...evt, event_date: evt.event_date ? new Date(evt.event_date) : null });
  };

  const handleDelete = async (id?: string) => {
    if (!id || !userId) return;

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
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <InputField label="Event Name" name="name" value={event.name} onChange={handleChange} />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <InputField label="Location" name="location" value={event.location} onChange={handleChange} />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <InputField
                label="Description"
                name="description"
                value={event.description}
                onChange={handleChange}
                multiline
                rows={3}
              />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <MultiInputField
                label="Required Skills"
                name="required_skills"
                value={event.required_skills}
                onChange={handleArrayChange}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <DropdownField
                label="Urgency"
                name="urgency"
                value={event.urgency}
                onChange={handleDropdownChange}
                options={urgencyOptions}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <DatePickerField
                label="Event Date"
                value={event.event_date}
                onChange={handleDateChange}
              />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <Box display="flex" justifyContent="flex-end" mt={2}>
                <SubmitButton
                  label={event.id ? "Update Event" : "Create Event"}
                  onClick={handleSubmit}
                  sx={{ px: 4 }}
                />
              </Box>
            </Grid>
          </Grid>
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
            <Grid container spacing={2}>
              {events.map((evt) => (
                <Grid key={evt.id} size={{ xs: 12, sm: 6, md: 4 }}>
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
                      {evt.location && (
                        <Box display="flex" alignItems="center" gap={1}>
                          <LocationOn fontSize="small" color="action" />
                          <Typography variant="body2" color="text.secondary" noWrap>{evt.location}</Typography>
                        </Box>
                      )}

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
                </Grid>
              ))}
            </Grid>
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