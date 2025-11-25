#!.venv/bin/python

import os
import sys

from loguru import logger
from pathlib import Path
from osmium import SimpleWriter, FileProcessor

from Settings import LOG, DATA



def Generate():
    InputFile =Path(f"{DATA}/belarus-latest-internal.osm.pbf")
    OutputFile = Path(f"{DATA}/belarus-latest-internal.osm.bz2")
    if OutputFile.exists():
        OutputFile.unlink()
    with SimpleWriter(OutputFile) as Writer:
        for Obj in FileProcessor(InputFile):
            if Obj.is_node():
                Writer.add_node(Obj)
            elif Obj.is_way():
                Writer.add_way(Obj)
            elif Obj.is_relation():
                Writer.add_relation(Obj)



# аналаг выканання каманды:
#osmium cat ../.data/belarus-latest-internal.osm.pbf -o ../.data/belarus-latest-internal.osm.bz2 --overwrite
if __name__ == "__main__":
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    #
    logger.add(LOG)
    logger.info("Start convert .pbf to .osm.bz2")
    Generate()
    logger.info("Done convert .pbf to .osm.bz2")
