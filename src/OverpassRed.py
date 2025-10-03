#!.venv/bin/python

import os
import sys
import geojson
import html
from datetime import datetime

from loguru import logger
import requests
from haversine import haversine

import Utils


Overpass = "https://maps.mail.ru/osm/tools/overpass/api/interpreter"

Shop = {
 'Прочие продовольственные неспециализорованные магазины со смешанным ассортиментом товаров, не включенные в другие типы': ["shop=convenience"],
 'Прочие непродовольственные неспециализированные магазины со смешанным ассортиментом товаров, не включенные в другие типы': [],
 'Прочие непродовльственные неспециализированные магазины с комбинированным ассортиментом товаров, не включенные в другие типы': [],
 'Комиссионный магазин': ["shop=second_hand"],
 'Автомобили': ["shop=car", "shop=car_repair"],
 'Прочие непродовольственные специализированные магазины, не включенные в другие типы': ["shop=erotic"],
 'Гипермаркет (непродовольственный)': ["shop=mall"],
 'Дом торговли': ["shop=mall"],
 'Товары для дома': ["shop=houseware"],
 'Строительные товары': ["shop=doityourself"],
 'Прочие непродовольственные неспециализированные магазины с универсальным ассортиментом товаров, не включенные в другие типы': ["shop=department_store"],
 'Универмаг': ["shop=convenience", "shop=department_store"],
 'Товары для сада и огорода': ["shop=garden_centre"],
 'Универмаг в сельских населенных пунктах': ["shop=convenience", "shop=country_store"],
 'Ювелирные изделия': ["shop=jewelry", "shop=gold_buyer"],
 'Часы': ["shop=watches"],
 'Одежда': ["shop=clothes", "shop=wool"],
 'Пиво': ["shop=brewing_supplies"],
 'Гастроном': ["shop=convenience"],
 'Продукты': ["shop=convenience", "shop=food"],
 'Обувь': ["shop=shoes", "shop=shoe_repair"],
 'Галантерея': ["shop=bag"],
 'Бытовая химия': ["shop=chemist"],
 'Кондитерские изделия': ["shop=chocolate", "shop=confectionery"],
 'Мини-магазин (мини-маркет, продукты)': ["shop=convenience"],
 'Книги': ["shop=books"],
 'Универсам': ["shop=department_store"],
 'Прочие продовольственные неспециализированные магазины с комбинированным ассортиментом товаров, не включенные в другие типы': ["shop=convenience"],
 'Зоотовары': ["shop=pet"],
 'Алкогольные напитки': ["shop=alcohol", "shop=beverages", "shop=brewing_supplies", "shop=deli", "shop=wine"],
 'Парфюмерно-косметические товары': ["shop=cosmetics", "shop=perfumery"],
 'Печатные издания': ["shop=kiosk"],
 'Канцелярские товары': ["shop=stationery"],
 'Ткани': ["shap=fabric", "shop=leather", "shop=sewing"],
 'Медицинская техника': ["shop=herbalist", "shop=medical_supply"],
 'Аптека': ["amenity=pharmacy"],
 'Бутик (салон-магазин)': ["shop=boutique", "shop=clothes", "shop=fashion", "shop=fashion_accessories", "shop=beauty"],
 'Сувениры': ["shop=gift"],
 'Цветы': ["shop=florist"],
 'Хлебобулочные изделия': ["shop=bakery", "shop=pasta", "shop=pastry", "shop=tortilla"],
 'Прочие продовольственные специализированные магазины, не включенные в другие типы': ["shop=convenience"],
 'Магазин &quot;Секонд-хэнд&quot;': ["shop=charity", "shop=second_hand"],
 'Обои': [],
 'Промтовары': ["shop=houseware"],
 'Хозяйственные товары': ["shop=houseware"],
 'Прочие продовольственные неспециализированные магазины с универсальным ассортиментом товаров, не включенные в другие типы': ["shop=convenience", "shop=department_store"],
 'Плодоовощная продукция': ["shop=food"],
 'Посуда': ["shop=houseware"],
 'Оптика': ["shop=optician"],
 'Мебель': ["shop=bed", "shop=furniture"],
 'Фототовары': ["shop=camera", "shop=photo"],
 'Молочные продукты': ["shop=cheese", "shop=dairy", "shop=ice_cream"],
 'Галантерея – парфюмерия': ["shop=perfumery"],
 'Мясные продукты': ["shop=butcher", "shop=deli", "shop=frozen_food"],
 'Охотничьи и рыболовные товары': ["shop=fishing", "shop=hunting"],
 'Электробытовые товары': ["shop=appliance", "shop=electronics", "shop=hifi", "shop=mobile_phone", "shop=radiotechnics", "shop=vacuum_cleaner"],
 'Товары для спорта и туризма': ["shop=outdoor"],
 'Автозапчасти': ["shop=car_parts"],
 'Магазин &quot;Сток&quot; (стоковый магазин)': [],
 'Средства связи': ["shop=mobile_phone"],
 'Игрушки': ["shop=toys"],
 'Компьютеры': ["shop=computer"],
 'Товары для женщин': ["shop=chemist"],
 'Товары для мужчин': [" shop=electrotools"],
 'Мёд': ["shop=food"],
 'Супермаркет': ["shop=supermarket"],
 'Гипермаркет (продовольственный)': ["shop=mall"],
 'Универсам в сельских населенных пунктах': ["shop=convenience", "shop=department_store"],
 'Ковры': ["shop=carpet"],
 'Музыкальные товары': ["shop=music", "shop=musical_instrument"],
 'Товары для детей (детский мир)': ["shop=baby_goods"],
 'Чай': ["shop=coffee", "shop=tea"],
 'Бакалейные товары': [],
 'Велосипеды': ["shop=bicycle"],
 'Кофе': ["shop=coffee"],
 'Спортивное питание': ["shop=health_food"],
 'Табачные изделия': ["shop=tobacco"],
 'Дискаунтер (продовольственный)': [],
 'Товары для шитья и рукоделия': ["shop=sewing"],
 'Рыбная продукция': ["shop=seafood"],
 'Комиссионный магазин по продаже автомобилей': ["shop=car", "shop=car_repair"],
 'Головные уборы': [],
 'Сделай сам': ["shop=bathroom_furnishing", "shop=doityourself", "shop=electrical", "shop=energy", "shop=fireplace", "shop=garden_furniture", "shop=hardware", "shop=paint"],
 'Безалкогольные напитки': ["shop=beverages"],
 'Плитка': [],
 'Дискаунтер (непродовольственный)': ["shop=variety_store"],
 'Антиквариат': ["shop=antiques", "shop=art"],
 'Здоровое питание': ["shop=deli", "shop=greengrocer", "shop=health_food", "shop=nuts", "shop=water", "shop=nutrition_supplements"],
 'Пиротехника': ["shop=pyrotechnics"],
 'Фермерские продукты': ["shop=deli", "shop=farm", "shop=greengrocer", "shop=spices", "shop=agrarian", "shop=garden_centre"],
}

