#!.venv/bin/python

#https://github.com/mapillaryby/ShopsValidator/

import os, sys
import json
import html
import urllib.request
from datetime import datetime
from pathlib import Path

import geojson
from loguru import logger

from Settings import LOG, DOCS, TEMP
from Utils import SetDate, SaveJson, SaveGeoJson, LoadJson


NF3 = { 'type', 'format:view', 'place:view', 'assortment:view', 'amenity:type', 'retail:place', 'cafe:type', 'mall:specialization', 'marketplace:type', 'marketplace:specialization', }
NF3sub = { 'category:class', 'category:group', 'category:subgroup', }
Status = ["red", "violet", "blue", "green"]


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


def GetDate(FileName):
    MarkStart = "<div class=\" stat-item\">Дата генерации "
    MarkEnd = "</div>\n"
    Result = {}
    if FileName.exists():
        with open(FileName, "r", encoding='utf-8') as File:
            Data = File.readlines()
            Data = "".join(Data)
            Start = Data.find(MarkStart) + len(MarkStart)
            End = Start + Data[Start::].find(MarkEnd)
            Data = Data[Start:End]
            Result = Data
    return Result



def Generate():
    FileName = Path(f"{TEMP}/shops.html")
    #
    logger.info("Downloading")
    urllib.request.urlretrieve("https://raw.githubusercontent.com/MapillaryBY/ShopsValidator/refs/heads/main/shops.html", FileName)
    DateTime = GetDate(FileName)
    #
    logger.info("get json")
    Data = LoadJson(FileName, Variable="markersData")
    SaveJson(f"{TEMP}/shops.js", Data)
    #
    logger.info("parse json")
    Features = []
    Base3NF = {}
    for Item in Data:
        if Item['format'] != "Киоск" and not(Item['building'] == "На рынке" and Item['format'] != "Магазин"): #Vodevil_Mark
            Geometry = geojson.Point((Item['lon'], Item['lat']))
            Item = Del('lon', Item)
            Item = Del('lat', Item)
            Properties = {}
            #
            Properties, Item = Del2('name', 'official_name', Properties, Item)
            Properties, Item = Del2('name1', 'name', Properties, Item)
            Properties, Item = Del2('name2', 'alt_name', Properties, Item)
            Properties, Item = Del2('address', 'addr:full', Properties, Item)
            Properties, Item = Del2('unp', 'ref:vatin', Properties, Item)
            Properties, Item = Del2('objectType', 'type', Properties, Item)#
            Properties, Item = Del2('amenityType', 'amenity:type', Properties, Item)
            Properties, Item = Del2('building', 'place:view', Properties, Item)#
            Properties, Item = Del2('id', 'ref:BY:trade_register', Properties, Item)
            Properties, Item = Del2('goods', 'category:subgroup', Properties, Item)
            Properties, Item = Del2('format', 'format:view', Properties, Item)#
            Properties, Item = Del2('square', 'trade:area', Properties, Item)
            Properties, Item = Del2('regDate', 'start_date', Properties, Item)
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
            #if 'ID' in Properties:
            # print(Item, Properties['official_name'])
            DetectStatus = Item['detectStatus']
            Properties['status'] = Status[DetectStatus]
            del Item['detectStatus']
            #
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
            #
            ID = None
            if 'ID' in Properties:
                ID = Properties['ID']
                del Properties['ID']
            Feature = geojson.Feature(id=ID, geometry=Geometry, properties=Properties)
            Features.append(Feature)
    #
    logger.info("save js")
    SaveJson(f"{TEMP}/shops.delete.js", Data)
    SetDate(f"{DOCS}/shops.date.js", "Update", DateTime)
    SaveJson(f"{DOCS}/shops.3nf.js", Base3NF, Const="Data3NF")
    SaveGeoJson(f"{DOCS}/shops.data.js", Features, Const="Data")



if __name__ == "__main__":
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    #
    logger.add(LOG)
    logger.info("Start shops")
    Generate()
    logger.info("Done shops")
