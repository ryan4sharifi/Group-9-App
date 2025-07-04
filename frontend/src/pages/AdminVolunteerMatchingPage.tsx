import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  TextField,
  Button,
  Card,
  CardContent,
  Autocomplete,
  Chip,
  Alert,
  Stack,
  Divider,
} from '@mui/material';
import {
  PersonAdd as PersonAddIcon,
  EventAvailable as EventIcon,
  Assignment as AssignmentIcon,
} from '@mui/icons-material';
import axios from 'axios';
import { useUser } from '../context/UserContext';
import SubmitButton from '../components/buttons/SubmitButton';

interface Volunteer {
  user_id: string;
  full_name: string;
  skills: string[];
  email: string;
}

interface Event {
  id: string;
  name: string;
  description: string;
  event_date: string;
  location: string;
  required_skills: string[];
  urgency: 'low' | 'medium' | 'high';
}

interface MatchSuggestion {
  volunteer: Volunteer;
  event: Event;
  matchPercentage: number;
  matchingSkills: string[];
}

const AdminVolunteerMatchingPage: React.FC = () => {
  const { role } = useUser();
  const [volunteers, setVolunteers] = useState<Volunteer[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [selectedVolunteer, setSelectedVolunteer] = useState<Volunteer | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [matchSuggestions, setMatchSuggestions] = useState<MatchSuggestion[]>([]);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (role === 'admin') {
      fetchVolunteers();
      fetchEvents();
    }
  }, [role]);

  const fetchVolunteers = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/volunteers');
      setVolunteers(response.data);
    } catch (err) {
      console.error('Error fetching volunteers:', err);
      setError('Failed to fetch volunteers');
    }
  };

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

  const generateMatchSuggestions = () => {
    if (!selectedVolunteer) return;

    const suggestions: MatchSuggestion[] = [];
    const volunteerSkills = new Set(selectedVolunteer.skills);

    events.forEach(event => {
      const eventSkills = new Set(event.required_skills);
      const matchingSkills = Array.from(volunteerSkills).filter(skill => 
        eventSkills.has(skill)
      );
      
      if (matchingSkills.length > 0) {
        const matchPercentage = Math.round((matchingSkills.length / event.required_skills.length) * 100);
        suggestions.push({
          volunteer: selectedVolunteer,
          event,
          matchPercentage,
          matchingSkills
        });
      }
    });

    suggestions.sort((a, b) => b.matchPercentage - a.matchPercentage);
    setMatchSuggestions(suggestions);
  };

  const handleManualMatch = async () => {
    if (!selectedVolunteer || !selectedEvent) {
      setError('Please select both a volunteer and an event');
      return;
    }

    try {
      await axios.post('http://localhost:8000/api/history', {
        user_id: selectedVolunteer.user_id,
        event_id: selectedEvent.id,
        status: 'Assigned'
      });

      await axios.post('http://localhost:8000/api/notifications', {
        user_id: selectedVolunteer.user_id,
        event_id: selectedEvent.id,
        message: `You have been assigned to "${selectedEvent.name}" by an administrator.`,
        type: 'assignment'
      });

      setSuccess(`Successfully matched ${selectedVolunteer.full_name} to ${selectedEvent.name}`);
      setSelectedVolunteer(null);
      setSelectedEvent(null);
      setMatchSuggestions([]);
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'Failed to create match');
      } else {
        setError('Failed to create match');
      }
    }
  };

  const handleSuggestionMatch = async (suggestion: MatchSuggestion) => {
    setSelectedVolunteer(suggestion.volunteer);
    setSelectedEvent(suggestion.event);
    await handleManualMatch();
  };

  const getUrgencyColor = (urgency: string): 'error' | 'warning' | 'success' | 'default' => {
    switch (urgency) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  if (role !== 'admin') {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">Access denied. Administrator privileges required.</Alert>
      </Container>
    );
  }

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, textAlign: 'center' }}>
        <Typography>Loading volunteers and events...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Volunteer Matching Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Match volunteers to events based on their skills and event requirements
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Using flexbox layout instead of Grid */}
      <Box sx={{ display: 'flex', gap: 3, flexDirection: { xs: 'column', md: 'row' } }}>
        {/* Manual Matching Form */}
        <Box sx={{ flex: 1 }}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <PersonAddIcon color="primary" />
              Manual Volunteer Matching
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <Stack spacing={3}>
              <Autocomplete
                options={volunteers}
                getOptionLabel={(volunteer) => `${volunteer.full_name} (${volunteer.email})`}
                value={selectedVolunteer}
                onChange={(_, newValue) => {
                  setSelectedVolunteer(newValue);
                  if (newValue) {
                    generateMatchSuggestions();
                  } else {
                    setMatchSuggestions([]);
                  }
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Select Volunteer"
                    placeholder="Search by name or email..."
                  />
                )}
                renderOption={(props, volunteer) => (
                  <Box component="li" {...props}>
                    <Box>
                      <Typography variant="subtitle2">{volunteer.full_name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {volunteer.email}
                      </Typography>
                      <Box sx={{ mt: 0.5 }}>
                        {volunteer.skills.slice(0, 3).map((skill, index) => (
                          <Chip
                            key={index}
                            label={skill}
                            size="small"
                            sx={{ mr: 0.5, mb: 0.5 }}
                          />
                        ))}
                        {volunteer.skills.length > 3 && (
                          <Chip
                            label={`+${volunteer.skills.length - 3} more`}
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Box>
                    </Box>
                  </Box>
                )}
              />

              <Autocomplete
                options={events}
                getOptionLabel={(event) => `${event.name} - ${new Date(event.event_date).toLocaleDateString()}`}
                value={selectedEvent}
                onChange={(_, newValue) => setSelectedEvent(newValue)}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Select Event"
                    placeholder="Search by event name..."
                  />
                )}
                renderOption={(props, event) => (
                  <Box component="li" {...props}>
                    <Box>
                      <Typography variant="subtitle2">{event.name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(event.event_date).toLocaleDateString()} • {event.location}
                      </Typography>
                      <Box sx={{ mt: 0.5 }}>
                        <Chip
                          label={event.urgency.toUpperCase()}
                          size="small"
                          color={getUrgencyColor(event.urgency)}
                          sx={{ mr: 0.5 }}
                        />
                        {event.required_skills.slice(0, 2).map((skill, index) => (
                          <Chip
                            key={index}
                            label={skill}
                            size="small"
                            variant="outlined"
                            sx={{ mr: 0.5 }}
                          />
                        ))}
                        {event.required_skills.length > 2 && (
                          <Chip
                            label={`+${event.required_skills.length - 2} more`}
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Box>
                    </Box>
                  </Box>
                )}
              />

              <SubmitButton
                label="Create Match"
                onClick={handleManualMatch}
                disabled={!selectedVolunteer || !selectedEvent}
                startIcon={<AssignmentIcon />}
              />
            </Stack>
          </Paper>
        </Box>

        {/* Match Suggestions */}
        <Box sx={{ flex: 1 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <EventIcon color="primary" />
              Suggested Matches
              {selectedVolunteer && (
                <Chip
                  label={`for ${selectedVolunteer.full_name}`}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              )}
            </Typography>
            <Divider sx={{ mb: 3 }} />

            {!selectedVolunteer ? (
              <Typography color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                Select a volunteer to see matching event suggestions
              </Typography>
            ) : matchSuggestions.length === 0 ? (
              <Typography color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                No matching events found for this volunteer's skills
              </Typography>
            ) : (
              <Stack spacing={2}>
                {matchSuggestions.map((suggestion, index) => (
                  <Card key={index} variant="outlined">
                    <CardContent sx={{ pb: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                        <Typography variant="h6" component="h3">
                          {suggestion.event.name}
                        </Typography>
                        <Chip
                          label={`${suggestion.matchPercentage}% Match`}
                          color="success"
                          size="small"
                        />
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        {new Date(suggestion.event.event_date).toLocaleDateString()} • {suggestion.event.location}
                      </Typography>

                      <Typography variant="caption" color="text.secondary">
                        Matching Skills:
                      </Typography>
                      <Box sx={{ mb: 2 }}>
                        {suggestion.matchingSkills.map((skill, skillIndex) => (
                          <Chip
                            key={skillIndex}
                            label={skill}
                            size="small"
                            color="success"
                            variant="filled"
                            sx={{ mr: 0.5, mb: 0.5 }}
                          />
                        ))}
                      </Box>

                      <Button
                        variant="contained"
                        size="small"
                        onClick={() => handleSuggestionMatch(suggestion)}
                        startIcon={<AssignmentIcon />}
                      >
                        Match Now
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </Stack>
            )}
          </Paper>
        </Box>
      </Box>
    </Container>
  );
};

export default AdminVolunteerMatchingPage;