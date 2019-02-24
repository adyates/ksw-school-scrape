"""Fetches school data from the official WKSA website via web scraping with BS4."""
# pylint: disable=invalid-name

import csv
from datetime import datetime
import io
import re

from bs4 import BeautifulSoup
import country_converter as coco
import phonenumbers as libphone
import requests

from . import gcs


SCHOOL_EXPORT_FILE = '../data/school_data.csv'


def isDirectRun():
    """Checks if this is being called as main or not."""
    return __name__ == '__main__'

def pullWksaCountryPages():
    """Scrapes the WKSA schools website for the list of countries WKSA has locations in."""
    KSW_SCHOOLS_PAGE = 'http://www.kuksoolwon.com/site/schools'
    r = requests.get(KSW_SCHOOLS_PAGE)
    schools_page = BeautifulSoup(r.text, 'lxml')
    schools_navigation = schools_page.select('#submenu_schools > a')

    print('Found %s countries for WKSA' % len(schools_navigation))

    ksw_countries = []
    for country_link in schools_navigation:
        link_href = country_link['href']
        country_name = country_link.get_text()

        country_code = coco.convert(names=[country_name], to='ISO2')
        print('%s  ->  %s (%s)' % (country_code, country_name, link_href))
        ksw_countries.append({
            'name': country_name,
            'link': link_href,
            'ISO-2': country_code
        })
    return ksw_countries


# Country page processing
def _getSchoolsContent(country_page, country_name, country_code):
    school_list = []
    subpage = country_page.select('div.schools_content > div')

    ksw_region = ''
    for section in subpage:
        # Determine if this is a region header or a school
        if 'region_name' in section['class']:
            ksw_region = section.get_text().title()
        else:
            city_div = section.select_one('div.city')

            # Overly verify that <br />s are properly handled in addresses
            contact_div = section.select_one('div.contact')
            _ = [contact_br.insert_after('\n') for contact_br in contact_div.select('br')]

            school_list.append({
                'country_name': country_name,
                'country_code': country_code,
                'region': ksw_region.strip(),
                'city': city_div.get_text().strip(),

                # Homepage may not be present
                'website': city_div.a['href'] if city_div.a else '',

                # Instructors hand-edit this section, so remove excessive newlines
                'address': str(re.sub(r'(\r?\n)+', ' ', contact_div.get_text()).strip()),
                'phone_numbers': [],
                'instructor': section.select_one('div.instructor').get_text().strip()
            })
    print('Found %s schools for %s' % (len(school_list), country_name))
    return school_list

def skipDirectoryInfo(*_):
    """No operation, reserved for countries with partial pages."""
    return []

def pullGenericDirectoryInfo(country_href, country_name, country_code):
    """Pull the school information from your average WKSA country page."""
    r = requests.get(country_href)
    country_page = BeautifulSoup(r.text, 'lxml')
    return _getSchoolsContent(country_page, country_name, country_code)

def pullUsaDirectoryInfo(country_href, country_name, country_code):
    """Pull the school information for America, because we're special."""
    KSW_REGIONS = 4

    school_list = []
    for geo_id in range(1, KSW_REGIONS + 1):
        r = requests.post(country_href, data={'geo_id': geo_id})
        usa_page = BeautifulSoup(r.text, 'lxml')
        subregion_schools = _getSchoolsContent(usa_page, country_name, country_code)
        school_list.extend(subregion_schools)
    return school_list

# Function map of how special countries should be handled
SPECIAL_COUNTRY_HANDLING = {
    'US': pullUsaDirectoryInfo,
    'BR': skipDirectoryInfo
}

