# Volunteer History Routes – Log, Retrieve, Update, Delete Participation Records

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.supabase_client import supabase

router = APIRouter()

# Pydantic model for validating volunteer participation logs
class VolunteerLog(BaseModel):
    user_id: str
    event_id: str
    status: str  # "Attended", "Signed Up", "Missed"

# Add a new participation record to volunteer_history table
@router.post("/history")
async def log_volunteer_participation(log: VolunteerLog):
    try:
        response = supabase.table("volunteer_history").insert(log.dict()).execute()
        return {"message": "Volunteer history created successfully.", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get volunteer history for a specific user by user_id
@router.get("/history/{user_id}")
async def get_volunteer_history(user_id: str):
    try:
        # Join with events table to fetch event details
        response = supabase.table("volunteer_history").select("*, events(*)").eq("user_id", user_id).execute()
        return {"history": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update a specific participation record by log_id
@router.put("/history/{log_id}")
async def update_volunteer_log(log_id: str, log: VolunteerLog):
    try:
        response = supabase.table("volunteer_history").update(log.dict()).eq("id", log_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="History entry not found")
        return {"message": "Volunteer history updated successfully.", "data": response.data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete a participation record by log_id
@router.delete("/history/{log_id}")
async def delete_volunteer_log(log_id: str):
    try:
        response = supabase.table("volunteer_history").delete().eq("id", log_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="History entry not found")
        return {"message": "Volunteer history deleted successfully."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))