#!.venv/bin/python

import os
import sys
from datetime import datetime
from collections import Counter
from pathlib import Path

import geojson
from loguru import logger

from Utils import GetOverpass, SetDate, LoadGeoJson, SaveGeoJson, SaveJson


def GetCoord(Elements):
 Result = {}
 for Element in Elements:
  S = Element['tags']['ref:BY:trade_register']
  Ref = int(S) if S.isdigit() else S
  if Ref not in Result:
   Result[Ref] = []
  if Element['type'] == "node":
   Result[Ref].append({ 'ID': f"n{Element['id']}", 'Coordinates': [Element['lon'], Element['lat']] })
  elif Element['type'] == "way":
   Result[Ref].append({ 'ID': f"w{Element['id']}", 'Coordinates': [Element['center']['lon'], Element['center']['lat']] })
 return Result


#def GetDoubles(Elements):
# Result = Counter([ Element['tags']['ref:BY:trade_register'] for Element in Elements ])
# return [ int(Key) for Key, Value in Result.items() if Value > 1 ]



def Generate():
 DateTime = datetime.now().strftime("%Y-%m-%dT%H:%M:00Z")
 SetDate("../docs/date.js", 'Update', DateTime)
 #
 logger.info("read js")
 Data = LoadGeoJson("../.temp/tr.5.json")
 #
 logger.info("read overpass")
 Greens = GetOverpass("[out:json];area[name='Беларусь'];nw['ref:BY:trade_register'](area);out center;")
 Elements = GetCoord(Greens['elements'])
 SaveJson("../.temp/tr.6.overpass.json", Greens)
 #
 logger.info("parse green")
 for Feature in Data['features']:
  Geometry, Properties = Feature['geometry'], Feature['properties']
  Ref = Properties.get('ref:BY:trade_register', "")
  if Ref in Elements.keys():
   Value = Elements.pop(Ref)
   if len(Value) == 1:
    Item = Value[0]
    Properties['ID'] = Item['ID']
    Lon, Lat = Item['Coordinates']
    Geometry['coordinates'] = geojson.Point((Lon, Lat))
    if Properties['status'] in ["red", "orange", "blue", "violet", "green"]:
     Properties['status'] = "green"
    elif Properties['status'] in ["gray"]:
     Properties['status'] = "black"
   else:
    Elements[Ref] = Value
 # калі засталіся неапрацаваныя аб'екты, значыць іх не павінна існаваць
 for Key, Value in Elements.items():
  if len(Value) == 1:
   Item = Value[0]
   Lon, Lat = Item['Coordinates']
   Geometry = geojson.Point((Lon, Lat))
   Properties = { 'ID': Item['ID'], 'ref:BY:trade_register': Key, 'status': "black", } # "black" if isinstance(Key, int) else "gold"
   Feature = geojson.Feature(geometry=Geometry, properties=Properties)
   Data['features'].append(Feature)
  else:
   for Item in Value:
    Lon, Lat = Item['Coordinates']
    Geometry = geojson.Point((Lon, Lat))
    Properties = { 'ID': Item['ID'], 'ref:BY:trade_register': Key, 'status': "gold", }
    Feature = geojson.Feature(geometry=Geometry, properties=Properties)
    Data['features'].append(Feature)
 #
 logger.info(f"обработано всего {len(Greens['elements'])} записей")
 #
 logger.info("write js")
 SaveGeoJson("../.temp/tr.6.json", Data)
 #SaveJson("../.temp/tr.6.absent.json", Elements)
 


if __name__ == "__main__":
 sys.stdin.reconfigure(encoding="utf-8")
 sys.stdout.reconfigure(encoding="utf-8")
 #
 logger.add(Path("../.log/tr.log"))
 logger.info("Start overpass all -> green\\gold\\black")
 Generate()
 logger.info("Done overpass all -> green\\gold\\black")

