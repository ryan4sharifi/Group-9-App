import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from app.routes import match
from app.routes.match import (
    MatchRequest, MatchResult, calculate_distance, calculate_skill_match,
    calculate_urgency_score, calculate_match_score
)
from app.routes.auth import create_access_token

app = FastAPI()
app.include_router(match.router)

# Test data
valid_match_request = {
    "user_id": "user123",
    "max_distance": 50.0,
    "urgency_weight": 0.3,
    "skill_weight": 0.5,
    "distance_weight": 0.2
}

# Test: Calculate Distance
def test_calculate_distance_mock():
    """Test distance calculation with mock (no API key)"""
    distance = calculate_distance("Miami, FL", "Orlando, FL")
    assert isinstance(distance, float)
    assert 0 <= distance <= 50

@patch("app.routes.match.GOOGLE_MAPS_API_KEY", "test_key")
@patch("app.routes.match.requests.get")
def test_calculate_distance_api_success(mock_get):
    """Test distance calculation with successful API response"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "status": "OK",
        "rows": [{
            "elements": [{
                "status": "OK",
                "distance": {"text": "25.5 mi"}
            }]
        }]
    }
    mock_get.return_value = mock_response
    
    distance = calculate_distance("Miami, FL", "Orlando, FL")
    assert distance == 25.5

@patch("app.routes.match.GOOGLE_MAPS_API_KEY", "test_key")
@patch("app.routes.match.requests.get")
def test_calculate_distance_api_failure(mock_get):
    """Test distance calculation with API failure"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "status": "ERROR",
        "rows": [{
            "elements": [{
                "status": "NOT_FOUND"
            }]
        }]
    }
    mock_get.return_value = mock_response
    
    distance = calculate_distance("Miami, FL", "Orlando, FL")
    assert distance == 999.0

@patch("app.routes.match.GOOGLE_MAPS_API_KEY", "test_key")
@patch("app.routes.match.requests.get")
def test_calculate_distance_api_exception(mock_get):
    """Test distance calculation with API exception"""
    mock_get.side_effect = Exception("API Error")
    
    distance = calculate_distance("Miami, FL", "Orlando, FL")
    assert distance == 999.0

# Test: Calculate Skill Match
def test_calculate_skill_match_perfect_match():
    """Test skill match calculation with perfect match"""
    user_skills = ["teamwork", "communication", "leadership"]
    event_skills = ["teamwork", "communication"]
    
    match_percentage = calculate_skill_match(user_skills, event_skills)
    assert match_percentage == 100.0

def test_calculate_skill_match_partial_match():
    """Test skill match calculation with partial match"""
    user_skills = ["teamwork", "communication"]
    event_skills = ["teamwork", "communication", "leadership"]
    
    match_percentage = calculate_skill_match(user_skills, event_skills)
    assert match_percentage == 66.66666666666667

def test_calculate_skill_match_no_match():
    """Test skill match calculation with no match"""
    user_skills = ["teamwork", "communication"]
    event_skills = ["leadership", "management"]
    
    match_percentage = calculate_skill_match(user_skills, event_skills)
    assert match_percentage == 0.0

def test_calculate_skill_match_empty_event_skills():
    """Test skill match calculation with empty event skills"""
    user_skills = ["teamwork", "communication"]
    event_skills = []
    
    match_percentage = calculate_skill_match(user_skills, event_skills)
    assert match_percentage == 0.0

def test_calculate_skill_match_case_insensitive():
    """Test skill match calculation is case insensitive"""
    user_skills = ["Teamwork", "COMMUNICATION"]
    event_skills = ["teamwork", "communication"]
    
    match_percentage = calculate_skill_match(user_skills, event_skills)
    assert match_percentage == 100.0

# Test: Calculate Urgency Score
def test_calculate_urgency_score_high():
    """Test urgency score calculation for high urgency"""
    score = calculate_urgency_score("high")
    assert score == 1.0

def test_calculate_urgency_score_medium():
    """Test urgency score calculation for medium urgency"""
    score = calculate_urgency_score("medium")
    assert score == 0.6

def test_calculate_urgency_score_low():
    """Test urgency score calculation for low urgency"""
    score = calculate_urgency_score("low")
    assert score == 0.3

def test_calculate_urgency_score_invalid():
    """Test urgency score calculation for invalid urgency"""
    score = calculate_urgency_score("invalid")
    assert score == 0.0

