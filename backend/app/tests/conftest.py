# backend/app/tests/conftest.py
import pytest
from unittest.mock import MagicMock, patch
from passlib.hash import bcrypt as passlib_bcrypt
import bcrypt # For Pylance

@pytest.fixture(autouse=True)
def mock_supabase_client():
    # Patch multiple import paths to ensure the mock is used everywhere
    with patch('app.supabase_client.supabase', autospec=True) as mock_supabase, \
         patch('app.routes.auth.supabase', autospec=True) as mock_auth_supabase, \
         patch('app.routes.profile.supabase', autospec=True) as mock_profile_supabase, \
         patch('app.routes.events.supabase', autospec=True) as mock_events_supabase, \
         patch('app.routes.history.supabase', autospec=True) as mock_history_supabase, \
         patch('app.routes.match.supabase', autospec=True) as mock_match_supabase, \
         patch('app.routes.notifications.supabase', autospec=True) as mock_notifications_supabase:
        
        # Configure one mock and use it for all paths
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table

        # Create mocks for select, eq, limit, insert, update, delete
        mock_select_builder = MagicMock()
        mock_eq_builder = MagicMock()
        mock_limit_builder = MagicMock()
        mock_insert_builder = MagicMock()
        mock_update_builder = MagicMock()
        mock_delete_builder = MagicMock()

        # Chain method calls
        mock_table.select.return_value = mock_select_builder
        mock_select_builder.eq.return_value = mock_eq_builder
        mock_eq_builder.limit.return_value = mock_limit_builder # For select().eq().limit().execute()

        mock_table.insert.return_value = mock_insert_builder
        mock_table.update.return_value = mock_update_builder
        mock_table.delete.return_value = mock_delete_builder

        # Copy the same configuration to all other mock instances
        for mock_sb in [mock_auth_supabase, mock_profile_supabase, 
                       mock_events_supabase, mock_history_supabase, mock_match_supabase, 
                       mock_notifications_supabase]:
            mock_sb.table.return_value = mock_table

        # --- IMPORTANT: Configure .execute(), .single().execute(), .maybe_single().execute() ---
        # For a standard .select().execute() or .select().eq().execute()
        mock_select_builder.execute.return_value.data = [] # Default: empty list for many rows
        mock_eq_builder.execute.return_value.data = []    # Default: empty list for many rows
        mock_limit_builder.execute.return_value.data = [] # Default: empty list for many rows

        # For .select().eq().single().execute()
        mock_eq_builder.single.return_value.execute.return_value.data = None # Default: no row found for single()
        mock_select_builder.single.return_value.execute.return_value.data = None # For select().single().execute()

        # For .select().eq().maybe_single().execute()
        mock_eq_builder.maybe_single.return_value.execute.return_value.data = None # Default: no row found for maybe_single()
        mock_select_builder.maybe_single.return_value.execute.return_value.data = None # For select().maybe_single().execute()


        # Default for insert/update/delete results (assuming they return data on success)
        mock_insert_builder.execute.return_value.data = [{"id": "mock-inserted-uuid-1"}]
        mock_update_builder.execute.return_value.data = [{"id": "mock-updated-uuid-1"}]
        mock_delete_builder.execute.return_value.data = [{"id": "mock-deleted-uuid-1"}]


        yield mock_supabase # Provide the mocked object to tests

# Fixture for a common test user password hash
@pytest.fixture
def hashed_password():
    return passlib_bcrypt.hash("test_password_123")

# Fixture for a valid test UUID (to avoid "invalid input syntax for type uuid" errors)
@pytest.fixture
def mock_uuid():
    # Use a real UUID string to satisfy type checks in backend
    return "123e4567-e89b-12d3-a456-426614174000"