import sys
import logging

from loguru import logger
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from nominatim_db import cli
from nominatim_db.config import Configuration

from Settings import LOG


NAME_DB = "nominatim";


class InterceptHandler(logging.Handler):
  def emit(self, record):
    try:
      level = logger.level(record.levelname).name
    except ValueError:
      level = record.levelno
    #
    frame, depth = logging.currentframe(), 2
    while frame.f_code.co_filename == logging.__file__:
      frame = frame.f_back
      depth += 1
    #
    logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())



def Generate():
  logger.info("remove Nominatim")
  #
  Postgres = psycopg2.connect(database="postgres")
  Postgres.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
  Cursor = Postgres.cursor();
  # 
  SqlQuery = "SELECT datname FROM pg_database WHERE datistemplate = false;"
  Cursor.execute(SqlQuery)
  logger.info("list of databases before removing: {list}", list=", ".join([Row[0] for Row in Cursor.fetchall()]))
  Cursor.execute(f"DROP DATABASE IF EXISTS {NAME_DB};")
  Cursor.execute(SqlQuery)
  logger.info("list of databases after removing: {list}", list=", ".join([Row[0] for Row in Cursor.fetchall()]))
  #
  logger.info("import Nominatim")
  Config = Configuration(None).get_os_env()
  Config['NOMINATIM_DATABASE_DSN'] = f"pgsql:dbname={NAME_DB}"
  Config['NOMINATIM_LANGUAGES'] = 'ru,be'
  Args = ["import", "--osm-file", "../.data/belarus-latest-internal.osm.pbf"]
  cli.nominatim(cli_args=Args, environ=Config)



# аналаг выканання каманды:
#dropdb nominatim
#nominatim import --osm-file ../.data/belarus-latest-internal.osm.pbf 2>&1 | tee ../.log/nominatim.log
if __name__ == "__main__":
  sys.stdin.reconfigure(encoding="utf-8")
  sys.stdout.reconfigure(encoding="utf-8")
  #
  logger.add(LOG)
  logger.info("Start nominatim db")
  logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
  logger.info("logging -> loguru")
  Generate()
  logger.info("Done nominatim db")
