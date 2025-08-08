import React, { useEffect, useState, useCallback } from 'react';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Paper,
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
  IconButton,
  Divider,
  useTheme,
  useMediaQuery,
  CircularProgress,
  MenuItem,
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
  MyLocation as MyLocationIcon,
  Place as PlaceIcon,
} from '@mui/icons-material';
import axios from 'axios';
import { useUser } from '../context/UserContext';
import SubmitButton from '../components/buttons/SubmitButton';
import ConfirmDialog from '../components/common/ConfirmDialog';
import DistanceDisplay from '../components/distance/DistanceDisplay';
import DistanceFilter from '../components/distance/DistanceFilter';
import { 
  addDistanceToEvents, 
  getDistanceToEvent,
  sortEventsByDistance, 
  filterEventsByDistance 
} from '../utils/distance';

interface Event {
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
  const [displayedEvents, setDisplayedEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [distanceLoading, setDistanceLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingEvent, setEditingEvent] = useState<Event | null>(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [eventToDelete, setEventToDelete] = useState<string | null>(null);
  
  // Distance filter states
  const [maxDistance, setMaxDistance] = useState(25);
  const [sortBy, setSortBy] = useState<'distance' | 'date' | 'name'>('distance');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [showNearbyOnly, setShowNearbyOnly] = useState(false);
  const [userLocation, setUserLocation] = useState<{lat: number, lng: number} | null>(null);
  
  const [form, setForm] = useState({
    name: '',
    description: '',
    event_date: '',
    address1: '',
    address2: '',
    city: '',
    state: '',
    zip_code: '',
    required_skills: [] as string[],
    urgency: 'medium' as 'low' | 'medium' | 'high'
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchEvents();
    getUserLocation();
  }, []);

  useEffect(() => {
    applyFiltersAndSorting();
  }, [events, maxDistance, sortBy, sortOrder, showNearbyOnly]);

  // Add distance information when userLocation becomes available
  useEffect(() => {
    if (userLocation && userId && events.length > 0) {
      // Only add distance info if events don't already have distance data
      const hasDistanceData = events.some(event => event.distance_value !== undefined);
      if (!hasDistanceData) {
        addDistanceInfo(events);
      }
    }
  }, [userLocation, userId]);

  const getFullAddress = (event: Event) => {
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
          // Don't show error to user, distance features will just be disabled
        }
      );
    }
  };

  const fetchEvents = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/events');
      const eventsData = response.data;
      
      // Set events immediately for progressive loading
      setEvents(eventsData);
      
      // Add distance information progressively if user location is available
      if (userLocation && userId) {
        addDistanceInfo(eventsData);
      }
    } catch (err) {
      console.error('Error fetching events:', err);
      setError('Failed to fetch events');
    } finally {
      setLoading(false);
    }
  };

  const addDistanceInfo = async (eventsData: Event[]) => {
    if (!userLocation || !userId) return;
    
    setDistanceLoading(true);
    try {
      // Get auth token
      const token = localStorage.getItem('token');
      if (!token) return;
      
      // Add distance information progressively - each event updates as calculation completes
      const updatedEvents = [...eventsData];
      
      // Process events in parallel but update UI as each completes
      await Promise.allSettled(
        eventsData.map(async (event, index) => {
          try {
            const distanceData = await getDistanceToEvent(event.id, token);
            if (distanceData) {
              updatedEvents[index] = {
                ...event,
                distance_text: distanceData.distance_text,
                duration_text: distanceData.duration_text,
                distance_value: distanceData.distance_value,
                duration_value: distanceData.duration_value,
                distance_cached: distanceData.cached,
              };
              
              // Update state immediately as each distance is calculated
              setEvents(prevEvents => {
                const newEvents = [...prevEvents];
                const eventIndex = newEvents.findIndex(e => e.id === event.id);
                if (eventIndex !== -1) {
                  newEvents[eventIndex] = updatedEvents[index];
                }
                return newEvents;
              });
            }
          } catch (err) {
            console.error(`Error calculating distance for event ${event.id}:`, err);
          }
        })
      );
    } catch (err) {
      console.error('Error adding distance information:', err);
    } finally {
      setDistanceLoading(false);
    }
  };

  const applyFiltersAndSorting = () => {
    let filteredEvents = [...events];
    
    if (showNearbyOnly && userLocation) {
      filteredEvents = filterEventsByDistance(filteredEvents, maxDistance);
    }
    
    const sortedEvents = sortEventsByDistance(filteredEvents, {
      sortBy,
      sortOrder
    });
    setDisplayedEvents(sortedEvents);
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
      address1: event.address1,
      address2: event.address2 || '',
      city: event.city,
      state: event.state,
      zip_code: event.zip_code,
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
      address1: '',
      address2: '',
      city: '',
      state: '',
      zip_code: '',
      required_skills: [],
      urgency: 'medium'
    });
  };

  const getUrgencyColor = (urgency: string) => {
    const normalizedUrgency = urgency.toLowerCase();
    switch (normalizedUrgency) {
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

      {/* Distance Filters */}
      {userLocation && (
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
          totalEventsCount={events.length}
        />
      )}

      {/* Location Status */}
      {!userLocation && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Box display="flex" alignItems="center" gap={1}>
            <MyLocationIcon />
            <Typography variant="body2">
              Enable location access to see distance information (in miles and km) for each event.
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

      {/* Sign-in reminder for distance features */}
      {userLocation && !userId && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Box display="flex" alignItems="center" gap={1}>
            <Typography variant="body2">
              Sign in to see distance calculations and use distance-based filtering for events.
            </Typography>
          </Box>
        </Alert>
      )}

      {distanceLoading && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Box display="flex" alignItems="center" gap={2}>
            <CircularProgress size={20} />
            <Typography variant="body2">
              Calculating distances to events... Events will update with distance information as calculations complete.
            </Typography>
          </Box>
        </Alert>
      )}

      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: {
          xs: '1fr',
          md: 'repeat(2, 1fr)',
          lg: 'repeat(3, 1fr)'
        },
        gap: 3
      }}>
        {displayedEvents.length === 0 ? (
          <Box sx={{ 
            gridColumn: '1 / -1', 
            textAlign: 'center', 
            py: 8,
            bgcolor: 'grey.50',
            borderRadius: 2
          }}>
            <EventIcon sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              {events.length === 0 
                ? 'No events available' 
                : showNearbyOnly 
                  ? `No events found within ${Math.round(maxDistance * 0.621371)} mi`
                  : 'No events match your current filters'
              }
            </Typography>
            {showNearbyOnly && events.length > 0 && (
              <Typography variant="body2" color="text.secondary">
                Try increasing the distance range or disable location filtering
              </Typography>
            )}
          </Box>
        ) : (
          displayedEvents.map((event) => (
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
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5, flex: 1 }}>
                      <Typography variant="body2">
                        {event.address1 ? `${event.address1}, ${event.city}, ${event.state} ${event.zip_code}` : 'No address available'}
                      </Typography>
                      {/* Distance Information */}
                      {userLocation && userId && (event.distance_text || event.duration_text) && (
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
                      {/* Show sign-in prompt when user not logged in but location available */}
                      {userLocation && !userId && (
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <PlaceIcon fontSize="small" color="action" sx={{ fontSize: 14 }} />
                          Sign in to see distance
                        </Typography>
                      )}
                    </Box>
                  </Box>
                </Stack>                  <Box>
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
          ))
        )}
      </Box>

      {/* Create/Edit Event Dialog */}
      <Dialog 
        open={dialogOpen} 
        onClose={handleCloseDialog} 
        maxWidth="md" 
        fullWidth
      >
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
              label="Address Line 1"
              fullWidth
              value={form.address1}
              onChange={(e) => setForm({ ...form, address1: e.target.value })}
              required
            />
            
            <TextField
              label="Address Line 2 (Optional)"
              fullWidth
              value={form.address2}
              onChange={(e) => setForm({ ...form, address2: e.target.value })}
            />
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                label="City"
                fullWidth
                value={form.city}
                onChange={(e) => setForm({ ...form, city: e.target.value })}
                required
              />
              <TextField
                label="State"
                fullWidth
                value={form.state}
                onChange={(e) => setForm({ ...form, state: e.target.value })}
                required
              />
              <TextField
                label="ZIP Code"
                fullWidth
                value={form.zip_code}
                onChange={(e) => setForm({ ...form, zip_code: e.target.value })}
                required
              />
            </Box>
            
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
            onClick={() => {
              const syntheticEvent = {
                preventDefault: () => {},
              } as React.FormEvent;
              handleSubmit(syntheticEvent);
            }}
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