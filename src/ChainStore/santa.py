#!.venv/bin/python

import os
import sys
from pathlib import Path
import json

from loguru import logger
import geojson
import requests

#sys.path.insert(1, "..")
from Settings import LOG_CS, TEMP
from Utils import GetRequest, GetOverpass, SaveJson, SaveGeoJson, LoadGeoJson, GetID
from UtilsChainStore import Headers, GetCoord, Check, GetItemsWithVATin


InfoName = "Санта Ритейл"
Info = {
 'Продукты': {
  'shop': "convenience",
  'name:be': "Санта",
  'name:ru': "Санта",
  'brand': "Санта",
  'brand:wikidata': "Q136678275",
  'operator': "ООО \"Санта Ритейл\"",
  'operator:wikidata': "Q128604965",
  'ref:vatin': 291313486,
  'website': "https://santaretail.by/",
 },
 'Санта': {
  'shop': "convenience",
  'name:be': "Санта",
  'name:ru': "Санта",
  'brand': "Санта",
  'brand:wikidata': "Q136678275",
  'operator': "ООО \"Санта Ритейл\"",
  'operator:wikidata': "Q128604965",
  'ref:vatin': 291313486,
  'website': "https://santaretail.by/",
 },
 'Санта Супер': {
  'shop': "supermarket",
  'name:be': "Санта Супер",
  'name:ru': "Санта Супер",
  'brand': "Санта Супер",
  'brand:wikidata': "Q136697457",
  'operator': "ООО \"Санта Ритейл\"",
  'operator:wikidata': "Q128604965",
  'ref:vatin': 291313486,
  'website': "https://santaretail.by/",
 },
 'Санта & Кэш': {
  'shop': "wholesale",
  'name:be': "Санта & Кэш",
  'name:ru': "Санта & Кэш",
  'brand': "Санта & Кэш",
  'brand:wikidata': "Q136697503",
  'operator': "ООО \"Санта Ритейл\"",
  'operator:wikidata': "Q128604965",
  'ref:vatin': 291313486,
  'website': "https://santaretail.by/",
 },
 'Санта & Фиш': {
  'shop': "convenience",
  'name:be': "Санта & Фіш",
  'name:ru': "Санта & Фиш",
  'brand': "Санта & Фиш",
  'brand:wikidata': "Q136697545",
  'operator': "ООО \"Санта Ритейл\"",
  'operator:wikidata': "Q128604965",
  'ref:vatin': 291313486,
  'website': "https://santaretail.by/",
 },
}



def ConvertOpeningHours(S):
 return S



def GetRequest1(URL, Headers=None):
 MarkStart = "<div id=\"map\" class=\"maps\" data-config='"
 MarkEnd = "'></div>\n"
 Response = requests.get(URL, headers=Headers)
 if Response.status_code == 200:
  Result = Response.text
  Start = Result.find(MarkStart) + len(MarkStart)
  End = Start + Result[Start::].find(MarkEnd)
  Result = Result[Start:End]
  Result = Result.replace("\\\"", "\"").replace("\\\\", "\\")
  Result = Result.replace("\n", "\\n").replace("\r", "\\r").strip()
  Result = json.loads(Result)
  return Result
 else:
  return {}



def Generate(Json):
 logger.info("Start {name}", name=InfoName)
 RefInTR = GetItemsWithVATin(Info, Json)
 #
 logger.info("get site")
 Data = GetRequest1("https://santaretail.by/adresa-magazinov/", Headers=Headers)
 SaveJson(f"{TEMP}/{InfoName}.site.json", Data)
 #
 logger.info("get overpass")
 Overpass = GetOverpass("[out:json];area[name='Беларусь'];nw[shop~'^(convenience|supermarket|wholesale)$'][name~'(Санта)'](area);out center meta;")
 SaveJson(f"{TEMP}/{InfoName}.overpass.json", Overpass)
 Elements = Overpass['elements']
 #
 logger.info("parse")
 Features = []
 for Item in Data:
  Name = Item['name'].split(" (")[0]
  Name = Name.replace("&", " & ").replace("  ", " ").replace("Санта Кэш", "Санта & Кэш")
  #
  Lat, Lon = Item['position'].split(",")
  Lat, Lon = float(Lat), float(Lon)
  Geometry = geojson.Point((Lon, Lat))
  #
  Properties = {}
  # з сеткі магазіна
  Shop = Info[Name]
  Properties |= Shop
  Ref = Item['id']
  Properties['ref:shop'] = Ref
  Properties['addr:full'] = Item['address']
  Properties['opening_hours'] = ConvertOpeningHours(f"{Item['timestart']}-{Item['timeend']}")
  Properties['website'] = f"https://santaretail.by/{Item['link']}"
  # шукаць у overpass і ў тарговым рэестры
  ID = None
  Properties['status'] = "red"
  Store = GetCoord(Lat, Lon, Ref, Elements)
  if Store is not None:
   Tags = Store['tags']
   if Check(Store, Shop):
    Properties['status'] = "green"
   elif 'ref:BY:trade_register' in Tags:
    Properties['status'] = "violet"
   else:
    Properties['status'] = "blue"
   ID = GetID(Store)
   if 'ref:BY:trade_register' in Tags:
    Properties['ref:BY:trade_register'] = Tags['ref:BY:trade_register']
   else:
    if ID in RefInTR:
     Tags['ref:BY:trade_register'] = RefInTR[ID]
   Geometry = geojson.Point((Store['lon'], Store['lat']))
  #
  Feature = geojson.Feature(id=ID, geometry=Geometry, properties=Properties)
  Features.append(Feature)
 # ёсць на карце, але адсутнічаюць у сетцы магазіна
 for Item in Elements:
  Lat, Lon = Item['lat'], Item['lon']
  Geometry = geojson.Point((Lon, Lat))
  Properties = {}
  ID = GetID(Item)
  Properties['name:ru'] = "?Санта"
  Properties['status'] = "black"
  #
  Feature = geojson.Feature(id=ID, geometry=Geometry, properties=Properties)
  Features.append(Feature)
 #
 logger.info("save js")
 FeatureCollection = geojson.FeatureCollection(Features)
 SaveGeoJson(f"{TEMP}/{InfoName}.ChainStore.json", FeatureCollection)
 logger.info("count {count}", count=len(Data))
 logger.info("Done {name}", name=InfoName)
