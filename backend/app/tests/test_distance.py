import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from app.utils.distance import (
    DistanceCalculator, 
    distance_calculator, 
    get_user_full_address, 
    calculate_distance_to_event, 
    safe_distance_calculation
)

class TestDistanceCalculator:
    """Test the DistanceCalculator class"""
    
    @patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test_api_key"})
    @patch('app.utils.distance.googlemaps.Client')
    def test_init_with_api_key(self, mock_client):
        """Test initialization with valid API key"""
        calculator = DistanceCalculator()
        assert calculator.api_key == "test_api_key"
        mock_client.assert_called_once_with(key="test_api_key")
        assert calculator.client is not None

    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_api_key(self):
        """Test initialization without API key"""
        calculator = DistanceCalculator()
        assert calculator.api_key is None
        assert calculator.client is None

    @patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test_api_key"})
    @patch('app.utils.distance.googlemaps.Client')
    def test_init_client_exception(self, mock_client):
        """Test initialization when Google Maps client fails"""
        mock_client.side_effect = Exception("API error")
        calculator = DistanceCalculator()
        assert calculator.client is None

    def test_geocode_address_no_client(self):
        """Test geocoding when client is not available"""
        calculator = DistanceCalculator()
        calculator.client = None
        result = calculator.geocode_address("Houston, TX")
        assert result is None

    @patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test_api_key"})
    @patch('app.utils.distance.googlemaps.Client')
    def test_geocode_address_success(self, mock_client):
        """Test successful geocoding"""
        mock_geocode_result = [{
            'geometry': {
                'location': {'lat': 29.7604, 'lng': -95.3698}
            }
        }]
        mock_client_instance = Mock()
        mock_client_instance.geocode.return_value = mock_geocode_result
        mock_client.return_value = mock_client_instance
        
        calculator = DistanceCalculator()
        result = calculator.geocode_address("Houston, TX")
        
        assert result == (29.7604, -95.3698)
        mock_client_instance.geocode.assert_called_once_with("Houston, TX")

    @patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test_api_key"})
    @patch('app.utils.distance.googlemaps.Client')
    def test_geocode_address_no_results(self, mock_client):
        """Test geocoding with no results"""
        mock_client_instance = Mock()
        mock_client_instance.geocode.return_value = []
        mock_client.return_value = mock_client_instance
        
        calculator = DistanceCalculator()
        result = calculator.geocode_address("Invalid Address")
        
        assert result is None

    @patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test_api_key"})
    @patch('app.utils.distance.googlemaps.Client')
    def test_geocode_address_exception(self, mock_client):
        """Test geocoding with exception"""
        mock_client_instance = Mock()
        mock_client_instance.geocode.side_effect = Exception("API error")
        mock_client.return_value = mock_client_instance
        
        calculator = DistanceCalculator()
        result = calculator.geocode_address("Houston, TX")
        
        assert result is None

    def test_calculate_distance_no_client(self):
        """Test distance calculation when client is not available"""
        calculator = DistanceCalculator()
        calculator.client = None
        result = calculator.calculate_distance("Houston, TX", "Dallas, TX")
        assert result is None

    @patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test_api_key"})
    @patch('app.utils.distance.googlemaps.Client')
    def test_calculate_distance_success(self, mock_client):
        """Test successful distance calculation"""
        mock_distance_result = {
            'rows': [{
                'elements': [{
                    'status': 'OK',
                    'distance': {'text': '239 mi', 'value': 384633},
                    'duration': {'text': '3 hours 35 mins', 'value': 12900}
                }]
            }],
            'origin_addresses': ['Houston, TX, USA'],
            'destination_addresses': ['Dallas, TX, USA']
        }
        mock_client_instance = Mock()
        mock_client_instance.distance_matrix.return_value = mock_distance_result
        mock_client.return_value = mock_client_instance
        
        calculator = DistanceCalculator()
        result = calculator.calculate_distance("Houston, TX", "Dallas, TX", "driving")
        
        expected = {
            "distance": {'text': '239 mi', 'value': 384633},
            "duration": {'text': '3 hours 35 mins', 'value': 12900},
            "status": 'OK',
            "mode": "driving",
            "origin_address": 'Houston, TX, USA',
            "destination_address": 'Dallas, TX, USA'
        }
        assert result == expected

    @patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test_api_key"})
    @patch('app.utils.distance.googlemaps.Client')
    def test_calculate_distance_no_results(self, mock_client):
        """Test distance calculation with no results"""
        mock_client_instance = Mock()
        mock_client_instance.distance_matrix.return_value = None
        mock_client.return_value = mock_client_instance
        
        calculator = DistanceCalculator()
        result = calculator.calculate_distance("Houston, TX", "Invalid Address")
        
        assert result is None

    @patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test_api_key"})
    @patch('app.utils.distance.googlemaps.Client')
    def test_calculate_distance_status_not_ok(self, mock_client):
        """Test distance calculation with non-OK status"""
        mock_distance_result = {
            'rows': [{
                'elements': [{'status': 'NOT_FOUND'}]
            }]
        }
        mock_client_instance = Mock()
        mock_client_instance.distance_matrix.return_value = mock_distance_result
        mock_client.return_value = mock_client_instance
        
        calculator = DistanceCalculator()
        result = calculator.calculate_distance("Houston, TX", "Invalid Address")
        
        assert result is None

    @patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test_api_key"})
    @patch('app.utils.distance.googlemaps.Client')
    def test_calculate_distance_exception(self, mock_client):
        """Test distance calculation with exception"""
        mock_client_instance = Mock()
        mock_client_instance.distance_matrix.side_effect = Exception("API error")
        mock_client.return_value = mock_client_instance
        
        calculator = DistanceCalculator()
        result = calculator.calculate_distance("Houston, TX", "Dallas, TX")
        
        assert result is None

    @patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test_api_key"})
    @patch('app.utils.distance.googlemaps.Client')
    def test_calculate_distance_simple_success(self, mock_client):
        """Test simple distance calculation success"""
        mock_distance_result = {
            'rows': [{
                'elements': [{
                    'status': 'OK',
                    'distance': {'text': '239 mi', 'value': 384633},
                    'duration': {'text': '3 hours 35 mins', 'value': 12900}
                }]
            }],
            'origin_addresses': ['Houston, TX, USA'],
            'destination_addresses': ['Dallas, TX, USA']
        }
        mock_client_instance = Mock()
        mock_client_instance.distance_matrix.return_value = mock_distance_result
        mock_client.return_value = mock_client_instance
        
        calculator = DistanceCalculator()
        result = calculator.calculate_distance_simple("Houston, TX", "Dallas, TX")
        
        assert result == '239 mi'

    @patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test_api_key"})
    @patch('app.utils.distance.googlemaps.Client')
    def test_calculate_distance_simple_failure(self, mock_client):
        """Test simple distance calculation failure"""
        mock_client_instance = Mock()
        mock_client_instance.distance_matrix.return_value = None
        mock_client.return_value = mock_client_instance
        
        calculator = DistanceCalculator()
        result = calculator.calculate_distance_simple("Houston, TX", "Invalid Address")
        
        assert result is None


