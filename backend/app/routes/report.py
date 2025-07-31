# Routes for generating admin reports related to volunteers and event participation
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.supabase_client import supabase
from app.routes.auth import verify_token

router = APIRouter()

class ReportFilter(BaseModel):
    """Filter parameters for reports"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None
    user_id: Optional[str] = None

class EventReport(BaseModel):
    """Event report model"""
    event_id: str
    event_name: str
    event_date: str
    location: str
    total_volunteers: int
    attended_volunteers: int
    attendance_rate: float

@router.get("/reports/volunteers")
async def volunteer_participation_report(
    filters: ReportFilter = None,
    current_user: dict = Depends(verify_token)
):
    """Generate comprehensive volunteer participation report"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        response = supabase.table("volunteer_history").select(
            "*, "
            "user_credentials!volunteer_history_user_id_fkey(" 
                "*, user_profiles(*)"  
            "), "
            "events(*)" 
        ).execute()

        
        return {"report": response.data}
    except Exception as e:
        print(f"Backend Error in volunteer_participation_report: {e}") 
        raise HTTPException(status_code=500, detail=str(e))

# Returns a summary of all events with number of volunteers who participated
@router.get("/reports/events")
async def event_participation_summary(
    filters: ReportFilter = None,
    current_user: dict = Depends(verify_token)
):
    """Generate event participation summary report"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Get all events
        events_query = supabase.table("events").select("*")
        if filters and filters.event_id:
            events_query = events_query.eq("id", filters.event_id)
        
        events_data = events_query.execute()
        
        # Get volunteer history
        history_query = supabase.table("volunteer_history").select("*")
        if filters:
            if filters.start_date:
                history_query = history_query.gte("created_at", filters.start_date)
            if filters.end_date:
                history_query = history_query.lte("created_at", filters.end_date)
        
        history_data = history_query.execute()
        
        # Process event statistics
        event_stats = {}
        for record in history_data.data:
            event_id = record["event_id"]
            if event_id not in event_stats:
                event_stats[event_id] = {
                    "total_volunteers": 0,
                    "attended_volunteers": 0
                }
            
            event_stats[event_id]["total_volunteers"] += 1
            if record["status"] in ["Attended", "Completed"]:
                event_stats[event_id]["attended_volunteers"] += 1
        
        # Generate reports
        reports = []
        for event in events_data.data:
            event_id = event["id"]
            stats = event_stats.get(event_id, {"total_volunteers": 0, "attended_volunteers": 0})
            
            completion_rate = (stats["attended_volunteers"] / stats["total_volunteers"] * 100) if stats["total_volunteers"] > 0 else 0
            
            reports.append(EventReport(
                event_id=event_id,
                event_name=event["name"],
                event_date=event["event_date"],
                location=event["location"],
                required_skills=event.get("required_skills", []),
                urgency=event.get("urgency", "low"),
                total_volunteers=stats["total_volunteers"],
                attended_volunteers=stats["attended_volunteers"],
                completion_rate=round(completion_rate, 2)
            ))
        
        return {"event_reports": reports}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/analytics")
async def get_analytics_dashboard(current_user: dict = Depends(verify_token)):
    """Get analytics dashboard data"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Get summary statistics
        total_volunteers = supabase.table("user_profiles").select("user_id").execute()
        total_events = supabase.table("events").select("id").execute()
        total_history = supabase.table("volunteer_history").select("id").execute()
        
        # Get recent activity (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        recent_activity = supabase.table("volunteer_history").select("*").gte("created_at", thirty_days_ago).execute()
        
        # Calculate engagement metrics
        engagement_stats = {}
        for record in recent_activity.data:
            month = record["created_at"][:7]  # YYYY-MM
            if month not in engagement_stats:
                engagement_stats[month] = {"signups": 0, "attendance": 0}
            
            engagement_stats[month]["signups"] += 1
            if record["status"] in ["Attended", "Completed"]:
                engagement_stats[month]["attendance"] += 1
        
        return {
            "summary": {
                "total_volunteers": len(total_volunteers.data),
                "total_events": len(total_events.data),
                "total_participations": len(total_history.data),
                "recent_activity_count": len(recent_activity.data)
            },
            "engagement_by_month": engagement_stats,
            "generated_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))