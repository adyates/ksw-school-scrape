#!/bin/bash

# Publish to hoh-gwuhn-scrape at the 1st of every month for UTC Noon
gcloud beta scheduler jobs delete monthly-scrape
gcloud beta scheduler jobs create pubsub monthly-scrape --topic="hoh-gwuhn-scrape" \
  --schedule="0 12 1 * *" --message-body="{}" \
  --description="Publish to hoh-gwuhn-scrape at the 1st of every month for UTC Noon" \
  --max-retry-attempts=5 --min-backoff="1h" --max-backoff="1d"
