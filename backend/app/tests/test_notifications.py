# backend/app/tests/test_notifications.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routes.auth import create_access_token
from unittest.mock import MagicMock
from datetime import datetime

client = TestClient(app)

# Helper function to create authenticated headers
def get_auth_headers(user_id: str = "test-user", role: str = "volunteer"):
    """Create JWT token and return authorization headers"""
    token_data = {"sub": user_id, "role": role}
    token = create_access_token(token_data)
    return {"Authorization": f"Bearer {token}"}

# Helper mock data for notifications
def get_mock_notification_data(id="notif-id-1", user_id="user-id-1", is_read=False, message="Test notification message", event_id=None):
    return {
        "id": id,
        "user_id": user_id,
        "message": message,
        "created_at": datetime.now().isoformat(),
        "is_read": is_read,
        "event_id": event_id
    }

def test_get_notifications_for_user_success(mock_supabase_client: MagicMock):
    user_id = "user-with-notifications"
    mock_notifications = [get_mock_notification_data(user_id=user_id, is_read=False), get_mock_notification_data(id="notif-2", user_id=user_id, is_read=True)]

    # Fix mock chain to match the actual route: select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = mock_notifications

    headers = get_auth_headers(user_id=user_id)
    response = client.get(f"/api/notifications/{user_id}", headers=headers)

    assert response.status_code == 200
    assert "notifications" in response.json()
    assert len(response.json()["notifications"]) == 2
    assert response.json()["notifications"][0]["user_id"] == user_id

def test_get_notifications_for_user_empty(mock_supabase_client: MagicMock):
    user_id = "user-no-notifications"

    # Fix mock chain to match the actual route: select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = []

    headers = get_auth_headers(user_id=user_id)
    response = client.get(f"/api/notifications/{user_id}", headers=headers)

    assert response.status_code == 200
    assert "notifications" in response.json()
    assert len(response.json()["notifications"]) == 0

def test_mark_notification_as_read_success(mock_supabase_client: MagicMock):
    notification_id = "notif-to-read"
    user_id = "test-user" # Required for route logic, not direct mock

    # Fix mock chain to match actual route: select("user_id").eq("id", notification_id).execute()
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = \
        [get_mock_notification_data(id=notification_id, user_id=user_id, is_read=False)]

    # Mock update operation: update({"is_read": True}).eq("id", notification_id).execute()
    mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = \
        [get_mock_notification_data(id=notification_id, user_id=user_id, is_read=True)]

    headers = get_auth_headers(user_id=user_id)
    response = client.put(f"/api/notifications/{notification_id}/read", headers=headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Notification marked as read"

def test_mark_notification_as_read_not_found(mock_supabase_client: MagicMock):
    notification_id = "nonexistent-notif"

    # Fix mock chain to match actual route: select("user_id").eq("id", notification_id).execute()
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

    headers = get_auth_headers()
    response = client.put(f"/api/notifications/{notification_id}/read", headers=headers)

    assert response.status_code == 404
    response_json = response.json()
    # Flexible checking for error message - could be "detail" or other keys
    if "detail" in response_json:
        assert "not found" in response_json["detail"].lower()
    elif "message" in response_json:
        assert "not found" in response_json["message"].lower()
    else:
        assert False, f"Expected error message not found in response: {response_json}"

def test_delete_notification_success(mock_supabase_client: MagicMock):
    notification_id = "notif-to-delete"
    user_id = "test-user"

    # Mock the select operation to verify ownership: select("user_id").eq("id", notification_id).execute()
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = \
        [{"user_id": user_id}]

    # Mock delete operation: delete().eq("id", notification_id).execute()  
    mock_supabase_client.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = \
        [{"id": notification_id}]

    headers = get_auth_headers(user_id=user_id)
    response = client.delete(f"/api/notifications/{notification_id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Notification deleted"

def test_delete_notification_not_found(mock_supabase_client: MagicMock):
    notification_id = "nonexistent-notif-delete"

    # Mock select to simulate not found: select("user_id").eq("id", notification_id).execute()
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

    headers = get_auth_headers()
    response = client.delete(f"/api/notifications/{notification_id}", headers=headers)

    assert response.status_code == 404
    response_json = response.json()
    # Flexible checking for error message - could be "detail" or other keys
    if "detail" in response_json:
        assert "not found" in response_json["detail"].lower()
    elif "message" in response_json:
        assert "not found" in response_json["message"].lower() 
    else:
        assert False, f"Expected error message not found in response: {response_json}"
