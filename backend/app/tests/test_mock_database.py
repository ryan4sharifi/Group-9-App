import pytest
from app.mock_database import (
    generate_id,
    get_current_timestamp,
    MockSupabaseResponse,
    MockSupabaseTable,
    MockSupabaseClient,
    initialize_mock_data,
    MOCK_USERS,
    MOCK_PROFILES,
    MOCK_EVENTS
)

def test_generate_id():
    """Test ID generation"""
    id1 = generate_id()
    id2 = generate_id()
    assert isinstance(id1, str)
    assert isinstance(id2, str)
    assert id1 != id2  # Should be unique

def test_get_current_timestamp():
    """Test timestamp generation"""
    timestamp = get_current_timestamp()
    assert isinstance(timestamp, str)
    assert "T" in timestamp  # ISO format

def test_mock_supabase_response():
    """Test MockSupabaseResponse"""
    response = MockSupabaseResponse(data={"test": "data"})
    assert response.data == {"test": "data"}
    assert response.error is None

def test_mock_supabase_table():
    """Test MockSupabaseTable initialization"""
    table = MockSupabaseTable("test_table")
    assert table.table_name == "test_table"

def test_mock_supabase_client():
    """Test MockSupabaseClient"""
    client = MockSupabaseClient()
    table = client.table("test_table")
    assert isinstance(table, MockSupabaseTable)

def test_initialize_mock_data():
    """Test mock data initialization"""
    initialize_mock_data()
    assert len(MOCK_USERS) > 0
    assert len(MOCK_PROFILES) > 0
    assert len(MOCK_EVENTS) > 0

def test_mock_data_structure():
    """Test that mock data has expected structure"""
    # Initialize mock data first
    initialize_mock_data()
    
    # Check users
    for user_id, user in MOCK_USERS.items():
        assert "email" in user
        assert "role" in user
        assert "created_at" in user
    
    # Check profiles - some may be minimal profiles created during registration
    for profile_id, profile in MOCK_PROFILES.items():
        # All profiles should have skills array
        assert "skills" in profile
        
        # Only check for full profile fields if it's not a minimal registration profile
        if "full_name" in profile:
            assert "city" in profile  # Full profiles should have complete data
    
    # Check events
    for event_id, event in MOCK_EVENTS.items():
        assert "name" in event
        assert "required_skills" in event
        assert "urgency" in event
