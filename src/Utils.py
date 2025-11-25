import os
import html
import json
import geojson
from pathlib import Path

import requests
from loguru import logger

from sys import platform
if platform == "linux" or platform == "linux2":
    import fcntl


def Normalize(Text):
    Text = ' '.join(Text.split())
    Text = Text.replace("\"\"", "\"")
    Text = Text.replace("''", "'")
    return html.escape(Text)


def DeNormalize(Text):
    Text = Text.replace("&quot;", "")
#    Text = Text.replace("", "")
    return Text
#    return html.unescape(Text)


def SaveJson(FileName, Json, Const=None, Variable=None):
    FileName = Path(FileName)
    with open(FileName, "w", encoding='utf-8') as File:
        if Const is not None:
            File.write(f"const {Const} =\n")
            json.dump(Json, File, indent=2, ensure_ascii=False, sort_keys=False)
            File.write(";\n")
        elif Variable is not None:
            File.write(f"const {Variable} =\n")
            json.dump(Json, File, indent=2, ensure_ascii=False, sort_keys=False)
            File.write(";\n")
        else:
            json.dump(Json, File, indent=2, ensure_ascii=False, sort_keys=False)


def SaveGeoJson(FileName, GeoJson, Const=None, Variable=None):
    FileName = Path(FileName)
    with open(FileName, "w", encoding='utf-8') as File:
        if Const is not None:
            File.write(f"const {Const} =\n")
            geojson.dump(GeoJson, File, indent=2, ensure_ascii=False, sort_keys=False)
            File.write(";\n")
        elif Variable is not None:
            File.write(f"const {Variable} =\n")
            geojson.dump(GeoJson, File, indent=2, ensure_ascii=False, sort_keys=False)
            File.write(";\n")
        else:
            geojson.dump(GeoJson, File, indent=2, ensure_ascii=False, sort_keys=False)


def LoadJson(FileName, Const=None, Variable=None):
    MarkStartConst = f"const {Const} ="
    MarkStartVar = f"var {Variable} ="
    MarkEnd = ";\n"
    FileName = Path(FileName)
    Result = {}
    if FileName.exists():
        with open(FileName, "r", encoding='utf-8') as File:
            Data = File.readlines()
            Data = "".join(Data)
            if Const is not None:
                Start = Data.find(MarkStartConst) + len(MarkStartConst)
                End = Start + Data[Start::].find(f";\n")
                Data = Data[Start:End]
            elif Variable is not None:
                Start = Data.find(MarkStartVar) + len(MarkStartVar)
                End = Start + Data[Start::].find(f";\n")
                Data = Data[Start:End]
            Result = json.loads(Data)
    return Result


def LoadGeoJson(FileName, Const=None, Variable=None):
    MarkStartConst = f"const {Const} ="
    MarkStartVar = f"var {Variable} ="
    MarkEnd = ";\n"
    FileName = Path(FileName)
    Result = {}
    if FileName.exists():
     with open(FileName, "r", encoding='utf-8') as File:
      Data = File.readlines()
      Data = "".join(Data)
      if Const is not None:
          Start = Data.find(MarkStartConst) + len(MarkStartConst)
          End = Start + Data[Start::].find(MarkEnd)
          Data = Data[Start:End]
      elif Variable is not None:
          Start = Data.find(MarkStartVar) + len(MarkStartVar)
          End = Start + Data[Start::].find(MarkEnd)
          Data = Data[Start:End]
      Result = geojson.loads(Data)
    return Result


# задаць дату абнаўлення
def SetDate(FileName, Key, Date):
    Dates = LoadJson(FileName, Const="ModifyDate");
    Dates[Key] = Date
    SaveJson(FileName, Dates, Const="ModifyDate")


def GetDate(FileName, Key):
    Dates = LoadJson(FileName, Const="ModifyDate");
    return Dates.get(Key, "")


def GetRequest(URL, Params=None, Cookies=None, Headers=None, Files=None, Json=None):
    Response = requests.get(URL, params=Params, cookies=Cookies, headers=Headers, files=Files, json=Json)
    if Response.status_code == 200:
        return Response.json()
    else:
        return {}


def PrepareElements(Overpass):
    Result = Overpass.copy()
    if 'elements' in Result:
        for Element in Result['elements']:
            if Element['type'] != "node" and 'center' in Element:
                Element['lat'], Element['lon'] = Element['center']['lat'], Element['center']['lon']
    return Result


#https://maps.mail.ru/osm/tools/overpass/
def GetOverpass(Overpass, URL="https://maps.mail.ru/osm/tools/overpass/api/interpreter"):
    Result = GetRequest(URL, Params={'data': Overpass})
    return PrepareElements(Result)


def GetID(Item):
    return f"{Item['type'][0]}{Item['id']}"


def RunOnce():
    if platform == "linux" or platform == "linux2":
        fh = open(os.path.realpath(__file__), 'r')
        try:
            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except:
            logger.exception("{file} already running…", file=__file__)
            #os._exit(1)
            return True
    else:
        logger.error("{file} not started in linux…", file=__file__)
    return False
