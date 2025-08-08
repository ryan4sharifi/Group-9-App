import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app, manager, handle_notification_update, ConnectionManager
from app.supabase_client import check_database_health
from app.routes.auth import create_access_token
import json

# Test: Root Endpoint
def test_root_endpoint():
    """Test the root endpoint"""
    client = TestClient(app)
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Volunteer Management System API v2.0"
    assert data["status"] == "operational"
    assert "JWT Authentication" in data["features"]
    assert "Real-time Notifications" in data["features"]

# Test: Health Check Endpoint
@patch("app.main.check_database_health")
def test_health_check_endpoint(mock_check_health):
    """Test the health check endpoint"""
    mock_check_health.return_value = {"status": "healthy"}
    
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "database" in data
    assert "websocket_connections" in data

@patch("app.main.check_database_health")
def test_health_check_endpoint_database_unhealthy(mock_check_health):
    """Test health check when database is unhealthy"""
    mock_check_health.side_effect = Exception("Database connection failed")
    
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unhealthy"
    assert "error" in data

# Test: WebSocket Endpoint
def test_websocket_endpoint_connection():
    """Test WebSocket connection"""
    client = TestClient(app)
    
    with client.websocket_connect("/ws/test-user-123") as websocket:
        # Test ping-pong
        websocket.send_text('{"type": "ping"}')
        data = websocket.receive_text()
        assert data == '{"type": "pong"}'
        
        # Test regular message
        websocket.send_text("Hello")
        data = websocket.receive_text()
        assert data == "Message received: Hello"

# Test: Connection Manager
@pytest.mark.asyncio
async def test_connection_manager_connect():
    """Test connection manager connect functionality"""
    test_manager = ConnectionManager()
    mock_websocket = MagicMock()
    mock_websocket.accept = AsyncMock()
    
    await test_manager.connect(mock_websocket, "test-user-456")
    assert "test-user-456" in test_manager.active_connections
    assert test_manager.active_connections["test-user-456"] == mock_websocket

@pytest.mark.asyncio
async def test_connection_manager_disconnect():
    """Test connection manager disconnect functionality"""
    test_manager = ConnectionManager()
    mock_websocket = MagicMock()
    
    # Add connection first
    test_manager.active_connections["test-user-789"] = mock_websocket
    assert "test-user-789" in test_manager.active_connections
    
    # Test disconnect
    test_manager.disconnect("test-user-789")
    assert "test-user-789" not in test_manager.active_connections

@pytest.mark.asyncio
async def test_connection_manager_send_personal_message():
    """Test sending personal message through connection manager"""
    test_manager = ConnectionManager()
    mock_websocket = MagicMock()
    mock_websocket.send_text = AsyncMock()
    
    # Add connection
    test_manager.active_connections["test-user-message"] = mock_websocket
    
    # Send message
    await test_manager.send_personal_message("Hello", "test-user-message")
    mock_websocket.send_text.assert_called_once_with("Hello")

@pytest.mark.asyncio
async def test_connection_manager_broadcast():
    """Test broadcasting message to all connections"""
    test_manager = ConnectionManager()
    
    # Setup multiple mock connections
    mock_ws1, mock_ws2 = MagicMock(), MagicMock()
    mock_ws1.send_text = AsyncMock()
    mock_ws2.send_text = AsyncMock()
    
    test_manager.active_connections["user1"] = mock_ws1
    test_manager.active_connections["user2"] = mock_ws2
    
    await test_manager.broadcast("Broadcast message")
    
    mock_ws1.send_text.assert_called_once_with("Broadcast message")
    mock_ws2.send_text.assert_called_once_with("Broadcast message")

# Test async functions with pytest-asyncio
@pytest.mark.asyncio
async def test_check_database_health_success():
    """Test database health check success"""
    with patch('app.supabase_client.supabase') as mock_supabase:
        mock_supabase.table.return_value.select.return_value.limit.return_value.execute.return_value.data = [{"id": 1}]
        
        result = await check_database_health()
        assert result["status"] == "healthy"
        assert result["database"] == "supabase"

