#!/bin/bash

python -m pytest --cov=hohgwuhn test/ --cov-report term --cov-report html \
  --cov-report xml:test-reports/coverage.xml
