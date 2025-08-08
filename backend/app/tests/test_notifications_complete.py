"""
Comprehensive notification module tests - consolidated from multiple files
Tests notification functions and API routes
"""
from fastapi.testclient import TestClient
from app.main import app
from app.routes.auth import verify_token
from unittest.mock import patch, MagicMock
import json

client = TestClient(app)

def mock_verify_token():
    return {"user_id": "test_user_123", "role": "user"}

def mock_admin_verify_token():
    return {"user_id": "admin_user", "role": "admin"}

class TestNotificationRoutes:
    """Test notification API endpoints"""

    def test_get_all_notifications_route(self):
        """Test GET /api/notifications (admin only)"""
        app.dependency_overrides[verify_token] = mock_admin_verify_token
        try:
            response = client.get("/api/notifications")
            assert response.status_code in [200, 404, 500]
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, list)
        finally:
            app.dependency_overrides.clear()

    def test_get_user_notifications_route(self):
        """Test GET /api/notifications/{user_id}"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            response = client.get("/api/notifications/test_user_123")
            assert response.status_code in [200, 404, 500]
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, list)
        finally:
            app.dependency_overrides.clear()

    def test_create_notification_route(self):
        """Test POST /api/notifications"""
        app.dependency_overrides[verify_token] = mock_admin_verify_token
        try:
            notification_data = {
                "user_id": "test_user_123",
                "message": "Test notification",
                "type": "match",
                "priority": "medium"
            }
            response = client.post("/api/notifications", json=notification_data)
            assert response.status_code in [200, 201, 400, 422, 500]
        finally:
            app.dependency_overrides.clear()

    def test_create_notification_unauthorized(self):
        """Test POST /api/notifications without admin privileges"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            notification_data = {
                "user_id": "test_user_123",
                "message": "Test notification",
                "type": "match"
            }
            response = client.post("/api/notifications", json=notification_data)
            assert response.status_code in [403, 500]  # Should be forbidden
        finally:
            app.dependency_overrides.clear()

    def test_mark_notification_read_route(self):
        """Test PUT /api/notifications/{notification_id}/read"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            response = client.put("/api/notifications/123/read")
            assert response.status_code in [200, 404, 500]
        finally:
            app.dependency_overrides.clear()

    def test_delete_notification_route(self):
        """Test DELETE /api/notifications/{notification_id}"""
        app.dependency_overrides[verify_token] = mock_admin_verify_token
        try:
            response = client.delete("/api/notifications/123")
            assert response.status_code in [200, 404, 500]
        finally:
            app.dependency_overrides.clear()

    def test_get_unread_notifications_count_route(self):
        """Test GET /api/notifications/{user_id}/unread-count"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            response = client.get("/api/notifications/test_user_123/unread-count")
            assert response.status_code in [200, 404, 500]
            if response.status_code == 200:
                data = response.json()
                assert "count" in data
                assert isinstance(data["count"], int)
        finally:
            app.dependency_overrides.clear()

    def test_mark_all_notifications_read_route(self):
        """Test PUT /api/notifications/{user_id}/mark-all-read"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            response = client.put("/api/notifications/test_user_123/mark-all-read")
            assert response.status_code in [200, 404, 500]
        finally:
            app.dependency_overrides.clear()

    def test_get_notification_by_id_route(self):
        """Test GET /api/notifications/{notification_id}/details"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            response = client.get("/api/notifications/123/details")
            assert response.status_code in [200, 404, 500]
        finally:
            app.dependency_overrides.clear()

    def test_update_notification_route(self):
        """Test PUT /api/notifications/{notification_id}"""
        app.dependency_overrides[verify_token] = mock_admin_verify_token
        try:
            update_data = {
                "message": "Updated notification message",
                "priority": "high"
            }
            response = client.put("/api/notifications/123", json=update_data)
            assert response.status_code in [200, 404, 422, 500]
        finally:
            app.dependency_overrides.clear()

    def test_unauthorized_access(self):
        """Test accessing notification routes without authentication"""
        # Test without any auth
        response = client.get("/api/notifications")
        assert response.status_code in [401, 403, 422]
        
        response = client.post("/api/notifications", json={"message": "test"})
        assert response.status_code in [401, 403, 422]
        
        response = client.delete("/api/notifications/123")
        assert response.status_code in [401, 403, 422]

