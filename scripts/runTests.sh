#!/bin/bash

python3 -m pytest --cov=hohgwuhn test/ --cov-report term --cov-report html \
  --cov-report xml:test-reports/coverage.xml
