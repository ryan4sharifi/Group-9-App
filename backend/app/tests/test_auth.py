<<<<<<< HEAD
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.routes.auth import UserRegister, UserLogin, validate_user_data, create_access_token, verify_token
from fastapi import HTTPException
from passlib.hash import bcrypt
from jose import jwt
import os

from app.main import app

# Test data
valid_user_data = {
    "email": "test@example.com",
    "password": "password123",
    "role": "volunteer"
}

valid_login_data = {
    "email": "test@example.com",
    "password": "password123"
}

# Test: User Registration
@patch("app.routes.auth.supabase")
def test_register_success(mock_supabase):
    """Test successful user registration"""
    # Mock user doesn't exist
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    
    # Mock successful user creation
    mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{"id": "user123"}]
    
    client = TestClient(app)
    response = client.post("/auth/register", json=valid_user_data)
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["user_id"] == "user123"
    assert response.json()["role"] == "volunteer"

@patch("app.routes.auth.supabase")
def test_register_existing_user(mock_supabase):
    """Test registration with existing email"""
    # Mock user already exists
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": "existing"}]
    
    client = TestClient(app)
    response = client.post("/auth/register", json=valid_user_data)
    
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_register_invalid_email():
    """Test registration with invalid email"""
    client = TestClient(app)
    response = client.post("/auth/register", json={
        "email": "invalid-email",
        "password": "password123",
        "role": "volunteer"
    })
    
    assert response.status_code == 422

def test_register_short_password():
    """Test registration with short password"""
    client = TestClient(app)
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "123",
        "role": "volunteer"
    })
    
    assert response.status_code == 422

# Test: User Login
@patch("app.routes.auth.supabase")
def test_login_success(mock_supabase):
    """Test successful user login"""
    # Mock user exists with hashed password
    hashed_password = bcrypt.hash("password123")
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
        "id": "user123",
        "password": hashed_password,
        "role": "volunteer"
    }]
    
    client = TestClient(app)
    response = client.post("/auth/login", json=valid_login_data)
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["user_id"] == "user123"

@patch("app.routes.auth.supabase")
def test_login_user_not_found(mock_supabase):
    """Test login with non-existent user"""
    # Mock user doesn't exist
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    
    client = TestClient(app)
    response = client.post("/auth/login", json=valid_login_data)
    
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

@patch("app.routes.auth.supabase")
def test_login_wrong_password(mock_supabase):
    """Test login with wrong password"""
    # Mock user exists with different password
    hashed_password = bcrypt.hash("differentpassword")
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
        "id": "user123",
        "password": hashed_password,
        "role": "volunteer"
    }]
    
    client = TestClient(app)
    response = client.post("/auth/login", json=valid_login_data)
    
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

# Test: Token Functions
def test_create_access_token():
    """Test JWT token creation"""
    data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(data)
    
    # Verify token can be decoded
    decoded = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
    assert decoded["sub"] == "user123"
    assert decoded["role"] == "volunteer"

def test_verify_token_valid():
    """Test valid token verification"""
    data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(data)
    
    # Mock HTTPAuthorizationCredentials
    mock_credentials = MagicMock()
    mock_credentials.credentials = token
    
    result = verify_token(mock_credentials)
    assert result["user_id"] == "user123"
    assert result["role"] == "volunteer"

def test_verify_token_invalid():
    """Test invalid token verification"""
    mock_credentials = MagicMock()
    mock_credentials.credentials = "invalid_token"
    
    with pytest.raises(HTTPException) as exc_info:
        verify_token(mock_credentials)
    
    assert exc_info.value.status_code == 401

# Test: Validation Functions
def test_validate_user_data_valid():
    """Test validation with valid data"""
    errors = validate_user_data(valid_user_data)
    assert not errors

def test_validate_user_data_missing_email():
    """Test validation with missing email"""
    data = {"password": "password123", "role": "volunteer"}
    errors = validate_user_data(data)
    assert "email" in errors

def test_validate_user_data_long_email():
    """Test validation with email too long"""
    data = {"email": "a" * 101 + "@example.com", "password": "password123", "role": "volunteer"}
    errors = validate_user_data(data)
    assert "email" in errors

def test_validate_user_data_short_password():
    """Test validation with short password"""
    data = {"email": "test@example.com", "password": "123", "role": "volunteer"}
    errors = validate_user_data(data)
    assert "password" in errors

def test_validate_user_data_invalid_role():
    """Test validation with invalid role"""
    data = {"email": "test@example.com", "password": "password123", "role": "invalid"}
    errors = validate_user_data(data)
    assert "role" in errors

# Test: Protected Routes
@patch("app.routes.auth.supabase")
def test_get_user_by_id_success(mock_supabase):
    """Test getting user by ID with valid token"""
    # Create valid token
    data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(data)
    
    # Mock user exists
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
        "email": "test@example.com",
        "role": "volunteer"
    }]
    
    client = TestClient(app)
    response = client.get("/auth/user/user123", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

@patch("app.routes.auth.supabase")
def test_get_user_by_id_unauthorized(mock_supabase):
    """Test getting user by ID with wrong user"""
    # Create token for different user
    data = {"sub": "user456", "role": "volunteer"}
    token = create_access_token(data)
    
    client = TestClient(app)
    response = client.get("/auth/user/user123", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 403

def test_verify_token_endpoint():
    """Test token verification endpoint"""
    data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(data)
    
    client = TestClient(app)
    response = client.post("/auth/verify-token", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert response.json()["valid"] == True
    assert response.json()["user_id"] == "user123"

# Test: Pydantic Models
def test_user_register_model():
    """Test UserRegister model validation"""
    user = UserRegister(
        email="test@example.com",
        password="password123",
        role="volunteer"
    )
    assert user.email == "test@example.com"
    assert user.password == "password123"
    assert user.role == "volunteer"

def test_user_login_model():
    """Test UserLogin model validation"""
    login = UserLogin(
        email="test@example.com",
        password="password123"
    )
    assert login.email == "test@example.com"
    assert login.password == "password123"
=======
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
    assert response.json()["message"] == "User registered successfully"
    assert response.json()["id"] == mock_uuid
    assert response.json()["role"] == "volunteer"

def test_register_user_email_exists(mock_supabase_client: MagicMock, mock_uuid: str):
    test_email = "existing@example.com"
    test_password = "password123"

    mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = \
        [{"id": mock_uuid}] # Simulate existing user

    response = client.post("/auth/register", json={"email": test_email, "password": test_password, "role": "volunteer"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_success(mock_supabase_client: MagicMock, hashed_password: str, mock_uuid: str):
    test_email = "test@login.com"
    test_role = "admin"

    mock_supabase_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = \
        [{"id": mock_uuid, "email": test_email, "password": hashed_password, "role": test_role}]

    response = client.post("/auth/login", json={"email": test_email, "password": "test_password_123"})

    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"
    assert response.json()["user_id"] == mock_uuid
    assert response.json()["role"] == test_role

def test_login_invalid_password(mock_supabase_client: MagicMock, hashed_password: str, mock_uuid: str):
    test_email = "test@login.com"
    wrong_password = "wrong_password"

    mock_supabase_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = \
        [{"id": mock_uuid, "email": test_email, "password": hashed_password, "role": "volunteer"}]

    response = client.post("/auth/login", json={"email": test_email, "password": wrong_password})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials."

def test_login_user_not_found(mock_supabase_client: MagicMock):
    test_email = "nonexistent@login.com"

    mock_supabase_client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = []

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

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

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
    assert response.json()["detail"] == "User account not found or already deleted."
>>>>>>> c7755f350084cea77c4aa9a597b23aaaaf0a615a
