import sys
import geojson
import html
from datetime import datetime

import requests

import Utils

#'ID':"n1100392221",
#'short':"https://osm.org/go/0lLuz03~DUNN",
#'Status':
#gray	Не найден на местности
#4	red	Не найден
#3	black	Нет в реестре, но есть на карте
#2	orange	Совпадение места
#	violet	Ликвидация
#1	blue	Совпадение имени
#0	green	Все в порядке


def ConvertDate(Text):
 Date = datetime.strptime(Text, "%d.%m.%Y").date()
 return Date.strftime("%Y-%m-%d") #%Y-%m-%dT%H:%M:%SZ


def GetTR():
# URL = f"https://maps.mail.ru/osm/tools/overpass/api/interpreter?data=[out:json];area[name=%22Беларусь%22];node[%22ref:BY:trade_register%22](area);out;"
 URL = f"https://maps.mail.ru/osm/tools/overpass/api/interpreter?data=[out:json];area[name=%22Беларусь%22];node[%22amenity%22](area);out;"
 Response = requests.get(URL)
 if Response.status_code == 200:
  Result = Response.json()
  return Result
 else:
  return None




TR = GetTR()

Utils.SaveJson("11121", "Overpass", TR)
print(f"{len(TR['elements'])}")


 




#https://maps.mail.ru/osm/tools/overpass/api/interpreter?data=[out:json];area[name=%22Беларусь%22];node[%22ref:BY:trade_register%22](area);out;

#way(poly:"51.838105 36.035249 51.562810 35.991534 51.563141 36.125976 51.681037 36.317305 51.780274 36.333813 51.837612 36.159021 51.838105 36.035249")[building][~"addr:."~"."];
#out;



