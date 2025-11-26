#!.venv/bin/python

import os
import sys
import time
from datetime import datetime
from pathlib import Path

from loguru import logger
import requests

from Settings import LOG, DOCS, TEMP
from Utils import SetDate, LoadGeoJson, SaveGeoJson, SaveJson


#VATin = json.loads(j, object_hook=KeysToInt)
def KeysToInt(Items):
    return { int(Key): Value for Key, Value in Items.items() }


Int = ['vunp', 'nmns', ]

#https://grp.nalog.gov.by/grp/rest-api
def GetMTD(VATin):
    URL = f"http://grp.nalog.gov.by/api/grp-public/data?unp={VATin}&charset=UTF-8&type=json"
    while True:
        Response = requests.get(URL)
        if Response.status_code == 200:
            Result = Response.json()['row']
            for Key, Value in Result.items():
                if Key in Int:
                    Result[Key] = int(Value)
            return Result
        elif Response.status_code == 400:
            return { 'ckodsost': "?", 'vkods': "Отсутствует", }
        else:
            logger.error("Код ошибки {status_code}: УНП={vatin}", status_code=Response.status_code, vatin=VATin)
            time.sleep(15)



def Generate():
    logger.info("read json")
    Data = LoadGeoJson(f"{TEMP}/tr.1.json")
    #
    logger.info("parse vatin")
    VATin = {}
    for Feature in Data['features']:
        Properties = Feature['properties']
        if 'ref:vatin' in Properties:
            Ref = Properties['ref:vatin']
            VATin[Ref] = {}
    logger.info("count vatin {features} -> {unique}", features=len(Data['features']), unique=len(VATin))
    #
    logger.info("read nalog.gov.by")
    for Index, Key in enumerate(VATin.keys()):
        VATin[str(Key)] = GetMTD(Key)
        #
        if Index % 5 == 0: # паўза каб сайт МНС не блакаваў
            time.sleep(1)
            if Index % 10000 == 0:
                if Index > 0:
                    logger.info("обработано {count} записей", count=Index)
    logger.info("обработано всего {count} записей", count=Index+1)
    #
    logger.info("parse")
    for Feature in Data['features']:
        Properties = Feature['properties']
        Ref = str(Properties['ref:vatin'])
        if VATin[Ref]['ckodsost'] != "1":
            Properties['MTD'] = f"({VATin[Ref]['ckodsost']}) {VATin[Ref]['vkods']}"
            Properties['status'] = "gray"
    #
    logger.info("write json")
    SaveJson(f"{TEMP}/tr.2.vatin.json", VATin)
    SaveGeoJson(f"{TEMP}/tr.2.json", Data)
 


if __name__ == "__main__":
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    #
    logger.add(LOG)
    logger.info("Start MTD to gray")
    Generate()
    DateTime = datetime.now().strftime("%Y-%m-%dT%H:%M:00Z")
    SetDate(f"{DOCS}/tr.date.js", 'MTD', DateTime)
    logger.info("Done MTD to gray")