@pytest.mark.asyncio
async def test_check_database_health_failure():
    """Test database health check failure"""
    with patch('app.supabase_client.supabase') as mock_supabase:
        mock_supabase.table.return_value.select.return_value.limit.return_value.execute.side_effect = Exception("Connection failed")
        
        result = await check_database_health()
        assert result["status"] == "unhealthy"
        assert "error" in result

@pytest.mark.asyncio 
async def test_handle_notification_update_success():
    """Test handling notification updates"""
    mock_manager = MagicMock()
    mock_manager.send_personal_message = AsyncMock()
    
    payload = {
        "new": {
            "user_id": "test-user",
            "message": "Test notification"
        }
    }
    
    with patch('app.main.manager', mock_manager):
        await handle_notification_update(payload)
        mock_manager.send_personal_message.assert_called_once()

@pytest.mark.asyncio
async def test_handle_notification_update_no_user_id():
    """Test handling notification updates without user_id"""
    mock_manager = MagicMock()
    mock_manager.send_personal_message = AsyncMock()
    
    payload = {
        "new": {
            "message": "Test notification"
            # No user_id
        }
    }
    
    with patch('app.main.manager', mock_manager):
        await handle_notification_update(payload)
        mock_manager.send_personal_message.assert_not_called()

@pytest.mark.asyncio
async def test_handle_notification_update_exception():
    """Test handling notification updates with exception"""
    # Test with malformed payload
    malformed_payload = {"invalid": "data"}
    
    # Should not raise exception
    await handle_notification_update(malformed_payload)

# Test: Real-time Notification Endpoint
def test_notify_realtime_endpoint_unauthorized():
    """Test real-time notification endpoint without admin access"""
    # Create non-admin token
    token_data = {"sub": "user123", "role": "volunteer"}
    token = create_access_token(token_data)
    
    client = TestClient(app)
    response = client.post("/api/notify-realtime", 
                          json={"user_id": "user456", "message": "Test message"},
                          headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 403
    assert "Admin access required" in response.json()["error"]

@patch("app.main.manager")
def test_notify_realtime_endpoint_success(mock_manager):
    """Test real-time notification endpoint with admin access"""
    # Create admin token
    token_data = {"sub": "admin123", "role": "admin"}
    token = create_access_token(token_data)
    
    # Mock the manager's broadcast method
    mock_manager.broadcast = AsyncMock()
    
    client = TestClient(app)
    response = client.post("/api/notify-realtime", 
                          json={"user_id": "user456", "message": "Test message"},
                          headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert response.json()["message"] == "Real-time notification sent"

# Test: Exception Handlers
def test_404_handler():
    """Test 404 exception handler"""
    client = TestClient(app)
    response = client.get("/nonexistent-endpoint")
    
    assert response.status_code == 404
    assert response.json()["message"] == "Endpoint not found"

# Test: App Configuration
def test_app_title_and_description():
    """Test that app has correct title and description"""
    assert app.title == "Volunteer Management System"
    assert app.description == "A comprehensive volunteer management system with real-time notifications"
    assert app.version == "2.0.0"

# Test: API Documentation Endpoints
def test_api_documentation_endpoints():
    """Test that API documentation endpoints are available"""
    client = TestClient(app)
    
    # Test OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    # Test docs
    response = client.get("/docs")
    assert response.status_code == 200
    
    # Test redoc
    response = client.get("/redoc")
    assert response.status_code == 200

# Test: Route Registration
def test_route_registration():
    """Test that all expected routes are registered"""
    routes = [route.path for route in app.routes]
    
    # Check that main routes exist
    assert "/" in routes
    assert "/health" in routes
    assert "/ws/{user_id}" in routes
    assert "/api/notify-realtime" in routes
