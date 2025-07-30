from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, constr
from typing import List
from app.supabase_client import supabase

router = APIRouter()

class Event(BaseModel):
    name: constr(max_length=100)
    description: str
    location: str
    required_skills: List[str]
    urgency: str
    event_date: str  # Format: 'YYYY-MM-DD'

def verify_admin(user_id: str):
    user_check = supabase.table("user_credentials").select("role").eq("id", user_id).single().execute()
    if not user_check.data or user_check.data["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can perform this action")

@router.post("/events")
async def create_event(event: Event, user_id: str):
    verify_admin(user_id)
    try:
        response = supabase.table("events").insert(event.dict()).execute()
        return {"message": "Event created", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events")
async def get_all_events():
    try:
        response = supabase.table("events").select("*").order("event_date", desc=False).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/{event_id}")
async def get_event_by_id(event_id: str):
    try:
        response = supabase.table("events").select("*").eq("id", event_id).single().execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Event not found")
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/events/{event_id}")
async def update_event(event_id: str, event: Event, user_id: str):
    verify_admin(user_id)
    try:
        response = supabase.table("events").update(event.dict()).eq("id", event_id).execute()
        return {"message": "Event updated", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/events/{event_id}")
async def delete_event(event_id: str, user_id: str):
    verify_admin(user_id)
    try:
        # Get event name for notifications
        event_res = supabase.table("events").select("name").eq("id", event_id).single().execute()
        if not event_res.data:
            raise HTTPException(status_code=404, detail="Event not found")
        event_name = event_res.data["name"]

        # Get all volunteer signups (user_ids)
        history_res = supabase.table("volunteer_history").select("user_id").eq("event_id", event_id).execute()
        user_ids = [row["user_id"] for row in history_res.data or []]

        # Notify each user
        for uid in user_ids:
            supabase.table("notifications").insert({
                "user_id": uid,
                "event_id": event_id,
                "message": f"The event '{event_name}' you signed up for has been canceled by the admin.",
                "is_read": False,
                
            }).execute()

       
        supabase.table("volunteer_history").delete().eq("event_id", event_id).execute()

        #
        supabase.table("events").delete().eq("id", event_id).execute()

        return {"message": "Event deleted and users notified"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))