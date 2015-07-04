# Hoh Gwuhn

## Short version
Script to scrape, standardize, and export the school owner data off of the 
[KSW](www.kuksoolwon.com/site/schools) website for later mashup.

If you are an intrepid person planning on using this, re-run locally, using any noted API keys.
Reusing the CSV from this project directly is a terrible idea for data staleness reasons.

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
