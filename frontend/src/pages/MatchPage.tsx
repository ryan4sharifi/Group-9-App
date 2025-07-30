import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import {
  Container,
  Typography,
  Snackbar,
  Alert,
  CircularProgress,
  Stack,
  Box,
  Paper,
  Chip,
  Button,
  Divider,
  Card,
  CardContent,
  CardActions,
  useTheme,
  useMediaQuery,
  Tooltip,
} from '@mui/material';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import PriorityHighIcon from '@mui/icons-material/PriorityHigh';
import WorkIcon from '@mui/icons-material/Work';
import { useUser } from '../context/UserContext';

interface Event {
  id: string;
  name: string;
  description: string;
  location: string;
  event_date: string;
  urgency: string;
  required_skills: string[];
}

interface VolunteerHistoryItem {
  id: string;
  event_id: string;
  status: string;
  user_id: string;
}

interface UserProfile {
  skills: string[];
}

const MatchPage: React.FC = () => {
  const { userId } = useUser();
  const [matchedEvents, setMatchedEvents] = useState<Event[]>([]);
  const [allEvents, setAllEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const [signedUpEvents, setSignedUpEvents] = useState<Set<string>>(new Set());
  const [signingUpEventId, setSigningUpEventId] = useState<string | null>(null);
  const [userSkills, setUserSkills] = useState<string[]>([]);

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const fetchData = useCallback(async () => {
    if (!userId) {
      setLoading(false);
      setAlert({ open: true, message: 'User not logged in.', severity: 'error' });
      return;
    }
    setLoading(true);
    try {
      const [matchedRes, allRes, historyRes, profileRes] = await Promise.all([
        axios.get(`http://localhost:8000/api/matched_events/${userId}`),
        axios.get(`http://localhost:8000/api/events`),
        axios.get(`http://localhost:8000/api/history/${userId}`),
        axios.get<UserProfile>(`http://localhost:8000/api/profile/${userId}`)
      ]);

      setMatchedEvents(matchedRes.data.matched_events || []);
      setAllEvents(allRes.data || []);

      const userHistory: VolunteerHistoryItem[] = historyRes.data.history || [];
      const signedUpIds = new Set<string>();
      userHistory.forEach(item => {
        if (item.status === 'Signed Up' || item.status === 'Attended' || item.status === 'Missed') {
            signedUpIds.add(item.event_id);
        }
      });
      setSignedUpEvents(signedUpIds);

      setUserSkills(Array.isArray(profileRes.data.skills) ? profileRes.data.skills : []);

    } catch (err) {
      console.error("Error fetching data:", err);
      setAlert({ open: true, message: 'Failed to load events or user data.', severity: 'error' });
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleSignup = async (eventId: string) => {
    if (!userId) {
      setAlert({ open: true, message: 'Please log in to sign up for events.', severity: 'error' });
      return;
    }

    setSigningUpEventId(eventId);
    try {
      await axios.post(`http://localhost:8000/api/history`, {
        user_id: userId,
        event_id: eventId,
        status: 'Signed Up',
      });
      setAlert({ open: true, message: 'Signed up successfully!', severity: 'success' });
      setSignedUpEvents(prev => new Set(prev).add(eventId));
    } catch (err) {
        console.error("Error signing up:", err);
      setAlert({ open: true, message: 'Failed to sign up', severity: 'error' });
    } finally {
      setSigningUpEventId(null);
    }
  };

  // --- UPDATED: Function to check if user has required skills (Any Skill Match) ---
  const hasRequiredSkills = (eventRequiredSkills: string[], currentUserSkills: string[]): boolean => {
    // If user has no skills in profile, they cannot sign up for events requiring skills
    if (!currentUserSkills || currentUserSkills.length === 0) {
      return false;
    }
    // If event requires no skills, user can sign up (unlikely per problem statement)
    if (!eventRequiredSkills || eventRequiredSkills.length === 0) {
        return true;
    }

    // Check if AT LEAST ONE required skill is present in user's skills (case-insensitive)
    return eventRequiredSkills.some(reqSkill => // <-- CHANGED from .every() to .some()
      currentUserSkills.some(userSkill => userSkill.toLowerCase() === reqSkill.toLowerCase())
    );
  };
  // --- END UPDATED ---


  const EventCard = ({ event }: { event: Event }) => {
    const hasSignedUp = signedUpEvents.has(event.id);
    const isSigningUp = signingUpEventId === event.id;

    const userMeetsSkillRequirements = hasRequiredSkills(event.required_skills, userSkills);
    // Adjust skillMessage for 'any match' logic
    const skillMessage = !userSkills || userSkills.length === 0
        ? "Please update your profile with your skills to sign up." // User has no skills in profile
        : !userMeetsSkillRequirements
        ? "You do not have any of the required skills for this event." // User has skills, but none match
        : ""; // User has at least one skill that matches

    const isDisabled = hasSignedUp || isSigningUp || !userMeetsSkillRequirements;

    return (
      <Card
        elevation={2}
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          borderRadius: 2,
          transition: '0.2s',
          '&:hover': { boxShadow: 6 },
          border: `1px solid ${theme.palette.divider}`,
        }}
      >
        <CardContent sx={{ flexGrow: 1, p: 3 }}>
          <Typography variant="subtitle1" fontWeight={600} color="primary.main" gutterBottom>
            {event.name}
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {event.description}
          </Typography>

          <Stack spacing={1.5} sx={{ mb: 2.5 }}>
            <Box display="flex" alignItems="center" gap={1}>
              <LocationOnIcon fontSize="small" />
              <Typography variant="caption">{event.location}</Typography>
            </Box>
            <Box display="flex" alignItems="center" gap={1}>
              <CalendarTodayIcon fontSize="small" />
              <Typography variant="caption">
                {new Date(event.event_date).toLocaleDateString(undefined, {
                  year: 'numeric', month: 'long', day: 'numeric'
                })}
              </Typography>
            </Box>
            <Box display="flex" alignItems="center" gap={1}>
              <PriorityHighIcon fontSize="small" sx={{ color: theme.palette.error.main }} />
              <Typography variant="caption" fontWeight="medium" color={
                event.urgency === 'High' ? 'error.main' :
                event.urgency === 'Medium' ? 'warning.main' : 'success.main'
              }>
                {event.urgency} Priority
              </Typography>
            </Box>
          </Stack>

          <Box display="flex" alignItems="center" gap={1} mb={1}>
            <WorkIcon fontSize="small" />
            <Typography variant="caption" fontWeight={600}>Required Skills</Typography>
          </Box>
          <Box display="flex" flexWrap="wrap" gap={0.8}>
            {event.required_skills.map((skill, idx) => (
              <Chip
                key={idx}
                label={skill}
                size="small"
                color="primary"
                variant="outlined"
                sx={{ pointerEvents: 'none', fontSize: '0.7rem' }}
              />
            ))}
          </Box>
        </CardContent>
        <CardActions sx={{ p: 2, pt: 0 }}>
          <Tooltip title={isDisabled && !isSigningUp && !hasSignedUp ? skillMessage : ""} arrow>
            <span>
              <Button
                variant="contained"
                fullWidth
                onClick={() => handleSignup(event.id)}
                disabled={isDisabled}
                sx={{ borderRadius: 2, fontWeight: 600, textTransform: 'none' }}
              >
                {isSigningUp
                  ? <CircularProgress size={24} color="inherit" />
                  : hasSignedUp
                  ? 'You Signed Up!'
                  : !userMeetsSkillRequirements
                  ? 'No Skills Match' // Updated text for no match
                  : 'Sign Up'
                }
              </Button>
            </span>
          </Tooltip>
        </CardActions>
      </Card>
    );
  };

  const renderEventList = (events: Event[]) => (
    <Box
      sx={{
        mt: 1,
        width: '100%',
        display: 'flex',
        flexWrap: 'wrap',
        gap: theme.spacing(3),
        '& > *': {
          width: isMobile ? '100%' : 'calc(50% - 12px)',
        },
        '@media (min-width: 900px)': {
            '& > *': {
                width: 'calc(33.33% - 16px)',
            }
        },
      }}
    >
      {events.map((event) => (
        <Box key={event.id}>
          <EventCard event={event} />
        </Box>
      ))}
    </Box>
  );

  const unmatchedEvents = allEvents.filter(e => !signedUpEvents.has(e.id));

  return (
    <Container maxWidth="lg" sx={{ py: { xs: 3, md: 5 } }}>
      <Typography variant="h4" fontWeight={700} color="primary.dark" gutterBottom>
        Volunteer Opportunities
      </Typography>

      {loading ? (
        <Stack alignItems="center" py={5}><CircularProgress /></Stack>
      ) : (
        <>
          <Paper elevation={0} sx={{ mb: 5 }}>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
              Your Matched Events
            </Typography>
            {matchedEvents.length ? renderEventList(matchedEvents) : (
              <Typography variant="body2" color="text.secondary">No events matched to your skills yet.</Typography>
            )}
          </Paper>

          <Paper elevation={0}>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
              All Other Volunteer Events
            </Typography>
            {unmatchedEvents.length ? renderEventList(unmatchedEvents) : (
              <Typography variant="body2" color="text.secondary">No additional events available.</Typography>
            )}
          </Paper>
        </>
      )}

      <Snackbar
        open={alert.open}
        autoHideDuration={5000}
        onClose={() => setAlert(prev => ({ ...prev, open: false }))}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity={alert.severity} variant="filled" sx={{ width: '100%' }}>
          {alert.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default MatchPage;