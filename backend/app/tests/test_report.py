# backend/app/tests/test_report.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import MagicMock
from datetime import date

client = TestClient(app)

# Helper mock data for reports
def get_mock_volunteer_history_item(id="vh1", user_id="u1", event_id="e1", status="Attended", has_profile=True, has_event=True):
    item = {
        "id": id,
        "status": status,
        "signed_up_at": "2025-07-30T17:54:53.279189",
        "user_id": user_id, # Include user_id from volunteer_history
        "event_id": event_id # Include event_id from volunteer_history
    }
    if has_profile:
        item["user_credentials"] = {
            "id": user_id,
            "email": f"user{user_id}@example.com",
            "user_profiles": {
                "full_name": f"Volunteer {user_id}"
            }
        }
    else:
        item["user_credentials"] = None # Or an empty object, depends on backend's exact None handling
    
    if has_event:
        item["events"] = {
            "id": event_id,
            "name": f"Event {event_id}",
            "location": "TX",
            "event_date": "2025-08-01"
        }
    else:
        item["events"] = None # Or an empty object

    return item

def get_mock_event_summary_item_data(event_id="e1", name="Event 1", date="2025-08-01", location="TX", volunteer_count=5):
    return {
        "event_id": event_id,
        "name": name,
        "date": date,
        "location": location,
        "volunteer_count": volunteer_count
    }

def test_volunteer_participation_report_success(mock_supabase_client: MagicMock):
    # Mock data to ensure 3 items are returned and have expected nested structure
    mock_report_data = [
        get_mock_volunteer_history_item("vh1", "u1", "e1"),
        get_mock_volunteer_history_item("vh2", "u2", "e1", "Signed Up"),
        get_mock_volunteer_history_item("vh3", "u1", "e2", "Missed")
    ]

    # Mock the main select call for the report
    mock_supabase_client.table.return_value.select.return_value.execute.return_value.data = mock_report_data

    response = client.get("/api/reports/volunteers")

    assert response.status_code == 200
    assert "report" in response.json()
    assert len(response.json()["report"]) == 3 # Assert 3 items
    assert response.json()["report"][0]["user_credentials"]["user_profiles"]["full_name"] == "Volunteer u1"
    assert response.json()["report"][0]["events"]["name"] == "Event e1"

def test_event_participation_summary_success(mock_supabase_client: MagicMock):
    # Mock history for the event count part
    # 2 for e1, 1 for e2
    mock_history_for_count = [
        {"event_id": "e1"}, {"event_id": "e1"}, {"event_id": "e2"}
    ]
    # Mock events data
    mock_events_data = [
        {"id": "e1", "name": "Event One", "event_date": "2025-09-01", "location": "CA"},
        {"id": "e2", "name": "Event Two", "event_date": "2025-09-02", "location": "NY"}
    ]

    # Use side_effect for sequential select calls in the backend route
    mock_supabase_client.table.return_value.select.side_effect = [
        # First call: select("event_id") for history
        MagicMock(return_value=MagicMock(execute=MagicMock(return_value=MagicMock(data=mock_history_for_count)))),
        # Second call: select("*") for events
        MagicMock(return_value=MagicMock(execute=MagicMock(return_value=MagicMock(data=mock_events_data))))
    ]

    response = client.get("/api/reports/events")

    assert response.status_code == 200
    assert "event_summary" in response.json()
    assert len(response.json()["event_summary"]) == 2 # Assert 2 events in summary
    assert response.json()["event_summary"][0]["name"] == "Event One"
    assert response.json()["event_summary"][0]["volunteer_count"] == 2 # Correct count for e1
    assert response.json()["event_summary"][1]["name"] == "Event Two"
    assert response.json()["event_summary"][1]["volunteer_count"] == 1 # Correct count for e2
