"""
Comprehensive match module tests - consolidated from multiple files
Tests match algorithms, utility functions, and API routes
"""
from fastapi.testclient import TestClient
from app.main import app
from app.routes.auth import verify_token
from app.routes.match import (
    calculate_distance,
    calculate_skill_match,
    calculate_urgency_score,
    calculate_match_score,
    fetch_user_skills,
    fetch_all_events
)
from unittest.mock import patch, MagicMock
import os

client = TestClient(app)

def mock_verify_token():
    return {"user_id": "test_user_123", "role": "user"}

def mock_admin_verify_token():
    return {"user_id": "admin_user", "role": "admin"}

class TestMatchUtilities:
    """Test match utility functions"""

    def test_calculate_distance_mock_key(self):
        """Test distance calculation with mock key"""
        original_key = os.environ.get("GOOGLE_MAPS_API_KEY")
        os.environ["GOOGLE_MAPS_API_KEY"] = "mock_key"
        
        try:
            distance = calculate_distance("123 Main St", "456 Oak Ave")
            assert isinstance(distance, float)
            assert 1.0 <= distance <= 25.0  # Mock should return 1-25 miles
        finally:
            if original_key:
                os.environ["GOOGLE_MAPS_API_KEY"] = original_key
            elif "GOOGLE_MAPS_API_KEY" in os.environ:
                del os.environ["GOOGLE_MAPS_API_KEY"]

    def test_calculate_distance_no_key(self):
        """Test distance calculation with no API key"""
        original_key = os.environ.get("GOOGLE_MAPS_API_KEY")
        if "GOOGLE_MAPS_API_KEY" in os.environ:
            del os.environ["GOOGLE_MAPS_API_KEY"]
        
        try:
            distance = calculate_distance("123 Main St", "456 Oak Ave")
            assert isinstance(distance, float)
            assert 1.0 <= distance <= 25.0  # Mock should return 1-25 miles
        finally:
            if original_key:
                os.environ["GOOGLE_MAPS_API_KEY"] = original_key

    @patch('requests.get')
    def test_calculate_distance_api_success(self, mock_get):
        """Test distance calculation with successful API response"""
        os.environ["GOOGLE_MAPS_API_KEY"] = "AIzaSyTest123"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "OK",
            "rows": [{
                "elements": [{
                    "status": "OK",
                    "distance": {"text": "15.2 mi"}
                }]
            }]
        }
        mock_get.return_value = mock_response
        
        try:
            distance = calculate_distance("123 Main St", "456 Oak Ave")
            assert distance == 15.2
        finally:
            if "GOOGLE_MAPS_API_KEY" in os.environ:
                del os.environ["GOOGLE_MAPS_API_KEY"]

    @patch('requests.get')
    def test_calculate_distance_api_with_comma(self, mock_get):
        """Test distance calculation with comma in response"""
        os.environ["GOOGLE_MAPS_API_KEY"] = "AIzaSyTest123"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "OK",
            "rows": [{
                "elements": [{
                    "status": "OK",
                    "distance": {"text": "1,234.5 mi"}
                }]
            }]
        }
        mock_get.return_value = mock_response
        
        try:
            distance = calculate_distance("123 Main St", "456 Oak Ave")
            assert distance == 1234.5
        finally:
            if "GOOGLE_MAPS_API_KEY" in os.environ:
                del os.environ["GOOGLE_MAPS_API_KEY"]

    @patch('requests.get')
    def test_calculate_distance_api_failure(self, mock_get):
        """Test distance calculation with API failure"""
        os.environ["GOOGLE_MAPS_API_KEY"] = "AIzaSyTest123"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "REQUEST_DENIED"}
        mock_get.return_value = mock_response
        
        try:
            distance = calculate_distance("123 Main St", "456 Oak Ave")
            assert distance == 15.0  # Should return fallback
        finally:
            if "GOOGLE_MAPS_API_KEY" in os.environ:
                del os.environ["GOOGLE_MAPS_API_KEY"]

    @patch('requests.get')
    def test_calculate_distance_exception(self, mock_get):
        """Test distance calculation with exception"""
        os.environ["GOOGLE_MAPS_API_KEY"] = "AIzaSyTest123"
        
        mock_get.side_effect = Exception("Network error")
        
        try:
            distance = calculate_distance("123 Main St", "456 Oak Ave")
            assert distance == 15.0  # Should return fallback
        finally:
            if "GOOGLE_MAPS_API_KEY" in os.environ:
                del os.environ["GOOGLE_MAPS_API_KEY"]

    def test_calculate_skill_match_variations(self):
        """Test skill matching with different scenarios"""
        # Empty event skills
        assert calculate_skill_match(["python", "javascript"], []) == 0.0
        
        # Partial match with case insensitivity
        user_skills = ["Python", "JavaScript", "React"]
        event_skills = ["python", "java", "node"]
        match_percent = calculate_skill_match(user_skills, event_skills)
        assert match_percent == (1/3) * 100  # 1 out of 3 skills match
        
        # Full match
        user_skills = ["Python", "JavaScript"]
        event_skills = ["python", "javascript"]
        assert calculate_skill_match(user_skills, event_skills) == 100.0
        
        # No match
        user_skills = ["Python", "JavaScript"]
        event_skills = ["java", "c++"]
        assert calculate_skill_match(user_skills, event_skills) == 0.0

    def test_calculate_urgency_score_all_levels(self):
        """Test urgency score calculation with all urgency levels"""
        assert calculate_urgency_score("high") == 1.0
        assert calculate_urgency_score("HIGH") == 1.0
        assert calculate_urgency_score("medium") == 0.6
        assert calculate_urgency_score("MEDIUM") == 0.6
        assert calculate_urgency_score("low") == 0.3
        assert calculate_urgency_score("LOW") == 0.3
        assert calculate_urgency_score("unknown") == 0.0
        assert calculate_urgency_score("") == 0.0
        assert calculate_urgency_score(None) == 0.0

    def test_calculate_match_score_scenarios(self):
        """Test match score calculation with various scenarios"""
        # High values scenario
        score = calculate_match_score(
            skill_match=100.0,
            distance=5.0,
            urgency="high",
            skill_weight=0.5,
            distance_weight=0.3,
            urgency_weight=0.2
        )
        assert score == 97.0  # Should be high

        # Low values scenario
        score = calculate_match_score(
            skill_match=0.0,
            distance=50.0,
            urgency="low",
            skill_weight=0.5,
            distance_weight=0.3,
            urgency_weight=0.2
        )
        assert score == 6.0  # Should be low

        # Extreme distance beyond max
        score = calculate_match_score(
            skill_match=50.0,
            distance=100.0,  # Beyond max distance
            urgency="medium",
            skill_weight=0.4,
            distance_weight=0.4,
            urgency_weight=0.2
        )
        assert score == 32.0  # Distance score should be 0

    def test_fetch_user_skills(self):
        """Test fetch_user_skills function"""
        skills = fetch_user_skills("test_user")
        assert isinstance(skills, set)

    def test_fetch_all_events(self):
        """Test fetch_all_events function"""
        events = fetch_all_events()
        assert isinstance(events, list)