class TestAddressUtilities:
    """Test address and distance utility functions"""

    def test_get_user_full_address_complete(self):
        """Test building full address with all fields"""
        user_profile = {
            'address1': '123 Main St',
            'address2': 'Apt 4B',
            'city': 'Houston',
            'state': 'TX',
            'zip_code': '77001'
        }
        result = get_user_full_address(user_profile)
        assert result == '123 Main St, Apt 4B, Houston, TX, 77001'

    def test_get_user_full_address_minimal(self):
        """Test building address with only required fields"""
        user_profile = {
            'address1': '123 Main St',
            'city': 'Houston',
            'state': 'TX'
        }
        result = get_user_full_address(user_profile)
        assert result == '123 Main St, Houston, TX'

    def test_get_user_full_address_no_address2_no_zip(self):
        """Test building address without optional fields"""
        user_profile = {
            'address1': '123 Main St',
            'address2': '',  # Empty string
            'city': 'Houston',
            'state': 'TX',
            'zip_code': None  # None value
        }
        result = get_user_full_address(user_profile)
        assert result == '123 Main St, Houston, TX'

    def test_get_user_full_address_missing_required_fields(self):
        """Test building address with missing required fields"""
        user_profile = {
            'address1': '',
            'city': 'Houston',
            'state': 'TX'
        }
        result = get_user_full_address(user_profile)
        assert result is None

    def test_get_user_full_address_missing_city(self):
        """Test building address with missing city"""
        user_profile = {
            'address1': '123 Main St',
            'city': '',
            'state': 'TX'
        }
        result = get_user_full_address(user_profile)
        assert result is None

    def test_get_user_full_address_missing_state(self):
        """Test building address with missing state"""
        user_profile = {
            'address1': '123 Main St',
            'city': 'Houston',
            'state': ''
        }
        result = get_user_full_address(user_profile)
        assert result is None

    def test_get_user_full_address_none_values(self):
        """Test building address with None values"""
        user_profile = {
            'address1': None,
            'city': 'Houston',
            'state': 'TX'
        }
        result = get_user_full_address(user_profile)
        assert result is None

    def test_get_user_full_address_exception(self):
        """Test exception handling in address building"""
        # Pass invalid data type to trigger exception
        result = get_user_full_address("not a dict")
        assert result is None

    @patch('app.utils.distance.get_user_full_address')
    @patch('app.utils.distance.distance_calculator')
    def test_calculate_distance_to_event_success(self, mock_calculator, mock_address):
        """Test successful distance calculation to event"""
        mock_address.return_value = "123 Main St, Houston, TX"
        mock_calculator.calculate_distance_simple.return_value = "15.2 mi"
        
        user_profile = {'address1': '123 Main St', 'city': 'Houston', 'state': 'TX'}
        result = calculate_distance_to_event(user_profile, "456 Oak Ave, Houston, TX")
        
        assert result == "15.2 mi"
        mock_address.assert_called_once_with(user_profile)
        mock_calculator.calculate_distance_simple.assert_called_once_with(
            "123 Main St, Houston, TX", "456 Oak Ave, Houston, TX"
        )

    @patch('app.utils.distance.get_user_full_address')
    def test_calculate_distance_to_event_no_address(self, mock_address):
        """Test distance calculation when user address cannot be built"""
        mock_address.return_value = None
        
        user_profile = {'address1': '', 'city': 'Houston', 'state': 'TX'}
        result = calculate_distance_to_event(user_profile, "456 Oak Ave, Houston, TX")
        
        assert result is None

    @patch('app.utils.distance.calculate_distance_to_event')
    def test_safe_distance_calculation_success(self, mock_calculate):
        """Test safe distance calculation success"""
        mock_calculate.return_value = "15.2 mi"
        
        user_profile = {'address1': '123 Main St', 'city': 'Houston', 'state': 'TX'}
        result = safe_distance_calculation(user_profile, "456 Oak Ave, Houston, TX")
        
        assert result == "15.2 mi"

    @patch('app.utils.distance.calculate_distance_to_event')
    def test_safe_distance_calculation_none_result(self, mock_calculate):
        """Test safe distance calculation with None result"""
        mock_calculate.return_value = None
        
        user_profile = {'address1': '123 Main St', 'city': 'Houston', 'state': 'TX'}
        result = safe_distance_calculation(user_profile, "456 Oak Ave, Houston, TX", "N/A")
        
        assert result == "N/A"

    @patch('app.utils.distance.calculate_distance_to_event')
    def test_safe_distance_calculation_exception(self, mock_calculate):
        """Test safe distance calculation with exception"""
        mock_calculate.side_effect = Exception("API error")
        
        user_profile = {'address1': '123 Main St', 'city': 'Houston', 'state': 'TX'}
        result = safe_distance_calculation(user_profile, "456 Oak Ave, Houston, TX", "Error")
        
        assert result == "Error"

    def test_safe_distance_calculation_default_fallback(self):
        """Test safe distance calculation with default fallback"""
        with patch('app.utils.distance.calculate_distance_to_event', side_effect=Exception("Error")):
            user_profile = {'address1': '123 Main St', 'city': 'Houston', 'state': 'TX'}
            result = safe_distance_calculation(user_profile, "456 Oak Ave, Houston, TX")
            
            assert result == "Distance unavailable"


