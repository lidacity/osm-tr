import os
import sys
from datetime import datetime

import requests
from loguru import logger
from jinja2 import Environment, FileSystemLoader
from dateutil import parser

import Utils


URL = "https://maps.mail.ru/osm/tools/overpass/api/interpreter"


def GetOverpass():
 Overpass = f"[out:json];area[name='Беларусь'];nw['ref:BY:trade_register'](area);out meta;"
 Response = requests.get(URL, params={'data': Overpass})
 if Response.status_code == 200:
  Result = Response.json()
  return Result
 else:
  return None


def GetHistory(Type, ID):
 Overpass = f"[out:json];timeline({Type},{ID});foreach(retro(u(t['created']))({Type}({ID});out meta;););"
 Response = requests.get(URL, params={'data': Overpass})
 if Response.status_code == 200:
  Result = Response.json()
  return Result
 else:
  return None


def GetUsers(List):
 Result = []
 Index = 1
 while List:
  Name, Max = "", 0
  for Key, Value in List.items():
   if len(Value) > Max:
    Max = len(Value)
    Name = Key
  #
  U = List.pop(Name)
  User = {}
  User['index'] = Index
  User['name'] = Name
  User['count'] = len(U)
  User['count60'] = 0
  User['timestamp:first'] = U[0]['timestamp']
  User['timestamp:last'] = U[0]['timestamp']
  Now = datetime.now()
  for Item in U:
   Date = parser.isoparse(Item['timestamp']).replace(tzinfo=None)
   Delta = Now - Date
   if Delta.days <= 60:
    User['count60'] += 1
   if User['timestamp:first'] > Item['timestamp']:
    User['timestamp:first'] = Item['timestamp']
   if User['timestamp:last'] < Item['timestamp']:
    User['timestamp:last'] = Item['timestamp']
  Days = (parser.isoparse(User['timestamp:last']) - parser.isoparse(User['timestamp:first'])).days
  if Days > 0:
   User['average'] = User['count'] / Days
  else:
   User['average'] = User['count']
  Result.append(User)
  Index += 1
 #
 return { 'Users': Result, 'DateTime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'PBFDateTime': Utils.GetDate("Nominatim") } #Geofabrik


def Jinja(Users):
 Loader = FileSystemLoader(searchpath="./")
 Env = Environment(loader=Loader)
 Template = Env.get_template("Stat.htm")
 Render = Template.render(Users)
 FileName = os.path.join("..", "docs", "stat.html")
 with open(FileName, mode="w", encoding="utf-8") as File:
  File.write(Render)



def Generate():
 Result = {}
 logger.info("get overpass")
 Json = GetOverpass()
 logger.info("parse overpass")
 for Index, Element in enumerate(Json['elements']):
  Type, ID = Element['type'], Element['id']
  Histories = GetHistory(Type, ID)
  for History in Histories['elements']:
   if 'tags' in History:
    if 'ref:BY:trade_register' in History['tags']:
     User = History['user']
     if User not in Result:
      Result[User] = []
     Item = {}
     Item['ID'] = f"{Type[0]}{ID}"
     Item['timestamp'] = History['timestamp']
     Result[User].append(Item)
     break
  #
  if Index % 100 == 0:
   if Index > 0:
    logger.info(f"обработано {Index} записей")
 logger.info(f"обработано всего {Index+1} записей")
 #
 logger.info("generate html")
 Users = GetUsers(Result)
 Jinja(Users)



if __name__ == "__main__":
 sys.stdin.reconfigure(encoding="utf-8")
 sys.stdout.reconfigure(encoding="utf-8")
 #
 logger.add(os.path.join("..", ".log", "tr.log"))
 if not Utils.RunOnce():
  logger.info("Start stat")
  Generate()
  logger.info("Done stat")
