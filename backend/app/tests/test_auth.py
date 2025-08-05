# backend/app/tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import MagicMock
from passlib.hash import bcrypt as passlib_bcrypt
import bcrypt # Explicitly import bcrypt

client = TestClient(app)

def test_register_user_success(mock_supabase_client: MagicMock, mock_uuid: str):
    test_email = "newuser@example.com"
    test_password = "password123"

    # Mock sequence of execute calls across different mock objects for clarity
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
        MagicMock(data=[]), # 1st select: email check (no existing user)
    ]
    mock_supabase_client.table.return_value.insert.return_value.execute.side_effect = [
        MagicMock(data=[{"id": mock_uuid, "email": test_email, "role": "volunteer"}]), # 1st insert: user_credentials
        MagicMock(data=[{"user_id": mock_uuid, "skills": []}]) # 2nd insert: user_profiles
    ]

    response = client.post("/auth/register", json={"email": test_email, "password": test_password, "role": "volunteer"})

    assert response.status_code == 200
    assert response.json()["message"] == "Registration successful"  # Match actual message
    # Don't check exact UUID since real UUID is generated - check it exists
    assert "user_id" in response.json()
    assert len(response.json()["user_id"]) > 0  # Verify UUID is not empty
    assert response.json()["role"] == "volunteer"

def test_register_user_email_exists(mock_supabase_client: MagicMock, mock_uuid: str):
    test_email = "existing@example.com"
    test_password = "password123"

    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = \
        [{"id": mock_uuid}] # Simulate existing user

    response = client.post("/auth/register", json={"email": test_email, "password": test_password, "role": "volunteer"})

    assert response.status_code == 409  # Should return 409 for duplicate email (as defined in auth.py)
    assert "already registered" in response.json()["detail"]

def test_login_success(mock_supabase_client: MagicMock, hashed_password: str, mock_uuid: str):
    test_email = "test@login.com"
    test_role = "admin"

    # Fix the mock chain to match the actual login route query (table -> select -> eq -> execute)
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = \
        [{"id": mock_uuid, "email": test_email, "password": hashed_password, "role": test_role}]

    response = client.post("/auth/login", json={"email": test_email, "password": "test_password_123"})

    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"
    assert response.json()["user_id"] == mock_uuid
    assert response.json()["role"] == test_role

def test_login_invalid_password(mock_supabase_client: MagicMock, hashed_password: str, mock_uuid: str):
    test_email = "test@login.com"
    wrong_password = "wrong_password"

    # Fix mock chain to match actual query (table -> select -> eq -> execute)
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = \
        [{"id": mock_uuid, "email": test_email, "password": hashed_password, "role": "volunteer"}]

    response = client.post("/auth/login", json={"email": test_email, "password": wrong_password})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_login_user_not_found(mock_supabase_client: MagicMock):
    test_email = "nonexistent@login.com"

    # Fix mock chain to match actual query (table -> select -> eq -> execute)
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

    response = client.post("/auth/login", json={"email": test_email, "password": "any_password"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_get_user_by_id_success(mock_supabase_client: MagicMock, mock_uuid: str):
    user_id = mock_uuid
    mock_email = "userget@example.com"
    mock_role = "volunteer"

    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = \
        [{"email": mock_email, "role": mock_role}]

    response = client.get(f"/auth/user/{user_id}")

    assert response.status_code == 200
    assert response.json()["email"] == mock_email
    assert response.json()["role"] == mock_role

def test_get_user_by_id_not_found(mock_supabase_client: MagicMock, mock_uuid: str):
    user_id = "00000000-0000-0000-0000-000000000000" # Use a valid but likely non-existent UUID format

    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

    response = client.get(f"/auth/user/{user_id}")

    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")
    
    assert response.status_code == 404
    # Check both possible response formats
    response_json = response.json()
    if "detail" in response_json:
        assert response_json["detail"] == "User not found"
    elif "message" in response_json:
        assert "not found" in response_json["message"].lower()

def test_delete_account_success(mock_supabase_client: MagicMock, mock_uuid: str):
    user_id_to_delete = mock_uuid

    # Mock responses for sequential delete calls (4 total)
    mock_supabase_client.table.return_value.delete.return_value.eq.return_value.execute.side_effect = [
        MagicMock(data=[{"id": "hist1"}]), # 1. Delete volunteer_history
        MagicMock(data=[{"id": "notif1"}]), # 2. Delete notifications
        MagicMock(data=[{"id": "profile1"}]), # 3. Delete user_profiles
        MagicMock(data=[{"id": user_id_to_delete}]) # 4. Delete user_credentials
    ]

    response = client.delete(f"/auth/delete_account/{user_id_to_delete}")

    assert response.status_code == 200
    assert response.json()["message"] == "Account and all associated data deleted successfully."


def test_delete_account_credentials_not_found(mock_supabase_client: MagicMock, mock_uuid: str):
    user_id_to_delete = mock_uuid

    mock_supabase_client.table.return_value.delete.return_value.eq.return_value.execute.side_effect = [
        MagicMock(data=[]), # volunteer_history (empty response)
        MagicMock(data=[]), # notifications (empty response)
        MagicMock(data=[]), # user_profiles (empty response)
        MagicMock(data=[])  # user_credentials (simulates not found)
    ]

    response = client.delete(f"/auth/delete_account/{user_id_to_delete}")

    assert response.status_code == 404
    # Check both possible response formats
    response_json = response.json()
    if "detail" in response_json:
        assert "not found" in response_json["detail"].lower()
    elif "message" in response_json:
        assert "not found" in response_json["message"].lower()
