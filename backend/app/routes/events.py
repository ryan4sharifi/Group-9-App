# Event Management API Routes using Supabase
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, constr
from typing import List
from app.supabase_client import get_supabase_client  #added import for Supabase client ** CHANGED THID **


router = APIRouter()
# Define event schema/validation for incoming requests
class Event(BaseModel):
    name: constr(max_length=100)
    description: str
    location: str
    required_skills: List[str]
    urgency: str
    event_date: str  # Format: 'YYYY-MM-DD'

# Utility to restrict certain operations to admin users only
def verify_admin(user_id: str):
    supabase = get_supabase_client() # Get the Supabase client **Changed to use the function**
    user_check = supabase.table("user_credentials").select("role").eq("id", user_id).single().execute()
    if not user_check.data or user_check.data["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can perform this action")

# Admin-only: Create a new event
@router.post("/events")
async def create_event(event: Event, user_id: str):
    verify_admin(user_id)
    try:
        response = supabase.table("events").insert(event.dict()).execute()
        return {"message": "Event created", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Public: Retrieve all events sorted by date
@router.get("/events")
async def get_all_events():
    try:
        response = supabase.table("events").select("*").order("event_date", desc=False).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Public: Retrieve a specific event by its ID
@router.get("/events/{event_id}")
async def get_event_by_id(event_id: str):
    try:
        response = supabase.table("events").select("*").eq("id", event_id).single().execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Event not found")
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Admin-only: Update event by ID
@router.put("/events/{event_id}")
async def update_event(event_id: str, event: Event, user_id: str):
    verify_admin(user_id)
    try:
        response = supabase.table("events").update(event.dict()).eq("id", event_id).execute()
        return {"message": "Event updated", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Admin-only: Delete event, notify volunteers, and clean up related data
@router.delete("/events/{event_id}")
async def delete_event(event_id: str, user_id: str):
    verify_admin(user_id)
    try:
        # Step 1: Get event name
        event_res = supabase.table("events").select("name").eq("id", event_id).single().execute()
        if not event_res.data:
            raise HTTPException(status_code=404, detail="Event not found")
        event_name = event_res.data["name"]

        # Step 2: Get all volunteer user_ids signed up
        history_res = supabase.table("volunteer_history").select("user_id").eq("event_id", event_id).execute()
        user_ids = [row["user_id"] for row in history_res.data or []]

        # Step 3: Send cancellation notifications to volunteers
        for uid in user_ids:
            supabase.table("notifications").insert({
                "user_id": uid,
                "event_id": event_id,
                "message": f"The event '{event_name}' you signed up for has been canceled by the admin.",
                "is_read": False,
            }).execute()

        # Step 4: Delete related volunteer history
        supabase.table("volunteer_history").delete().eq("event_id", event_id).execute()

        # Step 5: Delete the event
        supabase.table("events").delete().eq("id", event_id).execute()

        return {"message": "Event deleted and users notified"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))