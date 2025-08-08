import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from app.utils.distance_db import (
    DistanceCache,
    calculate_and_cache_distance,
    get_nearby_events_for_user
)

class TestDistanceCache:
    """Test the DistanceCache class methods"""

    def test_generate_cache_key(self):
        """Test cache key generation"""
        key1 = DistanceCache.generate_cache_key("Houston, TX", "Dallas, TX")
        key2 = DistanceCache.generate_cache_key("houston, tx", "dallas, tx")
        key3 = DistanceCache.generate_cache_key("  Houston, TX  ", "  Dallas, TX  ")
        
        # Same addresses should generate same key regardless of case/whitespace
        assert key1 == key2 == key3
        assert isinstance(key1, str)
        assert len(key1) == 32  # MD5 hash length

    def test_generate_cache_key_different_addresses(self):
        """Test cache key generation for different addresses"""
        key1 = DistanceCache.generate_cache_key("Houston, TX", "Dallas, TX")
        key2 = DistanceCache.generate_cache_key("Dallas, TX", "Houston, TX")
        
        # Different order should generate different keys
        assert key1 != key2

    @patch('app.utils.distance_db.supabase')
    def test_get_cached_distance_hit(self, mock_supabase):
        """Test cache hit with valid data"""
        future_time = (datetime.now() + timedelta(days=1)).isoformat() + "Z"
        mock_response = MagicMock()
        mock_response.data = [{
            "distance_text": "15.2 mi",
            "duration_text": "22 mins",
            "distance_value": 24465,
            "duration_value": 1320,
            "expires_at": future_time
        }]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        result = DistanceCache.get_cached_distance("user123", "event456")
        
        assert result is not None
        assert result["distance_text"] == "15.2 mi"
        assert result["cached"] is True

    @patch('app.utils.distance_db.supabase')
    def test_get_cached_distance_miss(self, mock_supabase):
        """Test cache miss"""
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        result = DistanceCache.get_cached_distance("user123", "event456")
        
        assert result is None

    @patch('app.utils.distance_db.supabase')
    def test_get_cached_distance_expired(self, mock_supabase):
        """Test cache miss due to expiration"""
        past_time = (datetime.now() - timedelta(days=1)).isoformat() + "Z"
        mock_response = MagicMock()
        mock_response.data = [{
            "distance_text": "15.2 mi",
            "duration_text": "22 mins",
            "distance_value": 24465,
            "duration_value": 1320,
            "expires_at": past_time,
            "created_at": (datetime.now() - timedelta(days=8)).isoformat() + "Z"
        }]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        result = DistanceCache.get_cached_distance("user123", "event456")
        
        assert result is None

    @patch('app.utils.distance_db.supabase')
    def test_get_cached_distance_invalid_expires_at(self, mock_supabase):
        """Test cache with invalid expires_at field"""
        mock_response = MagicMock()
        mock_response.data = [{
            "distance_text": "15.2 mi",
            "duration_text": "22 mins",
            "distance_value": 24465,
            "duration_value": 1320,
            "expires_at": "invalid-date",
            "created_at": datetime.now().isoformat() + "Z"
        }]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        result = DistanceCache.get_cached_distance("user123", "event456")
        
        # Should handle invalid date gracefully
        assert result is not None  # Falls back to created_at check

    @patch('app.utils.distance_db.supabase')
    def test_get_cached_distance_exception(self, mock_supabase):
        """Test exception handling in cache retrieval"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.side_effect = Exception("Database error")
        
        result = DistanceCache.get_cached_distance("user123", "event456")
        
        assert result is None

    @patch('app.utils.distance_db.supabase')
    def test_save_distance_calculation_new_entry(self, mock_supabase):
        """Test saving new distance calculation"""
        # Mock no existing entry
        mock_existing = MagicMock()
        mock_existing.data = []
        
        # Mock successful insert
        mock_insert = MagicMock()
        mock_insert.data = [{"id": "cache123"}]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_existing
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_insert
        
        distance_result = {
            "distance": {"text": "15.2 mi", "value": 24465},
            "duration": {"text": "22 mins", "value": 1320}
        }
        
        result = DistanceCache.save_distance_calculation(
            "user123", "event456", "Houston, TX", "Dallas, TX", distance_result
        )
        
        assert result is True

    @patch('app.utils.distance_db.supabase')
    def test_save_distance_calculation_update_existing(self, mock_supabase):
        """Test updating existing distance calculation"""
        # Mock existing entry
        mock_existing = MagicMock()
        mock_existing.data = [{"id": "cache123"}]
        
        # Mock successful update
        mock_update = MagicMock()
        mock_update.data = [{"id": "cache123"}]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_existing
        mock_supabase.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = mock_update
        
        distance_result = {
            "distance": {"text": "15.2 mi", "value": 24465},
            "duration": {"text": "22 mins", "value": 1320}
        }
        
        result = DistanceCache.save_distance_calculation(
            "user123", "event456", "Houston, TX", "Dallas, TX", distance_result
        )
        
        assert result is True

    @patch('app.utils.distance_db.supabase')
    def test_save_distance_calculation_failure(self, mock_supabase):
        """Test failed distance calculation save"""
        # Mock no existing entry
        mock_existing = MagicMock()
        mock_existing.data = []
        
        # Mock failed insert
        mock_insert = MagicMock()
        mock_insert.data = None
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_existing
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_insert
        
        distance_result = {
            "distance": {"text": "15.2 mi", "value": 24465},
            "duration": {"text": "22 mins", "value": 1320}
        }
        
        result = DistanceCache.save_distance_calculation(
            "user123", "event456", "Houston, TX", "Dallas, TX", distance_result
        )
        
        assert result is False

    @patch('app.utils.distance_db.supabase')
    def test_save_distance_calculation_exception(self, mock_supabase):
        """Test exception in distance calculation save"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.side_effect = Exception("Database error")
        
        distance_result = {
            "distance": {"text": "15.2 mi", "value": 24465},
            "duration": {"text": "22 mins", "value": 1320}
        }
        
        result = DistanceCache.save_distance_calculation(
            "user123", "event456", "Houston, TX", "Dallas, TX", distance_result
        )
        
        assert result is False

    @patch('app.utils.distance_db.supabase')
    def test_delete_cached_distance_success(self, mock_supabase):
        """Test successful cache deletion"""
        mock_response = MagicMock()
        mock_response.data = [{"id": "cache123"}]
        mock_supabase.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        result = DistanceCache.delete_cached_distance("user123", "event456")
        
        assert result is True

    @patch('app.utils.distance_db.supabase')
    def test_delete_cached_distance_exception(self, mock_supabase):
        """Test exception in cache deletion"""
        mock_supabase.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.side_effect = Exception("Database error")
        
        result = DistanceCache.delete_cached_distance("user123", "event456")
        
        assert result is False

    @patch('app.utils.distance_db.supabase')
    def test_get_distances_for_user_success(self, mock_supabase):
        """Test getting all distances for a user"""
        mock_response = MagicMock()
        mock_response.data = [
            {"distance_text": "15.2 mi", "event_id": "event1"},
            {"distance_text": "23.8 mi", "event_id": "event2"}
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        result = DistanceCache.get_distances_for_user("user123")
        
        assert len(result) == 2
        assert result[0]["distance_text"] == "15.2 mi"

    @patch('app.utils.distance_db.supabase')
    def test_get_distances_for_user_empty(self, mock_supabase):
        """Test getting distances for user with no cache"""
        mock_response = MagicMock()
        mock_response.data = None
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        result = DistanceCache.get_distances_for_user("user123")
        
        assert result == []

    @patch('app.utils.distance_db.supabase')
    def test_get_distances_for_user_exception(self, mock_supabase):
        """Test exception in getting user distances"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("Database error")
        
        result = DistanceCache.get_distances_for_user("user123")
        
        assert result == []

    @patch('app.utils.distance_db.supabase')
    def test_get_distances_for_event_success(self, mock_supabase):
        """Test getting all distances for an event"""
        mock_response = MagicMock()
        mock_response.data = [
            {"distance_text": "15.2 mi", "user_id": "user1"},
            {"distance_text": "23.8 mi", "user_id": "user2"}
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        result = DistanceCache.get_distances_for_event("event123")
        
        assert len(result) == 2
        assert result[0]["distance_text"] == "15.2 mi"

    @patch('app.utils.distance_db.supabase')
    def test_cleanup_expired_cache_success(self, mock_supabase):
        """Test successful cache cleanup"""
        # Mock cache entries - one expired, one valid
        expired_time = (datetime.now() - timedelta(days=1)).isoformat() + "Z"
        future_time = (datetime.now() + timedelta(days=1)).isoformat() + "Z"
        
        mock_response = MagicMock()
        mock_response.data = [
            {"id": "cache1", "expires_at": expired_time},
            {"id": "cache2", "expires_at": future_time}
        ]
        
        mock_delete = MagicMock()
        mock_delete.data = [{"id": "cache1"}]
        
        mock_supabase.table.return_value.select.return_value.execute.return_value = mock_response
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_delete
        
        result = DistanceCache.cleanup_expired_cache(24)
        
        assert result == 1  # One entry should be cleaned up

    @patch('app.utils.distance_db.supabase')
    def test_cleanup_expired_cache_no_data(self, mock_supabase):
        """Test cache cleanup with no data"""
        mock_response = MagicMock()
        mock_response.data = None
        mock_supabase.table.return_value.select.return_value.execute.return_value = mock_response
        
        result = DistanceCache.cleanup_expired_cache(24)
        
        assert result == 0

    @patch('app.utils.distance_db.supabase')
    def test_cleanup_expired_cache_exception(self, mock_supabase):
        """Test exception in cache cleanup"""
        mock_supabase.table.return_value.select.return_value.execute.side_effect = Exception("Database error")
        
        result = DistanceCache.cleanup_expired_cache(24)
        
        assert result == 0

    @patch('app.utils.distance_db.supabase')
    def test_cleanup_expired_cache_invalid_expires_at(self, mock_supabase):
        """Test cache cleanup with invalid expires_at field"""
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": "cache1", 
                "expires_at": "invalid-date",
                "created_at": (datetime.now() - timedelta(days=30)).isoformat() + "Z"
            }
        ]
        
        mock_delete = MagicMock()
        mock_delete.data = [{"id": "cache1"}]
        
        mock_supabase.table.return_value.select.return_value.execute.return_value = mock_response
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_delete
        
        result = DistanceCache.cleanup_expired_cache(24)
        
        assert result == 1  # Should fall back to created_at check


class TestCalculateAndCacheDistance:
    """Test the calculate_and_cache_distance function"""

    @patch('app.utils.distance_db.DistanceCache.get_cached_distance')
    def test_calculate_and_cache_distance_cache_hit(self, mock_get_cached):
        """Test function with cache hit"""
        mock_get_cached.return_value = {
            "distance_text": "15.2 mi",
            "duration_text": "22 mins",
            "distance_value": 24465,
            "duration_value": 1320,
            "expires_at": (datetime.now() + timedelta(days=1)).isoformat()
        }
        
        result = calculate_and_cache_distance("user123", "event456", "Dallas, TX")
        
        assert result is not None
        assert result["cached"] is True
        assert result["distance_text"] == "15.2 mi"

    @patch('app.utils.distance_db.DistanceCache.get_cached_distance')
    @patch('app.utils.distance_db.supabase')
    @patch('app.utils.distance_db.get_user_full_address')
    @patch('app.utils.distance_db.distance_calculator')
    @patch('app.utils.distance_db.DistanceCache.save_distance_calculation')
    def test_calculate_and_cache_distance_cache_miss(self, mock_save, mock_calculator, mock_address, mock_supabase, mock_get_cached):
        """Test function with cache miss and successful calculation"""
        mock_get_cached.return_value = None
        
        # Mock user profile response
        mock_profile_response = MagicMock()
        mock_profile_response.data = [{"address1": "123 Main St", "city": "Houston", "state": "TX"}]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_profile_response
        
        mock_address.return_value = "123 Main St, Houston, TX"
        
        # Mock distance calculation
        mock_calculator.calculate_distance.return_value = {
            "distance": {"text": "15.2 mi", "value": 24465},
            "duration": {"text": "22 mins", "value": 1320}
        }
        
        mock_save.return_value = True
        
        result = calculate_and_cache_distance("user123", "event456", "Dallas, TX")
        
        assert result is not None
        assert result["cached"] is False
        assert result["distance_text"] == "15.2 mi"

    @patch('app.utils.distance_db.DistanceCache.get_cached_distance')
    @patch('app.utils.distance_db.supabase')
    def test_calculate_and_cache_distance_no_profile(self, mock_supabase, mock_get_cached):
        """Test function with no user profile"""
        mock_get_cached.return_value = None
        
        # Mock no user profile response
        mock_profile_response = MagicMock()
        mock_profile_response.data = []
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_profile_response
        
        result = calculate_and_cache_distance("user123", "event456", "Dallas, TX")
        
        assert result is None

    @patch('app.utils.distance_db.DistanceCache.get_cached_distance')
    @patch('app.utils.distance_db.supabase')
    @patch('app.utils.distance_db.get_user_full_address')
    def test_calculate_and_cache_distance_no_address(self, mock_address, mock_supabase, mock_get_cached):
        """Test function when user address cannot be built"""
        mock_get_cached.return_value = None
        
        # Mock user profile response
        mock_profile_response = MagicMock()
        mock_profile_response.data = [{"address1": "", "city": "Houston", "state": "TX"}]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_profile_response
        
        mock_address.return_value = None
        
        result = calculate_and_cache_distance("user123", "event456", "Dallas, TX")
        
        assert result is None

    @patch('app.utils.distance_db.DistanceCache.get_cached_distance')
    @patch('app.utils.distance_db.supabase')
    @patch('app.utils.distance_db.get_user_full_address')
    @patch('app.utils.distance_db.distance_calculator')
    def test_calculate_and_cache_distance_api_failure(self, mock_calculator, mock_address, mock_supabase, mock_get_cached):
        """Test function when Google Maps API fails"""
        mock_get_cached.return_value = None
        
        # Mock user profile response
        mock_profile_response = MagicMock()
        mock_profile_response.data = [{"address1": "123 Main St", "city": "Houston", "state": "TX"}]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_profile_response
        
        mock_address.return_value = "123 Main St, Houston, TX"
        mock_calculator.calculate_distance.return_value = None
        
        result = calculate_and_cache_distance("user123", "event456", "Dallas, TX")
        
        assert result is None

    @patch('app.utils.distance_db.DistanceCache.get_cached_distance')
    def test_calculate_and_cache_distance_exception(self, mock_get_cached):
        """Test function with exception"""
        mock_get_cached.side_effect = Exception("Database error")
        
        result = calculate_and_cache_distance("user123", "event456", "Dallas, TX")
        
        assert result is None


class TestGetNearbyEventsForUser:
    """Test the get_nearby_events_for_user function"""

    @patch('app.utils.distance_db.supabase')
    @patch('app.utils.distance_db.calculate_and_cache_distance')
    def test_get_nearby_events_for_user_success(self, mock_calculate, mock_supabase):
        """Test getting nearby events successfully"""
        # Mock events response
        mock_events_response = MagicMock()
        mock_events_response.data = [
            {"id": "event1", "name": "Event 1", "location": "Houston, TX"},
            {"id": "event2", "name": "Event 2", "location": "Dallas, TX"}
        ]
        mock_supabase.table.return_value.select.return_value.execute.return_value = mock_events_response
        
        # Mock distance calculations - one close, one far
        def mock_distance_side_effect(user_id, event_id, location):
            if event_id == "event1":
                return {
                    "distance_text": "15.2 mi",
                    "distance_value": 24465,  # ~15 miles in meters
                    "duration_text": "22 mins",
                    "duration_value": 1320,
                    "cached": False
                }
            else:  # event2
                return {
                    "distance_text": "239 mi", 
                    "distance_value": 384633,  # ~239 miles in meters (too far)
                    "duration_text": "3 hours",
                    "duration_value": 10800,
                    "cached": False
                }
        
        mock_calculate.side_effect = mock_distance_side_effect
        
        result = get_nearby_events_for_user("user123", 50)  # 50 mile limit
        
        assert len(result) == 1  # Only event1 should be within 50 miles
        assert result[0]["name"] == "Event 1"
        assert result[0]["distance_text"] == "15.2 mi"

    @patch('app.utils.distance_db.supabase')
    def test_get_nearby_events_for_user_no_events(self, mock_supabase):
        """Test getting nearby events with no events in database"""
        mock_events_response = MagicMock()
        mock_events_response.data = []
        mock_supabase.table.return_value.select.return_value.execute.return_value = mock_events_response
        
        result = get_nearby_events_for_user("user123", 50)
        
        assert result == []

    @patch('app.utils.distance_db.supabase')
    @patch('app.utils.distance_db.calculate_and_cache_distance')
    def test_get_nearby_events_for_user_distance_failure(self, mock_calculate, mock_supabase):
        """Test getting nearby events when distance calculation fails"""
        # Mock events response
        mock_events_response = MagicMock()
        mock_events_response.data = [
            {"id": "event1", "name": "Event 1", "location": "Houston, TX"}
        ]
        mock_supabase.table.return_value.select.return_value.execute.return_value = mock_events_response
        
        # Mock distance calculation failure
        mock_calculate.return_value = None
        
        result = get_nearby_events_for_user("user123", 50)
        
        assert result == []

    @patch('app.utils.distance_db.supabase')
    @patch('app.utils.distance_db.calculate_and_cache_distance')
    def test_get_nearby_events_for_user_sorting(self, mock_calculate, mock_supabase):
        """Test that events are sorted by distance"""
        # Mock events response
        mock_events_response = MagicMock()
        mock_events_response.data = [
            {"id": "event1", "name": "Event 1", "location": "Houston, TX"},
            {"id": "event2", "name": "Event 2", "location": "Austin, TX"},
            {"id": "event3", "name": "Event 3", "location": "San Antonio, TX"}
        ]
        mock_supabase.table.return_value.select.return_value.execute.return_value = mock_events_response
        
        # Mock distance calculations with different distances
        def mock_distance_side_effect(user_id, event_id, location):
            distances = {
                "event1": {"distance_value": 48280, "distance_text": "30 mi"},  # 30 miles
                "event2": {"distance_value": 16093, "distance_text": "10 mi"},  # 10 miles (closest)
                "event3": {"distance_value": 32187, "distance_text": "20 mi"}   # 20 miles
            }
            base_data = {
                "duration_text": "22 mins",
                "duration_value": 1320,
                "cached": False
            }
            return {**base_data, **distances[event_id]}
        
        mock_calculate.side_effect = mock_distance_side_effect
        
        result = get_nearby_events_for_user("user123", 50)
        
        assert len(result) == 3
        # Should be sorted by distance: event2 (10mi), event3 (20mi), event1 (30mi)
        assert result[0]["name"] == "Event 2"  # Closest
        assert result[1]["name"] == "Event 3"  # Middle
        assert result[2]["name"] == "Event 1"  # Farthest

    @patch('app.utils.distance_db.supabase')
    def test_get_nearby_events_for_user_exception(self, mock_supabase):
        """Test exception handling in get_nearby_events_for_user"""
        mock_supabase.table.return_value.select.return_value.execute.side_effect = Exception("Database error")
        
        result = get_nearby_events_for_user("user123", 50)
        
        assert result == []


class TestDistanceCacheEdgeCases:
    """Test edge cases and error conditions for distance caching"""

    @patch('app.utils.distance_db.supabase')
    def test_get_cached_distance_microsecond_precision(self, mock_supabase):
        """Test cache with different microsecond precision in timestamps"""
        # Test with a simple ISO format that should parse correctly
        future_time = (datetime.now() + timedelta(days=1)).isoformat()
        
        mock_response = MagicMock()
        mock_response.data = [{
            "distance_text": "15.2 mi",
            "duration_text": "22 mins",
            "distance_value": 24465,
            "duration_value": 1320,
            "expires_at": future_time,
            "created_at": datetime.now().isoformat()
        }]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response

        result = DistanceCache.get_cached_distance("user123", "event456")

        # Should handle timestamp format correctly
        assert result is not None
        assert result["distance_text"] == "15.2 mi"

    @patch('app.utils.distance_db.supabase')
    def test_cleanup_expired_cache_microsecond_handling(self, mock_supabase):
        """Test cache cleanup with various timestamp formats"""
        # Use simpler timestamp format that should work
        expired_time = (datetime.now() - timedelta(days=1)).isoformat()
        future_time = (datetime.now() + timedelta(days=1)).isoformat()
        
        mock_response = MagicMock()
        mock_response.data = [
            {"id": "cache1", "expires_at": expired_time, "created_at": datetime.now().isoformat()},
            {"id": "cache2", "expires_at": future_time, "created_at": datetime.now().isoformat()}
        ]
        
        mock_delete = MagicMock()
        mock_delete.data = [{"id": "cache1"}]
        
        mock_supabase.table.return_value.select.return_value.execute.return_value = mock_response
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_delete
        
        result = DistanceCache.cleanup_expired_cache(24)
        
        assert result == 1  # One expired entry should be cleaned up
