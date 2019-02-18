""""Takes a file of scraped addresses and geocodes them, saving the result to a file.

When saving to local disk, uses 'data/school_geodata.csv'.

When saving to GCS, uses the same folder/file path as fetch.py

Uses the Google Maps Geocoding API.
"""

import io
import json
import os

import googlemaps
import pandas as pd

import fetch_wksa as fetch
import gcs


SCHOOL_GEODATA_FILE = 'data/school_geodata.csv'


def exportGeoData(school_df, file_name=None):
    """Write the geodata file from the dataframe, either to GCS or locally."""
    file_out = io.StringIO() if file_name else open(SCHOOL_GEODATA_FILE, 'w')

    # Write the CSV, but remove the pandas indices from the output
    school_df.to_csv(file_out, index=False)

    if file_name:
        # Save to GCS
        blob = gcs.getGeocodeBucket().blob('%s' % file_name)
        blob.upload_from_string(file_out.getvalue(), content_type='text/csv')

class LimitedApiManager:
    """Abstraction around any geocoding APIs that this file may need."""
    def __init__(self, cps):
        self.client = googlemaps.Client(
            key=os.environ['GOOGLE_GEOCODE_API_KEY'],
            queries_per_second=cps,
        )

    def get(self, address, country):
        """Get the geocoding results for a given address."""
        # Append the country to make isolate the search to the correct areas
        search_address = ', '.join([address, country])

        print('  Fetching %s' % search_address)
        results = self.client.geocode(search_address)
        print('  Found %s results for: %s' % (len(results), search_address))
        return results


def _loadGCSDataFile(file_name):
    """Get a file handle for a file from GCS."""
    file_stream = io.StringIO(
        gcs.getFetchBucket().blob(file_name).download_as_string().decode(),
        newline=''
    )
    return file_stream


def loadSchoolData(file_name=None):
    """Load school data from a file and process it."""
    data_file = _loadGCSDataFile(file_name) if file_name else open(fetch.SCHOOL_EXPORT_FILE, 'r')
    geocode_api = LimitedApiManager(30)

    school_df = pd.read_csv(data_file, keep_default_na=False)
    school_list = []  # Save each row for later re-write
    for row_tuple in school_df.iterrows():
        def _handleResponse(results, assure_address=True):
            """Process the results"""
            if len(results) != 1:
                if assure_address:
                    return None
                # Filter out only the approximate addresses
                results = [result for result in results if (
                    result['geometry']['location_type'] == 'APPROXIMATE'
                )]
            return results[0]

        # Fetch the address first.  If it fails, switch to city+state
        geocode_data = {
            'lat': '',
            'lon': '',
            'type': '',
            'formatted_address': '',
        }
        item = row_tuple[1]
        print('Processing %s' % item['Address'])
        geodata = (
            item['Address'] and _handleResponse(
                geocode_api.get(address=item['Address'], country=item['Country'])
            ) or
            _handleResponse(
                geocode_api.get(
                    address=('%s, %s' % (item['City'], item['Region'])),
                    country=item['Country']
                ),
                assure_address=False
            ))
        if not geodata:
            print('  Unable to find geodata for:\n%s' % json.dumps(item, indent=2))
            continue
        geometry = geodata['geometry']

        geocode_data.update({
            'lat': geometry['location']['lat'],
            'lon': geometry['location']['lng'],
            'type': geometry['location_type'],
            'formatted_address': geodata['formatted_address'],
        })
        school_list.append(geocode_data)

    # Create the new CSV columns in the dataframe
    school_df['Latitude'] = pd.Series([school['lat'] for school in school_list])
    school_df['Longitude'] = pd.Series([school['lon'] for school in school_list])
    school_df['Geocode Type'] = pd.Series([school['type'] for school in school_list])
    school_df['Google Address'] = pd.Series([school['formatted_address'] for school in school_list])

    exportGeoData(school_df, file_name)
    data_file.close()


def isDirectRun():
    return __name__ == '__main__'


if isDirectRun():
    loadSchoolData()
