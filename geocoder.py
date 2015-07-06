import csv
import time

import requests

import fetch


GOOGLE_GEOCODE_ENDPOINT = 'https://maps.googleapis.com/maps/api/geocode/json'
SCHOOL_GEODATA_FILE = 'data/school_geodata.csv'


def exportGeoData(school_list):
    with open(SCHOOL_GEODATA_FILE, 'wb') as csvout:
        writer = csv.DictWriter(csvout, [
            # Note that these are equivalent to the headers because of DictReader.fieldnames
                'City', 'Region', 'Address', 'Phone #s', 'Instructor', 'lat', 'lon', 'type'
            ], lineterminator='\n')

        header = {
            'Region': 'Region',
            'City': 'City',
            'Address': 'Address',
            'Phone #s':'Phone #s',
            'Instructor': 'Instructor',
            'lat': 'Latitude',
            'lon': 'Longitude',
            'type': 'Geocode Type'
        }

        writer.writerow(header)
        for school in school_list:
            writer.writerow(school)


class LimitedApiManager(object):

    def __init__(self, endpoint, cps, hardlimit, delay=1):
        self.endpoint = endpoint
        self.cps = cps
        self.delay = delay
        self.hardlimit = hardlimit
        self._req_count = 0

    def get(self, **kwargs):
        if self.cps <= self._req_count:
            print 'Pausing for a moment...'
            time.sleep(self.delay)
            self._req_count = 0
        self._req_count += 1
        return requests.get(self.endpoint, params=kwargs)


def loadSchoolData():

    geocode_api = LimitedApiManager(GOOGLE_GEOCODE_ENDPOINT, 5, 1)

    with open(fetch.SCHOOL_EXPORT_FILE, 'rb') as csv_in:
        school_data = csv.DictReader(csv_in)

        school_list = []  # Save each row for later re-write
        for item in school_data:
            def _handleResponse(response):
                json = response.json()
                result = json['results']
                if not result or (response.status_code != 200) or len(result) != 1:
                    return None
                geometry = result[0]['geometry']
                return geometry

            # Fetch the address first.  If it fails, switch to city+state
            geodata = (
                item['Address'] and _handleResponse(geocode_api.get(address=item['Address'])) or
                _handleResponse(geocode_api.get(address=('%s, %s' % (item['City'], item['Region'])))))
            location = geodata['location']

            item.update({
                'lat': location['lat'],
                'lon': location['lng'],
                'type': geodata['location_type']
            })
            school_list.append(item)

        exportGeoData(school_list)


if __name__ == '__main__':
    loadSchoolData()
