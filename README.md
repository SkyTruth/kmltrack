# kmltrack

[![Build Status](https://travis-ci.org/SkyTruth/kmltrack.svg?branch=master)](https://travis-ci.org/SkyTruth/kmltrack)

kmltrack converts a track (a series of lat/lon/timestamp and optional measurement values) into a kml file.

Source data can be in one of three formats: msgpack, json, csv

Licensed under GPL 3.0

# Installation

    pip install kmltrack
    
or

    git clone https://github.com/SkyTruth/kmltrack.git
    cd kmltrack
    python setup.py install

# Usage example
The following example converts speed values in the input (in knots for example) into color values. Color values are in the range [0.0, 1.0] for a color gradient from black to white over red and yellow (you can alternatively specify red, green and blue separately).

    kmltrack --map-color='float(speed) / 17.0' --map-course=cog input.json output.kml

Example input.json

    {'lat': 0.0, 'lon': 0.3, 'timestamp': '1970-01-01T00:00:00.000Z', 'course': 180.0, 'speed': 10.0}
    {'lat': 0.1, 'lon': 0.2, 'timestamp': '1970-01-01T12:00:00.000Z', 'course': 180.0, 'speed': 11.0}
    {'lat': 0.2, 'lon': 0.1, 'timestamp': '1970-01-02T00:00:00.000Z', 'course': 180.0, 'speed': 7.0}
    {'lat': 0.3, 'lon': 0.0, 'timestamp': '1970-01-02T12:00:00.000Z', 'course': 180.0, 'speed': 2.0}

# Developing

    git clone https://github.com/SkyTruth/kmltrack.git
    cd kmltrack
    virtualenv venv
    python setup.py develop easy_install kmltrack[cli,msgpack,test]
    pip install -r requirements-dev.txt
    nosetests --with-coverage
    

