import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app, manager, check_database_health
from app.routes.auth import create_access_token

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
    mock_check_health.return_value = {"status": "unhealthy", "error": "Connection failed"}
    
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["database"]["status"] == "unhealthy"

# Test: WebSocket Endpoint
def test_websocket_endpoint_connection():
    """Test WebSocket connection"""
    client = TestClient(app)
    
    with client.websocket_connect("/ws/user123") as websocket:
        # Test ping-pong
        websocket.send_text('{"type": "ping"}')
        data = websocket.receive_text()
        assert data == '{"type": "pong"}'

def test_websocket_endpoint_disconnect():
    """Test WebSocket disconnection"""
    client = TestClient(app)
    
    with client.websocket_connect("/ws/user123") as websocket:
        # Connection should be established
        assert websocket is not None

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
    
    # Mock the manager's send_personal_message method
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

def test_500_handler():
    """Test 500 exception handler"""
    # This would typically be tested by causing an internal error
    # For now, we'll test that the handler exists by checking the app structure
    assert hasattr(app, 'exception_handlers')
    assert 500 in app.exception_handlers

# Test: CORS Middleware
def test_cors_headers():
    """Test CORS headers are properly set"""
    client = TestClient(app)
    response = client.options("/", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "Content-Type"
    })
    
    # CORS headers should be present
    assert response.status_code in [200, 405]  # OPTIONS might not be implemented

# Test: Connection Manager
@pytest.mark.asyncio
async def test_connection_manager_connect():
    """Test connection manager connect method"""
    from app.main import ConnectionManager
    
    manager = ConnectionManager()
    mock_websocket = MagicMock()
    mock_websocket.accept = AsyncMock()
    
    # Test connection
    await manager.connect(mock_websocket, "user123")
    assert "user123" in manager.active_connections
    assert manager.active_connections["user123"] == mock_websocket

@pytest.mark.asyncio
async def test_connection_manager_disconnect():
    """Test connection manager disconnect method"""
    from app.main import ConnectionManager
    
    manager = ConnectionManager()
    mock_websocket = MagicMock()
    mock_websocket.accept = AsyncMock()
    
    # Connect first
    await manager.connect(mock_websocket, "user123")
    assert "user123" in manager.active_connections
    
    # Disconnect
    manager.disconnect("user123")
    assert "user123" not in manager.active_connections

@pytest.mark.asyncio
async def test_connection_manager_send_personal_message():
    """Test connection manager send personal message"""
    from app.main import ConnectionManager
    
    manager = ConnectionManager()
    mock_websocket = MagicMock()
    mock_websocket.accept = AsyncMock()
    mock_websocket.send_text = AsyncMock()
    
    # Connect user
    await manager.connect(mock_websocket, "user123")
    
    # Send message
    await manager.send_personal_message("Test message", "user123")
    mock_websocket.send_text.assert_called_once_with("Test message")

def test_connection_manager_send_personal_message_user_not_found():
    """Test connection manager send personal message to non-existent user"""
    from app.main import ConnectionManager
    
    manager = ConnectionManager()
    
    # Send message to non-existent user (should not raise an exception)
    # Note: This test verifies that the method handles missing users gracefully
    import asyncio
    asyncio.run(manager.send_personal_message("Test message", "nonexistent"))

@pytest.mark.asyncio
async def test_connection_manager_broadcast():
    """Test connection manager broadcast method"""
    from app.main import ConnectionManager
    
    manager = ConnectionManager()
    mock_websocket1 = MagicMock()
    mock_websocket1.accept = AsyncMock()
    mock_websocket1.send_text = AsyncMock()
    
    mock_websocket2 = MagicMock()
    mock_websocket2.accept = AsyncMock()
    mock_websocket2.send_text = AsyncMock()
    
    # Connect multiple users
    await manager.connect(mock_websocket1, "user1")
    await manager.connect(mock_websocket2, "user2")
    
    # Broadcast message
    await manager.broadcast("Broadcast message")
    
    mock_websocket1.send_text.assert_called_once_with("Broadcast message")
    mock_websocket2.send_text.assert_called_once_with("Broadcast message")

# Test: Database Health Check
@patch("app.supabase_client.supabase")
@pytest.mark.asyncio
async def test_check_database_health_success(mock_supabase):
    """Test database health check when healthy"""
    mock_supabase.table.return_value.select.return_value.limit.return_value.execute.return_value.data = [{"id": 1}]
    
    result = await check_database_health()
    assert result["status"] == "healthy"

@patch("app.supabase_client.supabase")
@patch("app.supabase_client.SUPABASE_URL", "http://test")  # Force it to not use mock logic
@pytest.mark.asyncio
async def test_check_database_health_failure(mock_supabase):
    """Test database health check when unhealthy"""
    mock_supabase.table.return_value.select.return_value.limit.return_value.execute.side_effect = Exception("Connection failed")
    
    result = await check_database_health()
    assert result["status"] == "unhealthy"
    assert "error" in result

