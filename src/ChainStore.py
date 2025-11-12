#!.venv/bin/python

import os
import sys
from glob import glob
from datetime import datetime
import re
from pathlib import Path

import geojson
from loguru import logger
from haversine import haversine

from Utils import GetDate, SetDate, SaveJson, SaveGeoJson, LoadGeoJson



def GetCoord(Lat, Lon, PAN, TR):
 Length = sys.maxsize
 for Item in TR['features']:
  if Item['properties'].get('operator:ref:BY:PAN', "") == PAN:
   Lat2, Lon2 = Item['geometry']['coordinates']
   Length1 = haversine((Lat, Lon), (Lat2, Lon2))
   if Length > Length1:
    Length, Result = Length1, Item
 #
 if Length == sys.maxsize:
  return None
 else:
  return Result



def Generate():
 logger.info("get json")
 Result = LoadGeoJson("../.temp/ChainStore.json")
 Features = Result['features']
 TR = LoadGeoJson("../.temp/tr.6.json")
 #
 for Item in Features:
  Geometry, Properties = Item['geometry'], Item['properties']
  Lat, Lon = Geometry['coordinates']
  PAN = Properties.get('operator:ref:BY:PAN', "?")
  Store = GetCoord(Lat, Lon, PAN, TR)
  if Store is not None:
   Addr = Item.get('addr:full', "")
   Item |= Store
   if Addr:
    Item['addr:full'] = Addr
 #
 logger.info("write json")
 FeatureCollection = geojson.FeatureCollection(Features)
 SaveGeoJson("../.temp/ChainStore1.json", FeatureCollection)



if __name__ == "__main__":
 sys.stdin.reconfigure(encoding="utf-8")
 sys.stdout.reconfigure(encoding="utf-8")
 #
 logger.add(Path("../.log/ChainStore.log"))
 logger.info("Start Chain Store")

 Generate()

# FileName = GetLastFile()
# Temp = GetDate("../docs/ChainStore.date.js", 'File')
# if Temp != FileName:
#  Generate(FileName)
#  SetDate("../docs/ChainStore.date.js", 'File', FileName)
# else:
#  logger.warning("already converted")
 logger.info("Done Chain Store")
