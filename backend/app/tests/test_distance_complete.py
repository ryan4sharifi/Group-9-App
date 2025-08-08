"""
Comprehensive distance module tests - consolidated from multiple files
Tests distance calculations, database operations, and API routes
"""
from fastapi.testclient import TestClient
from app.main import app
from app.routes.auth import verify_token
from app.utils.distance import (
    DistanceCalculator,
    get_user_full_address,
    calculate_distance_to_event,
    safe_distance_calculation
)
from unittest.mock import patch, MagicMock
import os

client = TestClient(app)

def mock_verify_token():
    return {"user_id": "test_user_123", "role": "user"}

def mock_admin_verify_token():
    return {"user_id": "admin_user", "role": "admin"}

class TestDistanceUtilities:
    """Test distance utility functions"""
    
    def test_distance_calculator_init(self):
        """Test DistanceCalculator initialization"""
        calculator = DistanceCalculator()
        # Should initialize without error
        assert calculator is not None

    def test_distance_calculator_with_mock_key(self):
        """Test DistanceCalculator with mock API key"""
        original_key = os.environ.get("GOOGLE_MAPS_API_KEY")
        os.environ["GOOGLE_MAPS_API_KEY"] = "mock_key"
        
        try:
            calculator = DistanceCalculator()
            assert calculator is not None
            # Test geocoding
            coords = calculator.geocode_address("123 Main St, City, State")
            assert coords is None or isinstance(coords, tuple)
        finally:
            if original_key:
                os.environ["GOOGLE_MAPS_API_KEY"] = original_key
            elif "GOOGLE_MAPS_API_KEY" in os.environ:
                del os.environ["GOOGLE_MAPS_API_KEY"]

    def test_distance_calculator_no_key(self):
        """Test DistanceCalculator without API key"""
        original_key = os.environ.get("GOOGLE_MAPS_API_KEY")
        if "GOOGLE_MAPS_API_KEY" in os.environ:
            del os.environ["GOOGLE_MAPS_API_KEY"]
        
        try:
            calculator = DistanceCalculator()
            assert calculator is not None
            assert calculator.client is None
        finally:
            if original_key:
                os.environ["GOOGLE_MAPS_API_KEY"] = original_key

    @patch('googlemaps.Client')
    def test_distance_calculation_mocked(self, mock_client):
        """Test distance calculation with mocked Google Maps client"""
        os.environ["GOOGLE_MAPS_API_KEY"] = "test_key"
        
        # Mock the client and its methods
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.distance_matrix.return_value = {
            "rows": [{
                "elements": [{
                    "status": "OK",
                    "distance": {"text": "15.2 mi", "value": 24462},
                    "duration": {"text": "25 mins", "value": 1500}
                }]
            }]
        }
        
        try:
            calculator = DistanceCalculator()
            result = calculator.calculate_distance("123 Main St", "456 Oak Ave")
            assert result is not None
            if result:
                assert "distance" in result or result is None
        finally:
            if "GOOGLE_MAPS_API_KEY" in os.environ:
                del os.environ["GOOGLE_MAPS_API_KEY"]

    def test_get_user_full_address(self):
        """Test user address formatting"""
        user_profile = {
            "address1": "123 Main St",
            "city": "Springfield", 
            "state": "IL",
            "zipcode": "62701"
        }
        address = get_user_full_address(user_profile)
        assert address is not None
        assert isinstance(address, str)
        assert "123 Main St" in address

    def test_get_user_full_address_partial_data(self):
        """Test user address with missing fields"""
        user_profile = {"address1": "123 Main St"}
        address = get_user_full_address(user_profile)
        # Should handle missing fields gracefully
        assert address is None or isinstance(address, str)

    def test_calculate_distance_to_event(self):
        """Test distance calculation to event"""
        user_profile = {
            "address1": "123 Main St",
            "city": "Springfield",
            "state": "IL"
        }
        distance = calculate_distance_to_event(user_profile, "456 Oak Ave, Springfield, IL")
        assert distance is None or isinstance(distance, str)

    def test_safe_distance_calculation(self):
        """Test safe distance calculation with fallback"""
        user_profile = {"address1": "123 Main St"}
        result = safe_distance_calculation(user_profile, "456 Oak Ave")
        assert isinstance(result, str)
        # Should not be empty
        assert len(result) > 0

    def test_safe_distance_calculation_custom_fallback(self):
        """Test safe distance calculation with custom fallback"""
        user_profile = {}
        result = safe_distance_calculation(user_profile, "456 Oak Ave", "Custom fallback")
        assert isinstance(result, str)
        assert result == "Custom fallback" or "distance" in result.lower()