def test_calculate_urgency_score_case_insensitive():
    """Test urgency score calculation is case insensitive"""
    score = calculate_urgency_score("HIGH")
    assert score == 1.0

# Test: Calculate Match Score
def test_calculate_match_score_perfect():
    """Test match score calculation with perfect match"""
    score = calculate_match_score(
        skill_match=100.0,
        distance=5.0,
        urgency="high",
        skill_weight=0.5,
        distance_weight=0.2,
        urgency_weight=0.3
    )
    
    # Expected: (1.0 * 0.5) + (0.9 * 0.2) + (1.0 * 0.3) = 0.5 + 0.18 + 0.3 = 0.98 * 100 = 98.0
    assert score == 98.0

def test_calculate_match_score_poor():
    """Test match score calculation with poor match"""
    score = calculate_match_score(
        skill_match=20.0,
        distance=45.0,
        urgency="low",
        skill_weight=0.5,
        distance_weight=0.2,
        urgency_weight=0.3
    )
    
    # Expected: (0.2 * 0.5) + (0.1 * 0.2) + (0.3 * 0.3) = 0.1 + 0.02 + 0.09 = 0.21 * 100 = 21.0
    assert score == 21.0

def test_calculate_match_score_zero_distance():
    """Test match score calculation with zero distance"""
    score = calculate_match_score(
        skill_match=50.0,
        distance=0.0,
        urgency="medium",
        skill_weight=0.5,
        distance_weight=0.2,
        urgency_weight=0.3
    )
    
    # Expected: (0.5 * 0.5) + (1.0 * 0.2) + (0.6 * 0.3) = 0.25 + 0.2 + 0.18 = 0.63 * 100 = 63.0
    assert score == 63.0

