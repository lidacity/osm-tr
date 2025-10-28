import os
import html
import json
import geojson
from pathlib import Path

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
# Text = Text.replace("", "")
 return Text
# return html.unescape(Text)


def SaveJson(FileName, Json, Variable=None):
 FileName = Path(FileName)
 with open(FileName, "w", encoding='utf-8') as File:
  if Variable is not None:
   File.write(f"const {Variable} =\n")
  json.dump(Json, File, indent=2, ensure_ascii=False, sort_keys=False)
  if Variable is not None:
   File.write(";\n")


def SaveGeoJson(FileName, GeoJson, Variable=None):
 FileName = Path(FileName)
 with open(FileName, "w", encoding='utf-8') as File:
  if Variable is not None:
   File.write(f"const {Variable} =\n")
  geojson.dump(GeoJson, File, indent=2, ensure_ascii=False, sort_keys=False)
  if Variable is not None:
   File.write(";\n")


def LoadJson(FileName, Variable=None):
 FileName = Path(FileName)
 Result = {}
 if os.path.isfile(FileName):
  with open(FileName, "r", encoding='utf-8') as File:
   Data = File.readlines()
   Data = "".join(Data)
   if Variable is not None:
    Start = Data.find(f"const {Variable} =") + len(f"const {Variable} =")
    End = Start + Data[Start::].find(f";\n")
    Data = Data[Start:End]
   Result = json.loads(Data)
 return Result


def LoadGeoJson(FileName, Variable=None):
 FileName = Path(FileName)
 Result = {}
 if os.path.isfile(FileName):
  with open(FileName, "r", encoding='utf-8') as File:
   Data = File.readlines()
   Data = "".join(Data)
   if Variable is not None:
    Start = Data.find(f"const {Variable} =") + len(f"const {Variable} =")
    End = Start + Data[Start::].find(f";\n")
    Data = Data[Start:End]
   Result = geojson.loads(Data)
 return Result


# задаць дату абнаўлення
def SetDate(FileName, Key, Date):
 Dates = LoadJson(FileName, Variable="ModifyDate");
 Dates[Key] = Date
 SaveJson(FileName, Dates, Variable="ModifyDate")


def GetDate(FileName, Key):
 Dates = LoadJson(FileName, Variable="ModifyDate");
 return Dates.get(Key, "")


def GetRequest(URL, Params={}, Cookies={}, Headers={}, Files={}, Json={}):
 Response = requests.get(URL, params=Params, cookies=Cookies, headers=Headers, files=Files, json=Json)
 if Response.status_code == 200:
  return Response.json()
 else:
  return {}


def RunOnce():
 if platform == "linux" or platform == "linux2":
  fh = open(os.path.realpath(__file__), 'r')
  try:
   fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
  except:
   logger.error(f"{__file__} already running...")
   #os._exit(1)
   return True
 else:
  logger.error(f"{__file__} not started in linux...")
 return False

