#!.venv/bin/python

import os
import sys
from pathlib import Path
import json

from loguru import logger
import geojson
import requests
from fake_useragent import UserAgent

sys.path.insert(1, "..")
from Utils import GetRequest, LoadGeoJson, SaveJson, SaveGeoJson


Info = {
 'name': "Евроторг",
 'operator': "ООО \"Евроторг\"",
 'shops': {
   'Евроопт Минимаркет': { 'operator:ref:BY:PAN': 101168731, 'shop': "convenience", 'operator:wikidata': "Q65455911", 'name:ru': "Евроопт Минимаркет", 'name:be': "Еўраопт Мінімаркет", 'brand': "Евроопт Минимаркет", 'website': "https://evroopt.by", },
   'Евроопт Маркет': { 'operator:ref:BY:PAN': 101168732, 'shop': "convenience", 'operator:wikidata': "Q65455869", 'name:ru': "Евроопт Маркет", 'name:be': "Еўраопт Маркет", 'brand': "Евроопт Market", 'website': "https://evroopt.by", },
   'Евроопт Супермаркет': { 'operator:ref:BY:PAN': 101168733, 'shop': "supermarket", 'operator:wikidata': "Q65455960", 'name:ru': "Евроопт Супер", 'name:be': "Еўраопт Супер", 'brand': "Евроопт Super", 'website': "https://evroopt.by", },
   'Евроопт Гипермаркет': { 'operator:ref:BY:PAN': 101168734, 'shop': "supermarket", 'operator:wikidata': "Q65455975", 'name:ru': "Евроопт Гипер", 'name:be': "Еўраопт Гіпер", 'brand': "Евроопт Hyper", 'website': "https://evroopt.by", },
   'Евроопт Prime': { 'operator:ref:BY:PAN': 101168735, 'shop': "supermarket", 'operator:wikidata': "Q136750549", 'name:ru': "Евроопт Прайм", 'name:be': "Еўраопт Прайм", 'brand': "Евроопт Prime", 'website': "https://evroopt.by", },
   'Хит!': { 'operator:ref:BY:PAN': 101168736, 'shop': "convenience", 'operator:wikidata': "Q126720469", 'name:ru': "Хит! Экспресс", 'name:be': "Хіт! Экспрэс", 'brand': "Хит! Экспресс", 'website': "https://hitdiscount.by/", },
   'Хит! Стандарт': { 'operator:ref:BY:PAN': 101168737, 'shop': "convenience", 'operator:wikidata': "Q136670971", 'name:ru': "Хит! Стандарт", 'name:be': "Хіт! Стандарт", 'brand': "Хит! Стандарт", 'website': "https://hitdiscount.by/", },
   'Грошык': { 'operator:ref:BY:PAN': 101168738, 'shop': "convenience", 'operator:wikidata': "Q136670774", 'name:ru': "Грошик", 'name:be': "Грошык",  'brand': "Грошык", 'website': "https://groshyk.by/", },
   'Кафетерий': {},
 },
}


def ConvertOpeningHours(S):
 return S


Browser = UserAgent()
Headers = {
 'user-agent': Browser.random,
}


def GetRequestEvroopt(URL, Headers=None):
 Response = requests.get(URL, headers=Headers)
 if Response.status_code == 200:
  Result = Response.text
  Start = Result.find(f"self.__next_f.push([1,\"23:") + len(f"self.__next_f.push([1,\"23:")
  End = Start + Result[Start::].find(f"\\n\"])")
  Result = Result[Start:End]
  Result = Result.replace("\\\"", "\"").replace("\\\\", "\\")
  Result = Result.replace("\n", "\\n").replace("\r", "\\r").strip()
  Result = json.loads(Result)
  return Result[3]['children'][1][3]['children'][1][3]['Shops']
 else:
  return {}


def GetRequest2(URL, Headers=None):
 Result = GetRequest(URL, Headers=Headers)
 return Result['shops']



def Generate(): 
 logger.info("get json")
 Result = LoadGeoJson("../../.temp/ChainStore.json")
 Features = Result['features']
 #
 logger.info("get ChainStore")
 Data = GetRequestEvroopt("https://evroopt.by/shops/", Headers=Headers)
 Data += GetRequest2("https://hitdiscount.by/mvc/publications/shops/points/", Headers=Headers)
 Data += GetRequest2("https://groshyk.by/mvc/publications/shops/points/", Headers=Headers)
 #
 logger.info("parse")
 for Item in Data:
  if 'name' in Item:
   Name = Item['name']
  else:
   Name = Item['ShopFormatName']
  #
  if Name in ["Хит!", "Грошык", ]:
   Lat, Lon = Item['gps'].split(",")
   Geometry = geojson.Point((float(Lon), float(Lat)))
  else:
   Coordinates = Item['Coordinates'][0]
   Lat, Lon = Coordinates['Latitude'], Coordinates['Longitude']
   Geometry = geojson.Point((Lon, Lat))
  #
  Properties = {}
  if Name in ["Хит!", "Грошык", ]:
   Shop = Info['shops'][Name]
   Properties |= Shop
   Properties['addr:full'] = Item['address']
   Properties['opening_hours'] = ConvertOpeningHours(Item['description'])
  else:
   Shop = Info['shops'][Name]
   Properties |= Shop
   Properties['ref'] = Item['ShopId']
   Properties['addr:full'] = Item['ShopAddressInfo'][0]['AddressNameFull']
   Properties['opening_hours'] = ConvertOpeningHours(Item['ShopSchedule'])
   Properties['image'] = [ Item['ShopBrandIconUrl'], ]
  Feature = geojson.Feature(geometry=Geometry, properties=Properties)
  Features.append(Feature)
 #
 logger.info("save js")
 SaveJson(f"../../.temp/{Info['name']}.json", Data)
 SaveGeoJson("../../.temp/ChainStore.json", Result)



if __name__ == "__main__":
 sys.stdin.reconfigure(encoding="utf-8")
 sys.stdout.reconfigure(encoding="utf-8")
 #
 logger.add(Path("../../.log/ChainStore.log"))
 logger.info(f"Start {Info['operator']}")
 Generate()
 logger.info(f"Done {Info['operator']}")
