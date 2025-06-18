from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.supabase_client import supabase

router = APIRouter()

class Notification(BaseModel):
    user_id: str
    message: str
    is_read: Optional[bool] = False
    type: Optional[str] = "match"  
    event_id: Optional[str] = None

@router.post("/notifications")
async def send_notification(notification: Notification):
    try:
        response = supabase.table("notifications").insert(notification.dict()).execute()
        return {"message": "Notification sent", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notifications/{user_id}")
async def get_user_notifications(user_id: str):
    try:
        response = supabase.table("notifications") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .execute()
        return {"notifications": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/notifications/{notification_id}/read")
async def mark_notification_as_read(notification_id: str):
    try:
        response = supabase.table("notifications") \
            .update({"is_read": True}) \
            .eq("id", notification_id) \
            .execute()
        return {"message": "Notification marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/notifications/{notification_id}")
async def delete_notification(notification_id: str):
    try:
        response = supabase.table("notifications") \
            .delete() \
            .eq("id", notification_id) \
            .execute()
        return {"message": "Notification deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))