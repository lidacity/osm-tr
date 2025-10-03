#!.venv/bin/python

import os
import sys
import time
from datetime import datetime

from loguru import logger
import requests

import Utils


#https://grp.nalog.gov.by/grp/rest-api
def GetMTD(PAN):
 URL = f"http://grp.nalog.gov.by/api/grp-public/data?unp={PAN}&charset=UTF-8&type=json"
 while True:
  Response = requests.get(URL)
  if Response.status_code == 200:
   Result = Response.json()
   return Result['row']
  elif Response.status_code == 400:
   return { 'ckodsost': "?", 'vkods': "Отсутствует", }
  else:
   logger.error(f"Код ошибки {Response.status_code}: УНП={PAN}")
   time.sleep(15)



def Generate():
 DateTime = datetime.now().strftime("%Y-%m-%dT%H:%M:00Z")
 Utils.SetDate('MTD', DateTime)
 #
 logger.info("read js")
 Data = Utils.LoadGeoJson(os.path.join(".temp", "shops.1.js"), "Data")
 #
 logger.info("parse nalog.gov.by")
 for Index, Feature in enumerate(Data['features']):
  Properties = Feature['properties']
  PAN = Properties['operator:ref:BY:PAN']
  MTD = GetMTD(PAN)
  if MTD['ckodsost'] != "1":
   Properties['MTD'] = f"({MTD['ckodsost']}) {MTD['vkods']}"
   Properties['status'] = "violet"
   #logger.warning(f"УНП={PAN}: {MTD['vnaimk']} - {MTD['vkods']} ({MTD['ckodsost']})")
  #
  if Index % 5 == 0: # паўза каб сайт МНС не блакаваў
   time.sleep(1)
   if Index % 10000 == 0:
    if Index > 0:
     logger.info(f"обработано {Index} записей")
 logger.info(f"обработано всего {Index+1} записей")
 #
 logger.info("write js")
 Utils.SaveGeoJson(os.path.join(".temp", "shops.2.js"), "Data", Data)
 


if __name__ == "__main__":
 sys.stdin.reconfigure(encoding="utf-8")
 sys.stdout.reconfigure(encoding="utf-8")
 #
 Path = os.path.dirname(os.path.abspath(__file__))
 logger.add(os.path.join(Path, ".log", "tr.log"))
 if not Utils.RunOnce():
  logger.info("Start MTD to violet")
  Generate()
  logger.info("Done MTD to violet")
