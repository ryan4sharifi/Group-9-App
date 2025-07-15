# Routes for generating admin reports related to volunteers and event participation
from fastapi import APIRouter, HTTPException
from app.supabase_client import supabase

router = APIRouter()

# Returns full volunteer participation data including user and event details
@router.get("/reports/volunteers")
async def volunteer_participation_report():
    try:
        # Join volunteer_history with user_profiles and events
        response = supabase.table("volunteer_history").select("*, user_profiles(*), events(*)").execute()
        return {"report": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Returns a summary of all events with number of volunteers who participated
@router.get("/reports/events")
async def event_participation_summary():
    try:
        # Get all volunteer history entries
        history = supabase.table("volunteer_history").select("event_id").execute().data

        participation = {}
        # Count number of volunteers per event
        for row in history:
            event_id = row["event_id"]
            participation[event_id] = participation.get(event_id, 0) + 1

        # Get all event details
        events = supabase.table("events").select("*").execute().data

        summary = []
        # Build summary list for each event
        for event in events:
            summary.append({
                "event_id": event["id"],
                "name": event["name"],
                "date": event["event_date"],
                "location": event["location"],
                "volunteer_count": participation.get(event["id"], 0)
            })

        return {"event_summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))