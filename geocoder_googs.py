""""Takes a file of scraped addresses and geocodes them.  Uses the Google Maps Geocoding API."""

import csv
import io
import json
import os

from google.cloud import storage
import googlemaps

import fetch
import gcs


SCHOOL_GEODATA_FILE = 'data/school_geodata.csv'


def exportGeoData(school_list, file_name=None):

    file_out = io.StringIO() if file_name else open(SCHOOL_GEODATA_FILE, 'w')

    with file_out as csvout:
        writer = csv.DictWriter(
            csvout, [
                # Original fields from the scrape
                'City', 'Region', 'Address', 'Phone #s', 'Instructor',
                # Google Maps additional data
                'lat', 'lon', 'type', 'formatted_address'
            ], lineterminator='\n')

        header = {
            'Region': 'Region',
            'City': 'City',
            'Address': 'Address',
            'Phone #s':'Phone #s',
            'Instructor': 'Instructor',
            'lat': 'Latitude',
            'lon': 'Longitude',
            'type': 'Geocode Type',
            'formatted_address': 'Google Address'
        }

        writer.writerow(header)
        for school in school_list:
            writer.writerow(school)

        if file_name:
            # Save to GCS
            blob = gcs.getGeocodeBucket().blob('%s' % file_name)
            blob.upload_from_string(file_out.getvalue(), content_type='text/csv')

class LimitedApiManager:

    def __init__(self, cps):
        self.client = googlemaps.Client(
            key=os.environ['GOOGLE_GEOCODE_API_KEY'],
            queries_per_second=cps,
        )

    def get(self, address):
        print('  Fetching %s' % address)
        results = self.client.geocode(address)

        if len(results) != 1:
            print('  Found %s results for: %s' % (len(results), address))
            return None
        return results[0]

def _loadGCSDataFile(file_name):
    file_stream = io.StringIO(
        gcs.getFetchBucket().blob(file_name).download_as_string().decode(),
        newline=''
    )
    return file_stream


def loadSchoolData(file_name=None):
    data_file = _loadGCSDataFile(file_name) if file_name else open(fetch.SCHOOL_EXPORT_FILE, 'r')
    geocode_api = LimitedApiManager(30)

    school_data = csv.DictReader(data_file)
    school_list = []  # Save each row for later re-write
    for item in school_data:
        def _handleResponse(result):
            if not result:
                return None
            return result

        # Fetch the address first.  If it fails, switch to city+state
        print('Processing %s' % item['Address'])
        geodata = (
            item['Address'] and _handleResponse(geocode_api.get(address=item['Address'])) or
            _handleResponse(geocode_api.get(
                address=('%s, %s' % (item['City'], item['Region'])))))
        if not geodata:
            print('  Unable to find geodata for:\n%s' % json.dumps(item, indent=2))
            continue
        geometry = geodata['geometry']

        item.update({
            'lat': geometry['location']['lat'],
            'lon': geometry['location']['lng'],
            'type': geometry['location_type'],
            'formatted_address': geodata['formatted_address'],
        })
        school_list.append(item)

    exportGeoData(school_list, file_name)
    data_file.close()


def isDirectRun():
    return __name__ == '__main__'


if isDirectRun():
    loadSchoolData()
