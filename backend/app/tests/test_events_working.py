import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import MagicMock

client = TestClient(app)

def test_get_all_events(mock_supabase_client: MagicMock):
    """Test retrieving all events"""
    # Mock the events response
    mock_events = [
        {
            "id": "event-001",
            "name": "Beach Cleanup Drive", 
            "description": "Community beach cleanup",
            "location": "CA",
            "required_skills": ["cleaning"],
            "urgency": "High"
        }
    ]
    mock_supabase_client.table.return_value.select.return_value.order.return_value.execute.return_value.data = mock_events
    
    response = client.get("/api/events")
    assert response.status_code == 200
    data = response.json()
    print(f"DEBUG: Response data type: {type(data)}")
    print(f"DEBUG: Response data: {data}")
    assert isinstance(data, list)

def test_get_event_by_id():
    """Test retrieving a specific event"""
    # Get all events first to get a valid ID
    events_response = client.get("/api/events")
    events = events_response.json()
    
    if events:
        event_id = events[0]["id"]
        response = client.get(f"/api/events/{event_id}")
        assert response.status_code == 200
        event_data = response.json()
        assert event_data["id"] == event_id

def test_event_validation_required_fields():
    """Test event creation validation"""
    incomplete_event = {
        "name": "Test Event"
        # Missing required fields: description, location, required_skills, urgency, event_date
    }
    
    response = client.post("/api/events", json=incomplete_event, params={"user_id": "admin-001"})
    assert response.status_code == 422  # Validation error

def test_event_name_length_validation():
    """Test event name length validation (max 100 chars)"""
    long_name_event = {
        "name": "A" * 101,  # Too long
        "description": "Test description",
        "location": "TX",
        "required_skills": ["Testing"],
        "urgency": "Medium",
        "event_date": "2025-08-01"
    }
    
    response = client.post("/api/events", json=long_name_event, params={"user_id": "admin-001"})
    assert response.status_code == 422  # Validation error

def test_create_event_non_admin_forbidden():
    """Test that non-admin users cannot create events"""
    event_data = {
        "name": "Test Event",
        "description": "Test description", 
        "location": "TX",
        "required_skills": ["Testing"],
        "urgency": "Medium",
        "event_date": "2025-08-01"
    }
    
    # Use volunteer user ID
    response = client.post("/api/events", json=event_data, params={"user_id": "volunteer-001"})
    assert response.status_code == 403  # Forbidden
