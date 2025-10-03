import os
import html
import json
import geojson
import re


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


def SaveJson(FileName, Name, Json, Option="w"):
 with open(FileName, Option, encoding='utf-8') as File:
  File.write(f"var {Name} =\n")
  json.dump(Json, File, indent=2, ensure_ascii=False, sort_keys=False)
  File.write(";\n")


def SaveGeoJson(FileName, Name, GeoJson):
 with open(FileName, "w", encoding='utf-8') as File:
  File.write(f"var {Name} =\n")
  geojson.dump(GeoJson, File, indent=2, ensure_ascii=False, sort_keys=False)
  File.write(";\n")


def LoadJson(FileName, Name):
 Result = {}
 if os.path.isfile(FileName):
  with open(FileName, "r", encoding='utf-8') as File:
   Data = File.readlines()
   #Data = "".join(Data).replace("\n", " ")
   #Data = re.search(f"var {Name} =(.*);", Data).group(1)
   Data = "".join(Data)
   Start = Data.find(f"var {Name} =") + len(f"var {Name} =")
   End = Start + Data[Start::].find(f";\n")
   Data = Data[Start:End]
   #Data = Data[1:] # 'Data[1:]' прапускае 'var {Var} ='
   #Data = "".join(Data)
   #Data = Data.strip()
   #Data = Data[:-1] # 'Data[:-1]' прапускае ';'
   Result = json.loads(Data)
 return Result