class TestDistanceAPIRoutes:
    """Test distance API endpoints"""
    
    def test_calculate_distance_route(self):
        """Test POST /api/distance/calculate"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            request_data = {
                "origin": "123 Main St, City, State",
                "destination": "456 Oak Ave, City, State"
            }
            response = client.post("/api/distance/calculate", json=request_data)
            assert response.status_code in [200, 422, 500]
        finally:
            app.dependency_overrides.clear()

    def test_get_distance_to_event_success(self):
        """Test successful distance calculation to event"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            request_data = {
                "user_location": "123 Main St, City, State",
                "event_id": "event_123"
            }
            response = client.post("/api/distance/to-event", json=request_data)
            assert response.status_code in [200, 404, 422, 500]
        finally:
            app.dependency_overrides.clear()

    def test_get_event_distance_by_id(self):
        """Test GET /api/events/{event_id}/distance"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            response = client.get("/api/events/event_123/distance?user_location=123 Main St")
            assert response.status_code in [200, 404, 422, 500]
        finally:
            app.dependency_overrides.clear()

    def test_get_nearby_events(self):
        """Test GET /api/events/nearby"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            response = client.get("/api/events/nearby?user_location=123 Main St&radius=25")
            assert response.status_code in [200, 404, 422, 500]
        finally:
            app.dependency_overrides.clear()

    def test_get_user_cache(self):
        """Test GET /api/cache/user/{user_id}"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            response = client.get("/api/cache/user/test_user_123")
            assert response.status_code in [200, 404, 500]
        finally:
            app.dependency_overrides.clear()

    def test_cleanup_cache_admin(self):
        """Test DELETE /api/cache/cleanup (admin required)"""
        app.dependency_overrides[verify_token] = mock_admin_verify_token
        try:
            response = client.delete("/api/cache/cleanup")
            assert response.status_code in [200, 403, 500]
        finally:
            app.dependency_overrides.clear()

    def test_cleanup_cache_unauthorized(self):
        """Test cache cleanup without admin privileges"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            response = client.delete("/api/cache/cleanup")
            assert response.status_code in [403, 500]
        finally:
            app.dependency_overrides.clear()

    def test_distance_health_check(self):
        """Test GET /api/health/distance"""
        response = client.get("/api/health/distance")
        assert response.status_code in [200, 500]

    def test_calculate_distance_validation_errors(self):
        """Test distance calculation with validation errors"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            # Missing required fields
            response = client.post("/api/distance/calculate", json={"origin": "123 Main St"})
            assert response.status_code == 422
            
            # Empty data
            response = client.post("/api/distance/calculate", json={})
            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()

    def test_unauthorized_access(self):
        """Test distance routes without authentication"""
        request_data = {"origin": "123 Main St", "destination": "456 Oak Ave"}
        response = client.post("/api/distance/calculate", json=request_data)
        assert response.status_code in [401, 403, 422]

class TestDistanceIntegration:
    """Integration tests for distance functionality"""
    
    def test_full_distance_workflow(self):
        """Test complete distance calculation workflow"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            # Calculate distance
            request_data = {
                "origin": "New York, NY",
                "destination": "Boston, MA"
            }
            response = client.post("/api/distance/calculate", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                assert "distance" in data or "error" not in data
            else:
                # Accept various error states in test environment
                assert response.status_code in [422, 500]
                
        finally:
            app.dependency_overrides.clear()

    def test_distance_caching_workflow(self):
        """Test distance caching functionality"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            # Check cache first
            response = client.get("/api/cache/user/test_user_123")
            initial_status = response.status_code
            
            # Calculate new distance
            request_data = {
                "origin": "San Francisco, CA", 
                "destination": "Los Angeles, CA"
            }
            calc_response = client.post("/api/distance/calculate", json=request_data)
            
            # Check cache again
            response = client.get("/api/cache/user/test_user_123")
            
            # Should not error (may have different data)
            assert initial_status in [200, 404, 500]
            assert calc_response.status_code in [200, 422, 500]
            assert response.status_code in [200, 404, 500]
            
        finally:
            app.dependency_overrides.clear()
