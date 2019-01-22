"""Wrapper file for use with Google Cloud Functions."""
from datetime import datetime

import fetch


def fetchData(data=None, context=None):
    """Wrapper around fetch.fetchData, intended to be called by scheduled cron only."""
    fetch.fetchData()
    print("Data fetch at %s" % datetime.today().strftime('%Y-%m-%d'))
