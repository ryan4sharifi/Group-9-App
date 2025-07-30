import React, { useEffect, useState } from 'react';
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
  Grid,
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

const MatchPage: React.FC = () => {
  const { userId } = useUser();
  const [matchedEvents, setMatchedEvents] = useState<Event[]>([]);
  const [allEvents, setAllEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  const theme = useTheme();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [matchedRes, allRes] = await Promise.all([
          axios.get(`http://localhost:8000/api/matched_events/${userId}`),
          axios.get(`http://localhost:8000/api/events`)
        ]);
        setMatchedEvents(matchedRes.data.matched_events || []);
        setAllEvents(allRes.data || []);
      } catch {
        setAlert({ open: true, message: 'Failed to load events', severity: 'error' });
      } finally {
        setLoading(false);
      }
    };
    if (userId) fetchData();
  }, [userId]);

  const handleSignup = async (eventId: string) => {
    try {
      await axios.post(`http://localhost:8000/api/history`, {
        user_id: userId,
        event_id: eventId,
        status: 'Signed Up',
      });
      setAlert({ open: true, message: 'Signed up successfully!', severity: 'success' });
    } catch {
      setAlert({ open: true, message: 'Failed to sign up', severity: 'error' });
    }
  };

  const EventCard = ({ event }: { event: Event }) => (
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
        <Button
          variant="contained"
          fullWidth
          onClick={() => handleSignup(event.id)}
          sx={{ borderRadius: 2, fontWeight: 600, textTransform: 'none' }}
        >
          Sign Up
        </Button>
      </CardActions>
    </Card>
  );

  const renderEventList = (events: Event[]) => (
    <Grid container spacing={3} sx={{ mt: 1, width: '100%' }}>
      {events.map((event) => (
        <Grid key={event.id} size={{ xs: 12, sm: 6 }}>
          <EventCard event={event} />
        </Grid>
      ))}
    </Grid>
  );

  const unmatchedEvents = allEvents.filter(e => !matchedEvents.some(m => m.id === e.id));

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
              Matched Events
            </Typography>
            {matchedEvents.length ? renderEventList(matchedEvents) : (
              <Typography variant="body2" color="text.secondary">No matched events.</Typography>
            )}
          </Paper>

          <Paper elevation={0}>
            <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
              All Other Events
            </Typography>
            {unmatchedEvents.length ? renderEventList(unmatchedEvents) : (
              <Typography variant="body2" color="text.secondary">No additional events.</Typography>
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