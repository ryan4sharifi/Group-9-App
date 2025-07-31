import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_all_states():
    """Test getting all states"""
    response = client.get("/api/states")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Check if Texas is in the list
    texas = next((state for state in data if state["code"] == "TX"), None)
    assert texas is not None
    assert texas["name"] == "Texas"

def test_get_state_by_code():
    """Test getting a specific state by code"""
    response = client.get("/api/states/TX")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "TX"
    assert data["name"] == "Texas"

def test_get_state_by_code_not_found():
    """Test getting a non-existent state"""
    response = client.get("/api/states/ZZ")
    assert response.status_code == 404

def test_get_state_by_code_lowercase():
    """Test getting state with lowercase code"""
    response = client.get("/api/states/ca")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "CA"
    assert data["name"] == "California"
