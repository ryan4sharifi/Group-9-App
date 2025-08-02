# Match volunteers to events based on skills, distance, and preferences
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.supabase_client import supabase
from app.routes.auth import verify_token
import requests
import os

# Get Google Maps API key from environment
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

router = APIRouter()

class MatchRequest(BaseModel):
    user_id: str
    max_distance: Optional[float] = 50.0  # Max distance in miles
    urgency_weight: Optional[float] = 0.3  # Weight for urgency in matching
    skill_weight: Optional[float] = 0.5    # Weight for skills in matching
    distance_weight: Optional[float] = 0.2  # Weight for distance in matching

class MatchResult(BaseModel):
    event_id: str
    event_name: str
    match_score: float
    skill_match_percentage: float
    distance_miles: float
    urgency_level: str
    reasons: List[str]

def calculate_distance(origin: str, destination: str) -> float:
    """Calculate distance between two addresses using Google Maps API"""
    # Check if we have a valid API key
    if not GOOGLE_MAPS_API_KEY or GOOGLE_MAPS_API_KEY == "mock_key":
        # Mock distance calculation for testing - return a reasonable distance
        # Use a hash-based approach that's more predictable
        hash_value = abs(hash(origin + destination))
        # Return a distance between 1 and 25 miles for testing
        return round((hash_value % 25) + 1, 2)
    
    try:
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            "origins": origin,
            "destinations": destination,
            "units": "imperial",
            "key": GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] == "OK" and data["rows"][0]["elements"][0]["status"] == "OK":
            distance_text = data["rows"][0]["elements"][0]["distance"]["text"]
            distance_miles = float(distance_text.replace(" mi", "").replace(",", ""))
            return distance_miles
        else:
            # Return a reasonable fallback distance instead of 999
            return 15.0  # Default to 15 miles if API fails
    except Exception:
        # Return a reasonable fallback distance instead of 999
        return 15.0

def calculate_skill_match(user_skills: List[str], event_skills: List[str]) -> float:
    """Calculate skill match percentage"""
    if not event_skills:
        return 0.0
    
    user_skills_set = set(skill.lower() for skill in user_skills)
    event_skills_set = set(skill.lower() for skill in event_skills)
    
    matching_skills = user_skills_set.intersection(event_skills_set)
    return (len(matching_skills) / len(event_skills_set)) * 100

def calculate_urgency_score(urgency: str) -> float:
    """Convert urgency to numerical score"""
    urgency_scores = {
        "high": 1.0,
        "medium": 0.6,
        "low": 0.3
    }
    return urgency_scores.get(urgency.lower(), 0.0)

def calculate_match_score(skill_match: float, distance: float, urgency: str, 
                         skill_weight: float, distance_weight: float, urgency_weight: float) -> float:
    """Calculate overall match score"""
    # Normalize skill match (0-100 to 0-1)
    skill_score = skill_match / 100
    
    # Normalize distance (inverse - closer is better, max 50 miles)
    distance_score = max(0, 1 - (distance / 50))
    
    # Get urgency score
    urgency_score = calculate_urgency_score(urgency)
    
    # Calculate weighted score
    total_score = (skill_score * skill_weight + 
                  distance_score * distance_weight + 
                  urgency_score * urgency_weight)
    
    return round(total_score * 100, 2)  # Convert back to percentage

def fetch_user_skills(user_id: str) -> set:
    """Helper function to fetch user skills from database"""
    try:
        result = supabase.table("user_profiles").select("skills").eq("user_id", user_id).execute()
        if result.data:
            return set(result.data[0].get("skills", []))
        return set()
    except Exception:
        return set()

def fetch_all_events() -> List[Dict]:
    """Helper function to fetch all events from database"""
    try:
        result = supabase.table("events").select("*").execute()
        return result.data if result.data else []
    except Exception:
        return []

# API route to match and notify volunteers about relevant events
@router.get("/match-and-notify/{user_id}")
async def match_and_notify(user_id: str) -> dict:
    """
    Matches a user to events based on skills and sends notifications if a new match is found.
    """
    try:
        user_skills = fetch_user_skills(user_id)
        all_events = fetch_all_events()

        matched_events = []

        for event in all_events:
            event_skills = set(event.get("required_skills", []))

            # Check if user's skills match required skills of event
            if user_skills.intersection(event_skills):
                matched_events.append(event)

                # Prevent sending duplicate notifications
                existing_notif = supabase.table("notifications") \
                    .select("id") \
                    .eq("user_id", user_id) \
                    .eq("event_id", event["id"]) \
                    .execute()

                if not existing_notif.data:
                    supabase.table("notifications").insert({
                        "user_id": user_id,
                        "event_id": event["id"],
                        "message": f"You've been matched with: {event['name']}",
                        "is_read": False
                    }).execute()

        return {"matched_events": matched_events}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API route to return matched events (without sending notifications)
