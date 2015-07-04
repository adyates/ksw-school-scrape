import csv
import re

from bs4 import BeautifulSoup 
import phonenumbers as libphone
import requests


def pullUsaDirectoryInfo():
    KSW_DIRECTORY_PAGE = 'http://www.kuksoolwon.com/site/schools/u.s.a.'
    KSW_REGIONS = 4
    
    school_list = []
    for geo_id in xrange(1, KSW_REGIONS + 1):
        r = requests.post(KSW_DIRECTORY_PAGE, data={'geo_id': geo_id})
        usa_page = BeautifulSoup(r.text, 'lxml')
        subpage = usa_page.select('div.schools_content > div')
        
        ksw_region = '' # For the US, this is the state as displayed on the leftmost column
        print 'Found %s schools' % len(subpage)
        for section in subpage:
            # Determine if this is a region header or a school
            if 'region_name' in section['class']:
                ksw_region = section.get_text().capitalize()
            else:
                school_list.append({
                    'region': ksw_region.strip(),
                    'city': section.select_one('div.city').get_text().strip(),
                    # Instructors seem to be able to hand-edit this section
                    'address': re.sub(r'\r?\n', ' ', section.select_one('div.contact').get_text()
                        ).encode('ascii', 'ignore').strip(),
                    'phone_numbers': [],
                    'instructor': section.select_one('div.instructor').get_text().strip()
                })
    return school_list


def separatePhoneNumbers(school_list):
    for school in school_list:
        phone_index_min = len(school['address'])
        for match in libphone.PhoneNumberMatcher(school['address'], 'US'):
            school['phone_numbers'].append(
                str(libphone.format_number(match.number, libphone.PhoneNumberFormat.NATIONAL)))
            phone_index_min = min(phone_index_min, match.start)
            
        # Reformat the phone numbers to be semi-colon delimited, if present
        school['phone_numbers'] = ';'.join(school['phone_numbers'])
        
        # Remove the phone numbers from the address.  Go by section because multiple numbers get
        # are not represented uniformly (e.g. Palmdale, CA)
        school['address'] = school['address'][:phone_index_min].strip()


def exportCSV(school_list):
    with open('school_data.csv', 'wb') as csvout:
        writer = csv.DictWriter(csvout, [
                'city', 'region', 'address', 'phone_numbers', 'instructor'
            ], lineterminator='\n')
        
        header = {
            'region': 'Region',
            'city': 'City', 
            'address': 'Address',
            'phone_numbers':'Phone #s', 
            'instructor': 'Instructor'
        }
        
        writer.writerow(header)
        for school in school_list:
            writer.writerow(school)


if __name__ == '__main__':
    school_list = pullUsaDirectoryInfo()
    separatePhoneNumbers(school_list)
    exportCSV(school_list)
