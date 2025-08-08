import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_states_data():
    """Sample states data for testing"""
    return [
        {"code": "TX", "name": "Texas"},
        {"code": "CA", "name": "California"},
        {"code": "FL", "name": "Florida"},
        {"code": "NY", "name": "New York"}
    ]

@pytest.fixture 
def mock_single_state():
    """Single state data for testing"""
    return {"code": "TX", "name": "Texas"}

@patch('app.routes.states.supabase')
def test_get_all_states(mock_supabase, mock_states_data):
    """Test getting all states"""
    # Mock supabase response
    mock_response = MagicMock()
    mock_response.data = mock_states_data
    mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response
    
    response = client.get("/api/states")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 4
    
    # Check if Texas is in the list
    texas = next((state for state in data if state["code"] == "TX"), None)
    assert texas is not None
    assert texas["name"] == "Texas"

@patch('app.routes.states.supabase')
def test_get_all_states_error(mock_supabase):
    """Test getting all states with database error"""
    mock_supabase.table.return_value.select.return_value.order.return_value.execute.side_effect = Exception("Database error")
    
    response = client.get("/api/states")
    assert response.status_code == 500
    assert "Failed to retrieve states" in response.json()["detail"]

@patch('app.routes.states.supabase')
def test_get_state_by_code(mock_supabase, mock_single_state):
    """Test getting a specific state by code"""
    # Mock supabase response
    mock_response = MagicMock()
    mock_response.data = mock_single_state
    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
    
    response = client.get("/api/states/TX")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "TX"
    assert data["name"] == "Texas"

@patch('app.routes.states.supabase')
def test_get_state_by_code_not_found(mock_supabase):
    """Test getting a non-existent state"""
    # Mock supabase response for not found - throw exception like real Supabase would
    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.side_effect = Exception("not found")
    
    response = client.get("/api/states/ZZ")
    assert response.status_code == 500  # Will be 500 due to exception handling

@patch('app.routes.states.supabase')
def test_get_state_by_code_database_error(mock_supabase):
    """Test getting state with database error"""
    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.side_effect = Exception("Database connection failed")
    
    response = client.get("/api/states/TX")
    assert response.status_code == 500
    assert "Failed to retrieve state" in response.json()["detail"]

@patch('app.routes.states.supabase')
def test_get_state_by_code_lowercase(mock_supabase):
    """Test getting state with lowercase code"""
    # Mock supabase response - verify uppercase conversion
    mock_response = MagicMock()
    mock_response.data = {"code": "CA", "name": "California"}
    mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
    
    response = client.get("/api/states/ca")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "CA"
    assert data["name"] == "California"
    
    # Verify that the code was converted to uppercase in the database query
    mock_supabase.table.return_value.select.return_value.eq.assert_called_with("code", "CA")

@patch('app.routes.states.supabase')
def test_initialize_states(mock_supabase):
    """Test initializing states table"""
    # Mock successful insert response
    mock_response = MagicMock()
    mock_response.data = [{"code": "TX", "name": "Texas"}] * 50  # Mock 50 states
    mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
    
    response = client.post("/api/states/initialize")
    assert response.status_code == 200
    data = response.json()
    assert "Successfully initialized 50 states" in data["message"]
    assert "data" in data

@patch('app.routes.states.supabase')
def test_initialize_states_error(mock_supabase):
    """Test initializing states with database error"""
    mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("Insert failed")
    
    response = client.post("/api/states/initialize")
    assert response.status_code == 500
    assert "Failed to initialize states" in response.json()["detail"]

def test_state_model_validation():
    """Test State model validation"""
    from app.routes.states import State
    
    # Valid state
    state = State(code="TX", name="Texas")
    assert state.code == "TX"
    assert state.name == "Texas"
