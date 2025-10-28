#!.venv/bin/python

import os
import sys
import geojson
from pathlib import Path

from loguru import logger

from Utils import LoadGeoJson, SaveGeoJson
import UtilsTrade


Regions = {
 'Брестская': [],
 'Витебская': [],
 'Гомельская': [],
 'Гродненская': [],
 'Минская': [],
 'Могилевская': [],
 'Минск': [],
 '': [],
}



def Generate():
 logger.info("read js")
 Data = LoadGeoJson("../.temp/shops.6.json")
 #
 logger.info("convert")
 for Feature in Data['features']:
  Geometry, Properties = Feature['geometry'], Feature['properties']
  Address = UtilsTrade.GetAddress(Properties, Full=False)
  if Address:
   R = Address[0][0]
   if R in Regions:
    Regions[R].append(Feature)
   else:
    Regions[''].append(Feature)
  elif Properties['status'] in ["gold", "black", ]:
   Regions[''].append(Feature)
 #
 logger.info("write js")
 for Index, Name in enumerate(Regions):
  FeatureCollection = geojson.FeatureCollection(Regions[Name])
  SaveGeoJson(f"../docs/shops.{Index + 1}.js", FeatureCollection, Variable=f"Data{Index + 1}")



if __name__ == "__main__":
 sys.stdin.reconfigure(encoding="utf-8")
 sys.stdout.reconfigure(encoding="utf-8")
 #
 logger.add(Path("../.log/tr.log"))
 logger.info("Start final convert")
 Generate()
 logger.info("Done final convert")