Cafe = {
 'Буфет': [],
 'Заготовочный объект (цех)': ["amenity=cafe"],
 'Фуд-трак': ["amenity=food_court"],
 'Иной тип': ["amenity=cafe"],
 'Столовая': ["fast_food=cafeteria"],
 'Вагон-ресторан': ["amenity=restaurant"],
 'Бар': ["amenity=bar", "amenity=pub"],
 'Кафе': ["amenity=cafe"],
 'Магазин кулинарии': [],
 'Кафетерий': ["amenity=cafe"],
 'Кофейня': ["amenity=cafe"],
 'Столовая-раздаточная': ["amenity=fast_food"],
 'Мини-кафе': ["amenity=cafe"],
 'Мини-бар': ["amenity=bar", "amenity=pub"],
 'Ресторан': ["amenity=restaurant"],
 'Летнее (сезонное) кафе': ["amenity=cafe"],
 'Ресторан быстрого обслуживания': ["amenity=fast_food"],
 'Закусочная': ["amenity=cafe"],
 'Ресторан-пивоварня': ["amenity=restaurant"],
 'Кафе быстрого обслуживания': ["amenity=fast_food"],
 'Лобби-бар': ["amenity=bar", "amenity=pub"],
 'Пиццерия': ["cuisine=pizza"],
 'Кондитерская': ["shop=confectionery"],
 'Бургерная': ["amenity=fast_food"],
 'Чебуречная': ["amenity=fast_food"],
 'Пончиковая': ["amenity=fast_food"],
 'Купе-бар': ["amenity=bar", "amenity=pub"],
 'Купе-буфет': ["amenity=cafe"],
}




