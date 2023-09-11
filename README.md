# 호권

[![CircleCI](https://circleci.com/gh/adyates/ksw-school-scrape/tree/master.svg?style=svg)](https://circleci.com/gh/adyates/ksw-school-scrape/tree/master)

## Short version
Script to scrape, standardize, and export the school owner data off of the
[KSW](https://www.kuksoolwon.com) website for later mashup.

If you are an intrepid person planning on using this, re-run locally, using any noted API keys.


## Setup

This project requires Python 3, and is developed against 3.7.1+.

Run the following to start the notebook properly:
```
## For the baseline interactive map with completed files
pip install -r requirements.txt
jupyter nbextension enable --py --sys-prefix ipyleaflet

## To enable the hohgwuhn library (assuming softlink for ./activate to env)
source activate
ipython kernel install --user --name=py3-hoh-gwuhn

# Run the notebook
jupyter notebook
```

For geocoding the addresses, this project also uses the Google Maps Platform Geocoding API.
Which means two things:
- You need to have a developer account for GCP setup with a Geocoding API
- You need to have billing enabled, as this will cost some amount of money

You will also need to set `GOOGLE_GEOCODE_API_KEY` in your environment to a valid Geocoding API key.

If you only want to visualize the data present or re-scrape the website, the API key is not needed.


## Long version

Part of a project to determine, from a given city, what the nearest school location should be
based on geolocating the current schools.  Since parts of the data website seems handcoded /
unstructured, given some of the wonky formatting issues and the lack of real Javascript on the
page (US regions are navigated by POST replies), the most reasonable thing to do is to parse out
the address information and reverse-lookup accordingly.

Doing it live is a bit cumbersome and not really needed, since the list of schools it not likely
to change on high interval relative to how I need to use this.

As a bonus, we might as well parse out the phone numbers since we can do that relatively easily
without writing this in Java thanks to @daviddrysdale and python-phonenumbers.


## Architecture notes

_At present, the beginning of the pipeline is broken as earlier this year WKSA completely rebuilt their website.  As a result, all the the bs4 code for scraping the schools is now broken until it is refactored to handle both the new site and the WKSA Korea site.  Running the data processing on older data should still work however._

With the exception of the final data location which is currently Firestore, the entire
toolchain is a series of cloud functions and GCS triggers, so that failures in processing
can be manually triggered as needed.

The entire process is kicked off by a cron schedule that runs on the 1st and 15th of every
month as configured in [createSchedule.sh](scripts/createSchedule.sh) (by publishing to the
`hoh-gwuhn-scrape` topic which triggers the first GCF). 

```
|-------|
|       | 
|  WKSA | -> fetch_wksa.py -> (/pandelyon-hoh-gwuhn-fetch) -> 
|_______|

    ---> geocoder_googs.py -> (/pandelyon-hoh-gwuhn-geocode) -> geoetl.py -> Cloud Firestore
```

Triggers are set at deploy time for each function in [the Circle config](.circleci/config.yml).

`geovis.py` exists only to generate a static map URL for validation / verification of the intermediate geocoded schools.
