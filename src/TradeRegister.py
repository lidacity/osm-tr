#!.venv/bin/python

import os
import sys
from glob import glob
from datetime import datetime
import re
from pathlib import Path

import geojson
from loguru import logger

from Settings import LOG, DOCS, DATA, TEMP
from Utils import GetDate, SetDate, SaveJson, SaveGeoJson, Normalize
import UtilsTrade


Bool = ['firm:is', 'retail:is', 'trade:is', 'place:is', ]
Float = ['trade:area', 'building:area', ]
Int = ['ref:vatin', 'amenity:cafe:capacity', 'amenity:canteen:capacity', 'mall:capacity', 'foodcourt:capacity', 'marketplace:capacity', 'marketplace:object:capacity', 'ref:BY:trade_register', ]
Date = ['start_date', ]
NF3 = { 'type', 'format:view', 'place:view', 'assortment:view', 'amenity:type', 'retail:place', 'cafe:type', 'mall:specialization', 'marketplace:type', 'marketplace:specialization', }
NF3sub = { 'category:class', 'category:group', 'category:subgroup', }


def ConvertDate(Text):
 Date = datetime.strptime(Text, "%d.%m.%Y").date()
 return Date.strftime("%Y-%m-%d") #%Y-%m-%dT%H:%M:%SZ


def GetDateFromFileName(FileName):
 Pattern = re.compile(r'\d\d.\d\d.\d\d\d\d')
 Matches = Pattern.findall(FileName)
 return ConvertDate(Matches[0]) if Matches else None


def GetLastFile():
 PathName = Path(f"{DATA}/*.csv").as_posix()
 ListOfFiles = glob(PathName)
 return max(ListOfFiles, key=os.path.getctime)



def Generate(FileName):
 logger.info("parse csv")
 Features = []
 Base3NF = {}
 with open(FileName, "r", encoding='cp1251') as File:
  Line = File.readline()
  Fulls = [Item.replace('""', '"') for Item in Line[1:-2].split('";"')]
  OldLine = ""
  #print(Keys)
  iii = 0
  for Line in File:
   Line = OldLine + Line
   OldLine = ""
   Values = [Normalize(Item) for Item in Line[1:-2].split('";"')]
   if len(Values) < len(Fulls): # импарт з крывога csv
    OldLine = Line
    continue
#   Items = {UtilsTrade.KeyList[Key]: Value for Key, Value in zip(Keys, Values) if Value}
#   for Key, Value in Items.copy().items():
   Items = {}
   for Full, Value in zip(Fulls, Values):
    if Value:
     Key = UtilsTrade.KeyList[Full]
     # ідэнтыфікатары
     if Key in NF3:
      if Key not in Base3NF:
       Base3NF[Key] = [f"{Key}.id"]
      if Value not in Base3NF[Key]:
       Base3NF[Key].append(Value)
      Items[f'{Key}.id'] = Base3NF[Key].index(Value)
     # пералік суполкі тавараў
     elif Key in NF3sub:
      if Key not in Base3NF:
       Base3NF[Key] = [f"{Key}.ids"]
      for SubItem in Value.split(";"):
       SubItem = SubItem.strip()
       if SubItem not in Base3NF[Key]:
        Base3NF[Key].append(SubItem)
       Index = Base3NF[Key].index(SubItem)
       if f'{Key}.ids' in Items:
        Items[f'{Key}.ids'].append(Index)
       else:
        Items[f'{Key}.ids'] = [Index]
     # пераўтварэнне тыпаў
     elif Key in Int:
      Items[Key] = int(Value)
     elif Key in Float:
      Items[Key] = float(Value)
     elif Key in Bool:
      Items[Key] = True if Value == "Да" else False if Value == "Нет" else logger.error("{Key}: неизвестный bool {Value}", Key=Key, Value=Value)
     elif Key in Date:
      Items[Key] = ConvertDate(Value)
     else:
      Items[Key] = Value
   #Items['status'] = "red"
   Geometry = geojson.Point((0, 0))
   Properties = Items
   Feature = geojson.Feature(geometry=Geometry, properties=Properties)
   Features.append(Feature)
   IsLine = True
 #
 logger.info("write json")
 FeatureCollection = geojson.FeatureCollection(Features)
 SaveJson(f"{DOCS}/tr.nf3.js", Base3NF, Const="Data3NF")
 SaveGeoJson(f"{TEMP}/tr.1.json", FeatureCollection)



if __name__ == "__main__":
 sys.stdin.reconfigure(encoding="utf-8")
 sys.stdout.reconfigure(encoding="utf-8")
 #
 logger.add(LOG)
 logger.info("Start trade register")
 FileName = GetLastFile()
 Temp = GetDate(f"{DOCS}/date.js", 'File')
 if Temp != FileName:
  Generate(FileName)
  SetDate(f"{DOCS}/date.js", 'File', FileName)
  Date = GetDateFromFileName(FileName.name)
  SetDate(f"{DOCS}/tr.date.js", 'Trade', Date)
 else:
  logger.warning("already converted")
 logger.info("Done trade register")