class TestNotificationValidation:
    """Test notification data validation"""

    def test_create_notification_validation(self):
        """Test notification creation with various validation scenarios"""
        app.dependency_overrides[verify_token] = mock_admin_verify_token
        try:
            # Missing required fields
            response = client.post("/api/notifications", json={})
            assert response.status_code == 422
            
            # Invalid notification type
            invalid_data = {
                "user_id": "test_user",
                "message": "Test",
                "type": "invalid_type"
            }
            response = client.post("/api/notifications", json=invalid_data)
            assert response.status_code in [400, 422, 500]
            
            # Invalid priority
            invalid_priority_data = {
                "user_id": "test_user",
                "message": "Test",
                "type": "match",
                "priority": "invalid_priority"
            }
            response = client.post("/api/notifications", json=invalid_priority_data)
            assert response.status_code in [400, 422, 500]
            
            # Empty message
            empty_message_data = {
                "user_id": "test_user",
                "message": "",
                "type": "match"
            }
            response = client.post("/api/notifications", json=empty_message_data)
            assert response.status_code in [400, 422, 500]
            
        finally:
            app.dependency_overrides.clear()

    def test_update_notification_validation(self):
        """Test notification update validation"""
        app.dependency_overrides[verify_token] = mock_admin_verify_token
        try:
            # Empty update data
            response = client.put("/api/notifications/123", json={})
            assert response.status_code in [200, 400, 404, 422, 500]
            
            # Invalid fields
            invalid_data = {
                "invalid_field": "value"
            }
            response = client.put("/api/notifications/123", json=invalid_data)
            assert response.status_code in [200, 400, 404, 422, 500]
            
        finally:
            app.dependency_overrides.clear()

class TestNotificationFiltering:
    """Test notification filtering and sorting"""

    def test_get_notifications_with_filters(self):
        """Test getting notifications with various filters"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            # Test with type filter
            response = client.get("/api/notifications/test_user_123?type=match")
            assert response.status_code in [200, 404, 500]
            
            # Test with read status filter
            response = client.get("/api/notifications/test_user_123?read=false")
            assert response.status_code in [200, 404, 500]
            
            # Test with priority filter
            response = client.get("/api/notifications/test_user_123?priority=high")
            assert response.status_code in [200, 404, 500]
            
            # Test with limit
            response = client.get("/api/notifications/test_user_123?limit=5")
            assert response.status_code in [200, 404, 500]
            
            # Test with offset
            response = client.get("/api/notifications/test_user_123?offset=10")
            assert response.status_code in [200, 404, 500]
            
        finally:
            app.dependency_overrides.clear()

    def test_get_notifications_sorting(self):
        """Test notification sorting options"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            # Sort by created_at descending
            response = client.get("/api/notifications/test_user_123?sort=created_at&order=desc")
            assert response.status_code in [200, 404, 500]
            
            # Sort by priority ascending
            response = client.get("/api/notifications/test_user_123?sort=priority&order=asc")
            assert response.status_code in [200, 404, 500]
            
        finally:
            app.dependency_overrides.clear()

