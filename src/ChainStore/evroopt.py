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


InfoName = "Евроторг"
Info = {
 'Евроопт Минимаркет': {
  'shop': "convenience",
  'name:be': "Еўраопт Мінімаркет",
  'name:ru': "Евроопт Минимаркет",
  'brand': "Евроопт Минимаркет",
  'brand:wikidata': "Q65455911",
  'operator': "ООО \"Евроторг\"",
  'operator:wikidata': "Q108565321",
  'ref:vatin': 101168731,
  'website': "https://evroopt.by/",
 },
 'Евроопт Маркет': {
  'shop': "convenience",
  'name:be': "Еўраопт Маркет",
  'name:ru': "Евроопт Маркет",
  'brand': "Евроопт Market",
  'brand:wikidata': "Q65455869",
  'operator': "ООО \"Евроторг\"",
  'operator:wikidata': "Q108565321",
  'ref:vatin': 101168731,
  'website': "https://evroopt.by/",
 },
 'Евроопт Супермаркет': {
  'shop': "supermarket",
  'name:be': "Еўраопт Супер",
  'name:ru': "Евроопт Супер",
  'brand': "Евроопт Super",
  'brand:wikidata': "Q65455960",
  'operator': "ООО \"Евроторг\"",
  'operator:wikidata': "Q108565321",
  'ref:vatin': 101168731,
  'website': "https://evroopt.by/",
 },
 'Евроопт Гипермаркет': {
  'shop': "supermarket",
  'name:be': "Еўраопт Гіпер",
  'name:ru': "Евроопт Гипер",
  'brand': "Евроопт Hyper",
  'brand:wikidata': "Q65455975",
  'operator': "ООО \"Евроторг\"",
  'operator:wikidata': "Q108565321",
  'ref:vatin': 101168731,
  'website': "https://evroopt.by/",
 },
 'Евроопт Prime': {
  'shop': "supermarket",
  'name:be': "Еўраопт Прайм",
  'name:ru': "Евроопт Прайм",
  'brand': "Евроопт Prime",
  'brand:wikidata': "Q136750549",
  'operator': "ООО \"Евроторг\"",
  'operator:wikidata': "Q108565321",
  'ref:vatin': 101168731,
  'website': "https://evroopt.by/",
 },
 'Хит!': {
  'shop': "convenience",
  'name:be': "Хіт! Экспрэс",
  'name:ru': "Хит! Экспресс",
  'brand': "Хит! Экспресс",
  'brand:wikidata': "Q126720469",
  'operator': "ООО \"Евроторг\"",
  'operator:wikidata': "Q108565321",
  'ref:vatin': 101168731,
  'website': "https://hitdiscount.by/",
 },
 'Хит! Стандарт': {
  'shop': "convenience",
  'name:be': "Хіт! Стандарт",
  'name:ru': "Хит! Стандарт",
  'brand': "Хит! Стандарт",
  'brand:wikidata': "Q136670971",
  'operator': "ООО \"Евроторг\"",
  'operator:wikidata': "Q108565321",
  'ref:vatin': 101168731,
  'website': "https://hitdiscount.by/",
 },
 'Грошык': {
  'shop': "convenience",
  'name:be': "Грошык",
  'name:ru': "Грошик",
  'brand': "Грошык",
  'brand:wikidata': "Q136670774",
  'operator': "ООО \"Евроторг\"",
  'operator:wikidata': "Q108565321",
  'ref:vatin': 101168731,
  'website': "https://groshyk.by/",
 },
 'Кафетерий': {},
}



def ConvertOpeningHours(S):
 return S


def GetRequest1(URL, Headers=None):
 MarkStart = "self.__next_f.push([1,\"2b:" #..23:.. 10 element of "self.__next_f.push"
 MarkEnd = "\\n\"])"
 Response = requests.get(URL, headers=Headers)
 if Response.status_code == 200:
  Result = Response.text
  Start = Result.find(MarkStart) + len(MarkStart)
  End = Start + Result[Start::].find(MarkEnd)
  Result = Result[Start:End]
  Result = Result.replace("\\\"", "\"").replace("\\\\", "\\")
  Result = Result.replace("\n", "\\n").replace("\r", "\\r").strip()
  Result = json.loads(Result)
  return Result[3]['children'][1][3]['children'][1][3]['Shops']
 else:
  return {}



def Generate(Json):
 logger.info("Start {name}", name=InfoName)
 RefInTR = GetItemsWithVATin(Info, Json)
 #
 logger.info("get site")
 Data = GetRequest1("https://evroopt.by/shops/", Headers=Headers)
 Data += GetRequest("https://hitdiscount.by/mvc/publications/shops/points/", Headers=Headers)['shops']
 Data += GetRequest("https://groshyk.by/mvc/publications/shops/points/", Headers=Headers)['shops']
 SaveJson(f"{TEMP}/{InfoName}.site.json", Data)
 #
 logger.info("get overpass")
 Overpass = GetOverpass("[out:json];area[name='Беларусь'];nw[shop~'^(convenience|supermarket|mall)$'][name~'(Еўраопт|Евроопт|Хіт|Хит|Грошык|Грошик)'](area);out center meta;")
 SaveJson(f"{TEMP}/{InfoName}.overpass.json", Overpass)
 Elements = Overpass['elements']
 #
 logger.info("parse")
 Features = []
 for Item in Data:
  if 'name' in Item:
   Name = Item['name']
  else:
   Name = Item['ShopFormatName']
  #
  if Name in ["Хит!", "Грошык", ]:
   Lat, Lon = Item['gps'].split(",")
   Lat, Lon = float(Lat), float(Lon)
  else:
   Coordinates = Item['Coordinates'][0]
   Lat, Lon = Coordinates['Latitude'], Coordinates['Longitude']
  Geometry = geojson.Point((Lon, Lat))
  #
  Properties = {}
  # з сеткі магазіна
  if Name in ["Хит!", "Грошык", ]:
   Shop = Info[Name]
   Ref = Item['publication_id']
   Properties |= Shop
   Properties['ref:shop'] = Ref
   Properties['addr:full'] = Item['address']
   Properties['opening_hours'] = ConvertOpeningHours(Item['description'])
  else:
   Shop = Info[Name]
   Properties |= Shop
   Ref = Item['ShopId']
   Properties['ref:shop'] = Ref
   Properties['addr:full'] = Item['ShopAddressInfo'][0]['AddressNameFull']
   Properties['opening_hours'] = ConvertOpeningHours(Item['ShopSchedule'])
   Properties['image'] = [ Item['ShopBrandIconUrl'], ]
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
  Properties['name:ru'] = "?Евроопт"
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
