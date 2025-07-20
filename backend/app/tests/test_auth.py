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
