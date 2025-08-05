# backend/app/tests/test_match.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routes.auth import create_access_token
from unittest.mock import MagicMock
from datetime import date

client = TestClient(app)

# Helper function to create authenticated headers
def get_auth_headers(user_id: str = "test-user", role: str = "volunteer"):
    """Create JWT token and return authorization headers"""
    token_data = {"sub": user_id, "role": role}
    token = create_access_token(token_data)
    return {"Authorization": f"Bearer {token}"}

# Helper mock data for user profile and events
def get_mock_user_profile_data(user_id="user-match-1-uuid", skills=None):
    return {
        "id": "mock-profile-id-uuid", # Profile has its own ID
        "user_id": user_id, # Ensure user_id is passed for linking
        "skills": skills if skills is not None else ["coding", "design"],
        "full_name": "Test User"
    }

def get_mock_event_data(event_id="event-match-1-uuid", name="Mock Event", required_skills=None, urgency="Medium"):
    return {
        "id": event_id,
        "name": name,
        "description": "Mock description.",
        "location": "CA",
        "required_skills": required_skills if required_skills is not None else ["coding"],
        "urgency": urgency,
        "event_date": str(date.today())
    }

# --- Tests for get_matched_events endpoint ---

def test_get_matched_events_success(mock_supabase_client: MagicMock):
    user_id = "user-with-matching-skills-uuid"
    
    # Mock sequence of `execute()` calls for fetch_user_skills and fetch_all_events
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
        # 1. For fetch_user_skills
        MagicMock(data=[get_mock_user_profile_data(user_id=user_id, skills=["coding", "leadership"])])
    ]
    # Mock `execute()` for fetch_all_events (no `eq` before it)
    mock_supabase_client.table.return_value.select.return_value.execute.return_value.data = [
        get_mock_event_data("event1-uuid", required_skills=["coding", "python"]),
        get_mock_event_data("event2-uuid", required_skills=["design", "ui/ux"]),
        get_mock_event_data("event3-uuid", required_skills=["public speaking"])
    ]

    response = client.get(f"/api/matched_events/{user_id}")

    assert response.status_code == 200
    assert "matched_events" in response.json()
    assert len(response.json()["matched_events"]) == 1
    assert response.json()["matched_events"][0]["id"] == "event1-uuid"
    assert response.json()["matched_events"][0]["name"] == "Mock Event"

def test_get_matched_events_no_user_profile(mock_supabase_client: MagicMock):
    user_id = "user-no-profile-uuid"
    
    # Add authentication headers since this endpoint now requires auth
    headers = get_auth_headers(user_id=user_id, role="volunteer")
    
    # The authenticated route calls match_volunteer_to_events which makes its own user_profile query
    # Mock this query to return empty data (profile not found)
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

    response = client.get(f"/api/matched_events/{user_id}", headers=headers)

    # The route actually returns 200 with empty matched_events when no profile is found
    # This is valid behavior - if no profile exists, there are no matches
    assert response.status_code == 200
    assert "matched_events" in response.json()
    assert len(response.json()["matched_events"]) == 0

def test_get_matched_events_user_has_no_skills(mock_supabase_client: MagicMock):
    user_id = "user-no-skills-uuid"
    
    # Mock fetch_user_skills to return profile with empty skills
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
        MagicMock(data=[get_mock_user_profile_data(user_id=user_id, skills=[])])
    ]
    # Mock all events
    mock_supabase_client.table.return_value.select.return_value.execute.return_value.data = [
        get_mock_event_data("e1-uuid", required_skills=["coding"]),
        get_mock_event_data("e2-uuid", required_skills=["design"])
    ]

    response = client.get(f"/api/matched_events/{user_id}")

    assert response.status_code == 200
    assert "matched_events" in response.json()
    assert len(response.json()["matched_events"]) == 0

def test_get_matched_events_no_matches(mock_supabase_client: MagicMock):
    user_id = "user-no-matches-uuid"
    
    # Mock user profile with skills that don't match any event skills
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
        MagicMock(data=[get_mock_user_profile_data(user_id=user_id, skills=["gardening"])])
    ]
    # Mock events that don't match
    mock_supabase_client.table.return_value.select.return_value.execute.return_value.data = [
        get_mock_event_data("e1-uuid", required_skills=["coding"]),
        get_mock_event_data("e2-uuid", required_skills=["design"])
    ]

    response = client.get(f"/api/matched_events/{user_id}")

    assert response.status_code == 200
    assert "matched_events" in response.json()
    assert len(response.json()["matched_events"]) == 0


