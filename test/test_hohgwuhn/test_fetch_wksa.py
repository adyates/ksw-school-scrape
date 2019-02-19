# pylint: disable=W0621,R0201
import copy

import pytest

from hohgwuhn import fetch_wksa as fetch

@pytest.fixture
def us_wksa_school():
    """Sample US school"""
    return {
        'country_name': 'U.S.A', 'country_code': 'US', 'region': 'Arizona', 'city': 'Phoenix',
        'website': '', 'address': 'NEW!!! 126 W. Desert Hills Phoenix, AZ 85086  623-337-0258',
        'phone_numbers': [], 'instructor': 'Inst. Angela Hoikka'
    }


@pytest.fixture
def kr_wksa_school():
    """Sample Korea school"""
    # pylint: disable=line-too-long
    return {
        'country_name': 'KOREA', 'country_code': 'KR', 'region': 'Busan', 'city': 'Phil',
        'website': '',
        'address': 'No.1001 Youngdong-Plaza JwaDong Haewoondae-Gu Busan Younggeun Gye 051-701-5588 018-563-7503',
        'phone_numbers': [], 'instructor': ''
    }

@pytest.fixture
def kr_wksa_school_gangwon():
    """Sample Korea school, formatted as the 설 | 경기 | 강원 schools"""
    # pylint: disable=line-too-long
    return {
        'country_name': 'KOREA', 'country_code': 'KR', 'region': 'Seoul | Gyeonggi | Gangwon',
        'city': 'Boknam Myuong', 'website': '',
        'address': '1111 3Ban Youngheung8Ri Youngwol-Eup Youngwol-Gun Gangwon 033-373-2124 011-9243-7468',
        'phone_numbers': [], 'instructor': ''
    }

@pytest.fixture
def kr_wksa_school_daegu():
    """The mislabeled Korean 대구 school"""
    # pylint: disable=line-too-long
    return {
        'country_name': 'KOREA', 'country_code': 'KR', 'region': 'Seoul | Gyeonggi | Gangwon',
        'city': 'Dong-Gu Daegu', 'website': '',
        'address': '136-156 Sinam4-Dong 053-942-4414 053-942-4415',
        'phone_numbers': [], 'instructor': ''
    }


class TestFetch:
    """Test utility functions related to fetching data."""

    def test_us_phone_number_extracted(self, us_wksa_school):
        """Verify US phone numbers are properly extracted."""
        test_school_list = [us_wksa_school]
        fetch.separatePhoneNumbers(test_school_list)
        school = test_school_list[0]
        assert school['phone_numbers'] == '(623) 337-0258'
        assert school['address'] == 'NEW!!! 126 W. Desert Hills Phoenix, AZ 85086'

    def test_kr_phone_number_extracted(self, kr_wksa_school):
        """Verify KR phone numbers are properly extracted."""
        # pylint: disable=line-too-long
        test_school_list = [kr_wksa_school]
        fetch.separatePhoneNumbers(test_school_list)
        school = test_school_list[0]
        assert school['phone_numbers'] == '051-701-5588;018-563-7503'
        assert school['address'] == 'No.1001 Youngdong-Plaza JwaDong Haewoondae-Gu Busan Younggeun Gye'

    def test_non_kr_school_skips_hankuk(self, us_wksa_school):
        """Verify that a US school gets skipped by Korean-specific processing."""
        test_school_list = [us_wksa_school]
        fetch.separatePhoneNumbers(test_school_list)
        original_school = copy.deepcopy(test_school_list[0])

        fetch.handleHankuk(test_school_list)
        assert original_school == test_school_list[0]

    def test_regular_kr_school_gets_corrected(self, kr_wksa_school):
        """Verify that a US school gets skipped by Korean-specific processing."""
        test_school_list = [copy.deepcopy(kr_wksa_school)]
        fetch.separatePhoneNumbers(test_school_list)

        assert kr_wksa_school != test_school_list[0]
        fetch.handleHankuk(test_school_list)
        school = test_school_list[0]

        assert school['instructor'] == 'Younggeun Gye'
        assert school['region'] == 'Busan'
        assert school['address'] == 'No.1001 Youngdong-Plaza JwaDong Haewoondae-Gu Busan'
        assert school['city'] == 'Phil'

    def test_gangwon_kr_school_gets_corrected(self, kr_wksa_school_gangwon):
        """Verify that a US school gets skipped by Korean-specific processing."""
        test_school_list = [copy.deepcopy(kr_wksa_school_gangwon)]
        fetch.separatePhoneNumbers(test_school_list)

        assert kr_wksa_school_gangwon != test_school_list[0]
        fetch.handleHankuk(test_school_list)
        school = test_school_list[0]

        assert school['instructor'] == 'Boknam Myuong'
        assert school['region'] == 'Gangwon'
        assert school['address'] == '1111 3Ban Youngheung8Ri Youngwol-Eup Youngwol-Gun Gangwon'
        assert school['city'] == 'Youngwol-Gun'

    def test_daegu_kr_school_gets_corrected(self, kr_wksa_school_daegu):
        """Verify that a US school gets skipped by Korean-specific processing."""
        test_school_list = [copy.deepcopy(kr_wksa_school_daegu)]
        fetch.separatePhoneNumbers(test_school_list)

        assert kr_wksa_school_daegu != test_school_list[0]
        fetch.handleHankuk(test_school_list)
        school = test_school_list[0]

        assert school['instructor'] == ''
        assert school['region'] == 'Daegu'
        assert school['address'] == '136-156 Sinam4-Dong Dong-Gu Daegu'
        assert school['city'] == 'Dong-Gu'
