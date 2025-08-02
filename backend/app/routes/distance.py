# Distance calculation API routes with database caching
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from app.utils.distance import distance_calculator, calculate_distance_to_event, safe_distance_calculation
from app.utils.distance_db import (
    DistanceCache, calculate_and_cache_distance, get_nearby_events_for_user
)
from app.supabase_client import supabase
from app.routes.auth import verify_token
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Request/Response models
class DistanceRequest(BaseModel):
    origin_address: str
    destination_address: str

class DistanceResponse(BaseModel):
    distance: str
    duration: str
    origin_address: str
    destination_address: str
    status: str

class SimpleDistanceResponse(BaseModel):
    distance: str
    status: str

class CachedDistanceResponse(BaseModel):
    distance_text: str
    duration_text: str
    distance_value: int
    duration_value: int
    cached: bool
    calculated_at: str

class EventWithDistanceResponse(BaseModel):
    id: str
    name: str
    description: str
    location: str
    required_skills: List[str]
    urgency: str
    event_date: str
    distance_text: str
    duration_text: str
    distance_value: int
    duration_value: int
    cached: bool

@router.post("/distance/calculate", response_model=DistanceResponse)
async def calculate_distance_between_addresses(
    request: DistanceRequest,
    current_user: dict = Depends(verify_token)
):
    """
    Calculate distance and travel time between two addresses
    Requires authentication
    """
    try:
        result = distance_calculator.calculate_distance(
            request.origin_address, 
            request.destination_address
        )
        
        if not result:
            raise HTTPException(
                status_code=400, 
                detail="Could not calculate distance. Please check the addresses and try again."
            )
            
        return DistanceResponse(
            distance=result['distance']['text'],
            duration=result['duration']['text'],
            origin_address=result['origin_address'],
            destination_address=result['destination_address'],
            status=result['status']
        )
        
    except Exception as e:
        logger.error(f"Distance calculation API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during distance calculation")

@router.get("/events/{event_id}/distance", response_model=CachedDistanceResponse)
async def get_distance_to_event(
    event_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Get distance from current user's address to a specific event location
    Uses caching to improve performance - checks cache first, then calculates if needed
    """
    try:
        user_id = current_user["user_id"]  # Changed from "sub" to "user_id"
        
        # Get event location
        event_result = supabase.table("events").select("location").eq("id", event_id).execute()
        if not event_result.data:
            raise HTTPException(status_code=404, detail="Event not found")
            
        event_location = event_result.data[0]["location"]
        
        # Calculate distance with caching
        distance_data = calculate_and_cache_distance(user_id, event_id, event_location)
        
        if not distance_data:
            raise HTTPException(
                status_code=400, 
                detail="Could not calculate distance. Please ensure your profile has a complete address."
            )
        
        return CachedDistanceResponse(**distance_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Event distance API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/events/nearby", response_model=List[EventWithDistanceResponse])
async def get_nearby_events(
    max_distance: float = Query(50, description="Maximum distance in miles"),
    current_user: dict = Depends(verify_token)
):
    """
    Get events within a certain distance of the user, sorted by proximity
    Uses caching for improved performance
    """
    try:
        user_id = current_user["sub"]
        
        events_with_distance = get_nearby_events_for_user(user_id, max_distance)
        
        return [EventWithDistanceResponse(**event) for event in events_with_distance]
        
    except Exception as e:
        logger.error(f"Nearby events API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/cache/user/{user_id}")
async def get_user_distance_cache(
    user_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Get all cached distance calculations for a user
    Admins can check any user, volunteers can only check themselves
    """
    try:
        # Check permissions
        current_user_id = current_user["sub"]
        current_user_role = current_user["role"]
        
        if current_user_role != "admin" and current_user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        cached_distances = DistanceCache.get_distances_for_user(user_id)
        
        return {
            "user_id": user_id,
            "cached_distances": cached_distances,
            "count": len(cached_distances)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User cache API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/cache/cleanup")
async def cleanup_expired_cache(
    hours: int = Query(24, description="Age threshold in hours"),
    current_user: dict = Depends(verify_token)
):
    """
    Clean up expired cache entries
    Admin only endpoint
    """
    try:
        # Check admin permissions
        if current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        cleanup_count = DistanceCache.cleanup_expired_cache(hours)
        
        return {
            "message": f"Cleaned up {cleanup_count} expired cache entries",
            "cleaned_count": cleanup_count,
            "age_threshold_hours": hours
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cache cleanup API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/events/{event_id}/distance/{user_id}", response_model=CachedDistanceResponse)
async def get_distance_for_user_to_event(
    event_id: str,
    user_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Get distance from specific user's address to event location
    Uses caching for improved performance
    Admins can check any user, volunteers can only check themselves
    """
    try:
        # Check permissions
        current_user_id = current_user["sub"]
        current_user_role = current_user["role"]
        
        if current_user_role != "admin" and current_user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
        # Get event location
        event_result = supabase.table("events").select("location").eq("id", event_id).execute()
        if not event_result.data:
            raise HTTPException(status_code=404, detail="Event not found")
            
        event_location = event_result.data[0]["location"]
        
        # Calculate distance with caching
        distance_data = calculate_and_cache_distance(user_id, event_id, event_location)
        
        if not distance_data:
            raise HTTPException(
                status_code=400, 
                detail="Could not calculate distance. Please ensure the user profile has a complete address."
            )
        
        return CachedDistanceResponse(**distance_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User-event distance API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health/distance")
async def distance_api_health():
    """
    Check if Google Maps API is available and working
    """
    try:
        if not distance_calculator.client:
            return {
                "status": "unavailable",
                "message": "Google Maps API client not initialized",
                "google_maps_available": False
            }
            
        # Test with a simple geocoding request
        test_result = distance_calculator.geocode_address("Houston, TX")
        
        return {
            "status": "healthy" if test_result else "limited",
            "message": "Google Maps API is available" if test_result else "Google Maps API has issues",
            "google_maps_available": test_result is not None
        }
        
    except Exception as e:
        logger.error(f"Distance API health check error: {e}")
        return {
            "status": "error",
            "message": f"Health check failed: {str(e)}",
            "google_maps_available": False
        }
