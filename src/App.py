#!.venv/bin/python

import os
import sys
from datetime import datetime
from pathlib import Path

from loguru import logger

from Settings import LOG, DOCS, DATA
from Utils import GetDate, SetDate

from Geofabrik import Generate as Geofabrik
if sys.platform in ["linux", "linux2"]:
    from NominatimDB import InterceptHandler, Generate as NominatimDB
from PBFtoOSM import Generate as PBFtoOSM
from Init_Osm3s import SystemdService, Clear, Generate as Init_Osm3s
from TradeRegister import GetLastFile, GetDateFromFileName, Generate as TradeRegister
from MTD import Generate as MTD
if sys.platform in ["linux", "linux2"]:
    from Nominatim import Generate as Nominatim
from OverpassOrange import Generate as OverpassOrange
from Check import Generate as Check
from Stat import Generate as Stat
from oshCounter import Generate as oshCounter
from OverpassGreen import Generate as OverpassGreen
from Convert import Generate as Convert
from ShopsValidator import Generate as ShopsValidator
from ChainStore import Generate as ChainStore
from Git import GitPush



if __name__ == "__main__":
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    #
    logger.add(LOG)
    logger.info("Start")

    FileName = GetLastFile()
    if FileName != GetDate(f"{DOCS}/tr.date.js", 'File'):
        #e-pasluga.by 3.13.06
        logger.warning("Update Trade Register")
        #python ./Geofabrik.py
        logger.warning("=== Start Geofabrik: download pbf ===")
        Date = Geofabrik()
        SetDate(f"{DOCS}/tr.date.js", 'Geofabrik', Date)
        logger.info("=== Done Geofabrik: download pbf ===")
        # https://nominatim.org/
        #python ./NominatimDB.py
        logger.warning("=== Start Nominatim: database ===")
        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
        logger.info("logging -> loguru")
        NominatimDB()
        logger.info("=== Done Nominatim: database ===")
        # https://download.geofabrik.de/bz2.html
        #python ./PBFtoOSM.py
        logger.warning("=== Start Osmium: convert .pbf to .osm.bz2 ===")
        PBFtoOSM()
        logger.info("=== Done Osmium: convert .pbf to .osm.bz2 ===")
        # https://wiki.openstreetmap.org/wiki/User:Breki/Overpass_API_Installation
        # https://dev.overpass-api.de/overpass-doc/en/more_info/setup.html
        #python ./Init_Osm3s.py
        logger.warning("=== Start init_osm3s.sh ===")
        Monitor = SystemdService("overpass")
        PlanetFile = Path(f"{DATA}/belarus-latest-internal.osm.bz2")
        DB = Path("~/db/").expanduser() # ensure trailing slash like original
        Exec = Path("~/osm-3s").expanduser()
        if Monitor.IsActive():
            Monitor.Stop()
        Clear(DB)
        Init_Osm3s(PlanetFile, DB, Exec)
        Monitor.Start()
        Monitor.IsActive()
        logger.info("=== Done init_osm3s.sh ===")
        # !!
        # 0->1, один раз в месяц, при чтении нового торгового реестра
        #python ./TradeRegister.py
        logger.warning("=== Start Trade register: parse ===")
        TradeRegister(FileName)
        SetDate(f"{DOCS}/tr.date.js", 'File', FileName)
        Date = GetDateFromFileName(FileName.name)
        SetDate(f"{DOCS}/tr.date.js", 'Trade', Date)
        logger.info("=== Done Trade register: parse ===")
        # 1->2, "" -> gray
        #python ./MTD.py
        logger.warning("=== Start ИМНС: gray ===")
        MTD()
        DateTime = datetime.now().strftime("%Y-%m-%dT%H:%M:00Z")
        SetDate(f"{DOCS}/tr.date.js", 'MTD', DateTime)
        logger.info("=== Done ИМНС: gray ===")
        # 2->3, "" gray red orange -> red orange
        #python ./Nominatim.py
        logger.warning("=== Start Nominatim: red/orange ===")
        Nominatim()
        logger.info("=== Done Nominatim: red/orange ===")
        # 3->4, orange -> blue violet
        #python ./OverpassOrange.py
        logger.warning("=== Start Overpass: blue/violet ===")
        OverpassOrange()
        DateTime = datetime.now().strftime("%Y-%m-%dT%H:%M:00Z")
        SetDate(f"{DOCS}/tr.date.js", 'Address', DateTime)
        logger.info("=== Done Overpass: blue/violet ===")
        # 4->5, red orange blue violet | delete
        #python ./Check.py
        logger.warning("=== Start Check: truncate ===")
        Check()
        logger.info("=== Done Check: truncate ===")
        #
        #python ./Stat.py
        #python ./oshCounter.py
        logger.warning("=== Start Statistic: dz ===")
        Stat()
        logger.info("=== Done Statistic: dz ===")
        logger.warning("=== Start Statistic: oshCounter ===")
        oshCounter()
        logger.info("=== Done Statistic: oshCounter ===")
    # !!
    # 5->6, один раз в час, all -> green gold black
    #python ./OverpassGreen.py
    logger.warning("=== Start Overpass: green/gold/black ===")
    OverpassGreen()
    DateTime = datetime.now().strftime("%Y-%m-%dT%H:%M:00Z")
    SetDate(f"{DOCS}/tr.date.js", 'Update', DateTime)
    logger.info("=== Done Overpass: green/gold/black ===")
    #
    #python ./Convert.py
    logger.warning("=== Start GitHub: split large files ===")
    Convert()
    logger.info("=== Done GitHub: split large files ===")
    #python ./ShopsValidator.py
    logger.warning("=== Start ShopsValidator: convert ===")
    ShopsValidator()
    logger.info("=== Done ShopsValidator: convert ===")
    #python ./ChainStore.py
    logger.warning("=== Start Chain Store ===")
    ChainStore()
    logger.info("=== Done Chain Store ===")
    #python ./Git.py
    logger.warning("=== Start GitHub: push ===")
    DateTime = datetime.now().strftime('%Y-%m-%d')
    Diff = GitPush(f"autogenerate Trade Register {DateTime}")
    if Diff:
        logger.debug("git push complete")
        #logger.debug(Diff)
    else:
        logger.error("Git error")
    logger.info("=== Done GitHub: push ===")
    #
    logger.info("Done")
