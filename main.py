"""Wrapper file for use with Google Cloud Functions."""
# pylint: disable=line-too-long
from datetime import datetime
import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from hohgwuhn import geocoder_googs
from hohgwuhn import geoetl
from hohgwuhn import fetch_wksa


def fetchData(data=None, context=None):
    # pylint: disable=unused-argument
    """Wrapper around fetch.fetchData, intended to be called by scheduled cron only.

    Deploy with:
        gcloud functions deploy fetchData --runtime python37 --trigger-topic hoh-gwuhn-scrape --memory 128
    """
    fetch_wksa.fetchData()
    fetch_string = "Data fetch at %s" % datetime.today().strftime('%Y-%m-%d')
    print(fetch_string)

    # Send email notification via SendGrid
    message = Mail(
        from_email='alvin@pandelyon.com',
        to_emails='alvn@pandelyon.com',
        subject='[GCF] WKSA %s' % fetch_string,
        html_content="""Fetch Completed"""
    )
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        # pylint: disable=E1101
        print(e.message)

def geocodeFile(data=None, context=None):
    # pylint: disable=unused-argument
    """Wrapper around geocoder_googs.loadSchoolData, intended to be called as GCF via GCS event.

    Deploy with:
        gcloud functions deploy geocodeFile --runtime python37 --trigger-resource pandelyon-hoh-gwuhn-fetch --memory 128 --trigger-event google.storage.object.finalize --timeout 540
    """
    geocoder_googs.loadSchoolData(data['name'])
    print("Data geocode for %s at %s" % (data['name'], datetime.today().strftime('%Y-%m-%d')))


def geoETL(data=None, context=None):
    # pylint: disable=unused-argument
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