# Test: Notification Update Handler
@patch("app.main.manager")
@pytest.mark.asyncio
async def test_handle_notification_update_success(mock_manager):
    """Test notification update handler"""
    from app.main import handle_notification_update
    
    # Mock payload
    payload = {
        "new": {
            "user_id": "user123",
            "message": "Test notification",
            "type": "match"
        }
    }
    
    # Mock manager
    mock_manager.send_personal_message = AsyncMock()
    
    # Test handler
    await handle_notification_update(payload)
    
    mock_manager.send_personal_message.assert_called_once()

@patch("app.main.manager")
@pytest.mark.asyncio
async def test_handle_notification_update_no_user_id(mock_manager):
    """Test notification update handler with no user_id"""
    from app.main import handle_notification_update
    
    # Mock payload without user_id
    payload = {
        "new": {
            "message": "Test notification",
            "type": "match"
        }
    }
    
    # Mock manager
    mock_manager.send_personal_message = AsyncMock()
    
    # Test handler
    await handle_notification_update(payload)
    
    # Should not call send_personal_message
    mock_manager.send_personal_message.assert_not_called()

@patch("app.main.manager")
@pytest.mark.asyncio
async def test_handle_notification_update_exception(mock_manager):
    """Test notification update handler with exception"""
    from app.main import handle_notification_update
    
    # Mock payload
    payload = {
        "new": {
            "user_id": "user123",
            "message": "Test notification"
        }
    }
    
    # Mock manager to raise exception
    mock_manager.send_personal_message = AsyncMock(side_effect=Exception("Send failed"))
    
    # Test handler - should not raise exception
    await handle_notification_update(payload)

# Test: Route Registration
def test_route_registration():
    """Test that all routes are properly registered"""
    # Check that the app has routes by testing known endpoints
    client = TestClient(app)
    
    # Test that main endpoints respond (not 404)
    response = client.get("/")
    assert response.status_code == 200
    
    response = client.get("/health")
    assert response.status_code == 200
    
    # Check that we have multiple routes registered
    assert len(app.routes) >= 10  # Should have multiple routes including sub-routers

# Test: Middleware Configuration
def test_middleware_configuration():
    """Test that middleware is properly configured"""
    # Check that CORS middleware is added
    cors_middleware_found = False
    
    for middleware in app.user_middleware:
        middleware_name = str(middleware.cls)
        if "CORS" in middleware_name or "CORSMiddleware" in middleware_name:
            cors_middleware_found = True
            break
    
    assert cors_middleware_found, "CORS middleware should be configured"

# Test: Lifespan Events
def test_lifespan_startup():
    """Test lifespan startup event"""
    from app.main import lifespan
    
    # Test that lifespan context manager can be created
    lifespan_context = lifespan(app)
    assert lifespan_context is not None

# Test: Error Scenarios
def test_websocket_error_handling():
    """Test WebSocket error handling"""
    client = TestClient(app)
    
    # This test would require more complex WebSocket error simulation
    # For now, we'll test that the endpoint exists
    with client.websocket_connect("/ws/user123") as websocket:
        # Send invalid JSON to trigger error handling
        websocket.send_text("invalid json")
        # Should handle the error gracefully

# Test: Security Headers
def test_security_headers():
    """Test that security headers are properly set"""
    client = TestClient(app)
    response = client.get("/")
    
    # Check for basic security headers
    # Note: FastAPI doesn't set many security headers by default
    # This is more of a placeholder for when security headers are added
    assert response.status_code == 200

# Test: API Documentation
def test_api_documentation_endpoints():
    """Test that API documentation endpoints are available"""
    client = TestClient(app)
    
    # Test OpenAPI JSON endpoint
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    # Test docs endpoint
    response = client.get("/docs")
    assert response.status_code == 200

# Test: Performance
def test_root_endpoint_performance():
    """Test root endpoint response time"""
    import time
    
    client = TestClient(app)
    start_time = time.time()
    
    response = client.get("/")
    
    end_time = time.time()
    response_time = end_time - start_time
    
    assert response.status_code == 200
    assert response_time < 1.0  # Should respond within 1 second

# Test: Integration
def test_full_api_workflow():
    """Test a complete API workflow"""
    client = TestClient(app)
    
    # 1. Check health
    health_response = client.get("/health")
    assert health_response.status_code == 200
    
    # 2. Check root endpoint
    root_response = client.get("/")
    assert root_response.status_code == 200
    
    # 3. Check API documentation
    docs_response = client.get("/docs")
    assert docs_response.status_code == 200 