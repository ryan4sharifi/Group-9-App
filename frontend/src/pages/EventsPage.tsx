import React, { useEffect, useState } from 'react';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Paper,
  MenuItem,
  Stack,
  Chip,
  Alert,
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  IconButton,
  Divider,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Event as EventIcon,
  LocationOn as LocationIcon,
  CalendarToday as CalendarIcon,
  Assignment as AssignmentIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import axios from 'axios';
import { useUser } from '../context/UserContext';
import SubmitButton from '../components/buttons/SubmitButton';
import ConfirmDialog from '../components/common/ConfirmDialog';

interface Event {
  id: string;
  name: string;
  description: string;
  event_date: string;
  location: string;
  required_skills: string[];
  urgency: 'low' | 'medium' | 'high';
}

const urgencyOptions = ['low', 'medium', 'high'];
const skillsOptions = [
  'Medical', 'Teaching', 'Logistics', 'Construction', 'Communication', 
  'Teamwork', 'Adaptability', 'Problem-solving', 'Leadership', 
  'Cultural Awareness', 'First Aid', 'Language Skills',
  'Technical and Digital Skills', 'Project Management', 'Research and Analysis'
];

const EventsPage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { userId, role } = useUser();
  const isAdmin = role === 'admin';
  
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingEvent, setEditingEvent] = useState<Event | null>(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [eventToDelete, setEventToDelete] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: '',
    description: '',
    event_date: '',
    location: '',
    required_skills: [] as string[],
    urgency: 'medium' as 'low' | 'medium' | 'high'
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/events');
      setEvents(response.data);
    } catch (err) {
      console.error('Error fetching events:', err);
      setError('Failed to fetch events');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      if (editingEvent) {
        await axios.put(`http://localhost:8000/api/events/${editingEvent.id}`, form, {
          params: { user_id: userId }
        });
        setSuccess('Event updated successfully!');
      } else {
        await axios.post('http://localhost:8000/api/events', form, {
          params: { user_id: userId }
        });
        setSuccess('Event created successfully!');
      }
      
      await fetchEvents();
      handleCloseDialog();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save event');
    }
  };

  const handleEdit = (event: Event) => {
    setEditingEvent(event);
    setForm({
      name: event.name,
      description: event.description,
      event_date: event.event_date,
      location: event.location,
      required_skills: event.required_skills,
      urgency: event.urgency
    });
    setDialogOpen(true);
  };

  const handleDelete = async (eventId: string) => {
    try {
      await axios.delete(`http://localhost:8000/api/events/${eventId}`, {
        params: { user_id: userId }
      });
      setSuccess('Event deleted successfully!');
      await fetchEvents();
      setDeleteConfirmOpen(false);
      setEventToDelete(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete event');
    }
  };

  const handleSkillToggle = (skill: string) => {
    const currentSkills = form.required_skills;
    const alreadySelected = currentSkills.includes(skill);
    
    if (alreadySelected) {
      setForm(prev => ({
        ...prev,
        required_skills: currentSkills.filter(s => s !== skill)
      }));
    } else {
      setForm(prev => ({
        ...prev,
        required_skills: [...currentSkills, skill]
      }));
    }
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingEvent(null);
    setForm({
      name: '',
      description: '',
      event_date: '',
      location: '',
      required_skills: [],
      urgency: 'medium'
    });
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, textAlign: 'center' }}>
        <Typography>Loading events...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1">
          Event Management
        </Typography>
        {isAdmin && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setDialogOpen(true)}
          >
            Create Event
          </Button>
        )}
      </Box>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 3 }}>{success}</Alert>}

      <Grid container spacing={3}>
        {events.map((event) => (
          <Grid item xs={12} md={6} lg={4} key={event.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Typography variant="h6" component="h2" sx={{ fontWeight: 600 }}>
                    {event.name}
                  </Typography>
                  <Chip
                    label={event.urgency.toUpperCase()}
                    size="small"
                    color={getUrgencyColor(event.urgency) as any}
                    variant="filled"
                  />
                </Box>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {event.description}
                </Typography>

                <Stack spacing={1} sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CalendarIcon fontSize="small" color="action" />
                    <Typography variant="body2">
                      {new Date(event.event_date).toLocaleDateString()}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LocationIcon fontSize="small" color="action" />
                    <Typography variant="body2">{event.location}</Typography>
                  </Box>
                </Stack>

                <Box>
                  <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                    Required Skills:
                  </Typography>
                  <Stack direction="row" spacing={0.5} flexWrap="wrap">
                    {event.required_skills.map((skill, index) => (
                      <Chip
                        key={index}
                        label={skill}
                        size="small"
                        variant="outlined"
                        sx={{ mb: 0.5 }}
                      />
                    ))}
                  </Stack>
                </Box>
              </CardContent>
              
              {isAdmin && (
                <CardActions sx={{ justifyContent: 'flex-end' }}>
                  <IconButton onClick={() => handleEdit(event)} color="primary">
                    <EditIcon />
                  </IconButton>
                  <IconButton 
                    onClick={() => {
                      setEventToDelete(event.id);
                      setDeleteConfirmOpen(true);
                    }}
                    color="error"
                  >
                    <DeleteIcon />
                  </IconButton>
                </CardActions>
              )}
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Create/Edit Event Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">
              {editingEvent ? 'Edit Event' : 'Create New Event'}
            </Typography>
            <IconButton onClick={handleCloseDialog}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <TextField
              label="Event Name"
              fullWidth
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
            
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={3}
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              required
            />
            
            <TextField
              label="Event Date"
              type="date"
              InputLabelProps={{ shrink: true }}
              fullWidth
              value={form.event_date}
              onChange={(e) => setForm({ ...form, event_date: e.target.value })}
              required
            />
            
            <TextField
              label="Location"
              fullWidth
              value={form.location}
              onChange={(e) => setForm({ ...form, location: e.target.value })}
              required
            />
            
            <TextField
              label="Urgency"
              select
              fullWidth
              value={form.urgency}
              onChange={(e) => setForm({ ...form, urgency: e.target.value as 'low' | 'medium' | 'high' })}
            >
              {urgencyOptions.map((level) => (
                <MenuItem key={level} value={level}>
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </MenuItem>
              ))}
            </TextField>

            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Required Skills
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap">
                {skillsOptions.map((skill) => (
                  <Chip
                    key={skill}
                    label={skill}
                    variant={form.required_skills.includes(skill) ? 'filled' : 'outlined'}
                    color="primary"
                    clickable
                    onClick={() => handleSkillToggle(skill)}
                    sx={{ mb: 1 }}
                  />
                ))}
              </Stack>
            </Box>
          </Stack>
        </DialogContent>
        
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <SubmitButton
            label={editingEvent ? 'Update Event' : 'Create Event'}
            onClick={handleSubmit}
            variant="contained"
            fullWidth={false}
          />
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={deleteConfirmOpen}
        title="Delete Event"
        description="Are you sure you want to delete this event? This action cannot be undone and will notify all signed-up volunteers."
        onClose={() => {
          setDeleteConfirmOpen(false);
          setEventToDelete(null);
        }}
        onConfirm={() => eventToDelete && handleDelete(eventToDelete)}
        confirmText="Delete"
        cancelText="Cancel"
      />
    </Container>
  );
};

export default EventsPage;
