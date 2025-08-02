# Distance calculation utilities using Google Maps API
import googlemaps
import os
from typing import Optional, Dict, Any, Tuple
import logging

# Set up logging for debugging
logger = logging.getLogger(__name__)

class DistanceCalculator:
    """Google Maps API client for distance calculations"""
    
    def __init__(self):
        """Initialize Google Maps client with API key"""
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            logger.warning("GOOGLE_MAPS_API_KEY not found in environment variables")
            self.client = None
        else:
            try:
                self.client = googlemaps.Client(key=self.api_key)
                logger.info("Google Maps client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Google Maps client: {e}")
                self.client = None
    
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert address to latitude/longitude coordinates
        
        Args:
            address: Full address string (e.g., "123 Main St, Houston, TX 77001")
            
        Returns:
            Tuple of (latitude, longitude) or None if geocoding fails
        """
        if not self.client:
            logger.error("Google Maps client not available")
            return None
            
        try:
            geocode_result = self.client.geocode(address)
            
            if not geocode_result:
                logger.warning(f"No geocoding results found for address: {address}")
                return None
                
            location = geocode_result[0]['geometry']['location']
            lat, lng = location['lat'], location['lng']
            
            logger.info(f"Geocoded '{address}' to ({lat}, {lng})")
            return (lat, lng)
            
        except Exception as e:
            logger.error(f"Error geocoding address '{address}': {e}")
            return None
    
    def calculate_distance(self, origin_address: str, destination_address: str) -> Optional[Dict[str, Any]]:
        """
        Calculate distance and travel time between two addresses
        
        Args:
            origin_address: Starting address
            destination_address: Destination address
            
        Returns:
            Dictionary containing distance and duration info or None if calculation fails
            Example: {
                "distance": {"text": "12.5 mi", "value": 20117},  # value in meters
                "duration": {"text": "18 mins", "value": 1080},   # value in seconds
                "status": "OK"
            }
        """
        if not self.client:
            logger.error("Google Maps client not available")
            return None
            
        try:
            # Use distance_matrix API for accurate distance/time calculation
            matrix_result = self.client.distance_matrix(
                origins=[origin_address],
                destinations=[destination_address],
                mode="driving",  # Can be "driving", "walking", "bicycling", "transit"
                units="imperial",  # Use miles instead of kilometers
                avoid=None  # Can avoid "tolls", "highways", "ferries", "indoor"
            )
            
            if not matrix_result or not matrix_result.get('rows'):
                logger.warning(f"No distance matrix results for {origin_address} to {destination_address}")
                return None
                
            element = matrix_result['rows'][0]['elements'][0]
            
            if element['status'] != 'OK':
                logger.warning(f"Distance calculation failed: {element['status']}")
                return None
                
            result = {
                "distance": element['distance'],
                "duration": element['duration'],
                "status": element['status'],
                "origin_address": matrix_result['origin_addresses'][0],
                "destination_address": matrix_result['destination_addresses'][0]
            }
            
            logger.info(f"Distance calculated: {result['distance']['text']} from {origin_address} to {destination_address}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating distance from '{origin_address}' to '{destination_address}': {e}")
            return None
    
    def calculate_distance_simple(self, origin_address: str, destination_address: str) -> Optional[str]:
        """
        Simple distance calculation that returns just the distance text
        
        Args:
            origin_address: Starting address
            destination_address: Destination address
            
        Returns:
            Distance as string (e.g., "12.5 mi") or None if calculation fails
        """
        result = self.calculate_distance(origin_address, destination_address)
        if result and result.get('distance'):
            return result['distance']['text']
        return None

# Global instance for reuse across the application
distance_calculator = DistanceCalculator()

def get_user_full_address(user_profile: Dict[str, Any]) -> Optional[str]:
    """
    Build full address string from user profile data
    
    Args:
        user_profile: User profile dictionary with address fields
        
    Returns:
        Full address string or None if required fields are missing
    """
    try:
        # Extract address components
        address1 = user_profile.get('address1', '').strip()
        address2 = user_profile.get('address2', '').strip()
        city = user_profile.get('city', '').strip()
        state = user_profile.get('state', '').strip()
        zip_code = user_profile.get('zip_code', '').strip()
        
        # Check if we have minimum required fields
        if not address1 or not city or not state:
            logger.warning("Missing required address fields in user profile")
            return None
            
        # Build address string
        address_parts = [address1]
        if address2:
            address_parts.append(address2)
        address_parts.append(f"{city}, {state}")
        if zip_code:
            address_parts.append(zip_code)
            
        full_address = ', '.join(address_parts)
        logger.info(f"Built full address: {full_address}")
        return full_address
        
    except Exception as e:
        logger.error(f"Error building user address: {e}")
        return None

def calculate_distance_to_event(user_profile: Dict[str, Any], event_location: str) -> Optional[str]:
    """
    Calculate distance from user's address to event location
    
    Args:
        user_profile: User profile with address information
        event_location: Event location string
        
    Returns:
        Distance string (e.g., "12.5 mi") or None if calculation fails
    """
    # Get user's full address
    user_address = get_user_full_address(user_profile)
    if not user_address:
        logger.warning("Could not build user address for distance calculation")
        return None
        
    # Calculate distance
    return distance_calculator.calculate_distance_simple(user_address, event_location)

# Error handling helper
def safe_distance_calculation(user_profile: Dict[str, Any], event_location: str, fallback: str = "Distance unavailable") -> str:
    """
    Safe distance calculation with fallback for errors
    
    Args:
        user_profile: User profile with address information
        event_location: Event location string
        fallback: Default message if calculation fails
        
    Returns:
        Distance string or fallback message
    """
    try:
        distance = calculate_distance_to_event(user_profile, event_location)
        return distance if distance else fallback
    except Exception as e:
        logger.error(f"Distance calculation error: {e}")
        return fallback
