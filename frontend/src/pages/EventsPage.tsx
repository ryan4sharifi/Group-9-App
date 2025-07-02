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
  Alert
} from '@mui/material';
import axios from 'axios';

type Event = {
  id: string;
  title: string;
  description: string;
  date: string;
  location: string;
  skills_required: string[];
  urgency: 'low' | 'medium' | 'high';
};

const urgencyOptions = ['low', 'medium', 'high'];
const skillsOptions = ['Medical', 'Teaching', 'Logistics', 'Construction','Communication', 'Teamwork', 'adaptability','Problem-solving', 'Leadership', 'Cultural Awareness', 'First Aid', 'Language Skills','Technical and Digital Skills', 'Project Management', 'Research and Analysis'];

const EventsPage: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [form, setForm] = useState({
    title: '',
    description: '',
    date: '',
    location: '',
    skills_required: [] as string[],
    urgency: 'medium'
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchEvents = async () => {
    try {
      const res = await axios.get('http://localhost:8000/events');//Backend API endpoint to fetch events, change later
      setEvents(res.data);
    } catch (err) {
      console.error('Error fetching events:', err);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const res = await axios.post('http://localhost:8000/events', form);//Backend API endpoint to create a new event, change later
      setEvents([...events, res.data]);
      setForm({
        title: '',
        description: '',
        date: '',
        location: '',
        skills_required: [],
        urgency: 'medium'
      });
      setSuccess('Event created successfully!');
    } catch (err) {
      console.error(err);
      setError('Failed to create event');
    }
  };

  const handleSkillToggle = (skill: string) => {// Function to toggle skills in the form
  const currentSkills = form.skills_required;// Copy the current skills array
  const alreadySelected = currentSkills.includes(skill); 
  let updatedSkills: string[];
  if (alreadySelected) {
    updatedSkills = currentSkills.filter((s) => s !== skill);
  } else {
    updatedSkills = [...currentSkills, skill];// Add the skill if not already selected
  }
  setForm({  // Update the form with the new skills list
    ...form,
    skills_required: updatedSkills
  });
};


  return (
    <Container maxWidth="md" sx={{ py: 6 }}>
      <Typography variant="h3" component="h1" align="center" gutterBottom>
        Event Management
      </Typography>

      <Typography variant="h6" gutterBottom>
        Create New Event
      </Typography>

      <Paper sx={{ p: 3, mb: 6 }} component="form" onSubmit={handleSubmit}>
        <Stack spacing={2}>
          <TextField
            label="Title"
            fullWidth
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
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
            label="Date"
            type="date"
            InputLabelProps={{ shrink: true }}
            fullWidth
            value={form.date}
            onChange={(e) => setForm({ ...form, date: e.target.value })}
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
                  variant={form.skills_required.includes(skill) ? 'filled' : 'outlined'}
                  color="primary"
                  clickable
                  onClick={() => handleSkillToggle(skill)}
                />
              ))}
            </Stack>
          </Box>

          <Button type="submit" variant="contained">
            Create Event
          </Button>

          {error && <Alert severity="error">{error}</Alert>}
          {success && <Alert severity="success">{success}</Alert>}
        </Stack>
      </Paper>

      <Typography variant="h5" gutterBottom>
        Existing Events
      </Typography>

      <Stack spacing={2}>
        {events.map((event) => (
          <Paper key={event.id} sx={{ p: 2 }}>
            <Typography variant="h6">{event.title}</Typography>
            <Typography variant="body2" color="text.secondary">
              {event.date} — {event.location}
            </Typography>
            <Typography variant="body2">{event.description}</Typography>
            <Stack direction="row" spacing={1} mt={1}>
              {event.skills_required.map((skill, i) => (
                <Chip key={i} label={skill} size="small" variant="outlined" />
              ))}
            </Stack>
            <Typography variant="caption" color="error">
              Urgency: {event.urgency.toUpperCase()}
            </Typography>
          </Paper>
        ))}
      </Stack>
    </Container>
  );
};

export default EventsPage;