# Test: Match Volunteer to Events
@patch("app.routes.match.supabase")
def test_match_volunteer_to_events_success(mock_supabase):
    """Test successful volunteer matching"""
    # Mock user profile
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
        "user_id": "user123",
        "skills": ["teamwork", "communication"],
        "address1": "123 Main St",
        "city": "Miami",
        "state": "FL"
    }]
    
    # Mock events
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = [
        {
            "id": "event1",
            "name": "Beach Cleanup",
            "location": "Miami Beach",
            "required_skills": ["teamwork"],
            "urgency": "high"
        },
        {
            "id": "event2",
            "name": "Food Drive",
            "location": "Orlando",
            "required_skills": ["leadership"],
            "urgency": "low"
        }
    ]
    
    # Create valid token
    token_data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.post("/match", json=valid_match_request, headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    matches = response.json()
    assert len(matches) > 0
    assert matches[0]["event_name"] == "Beach Cleanup"

@patch("app.routes.match.supabase")
def test_match_volunteer_to_events_unauthorized(mock_supabase):
    """Test volunteer matching without authorization"""
    # Create token for different user
    token_data = {"sub": "user456", "role": "volunteer"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.post("/match", json=valid_match_request, headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]

@patch("app.routes.match.supabase")
def test_match_volunteer_to_events_user_not_found(mock_supabase):
    """Test volunteer matching with non-existent user"""
    # Mock no user profile
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    
    # Create valid token
    token_data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.post("/match", json=valid_match_request, headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 404
    assert "User profile not found" in response.json()["detail"]

@patch("app.routes.match.supabase")
def test_match_volunteer_to_events_no_events(mock_supabase):
    """Test volunteer matching with no events available"""
    # Mock user profile
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
        "user_id": "user123",
        "skills": ["teamwork"],
        "address1": "123 Main St",
        "city": "Miami",
        "state": "FL"
    }]
    
    # Mock no events
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = []
    
    # Create valid token
    token_data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.post("/match", json=valid_match_request, headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert response.json() == []

# Test: Get Matched Events
@patch("app.routes.match.supabase")
def test_get_matched_events_success(mock_supabase):
    """Test getting matched events"""
    # Mock user profile
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
        "user_id": "user123",
        "skills": ["teamwork"]
    }]
    
    # Mock events
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = [
        {
            "id": "event1",
            "name": "Beach Cleanup",
            "required_skills": ["teamwork"]
        }
    ]
    
    # Create valid token
    token_data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.get("/matched_events/user123", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200

# Test: Batch Match
@patch("app.routes.match.supabase")
def test_batch_match_volunteers_admin_success(mock_supabase):
    """Test batch matching with admin access"""
    # Mock volunteers
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = [
        {"user_id": "user1", "skills": ["teamwork"]},
        {"user_id": "user2", "skills": ["communication"]}
    ]
    
    # Mock events
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = [
        {"id": "event1", "name": "Beach Cleanup", "required_skills": ["teamwork"]}
    ]
    
    # Create admin token
    token_data = {"sub": "admin123", "role": "admin"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.post("/batch-match", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200

@patch("app.routes.match.supabase")
def test_batch_match_volunteers_unauthorized(mock_supabase):
    """Test batch matching without admin access"""
    # Create non-admin token
    token_data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.post("/batch-match", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 403
    assert "Admin access required" in response.json()["detail"]

# Test: Match and Notify
@patch("app.routes.match.supabase")
def test_match_and_notify_success(mock_supabase):
    """Test match and notify functionality"""
    # Mock user skills
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {"skills": ["teamwork", "communication"]}
    ]
    
    # Mock events
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = [
        {
            "id": "event1",
            "name": "Beach Cleanup",
            "required_skills": ["teamwork"]
        }
    ]
    
    # Mock no existing notifications
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
    
    # Mock notification insertion
    mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{"id": "notif1"}]
    
    client = TestClient(app)
    response = client.get("/match-and-notify/user123")
    
    assert response.status_code == 200
    assert "matched_events" in response.json()

# Test: Pydantic Models
def test_match_request_model():
    """Test MatchRequest model validation"""
    request = MatchRequest(
        user_id="user123",
        max_distance=50.0,
        urgency_weight=0.3,
        skill_weight=0.5,
        distance_weight=0.2
    )
    
    assert request.user_id == "user123"
    assert request.max_distance == 50.0
    assert request.urgency_weight == 0.3
    assert request.skill_weight == 0.5
    assert request.distance_weight == 0.2

def test_match_request_model_defaults():
    """Test MatchRequest model with default values"""
    request = MatchRequest(user_id="user123")
    
    assert request.user_id == "user123"
    assert request.max_distance == 50.0
    assert request.urgency_weight == 0.3
    assert request.skill_weight == 0.5
    assert request.distance_weight == 0.2

def test_match_result_model():
    """Test MatchResult model validation"""
    result = MatchResult(
        event_id="event123",
        event_name="Beach Cleanup",
        match_score=85.5,
        skill_match_percentage=90.0,
        distance_miles=5.2,
        urgency_level="high",
        reasons=["Strong skill match", "Close location"]
    )
    
    assert result.event_id == "event123"
    assert result.event_name == "Beach Cleanup"
    assert result.match_score == 85.5
    assert result.skill_match_percentage == 90.0
    assert result.distance_miles == 5.2
    assert result.urgency_level == "high"
    assert len(result.reasons) == 2

# Test: Edge Cases
def test_calculate_match_score_extreme_values():
    """Test match score calculation with extreme values"""
    # Test with maximum distance
    score = calculate_match_score(
        skill_match=0.0,
        distance=50.0,
        urgency="low",
        skill_weight=0.5,
        distance_weight=0.2,
        urgency_weight=0.3
    )
    
    # Expected: (0.0 * 0.5) + (0.0 * 0.2) + (0.3 * 0.3) = 0.0 + 0.0 + 0.09 = 0.09 * 100 = 9.0
    assert score == 9.0

def test_calculate_match_score_negative_distance():
    """Test match score calculation with negative distance"""
    score = calculate_match_score(
        skill_match=50.0,
        distance=-5.0,
        urgency="medium",
        skill_weight=0.5,
        distance_weight=0.2,
        urgency_weight=0.3
    )
    
    # Distance score should be 1.0 for negative distance
    assert score > 0

# Test: Integration Scenarios
@patch("app.routes.match.supabase")
def test_complete_matching_workflow(mock_supabase):
    """Test complete matching workflow"""
    # Mock user profile
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
        "user_id": "user123",
        "skills": ["teamwork", "communication"],
        "address1": "123 Main St",
        "city": "Miami",
        "state": "FL"
    }]
    
    # Mock events
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = [
        {
            "id": "event1",
            "name": "Beach Cleanup",
            "location": "Miami Beach",
            "required_skills": ["teamwork"],
            "urgency": "high"
        }
    ]
    
    # Create valid token
    token_data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    
    # Test matching
    response = client.post("/match", json=valid_match_request, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    
    # Test getting matched events
    response = client.get("/matched_events/user123", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200 