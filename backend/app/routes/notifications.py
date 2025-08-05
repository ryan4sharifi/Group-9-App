# Notification Routes – Create, fetch, update, and delete user notifications

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.supabase_client import supabase
from app.routes.auth import verify_token
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter()

# Email configuration
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@volunteerapp.com")

# Notification schema for input validation
class Notification(BaseModel):
    user_id: str
    message: str
    type: Optional[str] = "match"    # Optional type (e.g., match, reminder)
    event_id: Optional[str] = None   # Can link to an event if needed

class NotificationCreate(BaseModel):
    user_id: str
    message: str
    type: str = "general"  # match, reminder, update, general
    event_id: Optional[str] = None
    send_email: bool = False

class BulkNotification(BaseModel):
    user_ids: List[str]
    message: str
    type: str = "general"
    event_id: Optional[str] = None
    send_email: bool = False

def send_email_notification(to_email: str, subject: str, message: str):
    """Send email notification using SMTP"""
    try:
        if not EMAIL_USERNAME or not EMAIL_PASSWORD:
            print("Email credentials not configured")
            return False
        
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        
        body = f"""
        <html>
        <body>
            <h2>Volunteer Management System</h2>
            <p>{message}</p>
            <hr>
            <p><small>This is an automated message from the Volunteer Management System.</small></p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

# Send a new notification to a user
@router.post("/notifications")
async def send_notification(
    notification: NotificationCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(verify_token)
):
    """Send notification to a user"""
    try:
        # Insert notification into database
        response = supabase.table("notifications").insert({
            "user_id": notification.user_id,
            "message": notification.message,
            "type": notification.type,
            "event_id": notification.event_id,
            "is_read": False,
            "created_at": datetime.now().isoformat()
        }).execute()
        
        # Send email if requested
        if notification.send_email:
            # Get user email
            user_profile = supabase.table("user_profiles").select("email").eq("user_id", notification.user_id).execute()
            if user_profile.data:
                email = user_profile.data[0].get("email")
                if email:
                    subject = f"Volunteer Notification - {notification.type.title()}"
                    background_tasks.add_task(send_email_notification, email, subject, notification.message)
        
        return {"message": "Notification sent successfully", "data": response.data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notifications/bulk")
async def send_bulk_notifications(
    bulk_notification: BulkNotification,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(verify_token)
):
    """Send notifications to multiple users - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        notifications_data = []
        emails_to_send = []
        
        for user_id in bulk_notification.user_ids:
            # Prepare notification data
            notifications_data.append({
                "user_id": user_id,
                "message": bulk_notification.message,
                "type": bulk_notification.type,
                "event_id": bulk_notification.event_id,
                "is_read": False,
                "created_at": datetime.now().isoformat()
            })
            
            # Prepare email data if needed
            if bulk_notification.send_email:
                user_profile = supabase.table("user_profiles").select("email").eq("user_id", user_id).execute()
                if user_profile.data:
                    email = user_profile.data[0].get("email")
                    if email:
                        emails_to_send.append({
                            "email": email,
                            "subject": f"Volunteer Notification - {bulk_notification.type.title()}",
                            "message": bulk_notification.message
                        })
        
        # Insert all notifications
        response = supabase.table("notifications").insert(notifications_data).execute()
        
        # Send emails in background
        for email_data in emails_to_send:
            background_tasks.add_task(
                send_email_notification,
                email_data["email"],
                email_data["subject"],
                email_data["message"]
            )
        
        return {
            "message": f"Bulk notifications sent to {len(bulk_notification.user_ids)} users",
            "email_count": len(emails_to_send)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Fetch all notifications for a specific user
@router.get("/notifications/{user_id}")
async def get_user_notifications(
    user_id: str,
    current_user: dict = Depends(verify_token)
):
    """Get notifications for a user"""
    # Verify authorization
    if current_user["user_id"] != user_id and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        response = supabase.table("notifications") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .execute()
        
        return {"notifications": response.data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mark a single notification as read
@router.put("/notifications/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    current_user: dict = Depends(verify_token)
):
    """Mark notification as read"""
    try:
        # Verify user owns this notification
        notification = supabase.table("notifications").select("user_id").eq("id", notification_id).execute()
        if not notification.data:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        if notification.data[0]["user_id"] != current_user["user_id"] and current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Update notification
        response = supabase.table("notifications") \
            .update({"is_read": True}) \
            .eq("id", notification_id) \
            .execute()
        
        return {"message": "Notification marked as read"}
    
    except HTTPException:
        raise  # Re-raise HTTPException to preserve status code
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete a specific notification
@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: dict = Depends(verify_token)
):
    """Delete a notification"""
    try:
        # Verify user owns this notification
        notification = supabase.table("notifications").select("user_id").eq("id", notification_id).execute()
        if not notification.data:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        if notification.data[0]["user_id"] != current_user["user_id"] and current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Delete notification
        response = supabase.table("notifications") \
            .delete() \
            .eq("id", notification_id) \
            .execute()
        
        return {"message": "Notification deleted"}
    
    except HTTPException:
        raise  # Re-raise HTTPException to preserve status code
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notifications/{user_id}/unread-count")
async def get_unread_count(
    user_id: str,
    current_user: dict = Depends(verify_token)
):
    """Get unread notification count for a user"""
    if current_user["user_id"] != user_id and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        response = supabase.table("notifications") \
            .select("id") \
            .eq("user_id", user_id) \
            .eq("is_read", False) \
            .execute()
        
        return {"unread_count": len(response.data)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))