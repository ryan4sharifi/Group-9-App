from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from app.routes import events

app = FastAPI()
app.include_router(events.router)

# Sample event
mock_event = {
    "name": "Beach Cleanup",
    "description": "Clean up the beach area",
    "location": "Miami Beach",
    "required_skills": ["teamwork", "physical stamina"],
    "urgency": "high",
    "event_date": "2025-08-01"
}

# Test: Create Event
@patch("app.routes.events.supabase")
def test_create_event(mock_supabase):
    # Pretend the user is admin
    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {"role": "admin"}
    # Pretend the event gets saved
    mock_supabase.table.return_value.insert.return_value.execute.return_value.data = {"id": "1", **mock_event}

    client = TestClient(app)
    response = client.post("/events", json=mock_event, params={"user_id": "admin123"})

    assert response.status_code == 200
    assert response.json()["message"] == "Event created"
    assert response.json()["data"]["name"] == "Beach Cleanup"

# Test: Get All Events
@patch("app.routes.events.supabase")
def test_get_all_events(mock_supabase):
    # Pretend one event exists
    mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value.data = [{"id": "1", **mock_event}]

    client = TestClient(app)
    response = client.get("/events")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Beach Cleanup"

# Test: Get Event by ID
@patch("app.routes.events.supabase")
def test_get_event_by_id(mock_supabase):
    # Pretend we found the event
    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {"id": "1", **mock_event}

    client = TestClient(app)
    response = client.get("/events/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Beach Cleanup"

# Test: Update Event
@patch("app.routes.events.supabase")
def test_update_event(mock_supabase):
    # Pretend the user is admin
    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {"role": "admin"}
    # Pretend the event gets updated
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = {"id": "1", **mock_event}

    client = TestClient(app)
    response = client.put("/events/1", json=mock_event, params={"user_id": "admin123"})

    assert response.status_code == 200
    assert response.json()["message"] == "Event updated"

# Test: Delete Event
@patch("app.routes.events.supabase")
def test_delete_event(mock_supabase):
    # Mock admin role and existing event
    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.side_effect = [
        MagicMock(data={"role": "admin"}),           # Check admin
        MagicMock(data={"id": "1", **mock_event})    # Get event details
    ]
    # Mock getting volunteers
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {"user_id": "u1"},
        {"user_id": "u2"}
    ]
    # You don’t need to mock deletes if the code doesn’t crash on them

    client = TestClient(app)
    response = client.delete("/events/1", params={"user_id": "admin123"})

    assert response.status_code == 200
    assert response.json()["message"] == "Event deleted and users notified"