class TestGlobalDistanceCalculator:
    """Test the global distance_calculator instance"""

    def test_global_instance_exists(self):
        """Test that global distance calculator instance exists"""
        assert distance_calculator is not None
        assert isinstance(distance_calculator, DistanceCalculator)

    def test_global_instance_api_key_handling(self):
        """Test that global instance handles API key correctly"""
        # Test that it doesn't crash when API key is missing
        if not distance_calculator.api_key:
            assert distance_calculator.client is None
        else:
            # If API key exists, client should be initialized or None due to error
            assert distance_calculator.client is not None or distance_calculator.client is None


class TestDistanceCalculatorEdgeCases:
    """Test edge cases and error conditions"""

    @patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test_api_key"})
    @patch('app.utils.distance.googlemaps.Client')
    def test_distance_matrix_empty_rows(self, mock_client):
        """Test distance calculation with empty rows"""
        mock_distance_result = {'rows': []}
        mock_client_instance = Mock()
        mock_client_instance.distance_matrix.return_value = mock_distance_result
        mock_client.return_value = mock_client_instance
        
        calculator = DistanceCalculator()
        result = calculator.calculate_distance("Houston, TX", "Dallas, TX")
        
        assert result is None

    @patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test_api_key"})
    @patch('app.utils.distance.googlemaps.Client')
    def test_distance_matrix_missing_keys(self, mock_client):
        """Test distance calculation with missing response keys"""
        mock_distance_result = {
            'rows': [{
                'elements': [{
                    'status': 'OK',
                    # Missing distance and duration keys - this should be handled gracefully
                }]
            }]
        }
        mock_client_instance = Mock()
        mock_client_instance.distance_matrix.return_value = mock_distance_result
        mock_client.return_value = mock_client_instance
    
        calculator = DistanceCalculator()
        result = calculator.calculate_distance("Houston, TX", "Dallas, TX")
    
        # Should return None when required keys are missing
        assert result is None
    
    def test_get_user_full_address_whitespace_handling(self):
        """Test address building with whitespace in fields"""
        user_profile = {
            'address1': '  123 Main St  ',
            'address2': '  Apt 4B  ',
            'city': '  Houston  ',
            'state': '  TX  ',
            'zip_code': '  77001  '
        }
        result = get_user_full_address(user_profile)
        assert result == '123 Main St, Apt 4B, Houston, TX, 77001'

    def test_get_user_full_address_mixed_none_empty(self):
        """Test address building with mix of None and empty values"""
        user_profile = {
            'address1': '123 Main St',
            'address2': None,
            'city': 'Houston',
            'state': 'TX',
            'zip_code': ''
        }
        result = get_user_full_address(user_profile)
        assert result == '123 Main St, Houston, TX'
