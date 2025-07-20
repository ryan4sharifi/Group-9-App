import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from app.routes import notifications
from app.routes.notifications import NotificationCreate, BulkNotification, send_email_notification
from app.routes.auth import create_access_token
from datetime import datetime

app = FastAPI()
app.include_router(notifications.router)

# Test data
valid_notification_data = {
    "user_id": "user123",
    "message": "You have been matched with an event!",
    "type": "match",
    "event_id": "event123",
    "send_email": False
}

valid_bulk_notification_data = {
    "user_ids": ["user1", "user2", "user3"],
    "message": "New event available!",
    "type": "general",
    "event_id": "event456",
    "send_email": False
}

# Test: Send Single Notification
@patch("app.routes.notifications.supabase")
def test_send_notification_success(mock_supabase):
    """Test successful notification sending"""
    # Mock successful notification insertion
    mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{"id": "notif123"}]
    
    # Create valid token
    token_data = {"sub": "admin123", "role": "admin"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.post("/notifications", json=valid_notification_data, headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert response.json()["message"] == "Notification sent successfully"

@patch("app.routes.notifications.supabase")
def test_send_notification_with_email(mock_supabase):
    """Test notification sending with email"""
    # Mock notification insertion
    mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{"id": "notif123"}]
    
    # Mock user profile with email
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"email": "test@example.com"}]
    
    # Create valid token
    token_data = {"sub": "admin123", "role": "admin"}
    token = create_access_token(token_data)
    
    notification_with_email = valid_notification_data.copy()
    notification_with_email["send_email"] = True
    
    client = TestClient(app)
    response = client.post("/notifications", json=notification_with_email, headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert response.json()["message"] == "Notification sent successfully"

@patch("app.routes.notifications.supabase")
def test_send_notification_server_error(mock_supabase):
    """Test notification sending with server error"""
    # Mock server error
    mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("Database error")
    
    # Create valid token
    token_data = {"sub": "admin123", "role": "admin"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.post("/notifications", json=valid_notification_data, headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]

# Test: Send Bulk Notifications
@patch("app.routes.notifications.supabase")
def test_send_bulk_notifications_success(mock_supabase):
    """Test successful bulk notification sending"""
    # Mock notification insertion
    mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{"id": "notif123"}]
    
    # Mock user profiles with emails
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {"email": "user1@example.com"},
        {"email": "user2@example.com"},
        {"email": "user3@example.com"}
    ]
    
    # Create valid admin token
    token_data = {"sub": "admin123", "role": "admin"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.post("/notifications/bulk", json=valid_bulk_notification_data, headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert "Bulk notifications sent" in response.json()["message"]
    assert response.json()["email_count"] == 3

@patch("app.routes.notifications.supabase")
def test_send_bulk_notifications_unauthorized(mock_supabase):
    """Test bulk notification sending without admin access"""
    # Create non-admin token
    token_data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.post("/notifications/bulk", json=valid_bulk_notification_data, headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 403
    assert "Admin access required" in response.json()["detail"]

@patch("app.routes.notifications.supabase")
def test_send_bulk_notifications_server_error(mock_supabase):
    """Test bulk notification sending with server error"""
    # Mock server error
    mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("Database error")
    
    # Create valid admin token
    token_data = {"sub": "admin123", "role": "admin"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.post("/notifications/bulk", json=valid_bulk_notification_data, headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]

# Test: Get User Notifications
@patch("app.routes.notifications.supabase")
def test_get_user_notifications_success(mock_supabase):
    """Test successful retrieval of user notifications"""
    # Mock notifications data
    notifications_data = [
        {"id": "notif1", "message": "Event reminder", "is_read": False},
        {"id": "notif2", "message": "Match notification", "is_read": True}
    ]
    
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = notifications_data
    
    # Create valid token for the same user
    token_data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.get("/notifications/user123", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert len(response.json()["notifications"]) == 2
    assert response.json()["notifications"][0]["message"] == "Event reminder"

@patch("app.routes.notifications.supabase")
def test_get_user_notifications_unauthorized(mock_supabase):
    """Test getting notifications for different user without admin access"""
    # Create token for different user
    token_data = {"sub": "user456", "role": "volunteer"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.get("/notifications/user123", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]

@patch("app.routes.notifications.supabase")
def test_get_user_notifications_admin_access(mock_supabase):
    """Test admin accessing any user's notifications"""
    # Mock notifications data
    notifications_data = [{"id": "notif1", "message": "Event reminder"}]
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = notifications_data
    
    # Create admin token
    token_data = {"sub": "admin123", "role": "admin"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.get("/notifications/user123", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert len(response.json()["notifications"]) == 1

# Test: Mark Notification as Read
@patch("app.routes.notifications.supabase")
def test_mark_notification_as_read_success(mock_supabase):
    """Test successful marking of notification as read"""
    # Mock notification exists and belongs to user
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"user_id": "user123"}]
    
    # Mock successful update
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": "notif123"}]
    
    # Create valid token for the same user
    token_data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.put("/notifications/notif123/read", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert response.json()["message"] == "Notification marked as read"

@patch("app.routes.notifications.supabase")
def test_mark_notification_as_read_not_found(mock_supabase):
    """Test marking non-existent notification as read"""
    # Mock notification not found
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    
    # Create valid token
    token_data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.put("/notifications/notif123/read", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 404
    assert "Notification not found" in response.json()["detail"]

@patch("app.routes.notifications.supabase")
def test_mark_notification_as_read_unauthorized(mock_supabase):
    """Test marking notification as read without authorization"""
    # Mock notification belongs to different user
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"user_id": "user456"}]
    
    # Create token for different user
    token_data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.put("/notifications/notif123/read", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]

# Test: Delete Notification
@patch("app.routes.notifications.supabase")
def test_delete_notification_success(mock_supabase):
    """Test successful notification deletion"""
    # Mock notification exists and belongs to user
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"user_id": "user123"}]
    
    # Mock successful deletion
    mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [{"id": "notif123"}]
    
    # Create valid token for the same user
    token_data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.delete("/notifications/notif123", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert response.json()["message"] == "Notification deleted"

@patch("app.routes.notifications.supabase")
def test_delete_notification_not_found(mock_supabase):
    """Test deleting non-existent notification"""
    # Mock notification not found
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    
    # Create valid token
    token_data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.delete("/notifications/notif123", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 404
    assert "Notification not found" in response.json()["detail"]

# Test: Get Unread Count
@patch("app.routes.notifications.supabase")
def test_get_unread_count_success(mock_supabase):
    """Test successful retrieval of unread count"""
    # Mock unread count
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [{"count": 5}]
    
    # Create valid token for the same user
    token_data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.get("/notifications/user123/unread-count", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert response.json()["unread_count"] == 5

# Test: Email Function
@patch("app.routes.notifications.smtplib.SMTP")
def test_send_email_notification_success(mock_smtp):
    """Test successful email sending"""
    # Mock SMTP server
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server
    
    result = send_email_notification("test@example.com", "Test Subject", "Test Message")
    
    assert result == True
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once()
    mock_server.send_message.assert_called_once()
    mock_server.quit.assert_called_once()

@patch("app.routes.notifications.smtplib.SMTP")
def test_send_email_notification_failure(mock_smtp):
    """Test email sending failure"""
    # Mock SMTP error
    mock_smtp.side_effect = Exception("SMTP error")
    
    result = send_email_notification("test@example.com", "Test Subject", "Test Message")
    
    assert result == False

def test_send_email_notification_no_credentials():
    """Test email sending without credentials"""
    # Temporarily remove credentials
    original_username = notifications.EMAIL_USERNAME
    original_password = notifications.EMAIL_PASSWORD
    
    try:
        notifications.EMAIL_USERNAME = None
        notifications.EMAIL_PASSWORD = None
        
        result = send_email_notification("test@example.com", "Test Subject", "Test Message")
        assert result == False
    finally:
        notifications.EMAIL_USERNAME = original_username
        notifications.EMAIL_PASSWORD = original_password

# Test: Pydantic Models
def test_notification_create_model():
    """Test NotificationCreate model validation"""
    notification = NotificationCreate(
        user_id="user123",
        message="Test notification",
        type="match",
        event_id="event123",
        send_email=False
    )
    
    assert notification.user_id == "user123"
    assert notification.message == "Test notification"
    assert notification.type == "match"
    assert notification.event_id == "event123"
    assert notification.send_email == False

def test_bulk_notification_model():
    """Test BulkNotification model validation"""
    bulk_notification = BulkNotification(
        user_ids=["user1", "user2"],
        message="Bulk test notification",
        type="general",
        event_id="event456",
        send_email=True
    )
    
    assert bulk_notification.user_ids == ["user1", "user2"]
    assert bulk_notification.message == "Bulk test notification"
    assert bulk_notification.type == "general"
    assert bulk_notification.event_id == "event456"
    assert bulk_notification.send_email == True

# Test: Edge Cases
def test_notification_with_default_values():
    """Test notification with default values"""
    notification = NotificationCreate(
        user_id="user123",
        message="Test notification"
    )
    
    assert notification.type == "general"
    assert notification.event_id is None
    assert notification.send_email == False

def test_bulk_notification_with_default_values():
    """Test bulk notification with default values"""
    bulk_notification = BulkNotification(
        user_ids=["user1"],
        message="Test bulk notification"
    )
    
    assert bulk_notification.type == "general"
    assert bulk_notification.event_id is None
    assert bulk_notification.send_email == False 