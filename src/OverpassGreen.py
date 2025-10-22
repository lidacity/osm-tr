import os
import sys
from datetime import datetime
from collections import Counter

import geojson
from loguru import logger
import requests

import Utils


URL = "https://maps.mail.ru/osm/tools/overpass/api/interpreter"


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


#https://maps.mail.ru/osm/tools/overpass/
def GetGreens():
 Overpass = f"[out:json];area[name='Беларусь'];nw['ref:BY:trade_register'](area);out center;"
 Response = requests.get(URL, params={'data': Overpass})
 if Response.status_code == 200:
  Result = Response.json()
  return Result
 else:
  return None


#def GetDoubles(Elements):
# Result = Counter([ Element['tags']['ref:BY:trade_register'] for Element in Elements ])
# return [ int(Key) for Key, Value in Result.items() if Value > 1 ]



def Generate():
 DateTime = datetime.now().strftime("%Y-%m-%dT%H:%M:00Z")
 Utils.SetDate('Update', DateTime)
 #
 logger.info("read js")
 Data = Utils.LoadGeoJson(os.path.join("..", ".temp", "shops.5.js"), "Data")
 #
 logger.info("read overpass")
 Greens = GetGreens()
 Elements = GetCoord(Greens['elements'])
 Utils.SaveJson(os.path.join("..", ".temp", "shops.6.overpass.js"), "Data", Greens)
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
 Utils.SaveGeoJson(os.path.join("..", ".temp", "shops.6.js"), "Data", Data)
 #Utils.SaveJson(os.path.join("..", ".temp", "shops.6.absent.js"), "Data", Elements)
 


if __name__ == "__main__":
 sys.stdin.reconfigure(encoding="utf-8")
 sys.stdout.reconfigure(encoding="utf-8")
 #
 logger.add(os.path.join("..", ".log", "tr.log"))
 if not Utils.RunOnce():
  logger.info("Start overpass all -> green\\gold\\black")
  Generate()
  logger.info("Done overpass all -> green\\gold\\black")

