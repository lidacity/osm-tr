#!.venv/bin/python

import os, sys
import glob
import json
import geojson
from datetime import datetime
from loguru import logger
import re

import Utils

Bool = ['firm:is', 'retail:is', 'trade:is', 'place:is', ]
Float = ['trade:area', 'building:area', ]
Int = ['operator:ref:BY:PAN', 'amenity:cafe:capacity', 'amenity:canteen:capacity', 'mall:capacity', 'foodcourt:capacity', 'marketplace:capacity', 'marketplace:object:capacity', 'ref:BY:trade_register', ]
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
 ListOfFiles = glob.glob(os.path.join(".data", "*.csv"))
 return max(ListOfFiles, key=os.path.getctime)



def Generate(FileName):
 Date = GetDateFromFileName(FileName)
 Utils.SetDate('Trade', Date)
 #
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
   Values = [Utils.Normalize(Item) for Item in Line[1:-2].split('";"')]
   if len(Values) < len(Fulls): # импарт з крывога csv
    OldLine = Line
    continue
#   Items = {Utils.KeyList[Key]: Value for Key, Value in zip(Keys, Values) if Value}
#   for Key, Value in Items.copy().items():
   Items = {}
   for Full, Value in zip(Fulls, Values):
    if Value:
     Key = Utils.KeyList[Full]
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
      Items[Key] = True if Value == "Да" else False if Value == "Нет" else print(f"{Key}: неизвестный bool {Value}")
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
 logger.info("write js")
 FeatureCollection = geojson.FeatureCollection(Features)
 Utils.SaveJson(os.path.join("docs", "shops.3nf.js"), "Data3NF", Base3NF)
 Utils.SaveGeoJson(os.path.join(".temp", f"shops.1.js"), "Data", FeatureCollection)



if __name__ == "__main__":
 sys.stdin.reconfigure(encoding="utf-8")
 sys.stdout.reconfigure(encoding="utf-8")
 #
 Path = os.path.dirname(os.path.abspath(__file__))
 logger.add(os.path.join(Path, ".log", "tr.log"))
 if not Utils.RunOnce():
  logger.info("Start trade register")
  FileName = GetLastFile()
  Temp = Utils.GetDate('File')
  if Temp != FileName:
   Utils.SetDate('File', FileName)
   Generate(FileName)
  else:
   logger.warning("already converted")
  logger.info("Done trade register")