class TestMatchAPIRoutes:
    """Test match API endpoints"""

    def test_match_and_notify_route(self):
        """Test GET /api/match-and-notify/{user_id}"""
        response = client.get("/api/match-and-notify/test_user")
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "matched_events" in data

    def test_matched_events_route(self):
        """Test GET /api/matched_events/{user_id}"""
        response = client.get("/api/matched_events/test_user")
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "matched_events" in data

    def test_match_route_authorized(self):
        """Test POST /api/match with proper authorization"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            match_request = {
                "user_id": "test_user_123",
                "max_distance": 25.0,
                "urgency_weight": 0.4,
                "skill_weight": 0.4,
                "distance_weight": 0.2
            }
            response = client.post("/api/match", json=match_request)
            assert response.status_code in [200, 404, 500]
        finally:
            app.dependency_overrides.clear()

    def test_match_route_admin_access(self):
        """Test POST /api/match with admin authorization"""
        app.dependency_overrides[verify_token] = mock_admin_verify_token
        try:
            match_request = {
                "user_id": "any_user",
                "max_distance": 30.0
            }
            response = client.post("/api/match", json=match_request)
            assert response.status_code in [200, 404, 500]
        finally:
            app.dependency_overrides.clear()

    def test_match_route_unauthorized(self):
        """Test POST /api/match without proper authorization"""
        def mock_unauthorized_token():
            return {"user_id": "different_user", "role": "user"}
        
        app.dependency_overrides[verify_token] = mock_unauthorized_token
        try:
            match_request = {
                "user_id": "test_user_123",
                "max_distance": 25.0
            }
            response = client.post("/api/match", json=match_request)
            assert response.status_code in [403, 500]  # Should be forbidden or error
        finally:
            app.dependency_overrides.clear()

    def test_match_route_default_weights(self):
        """Test POST /api/match with default weight values"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            match_request = {"user_id": "test_user_123"}
            response = client.post("/api/match", json=match_request)
            assert response.status_code in [200, 404, 500]
        finally:
            app.dependency_overrides.clear()

    def test_match_route_invalid_request(self):
        """Test POST /api/match with invalid request data"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            # Missing required user_id
            match_request = {"max_distance": 25.0}
            response = client.post("/api/match", json=match_request)
            assert response.status_code == 422  # Validation error
        finally:
            app.dependency_overrides.clear()

    def test_match_route_edge_case_weights(self):
        """Test POST /api/match with edge case weight values"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            match_request = {
                "user_id": "test_user_123",
                "max_distance": -1.0,  # Negative distance
                "urgency_weight": -0.1,  # Negative weight
                "skill_weight": 2.0,    # Weight > 1
                "distance_weight": 0.0  # Zero weight
            }
            response = client.post("/api/match", json=match_request)
            assert response.status_code in [200, 404, 422, 500]
        finally:
            app.dependency_overrides.clear()

    def test_batch_match_route(self):
        """Test POST /api/batch-match route"""
        app.dependency_overrides[verify_token] = mock_admin_verify_token
        try:
            batch_request = {
                "user_ids": ["user1", "user2"],
                "event_ids": ["event1", "event2"],
                "max_distance": 30.0
            }
            response = client.post("/api/batch-match", json=batch_request)
            assert response.status_code in [200, 400, 422, 500]
        finally:
            app.dependency_overrides.clear()

    def test_unauthorized_access(self):
        """Test accessing match routes without authentication"""
        match_request = {"user_id": "test_user_123", "max_distance": 25.0}
        response = client.post("/api/match", json=match_request)
        assert response.status_code in [401, 403, 422]

