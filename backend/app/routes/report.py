from fastapi import APIRouter, HTTPException
from app.supabase_client import supabase

router = APIRouter()

@router.get("/reports/volunteers")
async def volunteer_participation_report():
    try:
        response = supabase.table("volunteer_history").select("*, user_profiles(*), events(*)").execute()
        return {"report": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/events")
async def event_participation_summary():
    try:
        history = supabase.table("volunteer_history").select("event_id").execute().data

        participation = {}
        for row in history:
            event_id = row["event_id"]
            participation[event_id] = participation.get(event_id, 0) + 1

        events = supabase.table("events").select("*").execute().data

        summary = []
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