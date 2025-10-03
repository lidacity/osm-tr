import os, sys
import json
import geojson
import html
import urllib.request
import hashlib

from datetime import datetime
from loguru import logger

import Utils
from Git import GitPush


NF3 = { 'type', 'format:view', 'place:view', 'assortment:view', 'amenity:type', 'retail:place', 'cafe:type', 'mall:specialization', 'marketplace:type', 'marketplace:specialization', 'category:class', }
NF3sub = { 'category:group', 'category:subgroup', }


def Del(Key, Item):
 if Key in Item:
  del Item[Key]
 return Item


def Normalize(Text):
 if Text is None:
  return Text  
 if type(Text) == int:
  return Text
 #
 Text = ' '.join(Text.split())
 Text = Text.replace("\"\"", "\"")
 Text = Text.replace("''", "'")
 #
 return html.escape(Text)
  


def Del2(Key, New, Properties, Item):
 if Key in Item:
  Properties[New] = Normalize(Item[Key])
  del Item[Key]
 return Properties, Item


def GetMD5(FileName):
 Result = hashlib.md5()
 with open(FileName, "rb") as File:
  for Chunk in iter(lambda: File.read(4096), b""):
   Result.update(Chunk)
 return Result.hexdigest()


def GetDate(FileName):
 Result = {}
 if os.path.isfile(FileName):
  with open(FileName, "r", encoding='utf-8') as File:
   Data = File.readlines()
   Data = "".join(Data)
   Start = Data.find(f"<div class=\" stat-item\">Дата генерации ") + len(f"<div class=\" stat-item\">Дата генерации ")
   End = Start + Data[Start::].find(f"</div>\n")
   Data = Data[Start:End]
   Result = Data
 return Result



sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
Path = os.path.dirname(os.path.abspath(__file__))

logger.add(os.path.join(Path, ".log", "tr.log"))
logger.info("Start")
logger.info("Downloading")

FileName = "./.temp/shops.html"
urllib.request.urlretrieve("https://raw.githubusercontent.com/MapillaryBY/ShopsValidator/refs/heads/main/shops.html", FileName)

MD5 = GetMD5(FileName)

if os.path.isfile(f"{FileName}.md5"):
 with open(f"{FileName}.md5", "r") as File:
  Data = "".join(File.readlines()).strip()
 if Data == MD5:
  logger.warning("already updated")
  sys.exit()

Dates = Utils.LoadJson(os.path.join("docs", "date.js"), "ModifyDate");
Dates['Update'] = GetDate(FileName)
Utils.SaveJson(os.path.join("docs", "date.js"), "ModifyDate", Dates)

logger.info("get json")

Data = Utils.LoadJson(FileName, "markersData")

logger.info("parse json")
Features = []
Base3NF = {}

for Item in Data:
 Geometry = geojson.Point((Item['lon'], Item['lat']))
 Item = Del('lon', Item)
 Item = Del('lat', Item)
 Properties = {}
 #
 Properties, Item = Del2('name', 'official_name', Properties, Item)
 Properties, Item = Del2('name1', 'name', Properties, Item)
 Properties, Item = Del2('name2', 'alt_name', Properties, Item)
 Properties, Item = Del2('address', 'addr:full', Properties, Item)
 Properties, Item = Del2('unp', 'operator:ref:BY:PAN', Properties, Item)
 Properties, Item = Del2('objectType', 'type', Properties, Item)#
 Properties, Item = Del2('amenityType', 'amenity:type', Properties, Item)
 Properties, Item = Del2('building', 'place:view', Properties, Item)#
 Properties, Item = Del2('id', 'ref:BY:trade_register', Properties, Item)
 Properties, Item = Del2('goods', 'category:subgroup', Properties, Item)
 Properties, Item = Del2('format', 'format:view', Properties, Item)#
 Properties, Item = Del2('osmId', 'ID', Properties, Item)
 if Item['osmType'] == 0:
  Properties['ID'] = "n" + str(Properties['ID'])
 if Item['osmType'] == 1:
  Properties['ID'] = "w" + str(Properties['ID'])
 del Item['osmType']
 Properties, Item = Del2('shortCoords', 'shortCoords', Properties, Item) #??
 Properties, Item = Del2('contact', 'contact', Properties, Item)
 Properties, Item = Del2('distance', 'distance', Properties, Item) #??
 Properties, Item = Del2('food', 'food', Properties, Item) #??

#  if 'ID' in Properties:
#  print(Item, Properties['official_name'])
 if Item['detectStatus'] == 3:
  Properties['status'] = "green"
 elif Item['detectStatus'] == 2:
  Properties['status'] = "blue"
 elif Item['detectStatus'] == 1:
  Properties['status'] = "orange"
 else:
  Properties['status'] = "red"
 del Item['detectStatus']

 Items = {}
 for Key, Value in Properties.items():
  if Key in NF3:
   if Key not in Base3NF:
    Base3NF[Key] = [f"{Key}.id"]
   if Value not in Base3NF[Key]:
    Base3NF[Key].append(Value)
   Items[f'{Key}.id'] = Base3NF[Key].index(Value)
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
  else:
   Items[Key] = Value
 Properties = Items

 Feature = geojson.Feature(geometry=Geometry, properties=Properties)
 Features.append(Feature)

Utils.SaveJson("./docs/shops.3nf.js", "Data3NF", Base3NF)
Utils.SaveGeoJson("./docs/shops.data.js", "Data", Features)


with open(f"{FileName}.md5", "w") as File:
 File.write(MD5)

Diff = GitPush(f"autogenerate {datetime.now().strftime('%Y-%m-%d')}")
if Diff:
 pass #logger.info(f"git push complete:\n{Diff}")
else:
 logger.error(f"Git error")

logger.info("Done")