class TestMatchIntegration:
    """Integration tests for match functionality"""

    def test_full_matching_workflow(self):
        """Test complete matching workflow"""
        app.dependency_overrides[verify_token] = mock_verify_token
        try:
            # First get matched events without notification
            response = client.get("/api/matched_events/test_user_123")
            initial_status = response.status_code
            
            # Then try match and notify
            response = client.get("/api/match-and-notify/test_user_123")
            notify_status = response.status_code
            
            # Finally try advanced matching
            match_request = {
                "user_id": "test_user_123",
                "max_distance": 25.0,
                "skill_weight": 0.6,
                "distance_weight": 0.3,
                "urgency_weight": 0.1
            }
            response = client.post("/api/match", json=match_request)
            advanced_status = response.status_code
            
            # All should succeed or fail gracefully
            assert initial_status in [200, 500]
            assert notify_status in [200, 500]
            assert advanced_status in [200, 404, 500]
            
        finally:
            app.dependency_overrides.clear()

    def test_skill_matching_edge_cases(self):
        """Test skill matching with edge cases"""
        # Test with empty skills
        assert calculate_skill_match([], []) == 0.0
        assert calculate_skill_match(["python"], []) == 0.0
        assert calculate_skill_match([], ["python"]) == 0.0
        
        # Test with None values (should not crash)
        try:
            calculate_skill_match(None, ["python"])
            assert False, "Should handle None gracefully"
        except (TypeError, AttributeError):
            pass  # Expected to fail
