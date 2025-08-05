# backend/app/tests/test_history.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import MagicMock
from datetime import datetime

client = TestClient(app)

def get_mock_history_item(id="hist-id-1", user_id="user-id-1", event_id="event-id-1", status="Signed Up"):
    return {
        "id": id,
        "user_id": user_id,
        "event_id": event_id,
        "status": status,
        "signed_up_at": datetime.now().isoformat()
    }

def test_create_history_success(mock_supabase_client: MagicMock):
    user_id = "test-user-1-uuid"
    event_id = "test-event-1-uuid"
    status = "Signed Up"

    mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = \
        [{"id": "new-history-id", "user_id": user_id, "event_id": event_id, "status": status}]

    response = client.post("/api/history", json={"user_id": user_id, "event_id": event_id, "status": status})

    assert response.status_code == 200
    assert response.json()["message"] == "Volunteer history created successfully."
    assert "id" in response.json()["data"][0]  # data is a list, check first item

def test_create_history_invalid_data(mock_supabase_client: MagicMock):
    # Missing required 'event_id'
    invalid_data = {"user_id": "test-user-1", "status": "Signed Up"}

    response = client.post("/api/history", json=invalid_data)

    assert response.status_code == 422
    assert "detail" in response.json()
    assert any("event_id" in err["loc"] for err in response.json()["detail"])

def test_get_user_history_success(mock_supabase_client: MagicMock):
    user_id = "user-with-history-uuid"
    mock_history = [get_mock_history_item(user_id=user_id), get_mock_history_item(id="hist-2-uuid", user_id=user_id)]
    
    # Mock for history select (main query)
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = mock_history

    response = client.get(f"/api/history/{user_id}")

    assert response.status_code == 200
    assert "history" in response.json()
    assert len(response.json()["history"]) == 2
    assert response.json()["history"][0]["user_id"] == user_id

def test_get_user_history_empty(mock_supabase_client: MagicMock):
    user_id = "user-no-history-uuid"
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

    response = client.get(f"/api/history/{user_id}")

    assert response.status_code == 200
    assert "history" in response.json()
    assert len(response.json()["history"]) == 0

def test_update_history_status(mock_supabase_client: MagicMock):
    log_id = "log-to-update-uuid"
    new_status = "Attended"
    user_id = "test-user-id-uuid"
    event_id = "test-event-id-uuid"

    mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = \
        [{"id": log_id, "status": new_status}]

    response = client.put(f"/api/history/{log_id}", json={"user_id": user_id, "event_id": event_id, "status": new_status})

    assert response.status_code == 200
    assert response.json()["message"] == "Volunteer history updated successfully."
    assert response.json()["data"][0]["status"] == new_status

def test_update_history_not_found(mock_supabase_client: MagicMock):
    log_id = "nonexistent-log-uuid"
    new_status = "Attended"
    user_id = "test-user-id-uuid"
    event_id = "test-event-id-uuid"

    mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = []

    response = client.put(f"/api/history/{log_id}", json={"user_id": user_id, "event_id": event_id, "status": new_status})

    assert response.status_code == 404
    response_json = response.json()
    # Flexible checking for error message - could be "detail" or other keys
    if "detail" in response_json:
        assert "not found" in response_json["detail"].lower()
    elif "message" in response_json:
        assert "not found" in response_json["message"].lower()
    else:
        assert False, f"Expected error message not found in response: {response_json}"

def test_delete_history_entry(mock_supabase_client: MagicMock):
    log_id = "log-to-delete-uuid"

    mock_supabase_client.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = \
        [{"id": log_id}]

    response = client.delete(f"/api/history/{log_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Volunteer history deleted successfully."

def test_delete_history_not_found(mock_supabase_client: MagicMock):
    log_id = "nonexistent-log-uuid"

    mock_supabase_client.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = []

    response = client.delete(f"/api/history/{log_id}")

    assert response.status_code == 404
    response_json = response.json()
    # Flexible checking for error message - could be "detail" or other keys  
    if "detail" in response_json:
        assert "not found" in response_json["detail"].lower()
    elif "message" in response_json:
        assert "not found" in response_json["message"].lower()
    else:
        assert False, f"Expected error message not found in response: {response_json}"
