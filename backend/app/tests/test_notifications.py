# backend/app/tests/test_notifications.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import MagicMock
from datetime import datetime

client = TestClient(app)

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

    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = mock_notifications

    response = client.get(f"/api/notifications/{user_id}")

    assert response.status_code == 200
    assert "notifications" in response.json()
    assert len(response.json()["notifications"]) == 2
    assert response.json()["notifications"][0]["user_id"] == user_id

def test_get_notifications_for_user_empty(mock_supabase_client: MagicMock):
    user_id = "user-no-notifications"

    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

    response = client.get(f"/api/notifications/{user_id}")

    assert response.status_code == 200
    assert "notifications" in response.json()
    assert len(response.json()["notifications"]) == 0

def test_mark_notification_as_read_success(mock_supabase_client: MagicMock):
    notification_id = "notif-to-read"
    user_id = "test-user" # Required for route logic, not direct mock

    # Mock select to find the notification first (needed by the route's logic)
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value.data = \
        get_mock_notification_data(id=notification_id, user_id=user_id, is_read=False)

    # Mock update operation
    mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = \
        [get_mock_notification_data(id=notification_id, user_id=user_id, is_read=True)]

    response = client.put(f"/api/notifications/{notification_id}/read")

    assert response.status_code == 200
    assert response.json()["message"] == "Notification marked as read."
    assert response.json()["data"][0]["is_read"] is True

def test_mark_notification_as_read_not_found(mock_supabase_client: MagicMock):
    notification_id = "nonexistent-notif"

    # Mock select to simulate notification not found
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value.data = None

    response = client.put(f"/api/notifications/{notification_id}/read")

    assert response.status_code == 404
    assert response.json()["detail"] == "Notification not found."

def test_delete_notification_success(mock_supabase_client: MagicMock):
    notification_id = "notif-to-delete"

    # Mock delete operation
    mock_supabase_client.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = \
        [{"id": notification_id}]

    response = client.delete(f"/api/notifications/{notification_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Notification deleted successfully."

def test_delete_notification_not_found(mock_supabase_client: MagicMock):
    notification_id = "nonexistent-notif-delete"

    # Mock delete to simulate not found
    mock_supabase_client.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = []

    response = client.delete(f"/api/notifications/{notification_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Notification not found."
