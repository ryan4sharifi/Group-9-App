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
    assert "id" in response.json()["data"][0]  # Access first item in the list

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
    # Create mock events with specific names including "Beach Cleanup Drive"
    mock_events = [
        get_mock_event_data("e1", "Beach Cleanup Drive"),
        get_mock_event_data("e2", "Community Cleanup"), 
        get_mock_event_data("e3", "Park Maintenance")
    ]
    mock_supabase_client.table.return_value.select.return_value.order.return_value.execute.return_value.data = mock_events

    response = client.get("/api/events/")

    assert response.status_code == 200
    assert len(response.json()) >= 1  # At least one event from mock database
    # Check that our mock events are returned correctly
    assert "Beach Cleanup Drive" in [event["name"] for event in response.json()]

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
    # Check both possible response formats
    response_json = response.json()
    if "detail" in response_json:
        assert "not found" in response_json["detail"].lower()
    elif "message" in response_json:
        assert "not found" in response_json["message"].lower()

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
    response_json = response.json()
    # Flexible checking for error message - could be "detail" or other keys
    if "detail" in response_json:
        assert "not found" in response_json["detail"].lower()
    elif "message" in response_json:
        assert "not found" in response_json["message"].lower()
    else:
        assert False, f"Expected error message not found in response: {response_json}"

def test_delete_event_success(mock_supabase_client: MagicMock, mock_uuid: str):
    event_id = "event-to-delete-id-uuid"
    mock_user_id = mock_uuid

    # Setup multiple mock responses for the delete sequence
    mock_responses = []
    
    # 1. Admin verification: select("role").eq("id", user_id).single().execute()
    admin_response = MagicMock()
    admin_response.data = {"role": "admin"}
    mock_responses.append(admin_response)
    
    # 2. Get event name: select("name").eq("id", event_id).single().execute()
    event_name_response = MagicMock()
    event_name_response.data = {"name": "Test Event to Delete"}
    mock_responses.append(event_name_response)
    
    # 3. Get volunteer signups: select("user_id").eq("event_id", event_id).execute()
    signups_response = MagicMock()
    signups_response.data = [{"user_id": "vol1"}, {"user_id": "vol2"}]
    mock_responses.append(signups_response)
    
    # 4. Notification inserts - return success (may be called multiple times)
    notif_response = MagicMock()
    notif_response.data = [{"id": "notif1"}]
    
    # 5. Volunteer history delete
    history_delete_response = MagicMock()
    history_delete_response.data = []
    
    # 6. Final event delete
    event_delete_response = MagicMock()
    event_delete_response.data = [{"id": event_id}]
    
    # Setup the execute mock to return different responses in sequence
    execute_mock = MagicMock()
    execute_mock.side_effect = mock_responses + [notif_response] * 10 + [history_delete_response, event_delete_response]
    
    # Setup the full chain for all the different call patterns
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute = execute_mock
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute = execute_mock
    mock_supabase_client.table.return_value.insert.return_value.execute = execute_mock
    mock_supabase_client.table.return_value.delete.return_value.eq.return_value.execute = execute_mock

    response = client.delete(f"/api/events/{event_id}", params={"user_id": mock_user_id})

    assert response.status_code == 200
    assert response.json()["message"] == "Event deleted and users notified"

def test_delete_event_not_found(mock_supabase_client: MagicMock, mock_uuid: str):
    event_id = "nonexistent-event-id-uuid"
    mock_user_id = mock_uuid

    # Setup multiple mock responses for the delete sequence
    mock_responses = []
    
    # 1. Admin verification: select("role").eq("id", user_id).single().execute()
    admin_response = MagicMock()
    admin_response.data = {"role": "admin"}
    mock_responses.append(admin_response)
    
    # 2. Get event name: select("name").eq("id", event_id).single().execute()
    # This should return None for nonexistent event
    event_name_response = MagicMock()
    event_name_response.data = None  # Event not found
    mock_responses.append(event_name_response)
    
    # Setup the execute mock to return different responses in sequence
    execute_mock = MagicMock()
    execute_mock.side_effect = mock_responses
    
    # Setup the full chain for all the different call patterns
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute = execute_mock

    response = client.delete(f"/api/events/{event_id}", params={"user_id": mock_user_id})

    assert response.status_code == 404
    # Use flexible error checking pattern like other tests
    response_json = response.json()
    if "detail" in response_json:
        assert "Event not found" in response_json["detail"]
    elif "message" in response_json:
        assert "not found" in response_json["message"].lower()
    else:
        assert False, f"Expected error message not found in response: {response_json}"
