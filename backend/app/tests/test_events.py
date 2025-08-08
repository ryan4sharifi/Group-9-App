import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_event_data():
    """Sample event data for testing"""
    return {
        "name": "Community Cleanup",
        "description": "Help clean up local park", 
        "address1": "123 Main St",
        "address2": "Suite 100",
        "city": "Houston",
        "state": "TX",
        "zip_code": "77001",
        "required_skills": ["cleaning", "organizing"],
        "urgency": "Medium",
        "event_date": "2024-12-31"
    }

@pytest.fixture
def mock_event_response():
    """Mock event response with ID"""
    return {
        "id": "event-123",
        "name": "Community Cleanup",
        "description": "Help clean up local park", 
        "address1": "123 Main St",
        "address2": "Suite 100",
        "city": "Houston",
        "state": "TX",
        "zip_code": "77001",
        "required_skills": ["cleaning", "organizing"],
        "urgency": "Medium",
        "event_date": "2024-12-31"
    }

@patch('app.routes.events.supabase')
def test_create_event_success(mock_supabase, mock_event_data):
    """Test creating an event successfully"""
    # Mock supabase response
    mock_response = MagicMock()
    mock_response.data = [{"id": "event-123", **mock_event_data}]
    mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
    
    response = client.post("/api/events?user_id=user123", json=mock_event_data)
    assert response.status_code == 200
    assert "Event created" in response.json()["message"]
    assert "data" in response.json()

@patch('app.routes.events.supabase')
def test_create_event_invalid_data(mock_supabase):
    """Test creating event with invalid data"""
    invalid_data = {
        "description": "Missing name field",
        "address1": "123 Main St",
        "city": "Houston",
        "state": "TX",
        "required_skills": ["cleaning"],
        "urgency": "Medium",
        "event_date": "2024-12-31"
    }
    
    response = client.post("/api/events?user_id=user123", json=invalid_data)
    assert response.status_code == 422

@patch('app.routes.events.supabase')
def test_create_event_database_error(mock_supabase, mock_event_data):
    """Test creating event with database error"""
    mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("Database error")
    
    response = client.post("/api/events?user_id=user123", json=mock_event_data)
    assert response.status_code == 500

@patch('app.routes.events.supabase')
def test_get_all_events_success(mock_supabase, mock_event_response):
    """Test getting all events"""
    mock_response = MagicMock()
    mock_response.data = [mock_event_response]
    mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response
    
    response = client.get("/api/events")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Community Cleanup"

@patch('app.routes.events.supabase')
def test_get_all_events_error(mock_supabase):
    """Test getting all events with database error"""
    mock_supabase.table.return_value.select.return_value.order.return_value.execute.side_effect = Exception("Database error")
    
    response = client.get("/api/events")
    assert response.status_code == 500

@patch('app.routes.events.supabase')
def test_get_event_by_id_success(mock_supabase, mock_event_response):
    """Test getting event by ID"""
    mock_response = MagicMock()
    mock_response.data = mock_event_response
    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
    
    response = client.get("/api/events/event-123")
    assert response.status_code == 200
    assert response.json()["id"] == "event-123"
    assert response.json()["name"] == "Community Cleanup"

@patch('app.routes.events.supabase')
def test_get_event_by_id_not_found(mock_supabase):
    """Test getting non-existent event"""
    # Mock supabase to throw an exception like it would for invalid UUID
    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.side_effect = Exception("invalid input syntax for type uuid")
    
    response = client.get("/api/events/nonexistent")
    assert response.status_code == 500  # Will be 500 due to invalid UUID

@patch('app.routes.events.supabase')
def test_get_event_by_id_database_error(mock_supabase):
    """Test getting event with database error"""
    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.side_effect = Exception("Database error")
    
    response = client.get("/api/events/event-123")
    assert response.status_code == 500

@patch('app.routes.events.supabase')
def test_update_event_success(mock_supabase, mock_event_data):
    """Test updating an event"""
    mock_response = MagicMock()
    mock_response.data = [{"id": "event-123", **mock_event_data}]
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
    
    response = client.put("/api/events/event-123?user_id=user123", json=mock_event_data)
    assert response.status_code == 200
    assert "Event updated" in response.json()["message"]

@patch('app.routes.events.supabase')
def test_update_event_database_error(mock_supabase, mock_event_data):
    """Test updating event with database error"""
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception("Database error")
    
    response = client.put("/api/events/event-123?user_id=user123", json=mock_event_data)
    assert response.status_code == 500

@patch('app.routes.events.supabase')
def test_delete_event_success(mock_supabase):
    """Test deleting an event"""
    # Mock getting event name
    event_response = MagicMock()
    event_response.data = {"name": "Test Event"}
    
    # Mock getting volunteer history
    history_response = MagicMock()
    history_response.data = [{"user_id": "user1"}, {"user_id": "user2"}]
    
    # Mock notification and delete operations
    notif_response = MagicMock()
    notif_response.data = [{"id": "notif1"}]
    
    delete_response = MagicMock()
    delete_response.data = []
    
    # Set up the mock chain
    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = event_response
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = history_response
    mock_supabase.table.return_value.insert.return_value.execute.return_value = notif_response
    mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = delete_response
    
    response = client.delete("/api/events/event-123?user_id=user123")
    assert response.status_code == 200
    assert "Event deleted and users notified" in response.json()["message"]

@patch('app.routes.events.supabase')
def test_delete_event_not_found(mock_supabase):
    """Test deleting non-existent event"""
    # Mock event not found - throw exception for invalid UUID
    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.side_effect = Exception("invalid input syntax for type uuid")
    
    response = client.delete("/api/events/nonexistent?user_id=user123")
    assert response.status_code == 500  # Will be 500 due to invalid UUID

@patch('app.routes.events.supabase')
def test_delete_event_database_error(mock_supabase):
    """Test deleting event with database error"""
    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.side_effect = Exception("Database error")
    
    response = client.delete("/api/events/event-123?user_id=user123")
    assert response.status_code == 500

def test_event_model_validation():
    """Test Event model validation"""
    from app.routes.events import Event
    
    # Valid event
    event_data = {
        "name": "Test Event",
        "description": "Test description",
        "address1": "123 Main St",
        "city": "Houston",
        "state": "TX",
        "required_skills": ["skill1"],
        "urgency": "Medium",
        "event_date": "2024-12-31"
    }
    
    event = Event(**event_data)
    assert event.name == "Test Event"
    assert event.city == "Houston"
    
    # Test name length validation (max 100 chars)
    with pytest.raises(ValueError):
        long_name_data = event_data.copy()
        long_name_data["name"] = "a" * 101  # Too long
        Event(**long_name_data)

def test_event_optional_fields():
    """Test Event model with optional fields"""
    from app.routes.events import Event
    
    # Event without optional fields
    event_data = {
        "name": "Test Event",
        "description": "Test description",
        "address1": "123 Main St",
        "city": "Houston",
        "state": "TX",
        "required_skills": ["skill1"],
        "urgency": "Medium",
        "event_date": "2024-12-31"
    }
    
    event = Event(**event_data)
    assert event.address2 is None
    assert event.zip_code is None
    
    # Event with optional fields
    event_data_with_optional = event_data.copy()
    event_data_with_optional.update({
        "address2": "Suite 100",
        "zip_code": "77001"
    })
    
    event_with_optional = Event(**event_data_with_optional)
    assert event_with_optional.address2 == "Suite 100"
    assert event_with_optional.zip_code == "77001"
