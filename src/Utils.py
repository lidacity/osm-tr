import os
import html
import json
import geojson

from loguru import logger

from sys import platform
if platform == "linux" or platform == "linux2":
 import fcntl


KeyList = {
 'Полное наименование юр. лица или ФИО ИП': "official_name",
 'УНП': "operator:ref:BY:PAN",
 'Место нахождения юр. лица/место жительства ИП': "addr:full",
 'Тип объекта': "type",
 'Наименование объекта/доменное имя интернет-магазина': "alt_name#2",
 'Наименование объекта/доменное имя интернет-магазина': "alt_name",
 'Название торговой сети (при наличии)': "name",
 'Место нахождения объекта: область': "addr:region",
 'Место нахождения объекта: район': "addr:district",
 'Место нахождения объекта: населенный пункт': "addr:city",
 'Место нахождения объекта: улица': "addr:street",
 'Место нахождения объекта: дом и корпус': "addr:housenumber",
 'Место нахождения объекта: квартира/офис': "addr:door",
 'Контакты объекта': "contact",
 'Вид торгового объекта в зависимости от формата': "format:view",
 'Вид объекта в зависимости от места расположения': "place:view",
 'Вид торгового объекта в зависимости от ассортимента товаров': "assortment:view",
 'Вид торгового объекта в зависимости от способа организации торговли "Фирменный"': "firm:is",
 'Тип торгового объекта (при наличии)': "amenity:type",
 'Торговая площадь торгового объекта (при наличии), кв. м': "trade:area",
 'Вид торговли "Розничная"': "retail:is",
 'Вид торговли "Оптовая"': "trade:is",
 'Форма розничной торговли без использования торгового объекта': "retail:place",
 'Оптовая торговля без использования торгового объекта': "place:is",
 'Классы реализуемых товаров': "category:class",
 'Группы реализуемых товаров': "category:group",
 'Подгруппы реализуемых товаров': "category:subgroup",
 'Тип объекта общественного питания в зависимости от формата (при наличии)': "cafe:type",
 'Количество мест в объекте общественного питания (при наличии), ед.': "amenity:cafe:capacity",
 'Количество общедоступных мест в объекте общественного питания (при наличии), ед.': "amenity:canteen:capacity",
 'Специализации торгового центра': "mall:specialization",
 'Количество торговых объектов, размещенных в торговом центре, ед.': "mall:capacity",
 'Количество объектов общественного питания, размещенных в торговом центре (при наличии), ед.': "foodcourt:capacity",
 'Площадь торгового центра, отведенная под торговые объекты, кв. м': " building:area",
 'Тип рынка': "marketplace:type",
 'Специализация рынка (при наличии)': "marketplace:specialization",
 'Количество торговых мест, размещенных на территории рынка, ед.': "marketplace:capacity",
 'Количество торговых объектов, размещенных на территории рынка, ед.': "marketplace:object:capacity",
 'Регистрационный номер в Торговом реестре': "ref:BY:trade_register",
 'Дата включения сведений в Торговый реестр': "start_date",
}


#'Status':
#gray	Не найден на местности
#4	red	Не найден
#3	black	Нет в реестре, но есть на карте
#2	orange	Совпадение места
#1	blue	Совпадение имени
#0	green	Все в порядке


def ConvertDate(Text):
 Date = datetime.strptime(Text, "%d.%m.%Y").date()
 return Date.strftime("%Y-%m-%d") #%Y-%m-%dT%H:%M:%SZ



#Address0 = "addr:full"
#Address1 = [
# "addr:region",
# "addr:district",
# "addr:city",
# "addr:street",
# "addr:housenumber",
#]


#def GetAddress(Items):
# Result = " ".join([Items[Item] for Item in Address1 if Item in Items])
# if not Result:
#  Result = Items.get(Address0, "")
# return Result


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


def SaveJson(FileName, Name, Json):
 with open(FileName, "w", encoding='utf-8') as File:
  File.write(f"const {Name} =\n")
  json.dump(Json, File, indent=2, ensure_ascii=False, sort_keys=False)
  File.write(";\n")


def SaveGeoJson(FileName, Name, GeoJson):
 with open(FileName, "w", encoding='utf-8') as File:
  File.write(f"const {Name} =\n")
  geojson.dump(GeoJson, File, indent=2, ensure_ascii=False, sort_keys=False)
  File.write(";\n")


def LoadJson(FileName, Name):
 Result = {}
 if os.path.isfile(FileName):
  with open(FileName, "r", encoding='utf-8') as File:
   Data = File.readlines()
   Data = "".join(Data)
   Start = Data.find(f"const {Name} =") + len(f"const {Name} =")
   End = Start + Data[Start::].find(f";\n")
   Data = Data[Start:End]
   Result = json.loads(Data)
 return Result


def LoadGeoJson(FileName, Name):
 Result = {}
 if os.path.isfile(FileName):
  with open(FileName, "r", encoding='utf-8') as File:
   Data = File.readlines()
   Data = "".join(Data)
   Start = Data.find(f"const {Name} =") + len(f"const {Name} =")
   End = Start + Data[Start::].find(f";\n")
   Data = Data[Start:End]
   Result = geojson.loads(Data)
 return Result


# задаць дату абнаўлення
def SetDate(Key, Date):
 Dates = LoadJson(os.path.join("docs", "date.js"), "ModifyDate");
 Dates[Key] = Date
 SaveJson(os.path.join("docs", "date.js"), "ModifyDate", Dates)


def GetDate(Key):
 Dates = LoadJson(os.path.join("docs", "date.js"), "ModifyDate");
 return Dates.get(Key, "")


def NormalizeAddress(Address):
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


def GetAddress(Properties, Full=True):
 Result = []
 # адрас з частак
 Addr = [ Properties[Key] for Key in [ 'addr:region', 'addr:district', 'addr:city', 'addr:street', 'addr:housenumber' ] if Key in Properties ]
 Addr = NormalizeAddress(Addr)
 if Addr:
  Result.append(Addr)
 # поўны адрас
 if Full:
  if 'addr:full' in Properties:
   Addr = Properties['addr:full'].split(",")
   Addr = NormalizeAddress(Addr)
   if Addr:
    Result.append(Addr)
 #
 return Result


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

