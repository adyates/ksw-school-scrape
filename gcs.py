"""Utility functions for dealing with GCS and associated files."""
from google.cloud import storage


GCLOUD_FETCH_BUCKET = 'pandelyon-hoh-gwuhn-fetch'
GCLOUD_GEOCODE_BUCKET = 'pandelyon-hoh-gwuhn-geocode'

GCS_CLIENT = storage.Client()

def getFetchBucket():
    """Get the bucket used for storing scraped data."""
    return GCS_CLIENT.get_bucket(GCLOUD_FETCH_BUCKET)

def getGeocodeBucket():
    """Get the bucket used for storing geocoded data."""
    return GCS_CLIENT.get_bucket(GCLOUD_GEOCODE_BUCKET)
