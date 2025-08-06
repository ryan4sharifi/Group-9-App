# Distance database operations for caching Google Maps API results
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import hashlib
import logging
from app.supabase_client import supabase
from app.utils.distance import distance_calculator, get_user_full_address

logger = logging.getLogger(__name__)

class DistanceCache:
    """Database operations for caching distance calculations"""
    
    @staticmethod
    def generate_cache_key(origin_address: str, destination_address: str) -> str:
        """Generate a unique cache key for the address pair"""
        combined = f"{origin_address.lower().strip()}|{destination_address.lower().strip()}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    @staticmethod
    def get_cached_distance(user_id: str, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached distance calculation for user-event pair
        
        Args:
            user_id: User ID
            event_id: Event ID
            
        Returns:
            Cached distance data or None if not found/expired
        """
        try:
            # Query for cached distance
            response = supabase.table("distance_cache").select("*").eq("user_id", user_id).eq("event_id", event_id).execute()
            
            if response.data and len(response.data) > 0:
                cached_data = response.data[0]
                
                # Check if cache is still valid (24 hours)
                calculated_at = datetime.fromisoformat(cached_data["calculated_at"].replace("Z", "+00:00"))
                if datetime.now() - calculated_at < timedelta(hours=24):
                    logger.info(f"Found valid cached distance for user {user_id} to event {event_id}")
                    return cached_data
                else:
                    logger.info(f"Cache expired for user {user_id} to event {event_id}")
                    # Delete expired cache
                    DistanceCache.delete_cached_distance(user_id, event_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached distance: {e}")
            return None
    
    @staticmethod
    def save_distance_calculation(
        user_id: str, 
        event_id: str, 
        origin_address: str, 
        destination_address: str,
        distance_result: Dict[str, Any]
    ) -> bool:
        """
        Save distance calculation to cache
        
        Args:
            user_id: User ID
            event_id: Event ID
            origin_address: Origin address
            destination_address: Destination address
            distance_result: Result from Google Maps API
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            cache_data = {
                "user_id": user_id,
                "event_id": event_id,
                "origin_address": origin_address,
                "destination_address": destination_address,
                "distance_text": distance_result["distance"]["text"],
                "distance_value": distance_result["distance"]["value"],
                "duration_text": distance_result["duration"]["text"],
                "duration_value": distance_result["duration"]["value"],
                "calculated_at": datetime.now().isoformat()
            }
            
            # Use upsert to handle duplicates
            response = supabase.table("distance_cache").upsert(
                cache_data, 
                on_conflict=["user_id", "event_id"]
            ).execute()
            
            if response.data:
                logger.info(f"Saved distance calculation to cache: user {user_id} to event {event_id}")
                return True
            else:
                logger.error(f"Failed to save distance to cache: {response.error}")
                return False
                
        except Exception as e:
            logger.error(f"Error saving distance calculation: {e}")
            return False
    
    @staticmethod
    def delete_cached_distance(user_id: str, event_id: str) -> bool:
        """
        Delete cached distance calculation
        
        Args:
            user_id: User ID
            event_id: Event ID
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            response = supabase.table("distance_cache").delete().eq("user_id", user_id).eq("event_id", event_id).execute()
            logger.info(f"Deleted cached distance for user {user_id} to event {event_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting cached distance: {e}")
            return False
    
    @staticmethod
    def get_distances_for_user(user_id: str) -> List[Dict[str, Any]]:
        """
        Get all cached distances for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of cached distance calculations
        """
        try:
            response = supabase.table("distance_cache").select("*").eq("user_id", user_id).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error retrieving user distances: {e}")
            return []
    
    @staticmethod
    def get_distances_for_event(event_id: str) -> List[Dict[str, Any]]:
        """
        Get all cached distances for an event
        
        Args:
            event_id: Event ID
            
        Returns:
            List of cached distance calculations
        """
        try:
            response = supabase.table("distance_cache").select("*").eq("event_id", event_id).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error retrieving event distances: {e}")
            return []
    
    @staticmethod
    def cleanup_expired_cache(hours: int = 24) -> int:
        """
        Clean up expired cache entries
        
        Args:
            hours: Age threshold in hours (default 24)
            
        Returns:
            Number of entries cleaned up
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Note: In a real SQL database, you'd use a WHERE clause
            # For the mock database, we need to fetch and filter manually
            response = supabase.table("distance_cache").select("*").execute()
            
            cleanup_count = 0
            if response.data:
                for entry in response.data:
                    calculated_at = datetime.fromisoformat(entry["calculated_at"].replace("Z", "+00:00"))
                    if calculated_at < cutoff_time:
                        supabase.table("distance_cache").delete().eq("id", entry["id"]).execute()
                        cleanup_count += 1
            
            logger.info(f"Cleaned up {cleanup_count} expired cache entries")
            return cleanup_count
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
            return 0

# Enhanced distance calculation with caching
def calculate_and_cache_distance(user_id: str, event_id: str, event_location: str) -> Optional[Dict[str, Any]]:
    """
    Calculate distance with caching - checks cache first, then calculates if needed
    Only requires address1, city, and state from user profile. address2 is optional.
    
    Args:
        user_id: User ID
        event_id: Event ID  
        event_location: Event location string
        
    Returns:
        Distance data with caching info
    """
    try:
        logger.info(f"Starting distance calculation for user {user_id} to event {event_id}")
        
        # First check cache
        cached_result = DistanceCache.get_cached_distance(user_id, event_id)
        if cached_result:
            return {
                "distance_text": cached_result["distance_text"],
                "duration_text": cached_result["duration_text"],
                "distance_value": cached_result["distance_value"],
                "duration_value": cached_result["duration_value"],
                "cached": True,
                "calculated_at": cached_result["calculated_at"]
            }
        
        # Get user profile for address
        user_response = supabase.table("user_profiles").select("*").eq("user_id", user_id).execute()
        if not user_response.data:
            logger.error(f"No profile found for user {user_id}")
            return None
        
        user_profile = user_response.data[0]
        
        user_address = get_user_full_address(user_profile)
        
        if not user_address:
            logger.error(f"Could not build address for user {user_id}")
            return None
        
        # Calculate distance using Google Maps API
        distance_result = distance_calculator.calculate_distance(user_address, event_location)
        
        if not distance_result:
            logger.error(f"Google Maps API could not calculate distance from {user_address} to {event_location}")
            return None
        
        # Save to cache
        DistanceCache.save_distance_calculation(
            user_id, event_id, user_address, event_location, distance_result
        )
        
        return {
            "distance_text": distance_result["distance"]["text"],
            "duration_text": distance_result["duration"]["text"], 
            "distance_value": distance_result["distance"]["value"],
            "duration_value": distance_result["duration"]["value"],
            "cached": False,
            "calculated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in calculate_and_cache_distance: {e}")
        return None

def get_nearby_events_for_user(user_id: str, max_distance_miles: float = 50) -> List[Dict[str, Any]]:
    """
    Get events within a certain distance of user, sorted by distance
    
    Args:
        user_id: User ID
        max_distance_miles: Maximum distance in miles
        
    Returns:
        List of events with distance information, sorted by distance
    """
    try:
        # Get all events
        events_response = supabase.table("events").select("*").execute()
        if not events_response.data:
            return []
        
        events_with_distance = []
        max_distance_meters = max_distance_miles * 1609.34  # Convert miles to meters
        
        for event in events_response.data:
            distance_data = calculate_and_cache_distance(user_id, event["id"], event["location"])
            
            if distance_data and distance_data["distance_value"] <= max_distance_meters:
                event_with_distance = {**event, **distance_data}
                events_with_distance.append(event_with_distance)
        
        # Sort by distance
        events_with_distance.sort(key=lambda x: x["distance_value"])
        
        logger.info(f"Found {len(events_with_distance)} events within {max_distance_miles} miles for user {user_id}")
        return events_with_distance
        
    except Exception as e:
        logger.error(f"Error getting nearby events: {e}")
        return []
