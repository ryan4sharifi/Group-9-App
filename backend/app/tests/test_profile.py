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

    # Mock sequential selects: one for profile, one for credentials
    mock_supabase_client.table.return_value.select.return_value.eq.side_effect = [
        # First call: maybe_single() for profile_res (should find data)
        MagicMock(maybe_single=MagicMock(return_value=MagicMock(data=mock_profile, count=1))),
        # Second call: maybe_single() for creds_res (should find data)
        MagicMock(maybe_single=MagicMock(return_value=MagicMock(data={"email": mock_email, "role": mock_role}, count=1)))
    ]

    response = client.get(f"/api/profile/{user_id}")

    assert response.status_code == 200
    assert response.json()["full_name"] == "John Doe"
    assert response.json()["email"] == mock_email
    assert response.json()["role"] == mock_role
    assert "leadership" in response.json()["skills"]

def test_get_profile_not_found(mock_supabase_client: MagicMock):
    user_id = "nonexistent-profile"

    # Mock sequential selects: both return no data
    mock_supabase_client.table.return_value.select.return_value.eq.side_effect = [
        # First call: maybe_single() for profile_res (returns no data)
        MagicMock(maybe_single=MagicMock(return_value=MagicMock(data=None, count=0))),
        # Second call: maybe_single() for creds_res (returns no data)
        MagicMock(maybe_single=MagicMock(return_value=MagicMock(data=None, count=0)))
    ]

    response = client.get(f"/api/profile/{user_id}")

    # The backend get_profile route attempts to merge profile_data and creds_data.
    # If both are None, the backend still tries to return {**None, **None} which will raise a 500.
    # The detail message indicates this specific backend behavior.
    assert response.status_code == 500
    assert "detail" in response.json()
    assert "Failed to retrieve profile" in response.json()["detail"]


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
    assert response.json()["detail"] == "Profile not found or already deleted"
