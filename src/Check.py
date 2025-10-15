#!.venv/bin/python

import os
import sys
from datetime import datetime

from loguru import logger

import Utils


def Check(Geometry, Properties):
 Address = Utils.GetAddress(Properties, Full=False)
 if Geometry['coordinates'] == [0.0, 0.0]:
  return False
 elif Properties['official_name'][:30] == "Индивидуальный предприниматель" and Address == []:
  return False
 elif 'status' not in Properties:
  return False
 elif Properties['status'] not in ["black", "blue", "gold", "green", "orange", "red", ]: #"violet"
  return False
 else:
  return True



def Generate():
 logger.info("read js")
 Data = Utils.LoadGeoJson(os.path.join("..", ".temp", "shops.4.js"), "Data")
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
 Utils.SaveGeoJson(os.path.join("..", ".temp", "shops.5.js"), "Data", Data)
 Utils.SaveJson(os.path.join("..", ".temp", "shops.5.delete.js"), "Delete", Delete)
 


if __name__ == "__main__":
 sys.stdin.reconfigure(encoding="utf-8")
 sys.stdout.reconfigure(encoding="utf-8")
 #
 logger.add(os.path.join("..", ".log", "tr.log"))
 if not Utils.RunOnce():
  logger.info("Start check")
  Generate()
  logger.info("Done check")

