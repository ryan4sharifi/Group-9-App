import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from app.routes import profile
from app.routes.profile import UserProfileWithoutID
from datetime import date

app = FastAPI()
app.include_router(profile.router)

# Test data
valid_profile_data = {
    "full_name": "John Doe",
    "address1": "123 Main St",
    "address2": "Apt 4B",
    "city": "Miami",
    "state": "FL",
    "zip_code": "33101",
    "skills": ["teamwork", "communication"],
    "preferences": "Weekend events only",
    "availability": "2024-01-15",
    "role": "volunteer"
}

# Test: Create/Update Profile
@patch("app.routes.profile.supabase")
def test_create_or_update_profile_success(mock_supabase):
    """Test successful profile creation/update"""
    # Mock successful upsert
    mock_supabase.table.return_value.upsert.return_value.execute.return_value.data = [{"id": "profile123"}]
    
    client = TestClient(app)
    response = client.post("/profile/user123", json=valid_profile_data)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Profile saved"
    assert "data" in response.json()

@patch("app.routes.profile.supabase")
def test_create_or_update_profile_server_error(mock_supabase):
    """Test profile creation with server error"""
    # Mock server error
    mock_supabase.table.return_value.upsert.return_value.execute.side_effect = Exception("Database error")
    
    client = TestClient(app)
    response = client.post("/profile/user123", json=valid_profile_data)
    
    assert response.status_code == 500
    assert "Failed to save profile" in response.json()["detail"]

def test_create_or_update_profile_invalid_data():
    """Test profile creation with invalid data"""
    client = TestClient(app)
    
    # Test with invalid state (too long)
    invalid_data = valid_profile_data.copy()
    invalid_data["state"] = "FLORIDA"
    
    response = client.post("/profile/user123", json=invalid_data)
    assert response.status_code == 422

def test_create_or_update_profile_invalid_zip():
    """Test profile creation with invalid zip code"""
    client = TestClient(app)
    
    # Test with invalid zip code (too short)
    invalid_data = valid_profile_data.copy()
    invalid_data["zip_code"] = "123"
    
    response = client.post("/profile/user123", json=invalid_data)
    assert response.status_code == 422

# Test: Get Profile
@patch("app.routes.profile.supabase")
def test_get_profile_success(mock_supabase):
    """Test successful profile retrieval"""
    # Mock profile data
    profile_data = {
        "user_id": "user123",
        "full_name": "John Doe",
        "skills": ["teamwork"]
    }
    
    # Mock credentials data
    creds_data = {
        "email": "john@example.com",
        "role": "volunteer"
    }
    
    # Mock profile query
    mock_profile_response = MagicMock()
    mock_profile_response.data = profile_data
    mock_supabase.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_profile_response
    
    # Mock credentials query
    mock_creds_response = MagicMock()
    mock_creds_response.data = creds_data
    mock_supabase.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_creds_response
    
    client = TestClient(app)
    response = client.get("/profile/user123")
    
    assert response.status_code == 200
    assert response.json()["full_name"] == "John Doe"
    assert response.json()["email"] == "john@example.com"
    assert response.json()["role"] == "volunteer"

@patch("app.routes.profile.supabase")
def test_get_profile_no_data(mock_supabase):
    """Test profile retrieval with no data"""
    # Mock no profile data
    mock_profile_response = MagicMock()
    mock_profile_response.data = None
    mock_supabase.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_profile_response
    
    # Mock no credentials data
    mock_creds_response = MagicMock()
    mock_creds_response.data = None
    mock_supabase.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_creds_response
    
    client = TestClient(app)
    response = client.get("/profile/user123")
    
    assert response.status_code == 200
    assert response.json() == {}

@patch("app.routes.profile.supabase")
def test_get_profile_server_error(mock_supabase):
    """Test profile retrieval with server error"""
    # Mock server error
    mock_supabase.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.side_effect = Exception("Database error")
    
    client = TestClient(app)
    response = client.get("/profile/user123")
    
    assert response.status_code == 500
    assert "Failed to retrieve profile" in response.json()["detail"]

# Test: Delete Profile
@patch("app.routes.profile.supabase")
def test_delete_profile_success(mock_supabase):
    """Test successful profile deletion"""
    # Mock successful deletion
    mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [{"id": "profile123"}]
    
    client = TestClient(app)
    response = client.delete("/profile/user123")
    
    assert response.status_code == 200
    assert response.json()["message"] == "Profile deleted"

