# 호권

[![CircleCI](https://circleci.com/gh/adyates/ksw-school-scrape/tree/master.svg?style=svg)](https://circleci.com/gh/adyates/ksw-school-scrape/tree/master)

## Short version
Script to scrape, standardize, and export the school owner data off of the
[KSW](www.kuksoolwon.com/site/schools) website for later mashup.

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
