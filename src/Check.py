#!.venv/bin/python

import os
import sys
from datetime import datetime
from pathlib import Path

from loguru import logger

from Settings import LOG, DOCS, TEMP
from Utils import LoadGeoJson, SaveGeoJson, LoadJson, SaveJson
import UtilsTrade


def Check(Geometry, Properties):
    Address = UtilsTrade.GetAddress(Properties, Full=False)
    if Geometry['coordinates'] == [0.0, 0.0]:
        return False
    elif Properties['official_name'][:30] == "Индивидуальный предприниматель" and Address == []:
        return False
    elif 'status' not in Properties:
        return False
    elif Properties['status'] not in ["violet", "blue", "orange", "red", ]:
        return False
    else:
        return True



def Generate():
    logger.info("read json")
    Base3NF = LoadJson(f"{DOCS}/tr.nf3.js", Const="Data3NF")
    Data = LoadGeoJson(f"{TEMP}/tr.4.json")
    Delete = []
    #
    logger.info("parse")
    Exclude = []
    for Index, Item in enumerate(Base3NF['type']):
        if Item in ["Розничная торговля без использования торгового объекта", "Интернет-магазин", "Оптовая торговля без использования торгового объекта", ]:
            Exclude.append(Index)
    #
    logger.info("check")
    for Feature in Data['features']:
        Geometry, Properties = Feature['geometry'], Feature['properties']
        if not Check(Geometry, Properties):
            Delete.append(Feature)
        elif Properties['type.id'] in Exclude:
            Delete.append(Feature)
    logger.info("{count} записей для удаления", count=len(Delete))
    #
    for Index, Feature in enumerate(Delete):
        Data['features'].remove(Feature)
        #
        if Index % 10000 == 0:
            if Index > 0:
                logger.info("обработано {count} записей", count=Index)
    logger.info("{count} записей для сохранения", count=len(Data['features']))
    #
    logger.info("write json")
    SaveGeoJson(f"{TEMP}/tr.5.json", Data)
    SaveJson(f"{TEMP}/tr.5.delete.json", Delete)
 


if __name__ == "__main__":
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    #
    logger.add(LOG)
    logger.info("Start check")
    Generate()
    logger.info("Done check")