# --- Tests for match_and_notify endpoint ---

def test_match_and_notify_success_new_match(mock_supabase_client: MagicMock):
    user_id = "user-match-notify-uuid"
    event_id = "event-new-match-uuid"
    event_name = "New Match Event"
    
    # The route makes multiple calls in sequence:
    # 1. fetch_user_skills - user_profiles.select().eq().execute()
    # 2. fetch_all_events - events.select().execute()  
    # 3. For each match: notifications.select().eq().eq().execute() (check existing - TWO eq() calls!)
    # 4. If no existing: notifications.insert().execute()
    
    # Set up the mock chain to handle different database operations
    
    # Mock for fetch_user_skills call
    user_skills_mock = MagicMock()
    user_skills_mock.execute.return_value.data = [get_mock_user_profile_data(user_id=user_id, skills=["coding"])]
    
    # Mock for existing notification check (two .eq() calls)
    existing_notif_mock = MagicMock()
    existing_notif_mock.eq.return_value.execute.return_value.data = []  # No existing notification
    
    # Set up the table().select().eq() chain to return different mocks
    mock_supabase_client.table.return_value.select.return_value.eq.side_effect = [
        user_skills_mock,  # First call: fetch_user_skills
        existing_notif_mock  # Second call: existing notification check (first .eq())
    ]
    
    # Mock fetch_all_events (select().execute() without eq())
    mock_supabase_client.table.return_value.select.return_value.execute.return_value.data = [
        get_mock_event_data(event_id, event_name, required_skills=["coding"])
    ]
    
    # Mock the insert call for notification
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = [
        {"id": "new-notif-id", "user_id": user_id, "event_id": event_id, "message": f"You've been matched with: {event_name}"}
    ]

    response = client.get(f"/api/match-and-notify/{user_id}")

    assert response.status_code == 200
    assert "matched_events" in response.json()
    assert len(response.json()["matched_events"]) == 1
    assert response.json()["matched_events"][0]["id"] == event_id
    # Verify that notification insert was called
    mock_supabase_client.table.return_value.insert.assert_called_once()


def test_match_and_notify_success_duplicate_notification(mock_supabase_client: MagicMock):
    user_id = "user-notify-duplicate-uuid"
    event_id = "event-duplicate-match-uuid"
    
    # Mock sequence for select.execute() calls
    mock_supabase_client.table.return_value.select.return_value.eq.side_effect = [
        # 1. For fetch_user_skills
        MagicMock(execute=MagicMock(return_value=MagicMock(data=[get_mock_user_profile_data(user_id=user_id, skills=["coding"])], count=1))),
        # 2. For existing_notif check (should return existing data to signify duplicate)
        MagicMock(execute=MagicMock(return_value=MagicMock(data=[{"id": "existing-notif-id"}], count=1)))
    ]
    # Mock fetch_all_events (no `eq` before it)
    mock_supabase_client.table.return_value.select.return_value.execute.return_value.data = [
        get_mock_event_data(event_id, "Duplicate Match Event", required_skills=["coding"])
    ]
    # No mock for insert needed, as it should NOT be called

    response = client.get(f"/api/match-and-notify/{user_id}")

    assert response.status_code == 200
    assert "matched_events" in response.json()
    assert len(response.json()["matched_events"]) == 1
    assert response.json()["matched_events"][0]["id"] == event_id
    # Verify that notification insert was NOT called
    mock_supabase_client.table.return_value.insert.assert_not_called()


def test_match_and_notify_no_user_profile(mock_supabase_client: MagicMock):
    user_id = "user-no-profile-notify-uuid"
    
    # Mock user profile not found (fetch_user_skills returns empty set)
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [] # Empty data

    response = client.get(f"/api/match-and-notify/{user_id}")

    # The route returns 200 with empty matched_events when no profile/skills found
    # This is valid behavior - if no skills exist, there are no matches
    assert response.status_code == 200
    assert "matched_events" in response.json()
    assert len(response.json()["matched_events"]) == 0