def separatePhoneNumbers(school_list):
    """Strips out the phone numbers for a given country from the directory information."""
    for school in school_list:
        phone_index_min = len(school['address'])
        school_address = str(school['address'])
        for match in libphone.PhoneNumberMatcher(school_address, school['country_code']):
            school['phone_numbers'].append(
                str(libphone.format_number(match.number, libphone.PhoneNumberFormat.NATIONAL)))
            phone_index_min = min(phone_index_min, match.start)

        # Reformat the phone numbers to be semi-colon delimited, if present
        school['phone_numbers'] = ';'.join(school['phone_numbers'])

        # Remove the phone numbers from the address.  Go by section because multiple numbers get
        # are not represented uniformly (e.g. Palmdale, CA)
        school['address'] = school['address'][:phone_index_min].strip()


def exportCSV(school_list, scrape_region='WORLD'):
    """Write the file locally or buffer for GCS upload."""
    file_out = open(SCHOOL_EXPORT_FILE, 'w') if isDirectRun() else io.StringIO()

    with file_out as csvout:
        writer = csv.DictWriter(
            csvout,
            [
                'country_name', 'country_code', 'city', 'region',
                'address', 'website', 'phone_numbers', 'instructor'
            ],
            lineterminator='\n')

        header = {
            'country_name': 'Country',
            'country_code': 'Country Code',
            'region': 'Region',
            'city': 'City',
            'address': 'Address',
            'website': 'Website',
            'phone_numbers':'Phone #s',
            'instructor': 'Instructor'
        }

        writer.writerow(header)
        for school in school_list:
            writer.writerow(school)

        if not isDirectRun():
            # Save to GCS

            blob = gcs.getFetchBucket().blob(
                '%s/%s' % (scrape_region, datetime.today().strftime('%Y-%m-%d'))
            )
            blob.upload_from_string(file_out.getvalue(), content_type='text/csv')


def handleHankuk(wksa_schools):
    """Korean schools are formatted differently and needs some adjustment before geocoding."""
    for school in wksa_schools:
        if school['country_code'] != 'KR':
            # School must be Korea
            continue

        # The 4th column has the region, but may contain multiple cities for a region
        city_set = re.sub(r'\s[/|]\s', ' ', school['region']).split()
        if len(city_set) > 1:
            # Figure out which city we're in by using the address
            for region in city_set:
                if region in school['address']:
                    school['region'] = region

        # Split address as KR addresses list the instructor last, throwing off geocoding
        tokenized_address = school['address'].split()
        if school['region'] == school['address'].split()[-1]:
            # If the last token in the address is the City, the City column is the Instructor.
            # Replace it with token before the city in the address (should be district).
            new_boundary = school['address'].split()[-2]
            school['address'] += ' %s' % school['city']

            # Keep the Instructor and retokenize the address
            school['instructor'] = school['city']
            school['city'] = new_boundary
            tokenized_address = school['address'].split()

        elif school['region'] not in school['address']:
            # If region isn't in the address, then the City is in the Region. Fix all 3
            # e.g. Dong-Gu Daegu
            school['address'] += ' %s' % school['city']

            # Region is generally last in KR WKSA addresses
            school['region'] = school['city'].split()[-1]

            # Retokenize the address and set the new city
            tokenized_address = school['address'].split()
            new_boundary = school['address'].split()[-2]
            school['city'] = new_boundary

        if school['region'] == tokenized_address[-3]:
            # The last two tokens are the Instructor.  Cut and replace to Instructor column
            school['instructor'] = ' '.join(tokenized_address[-2:])
            school['address'] = ' '.join(tokenized_address[:-2])


def fetchData():
    """Fetch all the data from the KSW website."""
    wksa_countries = pullWksaCountryPages()
    wksa_schools = []
    for country in wksa_countries:
        handleCountry = SPECIAL_COUNTRY_HANDLING.get(country['ISO-2'], pullGenericDirectoryInfo)
        wksa_schools.extend(handleCountry(country['link'], country['name'], country['ISO-2']))
    separatePhoneNumbers(wksa_schools)
    handleHankuk(wksa_schools)
    exportCSV(wksa_schools)
    print('Exported %s WKSA schools' % len(wksa_schools))


if isDirectRun():
    fetchData()
