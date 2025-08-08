import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, Mock
from app.main import app
from app.utils.distance_db import DistanceCache

# Create test client
client = TestClient(app)

class TestDistanceRoutes:
    """Test distance calculation API routes"""
    
    def test_calculate_distance_between_addresses_unauthorized(self):
        """Test distance calculation without authentication"""
        request_data = {
            "origin_address": "Houston, TX",
            "destination_address": "Dallas, TX"
        }
        
        response = client.post("/api/distance/calculate", json=request_data)
        assert response.status_code == 403  # Forbidden (not authenticated)
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.distance_calculator')
    def test_calculate_distance_between_addresses_success(self, mock_calculator, mock_verify):
        """Test successful distance calculation between addresses"""
        # Mock authentication
        mock_verify.return_value = {"user_id": "user123", "role": "volunteer"}
        
        # Mock distance calculation
        mock_calculator.calculate_distance.return_value = {
            "distance": {"text": "239 mi"},
            "duration": {"text": "3 hours 35 mins"},
            "origin_address": "Houston, TX, USA",
            "destination_address": "Dallas, TX, USA",
            "status": "OK"
        }
        
        request_data = {
            "origin_address": "Houston, TX",
            "destination_address": "Dallas, TX"
        }
        
        headers = {"Authorization": "Bearer valid_token"}
        response = client.post("/api/distance/calculate", json=request_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["distance"] == "239 mi"
        assert data["duration"] == "3 hours 35 mins"
        assert data["status"] == "OK"
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.distance_calculator')
    def test_calculate_distance_between_addresses_failure(self, mock_calculator, mock_verify):
        """Test distance calculation failure"""
        # Mock authentication
        mock_verify.return_value = {"user_id": "user123", "role": "volunteer"}
        
        # Mock distance calculation failure
        mock_calculator.calculate_distance.return_value = None
        
        request_data = {
            "origin_address": "Invalid Address",
            "destination_address": "Another Invalid Address"
        }
        
        headers = {"Authorization": "Bearer valid_token"}
        response = client.post("/api/distance/calculate", json=request_data, headers=headers)
        
        assert response.status_code == 400
        assert "Could not calculate distance" in response.json()["detail"]
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.distance_calculator')
    def test_calculate_distance_between_addresses_exception(self, mock_calculator, mock_verify):
        """Test distance calculation with exception"""
        # Mock authentication
        mock_verify.return_value = {"user_id": "user123", "role": "volunteer"}
        
        # Mock distance calculation exception
        mock_calculator.calculate_distance.side_effect = Exception("API error")
        
        request_data = {
            "origin_address": "Houston, TX",
            "destination_address": "Dallas, TX"
        }
        
        headers = {"Authorization": "Bearer valid_token"}
        response = client.post("/api/distance/calculate", json=request_data, headers=headers)
        
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]
    
    def test_get_distance_to_event_unauthorized(self):
        """Test getting distance to event without authentication"""
        response = client.get("/api/events/event123/distance")
        assert response.status_code == 403  # Forbidden (not authenticated)
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.supabase')
    @patch('app.routes.distance.calculate_and_cache_distance')
    def test_get_distance_to_event_success(self, mock_calculate, mock_supabase, mock_verify):
        """Test successful distance to event calculation"""
        # Mock authentication
        mock_verify.return_value = {"user_id": "user123", "role": "volunteer"}
        
        # Mock event data
        mock_event_response = MagicMock()
        mock_event_response.data = [{
            "address1": "123 Main St",
            "address2": "Suite 100",
            "city": "Houston",
            "state": "TX",
            "zip_code": "77001"
        }]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_event_response
        
        # Mock distance calculation
        mock_calculate.return_value = {
            "distance_text": "15.2 mi",
            "duration_text": "22 mins",
            "distance_value": 24465,
            "duration_value": 1320,
            "cached": True,
            "expires_at": "2025-08-15T12:00:00Z"
        }
        
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/events/event123/distance", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["distance_text"] == "15.2 mi"
        assert data["duration_text"] == "22 mins"
        assert data["cached"] == True
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.supabase')
    def test_get_distance_to_event_not_found(self, mock_supabase, mock_verify):
        """Test distance to non-existent event"""
        # Mock authentication
        mock_verify.return_value = {"user_id": "user123", "role": "volunteer"}
        
        # Mock no event data
        mock_event_response = MagicMock()
        mock_event_response.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_event_response
        
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/events/nonexistent/distance", headers=headers)
        
        assert response.status_code == 404
        assert "Event not found" in response.json()["detail"]
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.supabase')
    @patch('app.routes.distance.calculate_and_cache_distance')
    def test_get_distance_to_event_calculation_failure(self, mock_calculate, mock_supabase, mock_verify):
        """Test distance calculation failure for event"""
        # Mock authentication
        mock_verify.return_value = {"user_id": "user123", "role": "volunteer"}
        
        # Mock event data
        mock_event_response = MagicMock()
        mock_event_response.data = [{
            "address1": "123 Main St",
            "address2": "",
            "city": "Houston",
            "state": "TX",
            "zip_code": "77001"
        }]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_event_response
        
        # Mock distance calculation failure
        mock_calculate.return_value = None
        
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/events/event123/distance", headers=headers)
        
        assert response.status_code == 400
        assert "Could not calculate distance" in response.json()["detail"]
    
    def test_get_nearby_events_unauthorized(self):
        """Test getting nearby events without authentication"""
        response = client.get("/api/events/nearby")
        assert response.status_code == 403  # Forbidden (not authenticated)
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.get_nearby_events_for_user')
    def test_get_nearby_events_success(self, mock_get_nearby, mock_verify):
        """Test successful nearby events retrieval"""
        # Mock authentication
        mock_verify.return_value = {"user_id": "user123", "role": "volunteer"}
        
        # Mock nearby events
        mock_get_nearby.return_value = [
            {
                "id": "event1",
                "name": "Community Cleanup",
                "description": "Help clean up the park",
                "address1": "123 Park Ave",
                "address2": "",
                "city": "Houston",
                "state": "TX",
                "zip_code": "77001",
                "required_skills": ["cleaning"],
                "urgency": "medium",
                "event_date": "2025-08-15",
                "distance_text": "15.2 mi",
                "duration_text": "22 mins",
                "distance_value": 24465,
                "duration_value": 1320,
                "cached": True
            }
        ]
        
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/events/nearby?max_distance=50", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Community Cleanup"
        assert data[0]["distance_text"] == "15.2 mi"
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.get_nearby_events_for_user')
    def test_get_nearby_events_default_distance(self, mock_get_nearby, mock_verify):
        """Test nearby events with default distance parameter"""
        # Mock authentication
        mock_verify.return_value = {"user_id": "user123", "role": "volunteer"}
        
        # Mock nearby events
        mock_get_nearby.return_value = []
        
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/events/nearby", headers=headers)  # No max_distance parameter
        
        assert response.status_code == 200
        assert response.json() == []
        # Verify default distance was used
        mock_get_nearby.assert_called_once_with("user123", 50)
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.get_nearby_events_for_user')
    def test_get_nearby_events_exception(self, mock_get_nearby, mock_verify):
        """Test nearby events with exception"""
        # Mock authentication
        mock_verify.return_value = {"user_id": "user123", "role": "volunteer"}
        
        # Mock exception
        mock_get_nearby.side_effect = Exception("Database error")
        
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/events/nearby", headers=headers)
        
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]
    
    def test_get_user_distance_cache_unauthorized(self):
        """Test getting user cache without authentication"""
        response = client.get("/api/cache/user/user123")
        assert response.status_code == 403  # Forbidden (not authenticated)
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.DistanceCache.get_distances_for_user')
    def test_get_user_distance_cache_self_access(self, mock_get_distances, mock_verify):
        """Test user accessing their own cache"""
        # Mock authentication - user accessing their own cache
        mock_verify.return_value = {"user_id": "user123", "role": "volunteer"}
        
        # Mock cached distances
        mock_get_distances.return_value = [
            {"distance_text": "15.2 mi", "event_id": "event1"},
            {"distance_text": "23.8 mi", "event_id": "event2"}
        ]
        
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/cache/user/user123", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user123"
        assert data["count"] == 2
        assert len(data["cached_distances"]) == 2
    
    @patch('app.routes.distance.verify_token')
    def test_get_user_distance_cache_forbidden(self, mock_verify):
        """Test user accessing another user's cache (forbidden)"""
        # Mock authentication - user trying to access another user's cache
        mock_verify.return_value = {"user_id": "user123", "role": "volunteer"}
        
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/cache/user/user456", headers=headers)  # Different user
        
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.DistanceCache.get_distances_for_user')
    def test_get_user_distance_cache_admin_access(self, mock_get_distances, mock_verify):
        """Test admin accessing any user's cache"""
        # Mock authentication - admin user
        mock_verify.return_value = {"user_id": "admin123", "role": "admin"}
        
        # Mock cached distances
        mock_get_distances.return_value = []
        
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/cache/user/user456", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user456"
        assert data["count"] == 0
    
    def test_cleanup_expired_cache_unauthorized(self):
        """Test cache cleanup without authentication"""
        response = client.delete("/api/cache/cleanup")
        assert response.status_code == 403  # Forbidden (not authenticated)
    
    @patch('app.routes.distance.verify_token')
    def test_cleanup_expired_cache_forbidden(self, mock_verify):
        """Test cache cleanup by non-admin user"""
        # Mock authentication - non-admin user
        mock_verify.return_value = {"user_id": "user123", "role": "volunteer"}
        
        headers = {"Authorization": "Bearer valid_token"}
        response = client.delete("/api/cache/cleanup", headers=headers)
        
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.DistanceCache.cleanup_expired_cache')
    def test_cleanup_expired_cache_success(self, mock_cleanup, mock_verify):
        """Test successful cache cleanup by admin"""
        # Mock authentication - admin user
        mock_verify.return_value = {"user_id": "admin123", "role": "admin"}
        
        # Mock cleanup result
        mock_cleanup.return_value = 5
        
        headers = {"Authorization": "Bearer valid_token"}
        response = client.delete("/api/cache/cleanup?hours=48", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["cleaned_count"] == 5
        assert data["age_threshold_hours"] == 48
        mock_cleanup.assert_called_once_with(48)
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.DistanceCache.cleanup_expired_cache')
    def test_cleanup_expired_cache_default_hours(self, mock_cleanup, mock_verify):
        """Test cache cleanup with default hours parameter"""
        # Mock authentication - admin user
        mock_verify.return_value = {"user_id": "admin123", "role": "admin"}
        
        # Mock cleanup result
        mock_cleanup.return_value = 3
        
        headers = {"Authorization": "Bearer valid_token"}
        response = client.delete("/api/cache/cleanup", headers=headers)  # No hours parameter
        
        assert response.status_code == 200
        data = response.json()
        assert data["cleaned_count"] == 3
        assert data["age_threshold_hours"] == 24  # Default value
        mock_cleanup.assert_called_once_with(24)
    
    def test_get_distance_for_user_to_event_unauthorized(self):
        """Test getting user-specific distance to event without authentication"""
        response = client.get("/api/events/event123/distance/user456")
        assert response.status_code == 403  # Forbidden (not authenticated)
    
    @patch('app.routes.distance.verify_token')
    def test_get_distance_for_user_to_event_forbidden(self, mock_verify):
        """Test user accessing another user's distance (forbidden)"""
        # Mock authentication - user trying to access another user's data
        mock_verify.return_value = {"user_id": "user123", "role": "volunteer"}
        
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/events/event123/distance/user456", headers=headers)
        
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.supabase')
    @patch('app.routes.distance.calculate_and_cache_distance')
    def test_get_distance_for_user_to_event_admin_success(self, mock_calculate, mock_supabase, mock_verify):
        """Test admin accessing user-specific distance to event"""
        # Mock authentication - admin user
        mock_verify.return_value = {"user_id": "admin123", "role": "admin"}
        
        # Mock event data
        mock_event_response = MagicMock()
        mock_event_response.data = [{
            "address1": "123 Main St",
            "address2": "",
            "city": "Houston",
            "state": "TX",
            "zip_code": "77001"
        }]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_event_response
        
        # Mock distance calculation
        mock_calculate.return_value = {
            "distance_text": "15.2 mi",
            "duration_text": "22 mins",
            "distance_value": 24465,
            "duration_value": 1320,
            "cached": False,
            "expires_at": "2025-08-15T12:00:00Z"
        }
        
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/events/event123/distance/user456", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["distance_text"] == "15.2 mi"
        assert data["cached"] == False
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.supabase')
    @patch('app.routes.distance.calculate_and_cache_distance')
    def test_get_distance_for_user_to_event_self_access(self, mock_calculate, mock_supabase, mock_verify):
        """Test user accessing their own distance to event"""
        # Mock authentication - user accessing their own data
        mock_verify.return_value = {"user_id": "user123", "role": "volunteer"}
        
        # Mock event data
        mock_event_response = MagicMock()
        mock_event_response.data = [{
            "address1": "123 Main St",
            "address2": None,
            "city": "Houston",
            "state": "TX",
            "zip_code": "77001"
        }]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_event_response
        
        # Mock distance calculation
        mock_calculate.return_value = {
            "distance_text": "15.2 mi",
            "duration_text": "22 mins",
            "distance_value": 24465,
            "duration_value": 1320,
            "cached": True,
            "expires_at": "2025-08-15T12:00:00Z"
        }
        
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/events/event123/distance/user123", headers=headers)  # Same user
        
        assert response.status_code == 200
        data = response.json()
        assert data["distance_text"] == "15.2 mi"
        assert data["cached"] == True
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.distance_calculator')
    def test_distance_api_health_unavailable(self, mock_calculator, mock_verify):
        """Test distance API health when unavailable"""
        # Mock no client
        mock_calculator.client = None
        
        response = client.get("/api/health/distance")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unavailable"
        assert data["google_maps_available"] == False
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.distance_calculator')
    def test_distance_api_health_healthy(self, mock_calculator, mock_verify):
        """Test distance API health when healthy"""
        # Mock working client
        mock_calculator.client = MagicMock()
        mock_calculator.geocode_address.return_value = {"lat": 29.7604, "lng": -95.3698}
        
        response = client.get("/api/health/distance")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["google_maps_available"] == True
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.distance_calculator')
    def test_distance_api_health_limited(self, mock_calculator, mock_verify):
        """Test distance API health when limited"""
        # Mock client with issues
        mock_calculator.client = MagicMock()
        mock_calculator.geocode_address.return_value = None
        
        response = client.get("/api/health/distance")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "limited"
        assert data["google_maps_available"] == False
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.distance_calculator')
    def test_distance_api_health_error(self, mock_calculator, mock_verify):
        """Test distance API health with exception"""
        # Mock client with exception
        mock_calculator.client = MagicMock()
        mock_calculator.geocode_address.side_effect = Exception("API error")
        
        response = client.get("/api/health/distance")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["google_maps_available"] == False


class TestDistanceRouteModels:
    """Test request/response models for distance routes"""
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.distance_calculator')
    def test_distance_request_validation(self, mock_calculator, mock_verify):
        """Test distance request model validation"""
        # Mock authentication
        mock_verify.return_value = {"user_id": "user123", "role": "volunteer"}
        
        # Test missing required fields
        headers = {"Authorization": "Bearer valid_token"}
        response = client.post("/api/distance/calculate", json={}, headers=headers)
        assert response.status_code == 422
        
        # Test missing one field
        response = client.post("/api/distance/calculate", 
                             json={"origin_address": "Houston, TX"}, 
                             headers=headers)
        assert response.status_code == 422
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.distance_calculator')
    def test_distance_response_format(self, mock_calculator, mock_verify):
        """Test distance response format"""
        # Mock authentication
        mock_verify.return_value = {"user_id": "user123", "role": "volunteer"}
        
        # Mock distance calculation
        mock_calculator.calculate_distance.return_value = {
            "distance": {"text": "239 mi"},
            "duration": {"text": "3 hours 35 mins"},
            "origin_address": "Houston, TX, USA",
            "destination_address": "Dallas, TX, USA",
            "status": "OK"
        }
        
        request_data = {
            "origin_address": "Houston, TX",
            "destination_address": "Dallas, TX"
        }
        
        headers = {"Authorization": "Bearer valid_token"}
        response = client.post("/api/distance/calculate", json=request_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields are present
        required_fields = ["distance", "duration", "origin_address", "destination_address", "status"]
        for field in required_fields:
            assert field in data
        
        # Verify data types and values
        assert isinstance(data["distance"], str)
        assert isinstance(data["duration"], str)
        assert data["status"] == "OK"


class TestDistanceRouteEdgeCases:
    """Test edge cases for distance routes"""
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.supabase')
    @patch('app.routes.distance.calculate_and_cache_distance')
    def test_event_address_formatting_with_address2(self, mock_calculate, mock_supabase, mock_verify):
        """Test event address formatting when address2 is present"""
        # Mock authentication
        mock_verify.return_value = {"user_id": "user123", "role": "volunteer"}
        
        # Mock event data with address2
        mock_event_response = MagicMock()
        mock_event_response.data = [{
            "address1": "123 Main St",
            "address2": "Suite 100",
            "city": "Houston",
            "state": "TX",
            "zip_code": "77001"
        }]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_event_response
        
        # Mock distance calculation
        mock_calculate.return_value = {
            "distance_text": "15.2 mi",
            "duration_text": "22 mins",
            "distance_value": 24465,
            "duration_value": 1320,
            "cached": False,
            "expires_at": "2025-08-15T12:00:00Z"
        }
        
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/events/event123/distance", headers=headers)
        
        assert response.status_code == 200
        
        # Verify the formatted address was used (with address2)
        expected_location = "123 Main St, Suite 100, Houston, TX 77001"
        mock_calculate.assert_called_once_with("user123", "event123", expected_location)
    
    @patch('app.routes.distance.verify_token')
    @patch('app.routes.distance.supabase')
    @patch('app.routes.distance.calculate_and_cache_distance')
    def test_event_address_formatting_without_address2(self, mock_calculate, mock_supabase, mock_verify):
        """Test event address formatting when address2 is not present"""
        # Mock authentication
        mock_verify.return_value = {"user_id": "user123", "role": "volunteer"}
        
        # Mock event data without address2
        mock_event_response = MagicMock()
        mock_event_response.data = [{
            "address1": "123 Main St",
            "address2": None,
            "city": "Houston",
            "state": "TX",
            "zip_code": "77001"
        }]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_event_response
        
        # Mock distance calculation
        mock_calculate.return_value = {
            "distance_text": "15.2 mi",
            "duration_text": "22 mins",
            "distance_value": 24465,
            "duration_value": 1320,
            "cached": False,
            "expires_at": "2025-08-15T12:00:00Z"
        }
        
        headers = {"Authorization": "Bearer valid_token"}
        response = client.get("/api/events/event123/distance", headers=headers)
        
        assert response.status_code == 200
        
        # Verify the formatted address was used (without address2)
        expected_location = "123 Main St, Houston, TX 77001"
        mock_calculate.assert_called_once_with("user123", "event123", expected_location)
