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
  MyLocation as MyLocationIcon,
} from '@mui/icons-material';
import axios from 'axios';
import { useUser } from '../context/UserContext';
import SubmitButton from '../components/buttons/SubmitButton';
import DistanceDisplay from '../components/distance/DistanceDisplay';
import DistanceFilter from '../components/distance/DistanceFilter';
import { 
  addDistanceToEvents, 
  sortEventsByDistance, 
  filterEventsByDistance 
} from '../utils/distance';

interface MatchedEvent {
  id: string;
  name: string;
  description: string;
  event_date: string;
  location?: string; // Legacy field for backward compatibility
  address1: string;
  address2?: string;
  city: string;
  state: string;
  zip_code: string;
  required_skills: string[];
  urgency: 'low' | 'medium' | 'high';
  distance_text?: string;
  duration_text?: string;
  distance_value?: number;
  duration_value?: number;
  distance_cached?: boolean;
}

interface UserSkills {
  skills: string[];
}

const VolunteerMatchingPage: React.FC = () => {
  const theme = useTheme();
  const { userId } = useUser();
  const [matchedEvents, setMatchedEvents] = useState<MatchedEvent[]>([]);
  const [displayedEvents, setDisplayedEvents] = useState<MatchedEvent[]>([]);
  const [userSkills, setUserSkills] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [distanceLoading, setDistanceLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [signingUp, setSigningUp] = useState<string | null>(null);
  
  // Distance filter states
  const [maxDistance, setMaxDistance] = useState(25);
  const [sortBy, setSortBy] = useState<'distance' | 'date' | 'name'>('distance');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [showNearbyOnly, setShowNearbyOnly] = useState(false);
  const [userLocation, setUserLocation] = useState<{lat: number, lng: number} | null>(null);

  useEffect(() => {
    if (userId) {
      fetchMatchedEvents();
      fetchUserSkills();
      getUserLocation();
    }
  }, [userId]);

  useEffect(() => {
    applyFiltersAndSorting();
  }, [matchedEvents, maxDistance, sortBy, sortOrder, showNearbyOnly]);

  const getFullAddress = (event: MatchedEvent) => {
    const parts = [
      event.address1,
      event.address2,
      event.city,
      `${event.state} ${event.zip_code}`
    ].filter(part => part && part.trim() !== '');
    
    const address = parts.join(', ');
    return address;
  };

  const getUserLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          });
        },
        (error) => {
          console.log('Could not get user location:', error);
        }
      );
    }
  };

  const applyFiltersAndSorting = () => {
    let filteredEvents = [...matchedEvents];
    
    if (showNearbyOnly && userLocation) {
      filteredEvents = filterEventsByDistance(filteredEvents, maxDistance);
    }
    
    const sortedEvents = sortEventsByDistance(filteredEvents, {
      sortBy,
      sortOrder
    });
    setDisplayedEvents(sortedEvents);
  };

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
      const eventsData = response.data.matched_events || [];
      setMatchedEvents(eventsData);
      
      // Add distance information if user location is available
      if (userLocation && userId) {
        await addDistanceInfo(eventsData);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch matched events');
    } finally {
      setLoading(false);
    }
  };

  const addDistanceInfo = async (eventsData: MatchedEvent[]) => {
    if (!userLocation || !userId) return;
    
    setDistanceLoading(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) return;
      
      const eventsWithDistance = await addDistanceToEvents(eventsData, token);
      setMatchedEvents(eventsWithDistance);
    } catch (err) {
      console.error('Error adding distance information:', err);
    } finally {
      setDistanceLoading(false);
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

      {/* Location Status */}
      {!userLocation && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Box display="flex" alignItems="center" gap={1}>
            <MyLocationIcon />
            <Typography variant="body2">
              Enable location access to see distance information and use distance-based filtering.
            </Typography>
            <Button 
              size="small" 
              onClick={getUserLocation}
              variant="outlined"
            >
              Enable Location
            </Button>
          </Box>
        </Alert>
      )}

      {distanceLoading && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Box display="flex" alignItems="center" gap={2}>
            <CircularProgress size={20} />
            <Typography variant="body2">
              Calculating distances to events...
            </Typography>
          </Box>
        </Alert>
      )}

      {/* Distance Filters */}
      {userLocation && matchedEvents.length > 0 && (
        <DistanceFilter
          maxDistance={maxDistance}
          sortBy={sortBy}
          sortOrder={sortOrder}
          showNearbyOnly={showNearbyOnly}
          onMaxDistanceChange={setMaxDistance}
          onSortByChange={setSortBy}
          onSortOrderChange={setSortOrder}
          onShowNearbyOnlyChange={setShowNearbyOnly}
          nearbyEventsCount={displayedEvents.length}
          totalEventsCount={matchedEvents.length}
        />
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
      {displayedEvents.length === 0 && matchedEvents.length > 0 && showNearbyOnly ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <EventIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            No Nearby Matched Events
          </Typography>
          <Typography color="text.secondary">
            No matched events found within {maxDistance} km. Try increasing the distance range.
          </Typography>
        </Paper>
      ) : displayedEvents.length === 0 ? (
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
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: {
            xs: '1fr',
            md: 'repeat(2, 1fr)',
            lg: 'repeat(3, 1fr)'
          },
          gap: 3
        }}>
          {displayedEvents.map((event) => {
            const matchingSkills = getMatchingSkills(event.required_skills);
            const matchPercentage = Math.round((matchingSkills.length / event.required_skills.length) * 100);
            
            return (
              <Card key={event.id} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
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

                    {/* Match Percentage and Distance */}
                    <Box sx={{ mb: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Chip
                        label={`${matchPercentage}% Match`}
                        color="success"
                        variant="outlined"
                        size="small"
                        icon={<CheckIcon />}
                      />
                      {userLocation && (event.distance_text || event.duration_text) && (
                        <DistanceDisplay
                          distance_text={event.distance_text}
                          duration_text={event.duration_text}
                          distance_value={event.distance_value}
                          duration_value={event.duration_value}
                          cached={event.distance_cached}
                          urgency={event.urgency}
                          variant="chip"
                          size="small"
                          showBothUnits={true}
                        />
                      )}
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
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5, flex: 1 }}>
                          <Typography variant="body2">
                            {event.address1 ? `${event.address1}, ${event.city}, ${event.state} ${event.zip_code}` : 'No address available'}
                          </Typography>
                          {/* Distance Information */}
                          {userLocation && (event.distance_text || event.duration_text) && (
                            <DistanceDisplay
                              distance_text={event.distance_text}
                              duration_text={event.duration_text}
                              distance_value={event.distance_value}
                              duration_value={event.duration_value}
                              cached={event.distance_cached}
                              urgency={event.urgency}
                              variant="compact"
                              showBothUnits={true}
                            />
                          )}
                        </Box>
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
            );
          })}
        </Box>
      )}
    </Container>
  );
};

export default VolunteerMatchingPage;