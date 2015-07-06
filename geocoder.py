import csv
import time

import requests


GOOGLE_GEOCODE_ENDPOINT = 'https://maps.googleapis.com/maps/api/geocode/json'
GOOGLE_STATIC_MAPS_ENDPOINT = (
    'https://maps.googleapis.com/maps/api/staticmap?size=1280x720&markers=%s')


def exportGeoData(school_list):
    with open('data/school_geodata.csv', 'wb') as csvout:
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


def exportMapsUrls(marker_data):
    for marker_list in marker_data:
        q = GOOGLE_STATIC_MAPS_ENDPOINT % '|'.join(marker_list)
        print q


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

    with open('data/school_data.csv', 'rb') as csv_in:
        school_data = csv.DictReader(csv_in)

        school_list = []  # Save each row for later re-write
        marker_data = [[]]  # Generate a sanity-check list of Google Static Map urls
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
            if len(marker_data[-1]) >= 100:
                # The Static Map API has a 2K char limit on URLs.  100 points per map is reasonable
                marker_data.append([])
            marker_data[-1].append('%s,%s' % (location['lat'], location['lng']))

        exportGeoData(school_list)
        exportMapsUrls(marker_data)


if __name__ == '__main__':
    loadSchoolData()
