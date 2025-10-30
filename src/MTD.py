#!.venv/bin/python

import os
import sys
import time
from datetime import datetime
from pathlib import Path

from loguru import logger
import requests

from Utils import SetDate, LoadGeoJson, SaveGeoJson


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


def SetMTD(Features, PAN, Text):
 for Feature in Features:
  Properties = Feature['properties']
  if Properties['operator:ref:BY:PAN'] == PAN:
   Properties['MTD'] = Text
   Properties['status'] = "gray"
   #logger.warning(f"УНП={PAN}: {Text}")



def Generate():
 DateTime = datetime.now().strftime("%Y-%m-%dT%H:%M:00Z")
 SetDate("../docs/date.js", 'MTD', DateTime)
 #
 logger.info("read js")
 Data = LoadGeoJson("../.temp/tr.1.json"))
 #
 logger.info("parse nalog.gov.by")
 for Index, Feature in enumerate(Data['features']):
  Properties = Feature['properties']
  if 'MTD' not in Properties:
   PAN = Properties['operator:ref:BY:PAN']
   MTD = GetMTD(PAN)
   if MTD['ckodsost'] != "1":
    SetMTD(Data['features'], PAN, f"({MTD['ckodsost']}) {MTD['vkods']}")
    ##Properties['MTD'] = f"({MTD['ckodsost']}) {MTD['vkods']}"
    ##Properties['status'] = "gray"
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
 SaveGeoJson("../.temp/tr.2.json", Data)
 


if __name__ == "__main__":
 sys.stdin.reconfigure(encoding="utf-8")
 sys.stdout.reconfigure(encoding="utf-8")
 #
 logger.add(Path("../.log/tr.log"))
 logger.info("Start MTD to gray")
 Generate()
 logger.info("Done MTD to gray")
