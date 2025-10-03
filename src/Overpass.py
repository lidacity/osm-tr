import os
import sys
import geojson
import html
from datetime import datetime

from loguru import logger
import requests

import Utils

Overpass = "https://maps.mail.ru/osm/tools/overpass/api/interpreter"



#https://maps.mail.ru/osm/tools/overpass/
def GetTR():
 URL = f"{Overpass}?data=[out:json];area[name='Беларусь'];nw['ref:BY:trade_register'](area);out center;"
 Response = requests.get(URL)
 if Response.status_code == 200:
  Result = Response.json()
  return Result
 else:
  return None




sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")

Path = os.path.dirname(os.path.abspath(__file__))
logger.add(os.path.join(Path, ".log", "tr.log"))
logger.info("Start Overpass")

Data = Utils.LoadGeoJson(os.path.join("docs", "shops.0.js"), "Data")

TR = GetTR()
Result = {}
for Item in TR['elements']:
 PAN = int(Item['tags']['ref:BY:trade_register'])
 if Item['type'] == "node":
  Result[PAN] = { 'ID': f"n{Item['id']}", 'lat': Item['lat'], 'lon': Item['lon'], }
 elif Item['type'] == "way":
  Result[PAN] = { 'ID': f"w{Item['id']}", 'lat': Item['center']['lat'], 'lon': Item['center']['lon'], }
print(Result)
sys.exit()


for Feature in Data['features']:
 PAN = Feature['properties']['operator:ref:BY:PAN']
 MNS = GetMNS(PAN)
 if MNS is None:
  Feature['properties']['status'] = "violet"
  logger.Error(f"УНП={PAN}: неизвестно")
 if MNS['ckodsost'] != "1":
  Feature['properties']['status'] = "green"
  logger.warning(f"УНП={PAN}: {MNS['vnaimk']} - {MNS['vkods']} ({MNS['ckodsost']})")

logger.info("write")
Utils.SaveGeoJson(os.path.join("docs", "shops2.js"), "Data", Data)
 
logger.info("Done Overpass")
