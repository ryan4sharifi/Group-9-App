from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from app.routes import events

app = FastAPI()
app.include_router(events.router)

# Sample event data
mock_event = {
    "name": "Beach Cleanup",
    "description": "Clean up the beach area",
    "location": "Miami Beach",
    "required_skills": ["teamwork", "physical stamina"],
    "urgency": "high",
    "event_date": "2025-08-01"
}

# Test creating an event
@patch("app.routes.events.get_supabase_client")
def test_create_event(mock_get_client):
    fake_supabase = MagicMock()
    mock_get_client.return_value = fake_supabase

    # Fake admin check
    fake_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {"role": "admin"}
    # Fake insert
    fake_supabase.table.return_value.insert.return_value.execute.return_value.data = {"id": "1", **mock_event}

    response = TestClient(app).post("/events", json=mock_event, params={"user_id": "admin123"})

    assert response.status_code == 200
    assert response.json()["message"] == "Event created"
    assert response.json()["data"]["name"] == "Beach Cleanup"

# Test getting all events
@patch("app.routes.events.get_supabase_client")
def test_get_all_events(mock_get_client):
    fake_supabase = MagicMock()
    mock_get_client.return_value = fake_supabase

    fake_supabase.table.return_value.select.return_value.order.return_value.execute.return_value.data = [mock_event]

    response = TestClient(app).get("/events")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Beach Cleanup"

# Test getting one event by ID
@patch("app.routes.events.get_supabase_client")
def test_get_event_by_id(mock_get_client):
    fake_supabase = MagicMock()
    mock_get_client.return_value = fake_supabase

    fake_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = mock_event

    response = TestClient(app).get("/events/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Beach Cleanup"

# Test updating an event
@patch("app.routes.events.get_supabase_client")
def test_update_event(mock_get_client):
    fake_supabase = MagicMock()
    mock_get_client.return_value = fake_supabase

    # Admin role
    fake_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {"role": "admin"}
    # Fake update
    fake_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = {"id": "1", **mock_event}

    response = TestClient(app).put("/events/1", json=mock_event, params={"user_id": "admin123"})

    assert response.status_code == 200
    assert response.json()["message"] == "Event updated"

# Test deleting an event
@patch("app.routes.events.get_supabase_client")
def test_delete_event(mock_get_client):
    fake_supabase = MagicMock()
    mock_get_client.return_value = fake_supabase

    # Step 1: Admin role
    fake_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.side_effect = [
        MagicMock(data={"role": "admin"}),  # Role check
        MagicMock(data={"name": "Beach Cleanup"})  # Event name
    ]
    # Step 2: Volunteer list
    fake_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {"user_id": "u1"},
        {"user_id": "u2"}
    ]
    # Step 3–5: Notifications and deletes = no error = pass

    response = TestClient(app).delete("/events/1", params={"user_id": "admin123"})

    assert response.status_code == 200
    assert response.json()["message"] == "Event deleted and users notified"
