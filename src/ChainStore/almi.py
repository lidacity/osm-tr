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


InfoName = "Юнифуд"
Info = {
 'Алми Супермаркет': {
  'shop': "supermarket",
  'name:be': "Алмі Супермаркет",
  'name:ru': "Алми Супермаркет",
  'brand': "Алми Супермаркет",
  'brand:wikidata': "Q136695896",
  'operator': "ЗАО \"Юнифуд\"",
  'operator:wikidata': "Q136823700",
  'ref:vatin': 800016624,
  'website': "https://almi.by/",
 },
 'Алми Универсам': {
  'shop': "convenience",
  'name:be': "Алмі Універсам",
  'name:ru': "Алми Универсам",
  'brand': "Алми Универсам",
  'brand:wikidata': "Q136824041",
  'operator': "ЗАО \"Юнифуд\"",
  'operator:wikidata': "Q136823700",
  'ref:vatin': 800016624,
  'website': "https://almi.by/",
 },
 'Алми Гастроном': {
  'shop': "convenience",
  'name:be': "Алмі Гастроном",
  'name:ru': "Алми Гастроном",
  'brand': "Алми Гастроном",
  'brand:wikidata': "Q136824042",
  'operator': "ЗАО \"Юнифуд\"",
  'operator:wikidata': "Q136823700",
  'ref:vatin': 800016624,
  'website': "https://almi.by/",
 },
}



def ConvertOpeningHours(S):
 return S


#var points = {};
#if (lat_c && lon_c)
def GetRequest1(URL, Headers=None):
 MarkStart = "var points = {};"
 MarkEnd = "if (lat_c && lon_c)"
 Response = requests.get(URL, headers=Headers)
 if Response.status_code == 200:
  Result = Response.text
  Start = Result.find(MarkStart) + len(MarkStart)
  End = Start + Result[Start::].find(MarkEnd)
  Result = Result[Start:End]
  while "  " in Result:
   Result = Result.replace("  ", " ")
#  Result = Result.replace("\n ", "\n")
  Result = Result.replace("var lat_c, lon_c;", "")
  Result = Result.replace("points['point_' + c] = new Array();", "")
  Result = Result.replace(" ;", "")
  Result = Result.replace("\n var c = 0;", "[\n  {")
  Result = Result.replace("\n c = c + 1;", " },\n  {")
  Result = Result.replace("\n var lat = ", "   'lat': ")
  Result = Result.replace(" var lon = ", "    'lon': ")
  Result = Result.replace("\n points['point_' + c]['free'] = ", "   'free': ")
  Result = Result.replace(" points['point_' + c]['lat'] = lat;", "")
  Result = Result.replace(" points['point_' + c]['lon'] = lon;", "")
  Result = Result.replace(" points['point_' + c]['name'] = ", "    'name': ")
  Result = Result.replace(" points['point_' + c]['address'] = ", "    'address': ")
  Result = Result.replace(" points['point_' + c]['placemark'] = null;", "")
  Result = Result.replace("'", "\"")
  Result = Result.replace(";", ",")
  while "\n\n" in Result:
   Result = Result.replace("\n\n", "\n")
  Result = Result.replace("\",\n  },", "\"\n  },")
  Result += " }\n]"
  Result = json.loads(Result)
  return Result
 else:
  return {}



def Generate(Json):
 logger.info("Start {name}", name=InfoName)
 RefInTR = GetItemsWithVATin(Info, Json)
 #
 logger.info("get site")
 Data = GetRequest1("https://almi.by/shops/", Headers=Headers)
 SaveJson(f"{TEMP}/{InfoName}.site.json", Data)
 #
 logger.info("get overpass")
 Overpass = GetOverpass("[out:json];area[name='Беларусь'];nw[shop~'^(convenience|supermarket)$'][name~'(Алми|Алмі|Almi)'](area);out center meta;")
 SaveJson(f"{TEMP}/{InfoName}.overpass.json", Overpass)
 Elements = Overpass['elements']
 #
 logger.info("parse")
 Features = []
 for Item in Data:
  if 'name' not in Item:
   continue
  Name = "Алми " + Item['name'].replace("«АЛМИ»", "").replace(" ", "")
  #
  Lat, Lon = Item['lat'], Item['lon']
  Geometry = geojson.Point((Lon, Lat))
  #
  Properties = {}
  # з сеткі магазіна
  Shop = Info[Name]
  Properties |= Shop
  Properties['addr:full'] = Item['address']
  # шукаць у overpass і ў тарговым рэестры
  ID = None
  Properties['status'] = "red"
  Store = GetCoord(Lat, Lon, None, Elements)
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
  Properties['name:ru'] = "?Алми"
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
