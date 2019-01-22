import csv
from urllib.parse import quote
import webbrowser

import geocoder_googs as geocoder

GOOGLE_STATIC_MAPS_ENDPOINT = (
    'https://maps.googleapis.com/maps/api/staticmap?size=1280x720&markers=')

# Compute the max number of markers I can safely add before hitting the Static Map API char limit.
# String of addition at the end is composed of the following:
#    Length of urlencoded delimiters: comma (lat/lon) and pipe (marker points)
#    2 numbers per point consisting of:
#        1 - Sign character
#        3 - Max number of digits used by integer part
#        1 - Decimal
#        7 - Max number of digits used by fractional part (Est. based on points used)
MAX_EST_MARKER_COUNT = (2048 - len(GOOGLE_STATIC_MAPS_ENDPOINT)) / (
    len(quote(',|')) + 2 * (1 + 3 + 1 + 7))


def exportMapsUrls():

    marker_data = [[]]  # Generate a sanity-check list of Google Static Map urls
    with open(geocoder.SCHOOL_GEODATA_FILE, 'rb') as csv_in:
        school_data = csv.DictReader(csv_in)
        for school in school_data:
            if len(marker_data[-1]) >= MAX_EST_MARKER_COUNT:
                marker_data.append([])
            marker_data[-1].append('%s,%s' % (school['Latitude'], school['Longitude']))

    for marker_list in marker_data:
        map_url = GOOGLE_STATIC_MAPS_ENDPOINT + '|'.join(marker_list)

        # Verify they will load in a pretty way
        webbrowser.open_new_tab(map_url)


if __name__ == '__main__':
    exportMapsUrls()
