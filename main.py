"""Wrapper file for use with Google Cloud Functions."""
from datetime import datetime

import geocoder_googs
import geoetl
import fetch


def fetchData(data=None, context=None):
    """Wrapper around fetch.fetchData, intended to be called by scheduled cron only.

    Deploy with:
        gcloud functions deploy fetchData --runtime python37 --trigger-topic hoh-gwuhn-scrape --memory 128
    """
    fetch.fetchData()
    print("Data fetch at %s" % datetime.today().strftime('%Y-%m-%d'))


def geocodeFile(data=None, context=None):
    """Wrapper around geocoder_googs.loadSchoolData, intended to be called as GCF via GCS event.

    Deploy with:
        gcloud functions deploy geocodeFile --runtime python37 --trigger-resource pandelyon-hoh-gwuhn-fetch --memory 128 --trigger-event google.storage.object.finalize --timeout 540
    """
    geocoder_googs.loadSchoolData(data['name'])
    print("Data geocode for %s at %s" % (data['name'], datetime.today().strftime('%Y-%m-%d')))


def geoETL(data=None, context=None):
    """Wrapper around geoetl.loadRegionFile, intended to be called as GCF via GCS event.

    Deploy with:
        gcloud functions deploy geoETL --runtime python37 --trigger-resource pandelyon-hoh-gwuhn-geocode --memory 128 --trigger-event google.storage.object.finalize --timeout 540
    """
    print('GCS Data')
    print(data)
    geoetl.loadCountryFile(data['name'])
    print(
        "Geocode data loaded to Firestore for %s at %s" % (
            data['name'],
            datetime.today().strftime('%Y-%m-%d')
        ))
