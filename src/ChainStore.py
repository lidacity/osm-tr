#!.venv/bin/python

import os
import sys
from glob import glob
from datetime import datetime
import re
from pathlib import Path

import geojson
from loguru import logger
from haversine import haversine, Unit

from Settings import LOG_CS, TEMP, DOCS
from Utils import SetDate, LoadGeoJson, SaveGeoJson

sys.path.insert(1, "ChainStore")
from Evroopt import Generate as Evroopt
from Santa import Generate as Santa
from Almi import Generate as Almi

Stores = [Evroopt, Santa, Almi]


def Split():
    logger.info("split js")
    Features = []
    PathName = Path(f"{TEMP}").resolve()
    for FileName in PathName.rglob("*.ChainStore.json"):
        logger.info("load {file}", file=FileName.name)
        Data = LoadGeoJson(FileName)
        Features += Data['features']
    #
    logger.info("save js")
    FeatureCollection = geojson.FeatureCollection(Features)
    SaveGeoJson(f"{DOCS}/ChainStore.data.js", FeatureCollection, Const="Data")
    #
    logger.info("date")
    DateTime = datetime.now().strftime("%Y-%m-%dT%H:%M:00Z")
    SetDate(f"{DOCS}/ChainStore.date.js", 'Update', DateTime)


def Process():
    logger.info("read json")
    Data = LoadGeoJson(f"{TEMP}/tr.6.json")
    for Store in Stores:
        Store(Data)


def Generate():
    Process()
    Split()


if __name__ == "__main__":
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    #
    logger.add(LOG_CS)
    logger.info("Start Chain Store")
    Generate()
    logger.info("Done Chain Store")