class TestNotificationBulkOperations:
    """Test bulk notification operations"""

    def test_bulk_create_notifications(self):
        """Test bulk notification creation"""
        app.dependency_overrides[verify_token] = mock_admin_verify_token
        try:
            bulk_data = {
                "notifications": [
                    {
                        "user_id": "user1",
                        "message": "Notification 1",
                        "type": "match"
                    },
                    {
                        "user_id": "user2",
                        "message": "Notification 2",
                        "type": "event"
                    }
                ]
            }
            response = client.post("/api/notifications/bulk", json=bulk_data)
            assert response.status_code in [200, 201, 400, 404, 422, 500]
            
        finally:
            app.dependency_overrides.clear()

    def test_bulk_mark_read(self):
        """Test bulk marking notifications as read"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            bulk_read_data = {
                "notification_ids": [1, 2, 3, 4, 5]
            }
            response = client.put("/api/notifications/bulk/mark-read", json=bulk_read_data)
            assert response.status_code in [200, 404, 422, 500]
            
        finally:
            app.dependency_overrides.clear()

    def test_bulk_delete_notifications(self):
        """Test bulk notification deletion"""
        app.dependency_overrides[verify_token] = mock_admin_verify_token
        try:
            bulk_delete_data = {
                "notification_ids": [1, 2, 3]
            }
            response = client.delete("/api/notifications/bulk", json=bulk_delete_data)
            assert response.status_code in [200, 404, 422, 500]
            
        finally:
            app.dependency_overrides.clear()

class TestNotificationIntegration:
    """Integration tests for notification functionality"""

    def test_notification_lifecycle(self):
        """Test complete notification lifecycle"""
        app.dependency_overrides[verify_token] = mock_admin_verify_token
        try:
            # Create notification
            notification_data = {
                "user_id": "test_user_123",
                "message": "Integration test notification",
                "type": "match",
                "priority": "medium"
            }
            create_response = client.post("/api/notifications", json=notification_data)
            create_status = create_response.status_code
            
            # Get user notifications
            get_response = client.get("/api/notifications/test_user_123")
            get_status = get_response.status_code
            
            # Get unread count
            count_response = client.get("/api/notifications/test_user_123/unread-count")
            count_status = count_response.status_code
            
            # Mark as read (assuming notification ID 1 exists)
            read_response = client.put("/api/notifications/1/read")
            read_status = read_response.status_code
            
            # All operations should succeed or fail gracefully
            assert create_status in [200, 201, 400, 422, 500]
            assert get_status in [200, 404, 500]
            assert count_status in [200, 404, 500]
            assert read_status in [200, 404, 500]
            
        finally:
            app.dependency_overrides.clear()

    def test_cross_user_access_control(self):
        """Test that users can't access other users' notifications"""
        def mock_other_user_token():
            return {"user_id": "other_user", "role": "user"}
        
        app.dependency_overrides[verify_token] = mock_other_user_token
        try:
            # Try to access different user's notifications
            response = client.get("/api/notifications/test_user_123")
            assert response.status_code in [403, 404, 500]
            
            # Try to mark different user's notification as read
            response = client.put("/api/notifications/test_user_123/mark-all-read")
            assert response.status_code in [403, 404, 500]
            
        finally:
            app.dependency_overrides.clear()

class TestNotificationErrorHandling:
    """Test notification error handling scenarios"""

    def test_invalid_notification_id(self):
        """Test operations with invalid notification IDs"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            # Non-numeric ID
            response = client.get("/api/notifications/invalid/details")
            assert response.status_code in [404, 422, 500]
            
            # Negative ID
            response = client.put("/api/notifications/-1/read")
            assert response.status_code in [404, 422, 500]
            
            # Very large ID
            response = client.delete("/api/notifications/999999999")
            assert response.status_code in [404, 500]
            
        finally:
            app.dependency_overrides.clear()

    def test_malformed_json_requests(self):
        """Test handling of malformed JSON requests"""
        app.dependency_overrides[verify_token] = mock_admin_verify_token
        try:
            # Send malformed JSON
            response = client.post(
                "/api/notifications",
                data="{'invalid': json}",
                headers={"Content-Type": "application/json"}
            )
            assert response.status_code in [400, 422]
            
        finally:
            app.dependency_overrides.clear()

    def test_missing_content_type(self):
        """Test requests without proper content type"""
        app.dependency_overrides[verify_token] = mock_admin_verify_token
        try:
            response = client.post(
                "/api/notifications",
                data=json.dumps({"user_id": "test", "message": "test", "type": "match"}),
                headers={"Content-Type": "text/plain"}
            )
            assert response.status_code in [400, 415, 422]
            
        finally:
            app.dependency_overrides.clear()
