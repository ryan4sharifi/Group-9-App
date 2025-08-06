// Distance calculation utilities for frontend
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

export interface DistanceData {
  distance_text: string;
  duration_text: string;
  distance_value: number;
  duration_value: number;
  cached: boolean;
  calculated_at: string;
}

export interface EventWithDistance {
  id: string;
  name: string;
  description: string;
  location?: string; // Legacy field for backward compatibility
  address1: string;
  address2?: string;
  city: string;
  state: string;
  zip_code: string;
  required_skills: string[];
  urgency: 'low' | 'medium' | 'high';
  event_date: string;
  distance_text?: string;
  duration_text?: string;
  distance_value?: number;
  duration_value?: number;
  cached?: boolean;
}

/**
 * Get distance from user to a specific event
 */
export const getDistanceToEvent = async (
  eventId: string,
  token: string
): Promise<DistanceData | null> => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/events/${eventId}/distance`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error(`Error fetching distance to event ${eventId}:`, error);
    return null;
  }
};

/**
 * Get nearby events within specified distance
 */
export const getNearbyEvents = async (
  maxDistance: number = 50,
  token: string
): Promise<EventWithDistance[]> => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/events/nearby?max_distance=${maxDistance}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching nearby events:', error);
    return [];
  }
};

/**
 * Get distance for a specific user to an event (admin only)
 */
export const getDistanceForUserToEvent = async (
  eventId: string,
  userId: string,
  token: string
): Promise<DistanceData | null> => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/events/${eventId}/distance/${userId}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error(`Error fetching distance for user ${userId} to event ${eventId}:`, error);
    return null;
  }
};

/**
 * Add distance information to a list of events
 */
export const addDistanceToEvents = async (
  events: any[],
  token: string
): Promise<EventWithDistance[]> => {
  const eventsWithDistance = await Promise.all(
    events.map(async (event) => {
      const distanceData = await getDistanceToEvent(event.id, token);
      
      if (distanceData) {
        return {
          ...event,
          distance_text: distanceData.distance_text,
          duration_text: distanceData.duration_text,
          distance_value: distanceData.distance_value,
          duration_value: distanceData.duration_value,
          cached: distanceData.cached,
        };
      }
      
      return event;
    })
  );
  
  return eventsWithDistance;
};

/**
 * Sort events by various criteria with direction support
 */
export const sortEventsByDistance = (
  events: EventWithDistance[],
  options: {
    sortBy: 'distance' | 'date' | 'name';
    sortOrder: 'asc' | 'desc';
  } = { sortBy: 'distance', sortOrder: 'asc' }
): EventWithDistance[] => {
  const { sortBy, sortOrder } = options;
  
  return events.sort((a, b) => {
    let comparison = 0;
    
    switch (sortBy) {
      case 'distance':
        // Events without distance data go to the end
        if (!a.distance_value && !b.distance_value) return 0;
        if (!a.distance_value) return 1;
        if (!b.distance_value) return -1;
        comparison = a.distance_value - b.distance_value;
        break;
        
      case 'date':
        const dateA = new Date(a.event_date).getTime();
        const dateB = new Date(b.event_date).getTime();
        comparison = dateA - dateB;
        break;
        
      case 'name':
        comparison = a.name.localeCompare(b.name);
        break;
        
      default:
        return 0;
    }
    
    return sortOrder === 'asc' ? comparison : -comparison;
  });
};

/**
 * Filter events by maximum distance
 */
export const filterEventsByDistance = (
  events: EventWithDistance[],
  maxDistanceKm: number
): EventWithDistance[] => {
  const maxDistanceMeters = maxDistanceKm * 1000; // Convert km to meters
  
  return events.filter(event => {
    if (!event.distance_value) return false;
    return event.distance_value <= maxDistanceMeters;
  });
};

/**
 * Format distance value to human readable string
 */
export const formatDistance = (distanceMeters: number, unit: 'km' | 'miles' = 'km'): string => {
  if (unit === 'miles') {
    const miles = distanceMeters / 1609.34;
    
    if (miles < 1) {
      return `${(miles * 5280).toFixed(0)} ft`;
    } else if (miles < 10) {
      return `${miles.toFixed(1)} mi`;
    } else {
      return `${miles.toFixed(0)} mi`;
    }
  } else {
    const kilometers = distanceMeters / 1000;
    
    if (kilometers < 1) {
      return `${distanceMeters.toFixed(0)} m`;
    } else if (kilometers < 10) {
      return `${kilometers.toFixed(1)} km`;
    } else {
      return `${kilometers.toFixed(0)} km`;
    }
  }
};

/**
 * Format distance with both miles and kilometers (miles primary)
 */
export const formatDistanceBoth = (distanceMeters: number): string => {
  const miles = formatDistance(distanceMeters, 'miles');
  const km = formatDistance(distanceMeters, 'km');
  return `${miles} (${km})`;
};

/**
 * Format duration value to human readable string
 */
export const formatDuration = (durationSeconds: number): string => {
  const hours = Math.floor(durationSeconds / 3600);
  const minutes = Math.floor((durationSeconds % 3600) / 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  } else {
    return `${minutes}m`;
  }
};

/**
 * Get urgency color for distance display
 */
export const getDistanceUrgencyColor = (
  distanceValue?: number,
  urgency?: string
): 'success' | 'warning' | 'error' | 'default' => {
  if (!distanceValue) return 'default';
  
  const miles = distanceValue / 1609.34;
  
  // Combine distance and urgency for color logic
  if (urgency === 'high') {
    return miles <= 25 ? 'success' : miles <= 50 ? 'warning' : 'error';
  } else if (urgency === 'medium') {
    return miles <= 50 ? 'success' : 'warning';
  } else {
    return miles <= 100 ? 'success' : 'default';
  }
};
