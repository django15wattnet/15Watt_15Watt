#!/usr/bin/env bash

# This script will create the PyPi package for 15Watt_Wsgi
# Upload it to PyPi with:
#     python3 -m twine upload --repository pypi dist/*

rm -rf pypiPackage
mkdir -p pypiPackage/src/15Watt_Wsgi
mkdir -p pypiPackage/tests

cp pyproject.toml pypiPackage/
cp README.md pypiPackage/
cp *.py pypiPackage/src/15Watt_Wsgi/

cd pypiPackage
python3 -m build

echo "Publish with: python3 -m twine upload --repository pypi dist/*"
