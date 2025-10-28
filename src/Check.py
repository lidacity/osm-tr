#!.venv/bin/python

import os
import sys
from datetime import datetime
from pathlib import Path

from loguru import logger

from Utils import LoadGeoJson, SaveGeoJson, SaveJson
import UtilsTrade


def Check(Geometry, Properties):
 Address = UtilsTrade.GetAddress(Properties, Full=False)
 if Geometry['coordinates'] == [0.0, 0.0]:
  return False
 elif Properties['official_name'][:30] == "Индивидуальный предприниматель" and Address == []:
  return False
 elif 'status' not in Properties:
  return False
 elif Properties['status'] not in ["violet", "blue", "orange", "red", ]:
  return False
 else:
  return True



def Generate():
 logger.info("read js")
 Data = LoadGeoJson("../.temp/shops.4.json")
 Delete = []
 #
 logger.info("check")
 for Feature in Data['features']:
  Geometry, Properties = Feature['geometry'], Feature['properties']
  if not Check(Geometry, Properties):
   Delete.append(Feature)
 #
 logger.info(f"{len(Delete)} записей для удаления")
 #
 for Index, Feature in enumerate(Delete):
  Data['features'].remove(Feature)
  #
  if Index % 10000 == 0:
   if Index > 0:
    logger.info(f"обработано {Index} записей")
 #
 logger.info(f"{len(Data['features'])} записей для сохранения")

 logger.info("write js")
 SaveGeoJson("../.temp/shops.5.json", Data)
 SaveJson("../.temp/shops.5.delete.json", Delete)
 


if __name__ == "__main__":
 sys.stdin.reconfigure(encoding="utf-8")
 sys.stdout.reconfigure(encoding="utf-8")
 #
 logger.add(Path("../.log/tr.log"))
 logger.info("Start check")
 Generate()
 logger.info("Done check")

