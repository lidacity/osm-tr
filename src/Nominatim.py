#!.venv/bin/python

import os
import sys

from loguru import logger
import asyncio
import nominatim_api as napi
import geojson

import Utils
import Download


async def Search(Query):
 async with napi.NominatimAPIAsync() as Api:
  return await Api.search(Query)


def GetDateFromFileName(FileName):
 Pattern = re.compile(r'\d\d.\d\d.\d\d\d\d')
 Matches = Pattern.findall(FileName)
 return ConvertDate(Matches[0]) if Matches else None



def Generate():
 OSM = Download.PBF(Download=False)
 #!!
 Date = OSM.ReadState()
 Utils.SetDate('Nominatim', Date)
 #
 logger.info("read js")
 Data = Utils.LoadGeoJson(os.path.join("..", ".temp", "shops.2.js"), "Data")
 #Delete = []
 #
 logger.info("parse nominatim")
 for Index, Feature in enumerate(Data['features']):
  Geometry, Properties = Feature['geometry'], Feature['properties']
  Status = Properties.get('status', "")
  #
  Addresses = Utils.GetAddress(Properties)
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
      logger.warning(f"адрес для {Properties.get('ref:BY:trade_register', "?")} ({Address[:-Count]} => '{Addr}') не найден")
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
      #logger.info(f"{Addr} = {Lon}, {Lat}")
      break
     else: # дадзены адрас не знойдзены, перайсці да наступнага кроку, паменшыць дакладнасць
      logger.warning(f"адрес для {Properties.get('ref:BY:trade_register', "?")} ({Address[:-Count]} => '{Addr}') не найден")
    else:
     continue
    break
   #else: # калі аніякага адраса не знайшлі
   # Delete.append(Feature)
   # Data['features'].remove(Feature)
   # logger.error(f"для {Properties.get('ref:BY:trade_register', "?")} с адресом ({Address[:-1]}) координаты не найдены")
  #
  if Index % 10000 == 0:
   if Index > 0:
    logger.info(f"обработано {Index} записей")
 logger.info(f"обработано всего {Index+1} записей")
 #
 logger.info("write js")
 Utils.SaveGeoJson(os.path.join("..", ".temp", "shops.3.js"), "Data", Data)
 #Utils.SaveJson(os.path.join("..", ".temp", "shops.3delete.js"), "Delete", Delete)



if __name__ == "__main__":
 sys.stdin.reconfigure(encoding="utf-8")
 sys.stdout.reconfigure(encoding="utf-8")
 #
 logger.add(os.path.join("..", ".log", "tr.log"))
 if not Utils.RunOnce():
  logger.info("Start nominatim to red\\orange")
  Generate()
  logger.info("Done nominatim to red\\orange")
