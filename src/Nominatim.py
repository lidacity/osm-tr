#!.venv/bin/python

import os
import sys
import asyncio

from loguru import logger
import nominatim_api as napi
import geojson
from pathlib import Path

from Settings import LOG, TEMP
from Utils import SetDate, LoadGeoJson, SaveGeoJson
import UtilsTrade


async def Search(Query):
 async with napi.NominatimAPIAsync() as Api:
  return await Api.search(Query)


def GetDateFromFileName(FileName):
 Pattern = re.compile(r'\d\d.\d\d.\d\d\d\d')
 Matches = Pattern.findall(FileName)
 return ConvertDate(Matches[0]) if Matches else None



def Generate():
 logger.info("read json")
 Data = LoadGeoJson(f"{TEMP}/tr.2.json")
 #
 logger.info("parse nominatim")
 for Index, Feature in enumerate(Data['features']):
  Geometry, Properties = Feature['geometry'], Feature['properties']
  Status = Properties.get('status', "")
  #
  Addresses = UtilsTrade.GetAddress(Properties, Full=False)
  if Status in ["gray"]:
   for Address in Addresses:
    for Count in range(1, len(Address)):
     Addr = ", ".join(Address[:-Count])
     Results = asyncio.run(Search(Addr))
     if Results:
      Lon, Lat = Results[0].centroid.x, Results[0].centroid.y
      Geometry['coordinates'] = geojson.Point((Lon, Lat))
      break
     else:
      logger.warning("адрес для {ref} ({address} => '{Addr}') не найден", ref=Properties.get('ref:BY:trade_register', "?"), address=Address[:-Count], Addr=Addr)
    else:
     continue
    break
  #
  elif Status in ["", "red", "orange"]:
   # сфармаваць спіс з адрасам
   for Address in Addresses:
    Properties['status'] = "red"
    # абыход па спісу адрасоў ад самага дакладнага да вельмі прыблізнага
    for Count in range(1, len(Address)):
     Addr = ", ".join(Address[:-Count])
     Results = asyncio.run(Search(Addr))
     if Results: # знайшлі
      Lon, Lat = Results[0].centroid.x, Results[0].centroid.y
      Geometry['coordinates'] = geojson.Point((Lon, Lat))
      if Count == 1:
       Properties['status'] = "orange"
      #logger.info("{Addr} = {Lon}, {Lat}", Addr=Addr, Lon=Lon, Lat=Lat)
      break
     else: # дадзены адрас не знойдзены, перайсці да наступнага кроку, паменшыць дакладнасць
      logger.warning("адрес для {ref} ({address} => '{Addr}') не найден", ref=Properties.get('ref:BY:trade_register', "?"), address=Address[:-Count], Addr=Addr)
    else:
     continue
    break
  #
  if Index % 10000 == 0:
   if Index > 0:
    logger.info("обработано {count} записей", count=Index)
 logger.info("обработано всего {count} записей", count=Index+1)
 #
 logger.info("write json")
 SaveGeoJson(f"{TEMP}/tr.3.json", Data)



if __name__ == "__main__":
 sys.stdin.reconfigure(encoding="utf-8")
 sys.stdout.reconfigure(encoding="utf-8")
 #
 logger.add(LOG)
 logger.info("Start nominatim to red\\orange")
 Generate()
 logger.info("Done nominatim to red\\orange")