@patch("app.routes.profile.supabase")
def test_delete_profile_not_found(mock_supabase):
    """Test profile deletion when profile doesn't exist"""
    # Mock no data returned (profile not found)
    mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = []
    
    client = TestClient(app)
    response = client.delete("/profile/user123")
    
    assert response.status_code == 404
    assert "Profile not found" in response.json()["detail"]

@patch("app.routes.profile.supabase")
def test_delete_profile_server_error(mock_supabase):
    """Test profile deletion with server error"""
    # Mock server error
    mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.side_effect = Exception("Database error")
    
    client = TestClient(app)
    response = client.delete("/profile/user123")
    
    assert response.status_code == 500
    assert "Failed to delete profile" in response.json()["detail"]

# Test: Get All Volunteers
@patch("app.routes.profile.supabase")
def test_get_all_volunteers_success(mock_supabase):
    """Test successful retrieval of all volunteers"""
    # Mock volunteers data
    volunteers_data = [
        {"user_id": "user1", "full_name": "John Doe", "skills": ["teamwork"], "email": "john@example.com"},
        {"user_id": "user2", "full_name": "Jane Smith", "skills": ["communication"], "email": "jane@example.com"}
    ]
    
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = volunteers_data
    
    client = TestClient(app)
    response = client.get("/volunteers")
    
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["full_name"] == "John Doe"
    assert response.json()[1]["full_name"] == "Jane Smith"

@patch("app.routes.profile.supabase")
def test_get_all_volunteers_empty(mock_supabase):
    """Test retrieval of volunteers when none exist"""
    # Mock empty data
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = []
    
    client = TestClient(app)
    response = client.get("/volunteers")
    
    assert response.status_code == 200
    assert response.json() == []

@patch("app.routes.profile.supabase")
def test_get_all_volunteers_server_error(mock_supabase):
    """Test retrieval of volunteers with server error"""
    # Mock server error
    mock_supabase.table.return_value.select.return_value.execute.side_effect = Exception("Database error")
    
    client = TestClient(app)
    response = client.get("/volunteers")
    
    assert response.status_code == 500
    assert "Failed to fetch volunteers" in response.json()["detail"]

# Test: Pydantic Model Validation
def test_user_profile_without_id_valid():
    """Test UserProfileWithoutID model with valid data"""
    profile = UserProfileWithoutID(
        full_name="John Doe",
        address1="123 Main St",
        city="Miami",
        state="FL",
        zip_code="33101",
        skills=["teamwork"],
        preferences="Weekend events",
        availability=date(2024, 1, 15),
        role="volunteer"
    )
    
    assert profile.full_name == "John Doe"
    assert profile.address1 == "123 Main St"
    assert profile.city == "Miami"
    assert profile.state == "FL"
    assert profile.zip_code == "33101"
    assert profile.skills == ["teamwork"]
    assert profile.preferences == "Weekend events"
    assert profile.availability == date(2024, 1, 15)
    assert profile.role == "volunteer"

def test_user_profile_without_id_invalid_state():
    """Test UserProfileWithoutID model with invalid state"""
    with pytest.raises(ValueError):
        UserProfileWithoutID(
            full_name="John Doe",
            state="FLORIDA"  # Too long
        )

def test_user_profile_without_id_invalid_zip():
    """Test UserProfileWithoutID model with invalid zip code"""
    with pytest.raises(ValueError):
        UserProfileWithoutID(
            full_name="John Doe",
            zip_code="123"  # Too short
        )

def test_user_profile_without_id_optional_fields():
    """Test UserProfileWithoutID model with optional fields"""
    profile = UserProfileWithoutID(
        full_name="John Doe"
    )
    
    assert profile.full_name == "John Doe"
    assert profile.address1 is None
    assert profile.skills == []

# Test: Edge Cases
def test_profile_with_date_conversion():
    """Test profile creation with date conversion"""
    profile_data = valid_profile_data.copy()
    profile_data["availability"] = "2024-01-15"
    
    # Test that the date string is properly handled
    profile = UserProfileWithoutID(**profile_data)
    assert profile.availability == date(2024, 1, 15)

def test_profile_with_empty_skills():
    """Test profile with empty skills list"""
    profile_data = valid_profile_data.copy()
    profile_data["skills"] = []
    
    profile = UserProfileWithoutID(**profile_data)
    assert profile.skills == []

def test_profile_with_none_values():
    """Test profile with None values for optional fields"""
    profile_data = {
        "full_name": "John Doe",
        "address1": None,
        "address2": None,
        "city": None,
        "state": None,
        "zip_code": None,
        "skills": None,
        "preferences": None,
        "availability": None,
        "role": None
    }
    
    profile = UserProfileWithoutID(**profile_data)
    assert profile.full_name == "John Doe"
    assert profile.address1 is None 