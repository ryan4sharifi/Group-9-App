# backend/app/tests/test_profile.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import MagicMock
from datetime import date

client = TestClient(app)

# Helper mock data for profile
def get_mock_profile_data(user_id="user-profile-id-1", skills=None, email="test@profile.com", role="volunteer"):
    return {
        "id": "profile-uuid", # Profile has its own ID
        "user_id": user_id,
        "full_name": "John Doe",
        "address1": "123 Main St",
        "address2": None, # Optional
        "city": "Anytown",
        "state": "TX",
        "zip_code": "12345",
        "skills": skills if skills is not None else ["python", "fastapi"],
        "preferences": "flexible hours",
        "availability": str(date.today()), # Format as string for consistency
        "created_at": "2025-01-01T10:00:00Z",
        # For the merged response from get_profile, these come from user_credentials
        "email": email,
        "role": role
    }

def test_create_or_update_profile_success(mock_supabase_client: MagicMock):
    user_id = "test-user-profile-1"
    profile_data = {
        "full_name": "Updated Name",
        "skills": ["react", "mui"], # Skills are now required
        "preferences": "night shifts"
    }

    # Mock the upsert operation
    mock_supabase_client.table.return_value.upsert.return_value.execute.return_value.data = \
        [{"id": "profile-uuid-updated", "user_id": user_id, **profile_data}]

    response = client.post(f"/api/profile/{user_id}", json=profile_data)

    assert response.status_code == 200
    assert response.json()["message"] == "Profile saved"
    assert "id" in response.json()["data"][0] # Check that an ID is present in the returned data
    assert response.json()["data"][0]["full_name"] == "Updated Name"
    assert "react" in response.json()["data"][0]["skills"]

def test_create_or_update_profile_invalid_skills(mock_supabase_client: MagicMock):
    user_id = "test-user-invalid"
    # No skills field provided (will trigger Pydantic validation error)
    invalid_profile_data = {"full_name": "Invalid User"}

    response = client.post(f"/api/profile/{user_id}", json=invalid_profile_data)

    assert response.status_code == 422 # Unprocessable Entity
    assert "detail" in response.json()
    assert any("skills" in err["loc"] for err in response.json()["detail"])

def test_get_profile_success(mock_supabase_client: MagicMock):
    user_id = "user-to-get-profile"
    mock_profile = get_mock_profile_data(user_id=user_id, skills=["leadership"])
    mock_email = "get@example.com"
    mock_role = "admin"

    # Mock the query chain: maybe_single fails, falls back to execute
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.maybe_single.side_effect = [
        # First call - profile query fails with AttributeError, should fallback to execute()
        AttributeError("maybe_single not available"),
        # Second call - creds query fails with AttributeError, should fallback to execute()  
        AttributeError("maybe_single not available")
    ]
    
    # Set up the execute() fallback calls
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
        MagicMock(data=[mock_profile]),  # First execute() call for profile
        MagicMock(data=[{"email": mock_email, "role": mock_role}])  # Second execute() call for creds
    ]

    response = client.get(f"/api/profile/{user_id}")

    assert response.status_code == 200
    assert response.json()["full_name"] == "John Doe"
    assert response.json()["email"] == mock_email
    assert response.json()["role"] == mock_role
    assert "leadership" in response.json()["skills"]

def test_get_profile_not_found(mock_supabase_client: MagicMock):
    user_id = "nonexistent-profile"

    # Mock the query chain: maybe_single fails, falls back to execute which returns empty data
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.maybe_single.side_effect = [
        # First call - profile query fails with AttributeError, should fallback to execute()
        AttributeError("maybe_single not available"),
        # Second call - creds query fails with AttributeError, should fallback to execute()  
        AttributeError("maybe_single not available")
    ]
    
    # Set up the execute() fallback calls to return empty data
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
        MagicMock(data=[]),  # First execute() call for profile - empty
        MagicMock(data=[])   # Second execute() call for creds - empty
    ]

    response = client.get(f"/api/profile/{user_id}")

    # When both profile_data and creds_data are empty ({}), the route raises 404
    assert response.status_code == 404
    # Use flexible error checking
    response_data = response.json()
    assert "detail" in response_data or "message" in response_data
    if "detail" in response_data:
        assert "not found" in response_data["detail"].lower()
    else:
        assert "not found" in response_data["message"].lower()


def test_delete_profile_success(mock_supabase_client: MagicMock):
    user_id = "user-to-delete-profile"

    mock_supabase_client.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = \
        [{"user_id": user_id}] # Mock that 1 item was deleted

    response = client.delete(f"/api/profile/{user_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Profile deleted"

def test_delete_profile_not_found(mock_supabase_client: MagicMock):
    user_id = "nonexistent-profile-delete"

    mock_supabase_client.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [] # Mock that 0 items were deleted

    response = client.delete(f"/api/profile/{user_id}")

    assert response.status_code == 404
    # Use flexible error checking like other successful tests
    response_data = response.json()
    assert "detail" in response_data or "message" in response_data
    if "detail" in response_data:
        assert "not found" in response_data["detail"].lower()
    else:
        assert "not found" in response_data["message"].lower()