@router.get("/matched_events/{user_id}")
async def get_matched_events(user_id: str) -> dict:
    """
    Returns matched events for a user based on skill intersection. No notifications are sent.
    """
    try:
        user_skills = fetch_user_skills(user_id)
        all_events = fetch_all_events()

        matched_events = [
            event for event in all_events
            if user_skills.intersection(set(event.get("required_skills", [])))
        ]

        return {"matched_events": matched_events}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/match", response_model=List[MatchResult])
async def match_volunteer_to_events(
    match_request: MatchRequest,
    current_user: dict = Depends(verify_token)
):
    """Advanced matching algorithm with distance, skills, and urgency"""
    try:
        # Verify user authorization
        if current_user["user_id"] != match_request.user_id and current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Get user profile
        user_profile = supabase.table("user_profiles").select("*").eq("user_id", match_request.user_id).execute()
        if not user_profile.data:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        user_data = user_profile.data[0]
        user_skills = user_data.get("skills", [])
        user_location = f"{user_data.get('address1', '')}, {user_data.get('city', '')}, {user_data.get('state', '')}"
        
        # Get all events
        events = supabase.table("events").select("*").execute()
        if not events.data:
            return []
        
        matches = []
        
        for event in events.data:
            # Calculate distance
            event_location = event.get("location", "")
            distance = calculate_distance(user_location, event_location)
            
            # Skip if too far
            if distance > match_request.max_distance:
                continue
            
            # Calculate skill match
            event_skills = event.get("required_skills", [])
            skill_match = calculate_skill_match(user_skills, event_skills)
            
            # Calculate overall match score
            match_score = calculate_match_score(
                skill_match,
                distance,
                event.get("urgency", "low"),
                match_request.skill_weight,
                match_request.distance_weight,
                match_request.urgency_weight
            )
            
            # Generate match reasons
            reasons = []
            if skill_match > 50:
                reasons.append(f"Strong skill match ({skill_match:.1f}%)")
            if distance < 10:
                reasons.append(f"Close location ({distance:.1f} miles)")
            if event.get("urgency") == "high":
                reasons.append("High priority event")
            
            matches.append(MatchResult(
                event_id=event["id"],
                event_name=event["name"],
                match_score=match_score,
                skill_match_percentage=skill_match,
                distance_miles=distance,
                urgency_level=event.get("urgency", "low"),
                reasons=reasons
            ))
        
        # Sort by match score (descending)
        matches.sort(key=lambda x: x.match_score, reverse=True)
        
        return matches
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/matched_events/{user_id}")
async def get_matched_events(user_id: str, current_user: dict = Depends(verify_token)):
    """Get matched events for a user (backward compatibility)"""
    try:
        match_request = MatchRequest(user_id=user_id)
        return await match_volunteer_to_events(match_request, current_user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-match")
async def batch_match_volunteers(current_user: dict = Depends(verify_token)):
    """Match all volunteers to events - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Get all volunteers
        volunteers = supabase.table("user_profiles").select("user_id").execute()
        if not volunteers.data:
            return {"message": "No volunteers found"}
        
        total_matches = 0
        
        for volunteer in volunteers.data:
            user_id = volunteer["user_id"]
            match_request = MatchRequest(user_id=user_id)
            
            # Get matches for this volunteer
            matches = await match_volunteer_to_events(match_request, {"user_id": user_id, "role": "admin"})
            
            # Create notifications for top matches
            for match in matches[:3]:  # Top 3 matches
                if match.match_score > 50:  # Only notify for good matches
                    supabase.table("notifications").insert({
                        "user_id": user_id,
                        "event_id": match.event_id,
                        "message": f"New match: {match.event_name} ({match.match_score:.1f}% match)",
                        "type": "match",
                        "is_read": False
                    }).execute()
                    total_matches += 1
        
        return {"message": f"Batch matching completed. {total_matches} notifications sent."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))