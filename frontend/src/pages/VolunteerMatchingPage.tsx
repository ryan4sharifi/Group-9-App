import React, { useEffect, useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Stack,
  Alert,
  CircularProgress,
  Grid,
  Paper,
  Divider,
  useTheme,
} from '@mui/material';
import {
  EventAvailable as EventIcon,
  LocationOn as LocationIcon,
  CalendarToday as CalendarIcon,
  Assignment as AssignmentIcon,
  NotificationAdd as NotifyIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';
import axios from 'axios';
import { useUser } from '../context/UserContext';
import SubmitButton from '../components/buttons/SubmitButton';

interface MatchedEvent {
  id: string;
  name: string;
  description: string;
  event_date: string;
  location: string;
  required_skills: string[];
  urgency: 'low' | 'medium' | 'high';
}

interface UserSkills {
  skills: string[];
}

const VolunteerMatchingPage: React.FC = () => {
  const theme = useTheme();
  const { userId } = useUser();
  const [matchedEvents, setMatchedEvents] = useState<MatchedEvent[]>([]);
  const [userSkills, setUserSkills] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [signingUp, setSigningUp] = useState<string | null>(null);

  useEffect(() => {
    if (userId) {
      fetchMatchedEvents();
      fetchUserSkills();
    }
  }, [userId]);

  const fetchUserSkills = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/profile/${userId}`);
      setUserSkills(response.data.skills || []);
    } catch (err) {
      console.error('Error fetching user skills:', err);
    }
  };

  const fetchMatchedEvents = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/matched_events/${userId}`);
      setMatchedEvents(response.data.matched_events || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch matched events');
    } finally {
      setLoading(false);
    }
  };

  const handleSignUp = async (eventId: string) => {
    setSigningUp(eventId);
    setError(null);
    setSuccess(null);

    try {
      // Log volunteer participation
      await axios.post('http://localhost:8000/api/history', {
        user_id: userId,
        event_id: eventId,
        status: 'Signed Up'
      });

      // Trigger matching and notification
      await axios.get(`http://localhost:8000/api/match-and-notify/${userId}`);

      setSuccess('Successfully signed up for the event!');
      
      // Remove the event from matched events since user signed up
      setMatchedEvents(prev => prev.filter(event => event.id !== eventId));
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to sign up for event');
    } finally {
      setSigningUp(null);
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getMatchingSkills = (eventSkills: string[]) => {
    return eventSkills.filter(skill => userSkills.includes(skill));
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Finding events that match your skills...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Volunteer Matching
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Events that match your skills and interests
        </Typography>
      </Box>

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

      {/* User Skills Display */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <AssignmentIcon color="primary" />
          Your Skills
        </Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap">
          {userSkills.length > 0 ? (
            userSkills.map((skill, index) => (
              <Chip
                key={index}
                label={skill}
                color="primary"
                variant="filled"
                sx={{ mb: 1 }}
              />
            ))
          ) : (
            <Typography color="text.secondary">
              No skills listed. Please update your profile to get better matches.
            </Typography>
          )}
        </Stack>
      </Paper>

      {/* Matched Events */}
      {matchedEvents.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <EventIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            No Matching Events Found
          </Typography>
          <Typography color="text.secondary">
            {userSkills.length === 0 
              ? "Add skills to your profile to get personalized event recommendations."
              : "No events currently match your skills. Check back later for new opportunities!"
            }
          </Typography>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {matchedEvents.map((event) => {
            const matchingSkills = getMatchingSkills(event.required_skills);
            const matchPercentage = Math.round((matchingSkills.length / event.required_skills.length) * 100);
            
            return (
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

                    {/* Match Percentage */}
                    <Box sx={{ mb: 2 }}>
                      <Chip
                        label={`${matchPercentage}% Match`}
                        color="success"
                        variant="outlined"
                        size="small"
                        icon={<CheckIcon />}
                      />
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {event.description}
                    </Typography>

                    <Stack spacing={1} sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CalendarIcon fontSize="small" color="action" />
                        <Typography variant="body2">
                          {new Date(event.event_date).toLocaleDateString('en-US', {
                            weekday: 'long',
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                          })}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <LocationIcon fontSize="small" color="action" />
                        <Typography variant="body2">{event.location}</Typography>
                      </Box>
                    </Stack>

                    <Divider sx={{ my: 2 }} />

                    {/* Skills Matching */}
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                        Your Matching Skills:
                      </Typography>
                      <Stack direction="row" spacing={0.5} flexWrap="wrap">
                        {matchingSkills.map((skill, index) => (
                          <Chip
                            key={index}
                            label={skill}
                            size="small"
                            color="success"
                            variant="filled"
                            sx={{ mb: 0.5 }}
                          />
                        ))}
                      </Stack>
                    </Box>

                    <Box>
                      <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                        Additional Skills Needed:
                      </Typography>
                      <Stack direction="row" spacing={0.5} flexWrap="wrap">
                        {event.required_skills
                          .filter(skill => !matchingSkills.includes(skill))
                          .map((skill, index) => (
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
                  
                  <CardActions sx={{ p: 2, pt: 0 }}>
                    <SubmitButton
                      label={signingUp === event.id ? "Signing Up..." : "Sign Up"}
                      onClick={() => handleSignUp(event.id)}
                      loading={signingUp === event.id}
                      disabled={signingUp === event.id}
                      startIcon={<NotifyIcon />}
                      fullWidth
                      variant="contained"
                    />
                  </CardActions>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}
    </Container>
  );
};

export default VolunteerMatchingPage;