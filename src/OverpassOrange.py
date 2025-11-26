#!.venv/bin/python

import os
import sys
from datetime import datetime
from pathlib import Path

from loguru import logger
from haversine import haversine
import geojson

from Settings import LOG, DOCS, TEMP
from Utils import GetOverpass, SetDate, LoadGeoJson, LoadJson, SaveGeoJson, DeNormalize, GetID


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
    return { 'ID': GetID(Item), 'Coordinates': [Item['lon'], Item['lat']] }


@logger.catch
def GetBlue(Lat, Lon, Names):
    for Name in Names:
        Overpass = f"[out:json];(node['name'~'{Name}'](around:150.0,{Lat},{Lon});node['name:ru'~'{Name}'](around:150.0,{Lat},{Lon}););out qt center;"
        Result = GetOverpass(Overpass, URL="http://localhost:8091/api/interpreter")
        if 'elements' in Result:
            if len(Result['elements']) > 0:
                return GetCoord(Lat, Lon, Result['elements'])
    return None


def GetKeys(Key, Properties, NF3, Array):
    if f'{Key}.id' in Properties:
        ID = Properties[f'{Key}.id']
        return Array.get(NF3[Key][ID], [])
    else:
        return []


@logger.catch
def GetViolet(Lat, Lon, Keys):
    Overpass = "[out:json];("
    for Key in Keys:
        Overpass += f"node[{Key}](around:100.0,{Lat},{Lon});"
    Overpass += ");out qt center;"
    #
    Result = GetOverpass(Overpass, URL="http://localhost:8091/api/interpreter")
    if len(Result['elements']) > 0:
        return GetCoord(Lat, Lon, Result['elements'])
    return None



def Generate():
    logger.info("read json")
    Data = LoadGeoJson(f"{TEMP}/tr.3.json")
    NF3 = LoadJson(f"{DOCS}/tr.nf3.js", Const="Data3NF")
    #
    logger.info("parse orange")
    for Index, Feature in enumerate(Data['features']):
        Geometry, Properties = Feature['geometry'], Feature['properties']
        Status = Properties.get('status', "")
        if Status in ["orange"]:
         Name = [ DeNormalize(Properties[Key]) for Key in ['name', 'alt_name', 'official_name'] if Key in Properties ]
         if Name:
             Lon, Lat = Geometry['coordinates']
             Coord = GetBlue(Lat, Lon, Name)
             if Coord is not None:
                 Feature['id'] = Coord['ID']
                 Lon, Lat = Coord['Coordinates']
                 Geometry['coordinates'] = geojson.Point((Lon, Lat))
                 Properties['status'] = "blue"
                 #logger.info("{ref} {name} blue = {Lon}, {Lat}", ref=Properties.get('ref:BY:trade_register', "?"), name=Properties.get('name', ""), Lon=Lon, Lat=Lat)
             else:
                 Keys = GetKeys('amenity:type', Properties, NF3, Shop) + GetKeys('cafe:type', Properties, NF3, Cafe)
                 if Keys:
                     Coord = GetViolet(Lat, Lon, Keys)
                     if Coord is not None:
                         Feature['id'] = Coord['ID']
                         Lon, Lat = Coord['Coordinates']
                         Geometry['coordinates'] = geojson.Point((Lon, Lat))
                         Properties['status'] = "violet"
                         #logger.info("{ref} {name} orange = {Lon}, {Lat}", ref=Properties.get('ref:BY:trade_register', "?"), name=Properties.get('name', ""), Lon=Lon, Lat=Lat)
        #
        if Index % 10000 == 0:
            if Index > 0:
                logger.info("обработано {count} записей", count=Index)
    logger.info("обработано всего {count} записей", count=Index+1)
    #
    logger.info("write json")
    SaveGeoJson(f"{TEMP}/tr.4.json", Data)



if __name__ == "__main__":
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    #
    logger.add(LOG)
    logger.info("Start overpass orange to blue/violet")
    Generate()
    DateTime = datetime.now().strftime("%Y-%m-%dT%H:%M:00Z")
    SetDate(f"{DOCS}/tr.date.js", 'Address', DateTime)
    logger.info("Done overpass orange to blue/violet")
