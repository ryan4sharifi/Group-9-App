import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from app.routes import history
from app.routes.history import VolunteerLog

app = FastAPI()
app.include_router(history.router)

# Test data
valid_volunteer_log = {
    "user_id": "user123",
    "event_id": "event456",
    "status": "Attended"
}

# Test: Log Volunteer Participation
@patch("app.routes.history.supabase")
def test_log_volunteer_participation_success(mock_supabase):
    """Test successful volunteer participation logging"""
    # Mock successful insertion
    mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{"id": "log123"}]
    
    client = TestClient(app)
    response = client.post("/history", json=valid_volunteer_log)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Participation logged"
    assert "data" in response.json()

@patch("app.routes.history.supabase")
def test_log_volunteer_participation_server_error(mock_supabase):
    """Test volunteer participation logging with server error"""
    # Mock server error
    mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("Database error")
    
    client = TestClient(app)
    response = client.post("/history", json=valid_volunteer_log)
    
    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]

def test_log_volunteer_participation_invalid_data():
    """Test volunteer participation logging with invalid data"""
    client = TestClient(app)
    
    # Test with missing required field
    invalid_data = {
        "user_id": "user123",
        "event_id": "event456"
        # Missing status
    }
    
    response = client.post("/history", json=invalid_data)
    assert response.status_code == 422

# Test: Get Volunteer History
@patch("app.routes.history.supabase")
def test_get_volunteer_history_success(mock_supabase):
    """Test successful retrieval of volunteer history"""
    # Mock history data with event details
    history_data = [
        {
            "id": "log1",
            "user_id": "user123",
            "event_id": "event456",
            "status": "Attended",
            "events": {
                "name": "Beach Cleanup",
                "location": "Miami Beach"
            }
        },
        {
            "id": "log2",
            "user_id": "user123",
            "event_id": "event789",
            "status": "Signed Up",
            "events": {
                "name": "Food Drive",
                "location": "Community Center"
            }
        }
    ]
    
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = history_data
    
    client = TestClient(app)
    response = client.get("/history/user123")
    
    assert response.status_code == 200
    assert len(response.json()["history"]) == 2
    assert response.json()["history"][0]["status"] == "Attended"
    assert response.json()["history"][0]["events"]["name"] == "Beach Cleanup"

@patch("app.routes.history.supabase")
def test_get_volunteer_history_empty(mock_supabase):
    """Test retrieval of volunteer history when none exists"""
    # Mock empty data
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    
    client = TestClient(app)
    response = client.get("/history/user123")
    
    assert response.status_code == 200
    assert response.json()["history"] == []

@patch("app.routes.history.supabase")
def test_get_volunteer_history_server_error(mock_supabase):
    """Test retrieval of volunteer history with server error"""
    # Mock server error
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("Database error")
    
    client = TestClient(app)
    response = client.get("/history/user123")
    
    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]

# Test: Update Volunteer Log
@patch("app.routes.history.supabase")
def test_update_volunteer_log_success(mock_supabase):
    """Test successful volunteer log update"""
    # Mock successful update
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": "log123"}]
    
    client = TestClient(app)
    response = client.put("/history/log123", json=valid_volunteer_log)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Participation log updated"
    assert "data" in response.json()

@patch("app.routes.history.supabase")
def test_update_volunteer_log_server_error(mock_supabase):
    """Test volunteer log update with server error"""
    # Mock server error
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception("Database error")
    
    client = TestClient(app)
    response = client.put("/history/log123", json=valid_volunteer_log)
    
    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]

def test_update_volunteer_log_invalid_data():
    """Test volunteer log update with invalid data"""
    client = TestClient(app)
    
    # Test with invalid status
    invalid_data = {
        "user_id": "user123",
        "event_id": "event456",
        "status": "InvalidStatus"
    }
    
    response = client.put("/history/log123", json=invalid_data)
    assert response.status_code == 422

