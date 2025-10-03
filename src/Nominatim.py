#!.venv/bin/python

import os
import sys
import geojson

from loguru import logger
import asyncio
import nominatim_api as napi

import Utils


async def Search(Query):
 async with napi.NominatimAPIAsync() as Api:
  return await Api.search(Query)


def GetDateFromFileName(FileName):
 Pattern = re.compile(r'\d\d.\d\d.\d\d\d\d')
 Matches = Pattern.findall(FileName)
 return ConvertDate(Matches[0]) if Matches else None


def Normalize(Address):
 Result = []
 for Index, Item in enumerate(Address):
  Item = Item.strip()
  if not(Index == 0 and Item.isdigit()):
   # выдаліць пачатковыя літары
   for Start in ["с/с", "аг.", "г.", "д.", "пр-т", "пр.", "Пр.", "Пл.", "тр-т", "б-р", "ул.", "ул ", "пер.", "Пер.", "переулок", "пр-д", "проспект", "улица", "Пр-т.", "Пр-т", "Им.", "гп ", "район", "Ст.", ]:
    if Item[:len(Start)] == Start:
     Item = Item[len(Start):]
   Item = Item.strip()
   # выдаліць канцавыя літары
   for End in ["обл.", "р-н.", "р-н", "А.А.", "с/с", ]:
    if Item[-len(End):] == End:
     Item = Item[:-len(End)]
   Item = Item.strip()
   # выдаліць, калі пачынаецца з
   for Start in ["ком.", "оф.", "каб.", "пом.", "кв.", "район", "офис", "административное", "помещение", "Инв.", "кабинет", "этаж", "торговый объект", "нежилое помещение", "нежилое пом.", ]:
    if Item[:len(Start)] == Start:
     Item = ""
   Item = Item.strip()
   # выдаліць, калі заканчваецца на
   for End in ["с-с.", "этаж", "помещение", "зданию", " под", " эт", ]:
    if Item[-len(End):] == End:
     Item = ""
   Item = Item.strip()
   # замяніць некаторыя супадзенні
   for Replace in ["р-н Центральный (г. Минск)", "р-н Ленинский (г. Минск)", "р-н Советский (г.Минск)", "р-н Московский (г. Минск)", "р-н Октябрьский (г. Минск)", "р-н Первомайский (г. Минск)", "р-н Партизанский (г. Минск)", "р-н Фрунзенский (г. Минск)", "р-н Заводской (г. Минск)", "р-н Ленинский (г. Могилев)", "р-н Октябрьский (г. Могилев)", "р-н Ленинский (г. Брест)", "р-н Московский (г. Брест)", "р-н Октябрьский (г. Витебск)",	"р-н Первомайский (г. Витебск)", "р-н Железнодорожный (г. Витебск)", "р-н Ленинский (г. Гродно)", "р-н Октябрьский (г. Гродно)", "р-н Центральный (г. Гомель)", "р-н Советский (г. Гомель)", "р-н Железнодорожный (г. Гомель)",  "р-н Новобелицкий (г. Гомель)", "р-н Ленинский (г. Бобруйск)", "р-н Первомайский (г. Бобруйск)", ]:
    Item = Item.replace(Replace, "")
   for Replace in ["техподполье", "&quot;", "Газ.", "АХЗ УП Ватра", "(открытая площадка)", "(аг.)", ]:
    Item = Item.replace(Replace, "")
   Item = Item.strip()
   # выдаліць пачатковыя літары яшчэ раз
   for Start in ["Б.", "В.", "Ф.", "П.", "К.", "Я.", "Э.", "Д.", "М.", "Л.", "О.", "Зм.", "С.", "А.", "Ю.", "Ак.", "И.", "Е.", "З.", ]:
    if Item[:len(Start)] == Start:
     Item = Item[len(Start):]
   #
   if Item:
    Result.append(Item)
 #
 if Result:
  Result.append("")
 return Result


def GetAddress(Properties):
 Result = []
 # адрас з частак
 Addr = [ Properties[Key] for Key in [ 'addr:region', 'addr:district', 'addr:city', 'addr:street', 'addr:housenumber' ] if Key in Properties ]
 Addr = Normalize(Addr)
 if Addr:
  Result.append(Addr)
 # поўны адрас
 if 'addr:full' in Properties:
  Addr = Properties['addr:full'].split(",")
  Addr = Normalize(Addr)
  if Addr:
   Result.append(Addr)
 #
 return Result



def Generate():
# Date = GetDateFromFileName(FileName)
# Utils.SetDate('Nominatim', Date)
# DateTime = datetime.now().strftime("%Y-%m-%dT%H:%M:00Z")
# Utils.SetDate('Nominatim', DateTime)
 #
 logger.info("read js")
 Data = Utils.LoadGeoJson(os.path.join(".temp", "shops.2.js"), "Data")
 Delete = []
 #
 logger.info("parse nominatim")
 for Index, Feature in enumerate(Data['features']):
  Geometry, Properties = Feature['geometry'], Feature['properties']
  Status = Properties.get('status', "")
  if Status in ["", "violet", "red"]:
   # сфармаваць спіс з адрасам
   for Address in GetAddress(Properties):
    Properties['addr:accuracy'] = True
    # абыход па спісу адрасоў ад самага дакладнага да вельмі прыблізнага
    for Count in range(1, len(Address)):
     Addr = ", ".join(Address[:-Count])
     Results = asyncio.run(Search(Addr))
     if Results: # знайшлі
      Lon, Lat = Results[0].centroid.x, Results[0].centroid.y
      Geometry['coordinates'] = [Lon, Lat]
      Properties['status'] = "red"
      #logger.info(f"{Addr} = {Lon}, {Lat}")
      break
     else: # дадзены адрас не знойдзены, перайсці да наступнага кроку, паменшыць дакладнасць
      logger.warning(f"адрес для {Properties.get('ref:BY:trade_register', "?")} ({Address[:-Count]} => '{Addr}') не найден")
      Properties['addr:accuracy'] = False
    else:
     continue
    break
   else: # калі аніякага адраса не знайшлі
    Delete.append(Feature)
    Data['features'].remove(Feature)
    logger.error(f"для {Properties.get('ref:BY:trade_register', "?")} с адресом ({Address[:-1]}) координаты не найдены")
  #
  if Index % 10000 == 0:
   if Index > 0:
    logger.info(f"обработано {Index} записей")
 logger.info(f"обработано всего {Index+1} записей")
 #
 logger.info("write js")
 Utils.SaveGeoJson(os.path.join(".temp", "shops.3.js"), "Data", Data)
 Utils.SaveJson(os.path.join(".temp", "shops.3delete.js"), "Delete", Delete)



if __name__ == "__main__":
 sys.stdin.reconfigure(encoding="utf-8")
 sys.stdout.reconfigure(encoding="utf-8")
 #
 Path = os.path.dirname(os.path.abspath(__file__))
 logger.add(os.path.join(Path, ".log", "tr.log"))
 if not Utils.RunOnce():
  logger.info("Start nominatim to red")
  Generate()
  logger.info("Done nominatim to red")
