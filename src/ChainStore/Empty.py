#!.venv/bin/python

import os
import sys
from pathlib import Path

import geojson
from loguru import logger

sys.path.insert(1, "..")
from Utils import SaveGeoJson



def Generate():
 Features = []
 FeatureCollection = geojson.FeatureCollection(Features)
 SaveGeoJson("../../.temp/ChainStore.json", FeatureCollection)



if __name__ == "__main__":
 sys.stdin.reconfigure(encoding="utf-8")
 sys.stdout.reconfigure(encoding="utf-8")
 #
 logger.add(Path("../../.log/ChainStore.log"))
 logger.info("Start empty")
 Generate()
 logger.info("Done empty")