# Test: Delete Volunteer Log
@patch("app.routes.history.supabase")
def test_delete_volunteer_log_success(mock_supabase):
    """Test successful volunteer log deletion"""
    # Mock successful deletion
    mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [{"id": "log123"}]
    
    client = TestClient(app)
    response = client.delete("/history/log123")
    
    assert response.status_code == 200
    assert response.json()["message"] == "Participation log deleted"

@patch("app.routes.history.supabase")
def test_delete_volunteer_log_server_error(mock_supabase):
    """Test volunteer log deletion with server error"""
    # Mock server error
    mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.side_effect = Exception("Database error")
    
    client = TestClient(app)
    response = client.delete("/history/log123")
    
    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]

# Test: Pydantic Model Validation
def test_volunteer_log_model_valid():
    """Test VolunteerLog model with valid data"""
    log = VolunteerLog(
        user_id="user123",
        event_id="event456",
        status="Attended"
    )
    
    assert log.user_id == "user123"
    assert log.event_id == "event456"
    assert log.status == "Attended"

def test_volunteer_log_model_missing_fields():
    """Test VolunteerLog model with missing fields"""
    with pytest.raises(ValueError):
        VolunteerLog(
            user_id="user123",
            event_id="event456"
            # Missing status
        )

def test_volunteer_log_model_empty_fields():
    """Test VolunteerLog model with empty fields"""
    with pytest.raises(ValueError):
        VolunteerLog(
            user_id="",
            event_id="event456",
            status="Attended"
        )

# Test: Edge Cases
def test_volunteer_log_different_statuses():
    """Test volunteer log with different status values"""
    statuses = ["Attended", "Signed Up", "Missed"]
    
    for status in statuses:
        log = VolunteerLog(
            user_id="user123",
            event_id="event456",
            status=status
        )
        assert log.status == status

def test_volunteer_log_long_ids():
    """Test volunteer log with long user and event IDs"""
    long_user_id = "user" + "1" * 50
    long_event_id = "event" + "1" * 50
    
    log = VolunteerLog(
        user_id=long_user_id,
        event_id=long_event_id,
        status="Attended"
    )
    
    assert log.user_id == long_user_id
    assert log.event_id == long_event_id

# Test: Integration Scenarios
@patch("app.routes.history.supabase")
def test_complete_volunteer_history_workflow(mock_supabase):
    """Test complete workflow: log, retrieve, update, delete"""
    # Step 1: Log participation
    mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{"id": "log123"}]
    
    client = TestClient(app)
    response = client.post("/history", json=valid_volunteer_log)
    assert response.status_code == 200
    
    # Step 2: Retrieve history
    history_data = [{"id": "log123", "user_id": "user123", "event_id": "event456", "status": "Attended", "events": {"name": "Test Event"}}]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = history_data
    
    response = client.get("/history/user123")
    assert response.status_code == 200
    assert len(response.json()["history"]) == 1
    
    # Step 3: Update log
    updated_log = valid_volunteer_log.copy()
    updated_log["status"] = "Missed"
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": "log123"}]
    
    response = client.put("/history/log123", json=updated_log)
    assert response.status_code == 200
    
    # Step 4: Delete log
    mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [{"id": "log123"}]
    
    response = client.delete("/history/log123")
    assert response.status_code == 200

# Test: Error Handling
@patch("app.routes.history.supabase")
def test_log_volunteer_participation_network_error(mock_supabase):
    """Test volunteer participation logging with network error"""
    # Mock network error
    mock_supabase.table.return_value.insert.return_value.execute.side_effect = ConnectionError("Network error")
    
    client = TestClient(app)
    response = client.post("/history", json=valid_volunteer_log)
    
    assert response.status_code == 500
    assert "Network error" in response.json()["detail"]

@patch("app.routes.history.supabase")
def test_get_volunteer_history_timeout_error(mock_supabase):
    """Test volunteer history retrieval with timeout error"""
    # Mock timeout error
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = TimeoutError("Query timeout")
    
    client = TestClient(app)
    response = client.get("/history/user123")
    
    assert response.status_code == 500
    assert "Query timeout" in response.json()["detail"] 