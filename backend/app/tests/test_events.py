# backend/app/tests/test_events.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import MagicMock
from datetime import date

client = TestClient(app)

def get_mock_event_data(id="event-id-123", name="Community Cleanup", description="Help clean up local park.", location="CA", required_skills=None, urgency="Medium", event_date=None):
    return {
        "id": id,
        "name": name,
        "description": description,
        "location": location,
        "required_skills": required_skills if required_skills is not None else ["sweeping", "lifting"],
        "urgency": urgency,
        "event_date": event_date if event_date is not None else str(date.today())
    }

# --- Helper for Admin Verification (to be mocked for verify_admin) ---
def mock_verify_admin_success(mock_supabase_client: MagicMock, user_id: str):
    # This mocks the .single().execute() call inside verify_admin()
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = \
        {"role": "admin"}

def mock_verify_admin_fail(mock_supabase_client: MagicMock, user_id: str):
    # This mocks the .single().execute() call inside verify_admin() for non-admin
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = \
        {"role": "volunteer"} # Or None if the user isn't found at all

def test_create_event_success(mock_supabase_client: MagicMock, mock_uuid: str):
    event_data = {
        "name": "New Event", "description": "Desc", "location": "NY",
        "required_skills": ["org"], "urgency": "Low", "event_date": "2025-09-01"
    }
    mock_user_id = mock_uuid # Use valid UUID format for user_id

    mock_verify_admin_success(mock_supabase_client, mock_user_id) # Mock admin verification

    mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = \
        [{"id": "new-event-uuid", **event_data}]

    response = client.post("/api/events/", params={"user_id": mock_user_id}, json=event_data)

    assert response.status_code == 200
    assert response.json()["message"] == "Event created successfully"
    assert "id" in response.json()["data"]

def test_create_event_invalid_data(mock_supabase_client: MagicMock, mock_uuid: str):
    # Missing required 'name' field
    invalid_event_data = {"description": "Desc", "location": "NY", "required_skills": [], "urgency": "Low", "event_date": "2025-09-01"}
    mock_user_id = mock_uuid # Use valid UUID format

    mock_verify_admin_success(mock_supabase_client, mock_user_id) # Mock admin verification

    response = client.post("/api/events/", params={"user_id": mock_user_id}, json=invalid_event_data)

    assert response.status_code == 422
    assert "detail" in response.json()
    assert any("name" in err["loc"] for err in response.json()["detail"])

def test_get_all_events_success(mock_supabase_client: MagicMock):
    mock_events = [get_mock_event_data("e1"), get_mock_event_data("e2"), get_mock_event_data("e3")]
    mock_supabase_client.table.return_value.select.return_value.execute.return_value.data = mock_events

    response = client.get("/api/events/")

    assert response.status_code == 200
    assert len(response.json()) == 3
    assert response.json()[0]["name"] == "Community Cleanup" # Assuming this is from get_mock_event_data("e1")

def test_get_event_by_id_success(mock_supabase_client: MagicMock):
    event_id = "specific-event-id-uuid"
    mock_event = get_mock_event_data(event_id)
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value.data = mock_event

    response = client.get(f"/api/events/{event_id}")

    assert response.status_code == 200
    assert response.json()["id"] == event_id
    assert response.json()["name"] == "Community Cleanup"

def test_get_event_by_id_not_found(mock_supabase_client: MagicMock):
    event_id = "nonexistent-event-id-uuid"
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value.data = None

    response = client.get(f"/api/events/{event_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"

def test_update_event_success(mock_supabase_client: MagicMock, mock_uuid: str):
    event_id = "event-to-update-id-uuid"
    updated_data = {"name": "Updated Event Name", "description": "New description.", "location": "NY", "required_skills": ["react"], "urgency": "High", "event_date": "2025-10-01"}
    mock_user_id = mock_uuid

    mock_verify_admin_success(mock_supabase_client, mock_user_id) # Mock admin verification

    mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = \
        [{"id": event_id, **updated_data}]

    response = client.put(f"/api/events/{event_id}", params={"user_id": mock_user_id}, json=updated_data)

    assert response.status_code == 200
    assert response.json()["message"] == "Event updated successfully"
    assert response.json()["data"][0]["name"] == "Updated Event Name"

def test_update_event_not_found(mock_supabase_client: MagicMock, mock_uuid: str):
    event_id = "nonexistent-event-id-uuid"
    updated_data = {"name": "Nonexistent", "description": "Desc", "location": "NY", "required_skills": [], "urgency": "Low", "event_date": "2025-01-01"}
    mock_user_id = mock_uuid

    mock_verify_admin_success(mock_supabase_client, mock_user_id) # Mock admin verification

    mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = []

    response = client.put(f"/api/events/{event_id}", params={"user_id": mock_user_id}, json=updated_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found."

def test_delete_event_success(mock_supabase_client: MagicMock, mock_uuid: str):
    event_id = "event-to-delete-id-uuid"
    mock_user_id = mock_uuid

    mock_verify_admin_success(mock_supabase_client, mock_user_id) # Mock admin verification

    mock_supabase_client.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = \
        [{"id": event_id}]

    response = client.delete(f"/api/events/{event_id}", params={"user_id": mock_user_id})

    assert response.status_code == 200
    assert response.json()["message"] == "Event deleted successfully."

def test_delete_event_not_found(mock_supabase_client: MagicMock, mock_uuid: str):
    event_id = "nonexistent-event-id-uuid"
    mock_user_id = mock_uuid

    mock_verify_admin_success(mock_supabase_client, mock_user_id) # Mock admin verification

    mock_supabase_client.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = []

    response = client.delete(f"/api/events/{event_id}", params={"user_id": mock_user_id})

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found."
