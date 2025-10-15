#!.venv/bin/python

import os
import sys
import geojson

from loguru import logger

import Utils as Utils


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
 Data = Utils.LoadGeoJson(os.path.join("..", ".temp", "shops.6.js"), "Data")
 #
 logger.info("convert")
 for Feature in Data['features']:
  Geometry, Properties = Feature['geometry'], Feature['properties']
  Address = Utils.GetAddress(Properties)
  if Address:
   R = Address[0][0]
   if R in Regions:
    Regions[R].append(Feature)
   else:
    Regions[''].append(Feature)
  elif Properties['status'] in ["black", ]:
   Regions[''].append(Feature)
 #
 logger.info("write js")
 for Index, Name in enumerate(Regions):
  FeatureCollection = geojson.FeatureCollection(Regions[Name])
  Utils.SaveGeoJson(os.path.join("..", "docs", f"shops.{Index + 1}.js"), f"Data{Index + 1}", FeatureCollection)



if __name__ == "__main__":
 sys.stdin.reconfigure(encoding="utf-8")
 sys.stdout.reconfigure(encoding="utf-8")
 #
 logger.add(os.path.join("..", ".log", "tr.log"))
 if not Utils.RunOnce():
  logger.info("Start final convert")
  Generate()
  logger.info("Done final convert")

