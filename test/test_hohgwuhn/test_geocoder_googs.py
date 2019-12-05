# pylint: disable=W0621,R0201
import pytest

from hohgwuhn import geocoder_googs as geocoder

@pytest.fixture
def geocenter_wksa_school():
    """Sample Geocenter-only WKSA school"""
    return [{
        'address_components': [{
            'long_name': 'Okinawa',
            'short_name': 'Okinawa',
            'types': ['locality', 'political']
        }, {
            'long_name': 'Yamauchi',
            'short_name': 'Yamauchi',
            'types': ['political', 'sublocality', 'sublocality_level_2']
        }, {
            'long_name': 'Okinawa',
            'short_name': 'Okinawa',
            'types': ['administrative_area_level_1', 'political']
        }, {
            'long_name': 'Japan',
            'short_name': 'JP',
            'types': ['country', 'political']
        }, {
            'long_name': '904-0000',
            'short_name': '904-0000',
            'types': ['postal_code']
        }],
        'formatted_address': 'Yamauchi, Okinawa, 904-0000, Japan',
        'geometry': {
            'location': {'lat': 26.3395214, 'lng': 127.7749353},
            'location_type': 'GEOMETRIC_CENTER',
            'viewport': {
                'northeast': {'lat': 26.3408703802915, 'lng': 127.7762842802915},
                'southwest': {'lat': 26.3381724197085, 'lng': 127.7735863197085}
            }
        },
        'partial_match': True,
        'place_id': 'ChIJyScC2jcS5TQRF7ID3dD2AW4',
        'plus_code': {
            'compound_code': '8QQF+RX Okinawa, Japan',
            'global_code': '7QR98QQF+RX'
        },
        'types': ['establishment', 'gym', 'health', 'point_of_interest']
    }, {
        'address_components': [{
            'long_name': 'Japan',
            'short_name': 'JP',
            'types': ['country', 'political']
        }, {
            'long_name': 'Azahigashi',
            'short_name': 'Azahigashi',
            'types': ['political', 'sublocality', 'sublocality_level_2']
        }, {
            'long_name': 'Kadena',
            'short_name': 'Kadena',
            'types': ['locality', 'political']
        }, {
            'long_name': 'Nakagami District',
            'short_name': 'Nakagami District',
            'types': ['administrative_area_level_2', 'political']
        }, {
            'long_name': 'Okinawa',
            'short_name': 'Okinawa',
            'types': ['administrative_area_level_1', 'political']
        }],
        'formatted_address': 'Azahigashi, Kadena, Nakagami District, Okinawa, Japan',
        'geometry': {
            'location': {'lat': 26.3556897, 'lng': 127.7678754},
            'location_type': 'GEOMETRIC_CENTER',
            'viewport': {
                'northeast': {'lat': 26.35703868029151, 'lng': 127.7692243802915},
                'southwest': {'lat': 26.3543407197085, 'lng': 127.7665264197085}
            }
        },
        'partial_match': True,
        'place_id': 'ChIJ6ypdpi4S5TQRpph-c1CUQmg',
        'plus_code': {
            'compound_code': '9Q49+75 Kadena, Okinawa, Japan',
            'global_code': '7QR99Q49+75'
        },
        'types': ['establishment', 'point_of_interest']
    }]


class TestHandleMapsResponse:
    """Verifies the handling of various responses from Google Maps"""
    # pylint: disable=W0212

    def test_assure_returns_none_for_geocenters(self, geocenter_wksa_school):
        """Verify None is returned when no approximates and address assured"""
        test_results = geocoder._handleResponse(
            geocenter_wksa_school,
            assure_address=True
        )

        assert test_results is None

    def test_handle_no_approximate_locations_found(self, geocenter_wksa_school):
        """Verify that a school without an approx. results is still saved."""
        test_results = geocoder._handleResponse(
            geocenter_wksa_school,
            assure_address=False
        )

        assert test_results
        assert test_results == geocenter_wksa_school[0]