def GetCoord(Lat, Lon, Elements):
 Length = sys.maxsize
 for Item in Elements:
  Length1 = haversine((Lat, Lon), (Item['lat'], Item['lon']))
  if Length > Length1:
   Length, Result = Length1, Item
 return { 'ID': f"{Item['type'][0]}{Item['id']}", 'Coordinates': [Item['lon'], Item['lat']] }


#https://maps.mail.ru/osm/tools/overpass/
def GetBlue(Lat, Lon, Names):
 for Name in Names:
  URL = f"{Overpass}?data=[out:json];area[name='Беларусь'];(node['name'~'{Name}'](around:1000.0,{Lat},{Lon});node['name:ru'~'{Name}'](around:1000.0,{Lat},{Lon}););out qt center;"
  Response = requests.get(URL)
  if Response.status_code == 200:
   Result = Response.json()
   if len(Result['elements']) > 0:
    return GetCoord(Lat, Lon, Result['elements'])
 return None


def GetKeys(Key, Properties, NF3, Array):
 if f'{Key}.id' in Properties:
  ID = Properties[f'{Key}.id']
  return Array.get(NF3[Key][ID], [])
 else:
  return []


#https://maps.mail.ru/osm/tools/overpass/
def GetOrange(Lat, Lon, Keys):
 Query = "[out:json];area[name='Беларусь'];("
 for Key in Keys:
  Query += f"node[{Key}](around:100.0,{Lat},{Lon});"
 Query += ");out qt center;"
 #
 URL = f"{Overpass}?data={Query}"
 #
 Response = requests.get(URL)
 if Response.status_code == 200:
  Result = Response.json()
  if len(Result['elements']) > 0:
   return GetCoord(Lat, Lon, Result['elements'])
 return None



def Generate():
# Date = GetDateFromFileName(FileName)
# Utils.SetDate('Nominatim', Date)
# DateTime = datetime.now().strftime("%Y-%m-%dT%H:%M:00Z")
# Utils.SetDate('Nominatim', DateTime)
 #
 logger.info("read js")
 Data = Utils.LoadGeoJson(os.path.join(".temp", "shops.3.js"), "Data")
 NF3 = Utils.LoadJson(os.path.join("docs", "shops.3nf.js"), "Data3NF")
 #
 logger.info("parse red")
 #
 for Index, Feature in enumerate(Data['features']):
  Geometry, Properties = Feature['geometry'], Feature['properties']
  Status = Properties.get('status', "")
  if Status in ["red"] and Properties['addr:accuracy']:
   Name = [ Properties[Key] for Key in ['name', 'alt_name', 'official_name'] if Key in Properties ]
   if Name:
    Lon, Lat = Geometry['coordinates']
    Coord = GetBlue(Lat, Lon, Name)
    if Coord is not None:
     Properties['ID'] = Coord['ID']
     Geometry['coordinates'] = Coord['Coordinates']
     Properties['status'] = "blue"
     logger.info(f"{Properties.get('ref:BY:trade_register', "?")} {Properties.get('name', "")} blue = {Lon}, {Lat}")
    else:
     Keys = GetKeys('amenity:type', Properties, NF3, Shop) + GetKeys('cafe:type', Properties, NF3, Cafe)
     if Keys:
      Coord = GetOrange(Lat, Lon, Keys)
      if Coord is not None:
       Properties['ID'] = Coord['ID']
       Geometry['coordinates'] = Coord['Coordinates']
       Properties['status'] = "orange"
       logger.info(f"{Properties.get('ref:BY:trade_register', "?")} {Properties.get('name', "")} orange = {Lon}, {Lat}")
  #
  if Index % 10000 == 0:
   if Index > 0:
    logger.info(f"обработано {Index} записей")
 logger.info(f"обработано всего {Index+1} записей")
 #
 logger.info("write js")
 Utils.SaveGeoJson(os.path.join(".temp", "shops.4.js"), "Data", Data)



if __name__ == "__main__":
 sys.stdin.reconfigure(encoding="utf-8")
 sys.stdout.reconfigure(encoding="utf-8")
 #
 Path = os.path.dirname(os.path.abspath(__file__))
 logger.add(os.path.join(Path, ".log", "tr.log"))
 if not Utils.RunOnce():
  logger.info("Start overpass red to blue/orange")
  Generate()
  logger.info("Done overpass red to blue/orange")

