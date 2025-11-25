#!.venv/bin/python

import os
import sys
from datetime import datetime
from pathlib import Path

from loguru import logger
from jinja2 import Environment, FileSystemLoader
from dateutil import parser

from Settings import LOG, DOCS
from Utils import GetOverpass, GetDate, GetID


def GetJson():
 Overpass = f"[out:json];area[name='Беларусь'];nw['ref:BY:trade_register'](area);out meta;"
 return GetOverpass(Overpass)#, URL="http://localhost:8091/api/interpreter")


def GetHistory(Type, ID):
 Overpass = f"[out:json];timeline({Type},{ID});foreach(retro(u(t['created']))({Type}({ID});out meta;););"
 return GetOverpass(Overpass)#, URL="http://localhost:8091/api/interpreter")


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
 return { 'Users': Result, 'DateTime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'PBFDateTime': GetDate(f"{DOCS}/tr.date.js", 'Geofabrik') }


def Jinja(Users):
 Loader = FileSystemLoader(searchpath="./")
 Env = Environment(loader=Loader)
 Template = Env.get_template("Stat.htm")
 Render = Template.render(Users)
 FileName = Path(f"{DOCS}/stat.html")
 with open(FileName, mode="w", encoding="utf-8") as File:
  File.write(Render)



def Generate():
 Result = {}
 logger.info("get overpass")
 Json = GetJson()
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
     Item['ID'] = GetID(Element)
     Item['timestamp'] = History['timestamp']
     Result[User].append(Item)
     break
  #
  if Index % 100 == 0:
   if Index > 0:
    logger.info("обработано {count} записей", count=Index)
 logger.info("обработано всего {count} записей", count=Index+1)
 #
 logger.info("generate html")
 Users = GetUsers(Result)
 Jinja(Users)



if __name__ == "__main__":
 sys.stdin.reconfigure(encoding="utf-8")
 sys.stdout.reconfigure(encoding="utf-8")
 #
 logger.add(LOG)
 logger.info("Start stat")
 Generate()
 logger.info("Done stat")
