""""Takes a file of geocoded addresses and pushes them to Cloud Firestore in two collections.

The first collection records the metadata around the scrape file itself:

=============
scrape_record
-------------
- Country: Country scraped.  Currently {'USA'}
- Date: Date the file was scraped in YYYY-mm-dd format
- GCS Location: The location of the file, in case we need to get it later
=============

The second collection corresponds to an individual location

===============
school_location
---------------
* Metadata: Each field in the geocoded file, re-written into snake case
- scrape_record_id: The scrape_record this school came from
- Country: For filtering, the denormalized Country from the given scrape_record
"""
import csv
import io
from os.path import getmtime
import re
from time import gmtime, strftime

from google.cloud import firestore

from . import gcs
from . import geocoder_googs


FIRESTORE = firestore.Client()

def _loadGCSDataFile(file_name):
    file_stream = io.StringIO(
        gcs.getGeocodeBucket().blob(file_name).download_as_string().decode(),
        newline=''
    )
    return file_stream

def loadCountryFile(file_name=None):
    # Get derived fields
    country_file = (
        _loadGCSDataFile(file_name) if file_name else open(geocoder_googs.SCHOOL_GEODATA_FILE, 'r')
    )
    country_name, scrape_date = (
        file_name.split('/')[-2:] if file_name else (
            'USA', strftime('%Y-%m-%d', gmtime(getmtime(geocoder_googs.SCHOOL_GEODATA_FILE)))
        )
    )

    #####   Build the document sets
    # Scrape Record
    scrape_record_id = '%s-%s' % (country_name, scrape_date)
    scrape_record = {
        'country': country_name,
        'date': scrape_date,
        'gcs_location': file_name or ''
    }

    # Schools
    school_data = csv.DictReader(country_file)
    school_list = []
    for item in school_data:
        school_list.append({
            # Geocoded data
            'region': item['Region'],
            'city': item['City'],
            'raw_address': item['Address'],
            'phone_numbers': item['Phone #s'],
            'instructor': item['Instructor'],
            'lat': item['Latitude'],
            'lon': item['Longitude'],
            'type': item['Geocode Type'],
            'google_address': item.get('Google Address', ''),

            # Scrape record data
            'country': country_name,
            'scrape_record_id': scrape_record_id
        })

    ##### Add all of them to Cloud Firestore
    batch = FIRESTORE.batch()
    scrape_record_ref = FIRESTORE.collection('scrape_record').document(scrape_record_id)
    # Scrape record
    batch.set(scrape_record_ref, scrape_record)

    # Schools, stored as a subcollection of the record
    for school in school_list:
        # Imperfect and remove spacing and bad characters
        school_id = re.sub(
            r'[/\s]',
            '',
            '%s-%s-%s' % (country_name, school['region'], school['city'])
        )
        batch.set(
            scrape_record_ref.collection('school_location').document(school_id),
            school
        )

    # Save
    batch.commit()


def isDirectRun():
    return __name__ == '__main__'


if isDirectRun():
    loadCountryFile()
