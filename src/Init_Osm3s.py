#!.venv/bin/python

import os
import sys

import bz2
import shlex
import shutil
import subprocess

from loguru import logger
from pathlib import Path

from Settings import LOG, DATA


CHUNK_SIZE = 64 * 1024  # 64 KiB


class SystemdService(object):
    '''A systemd service object with methods to check it's activity, and to stop() and start() it.'''

    def __init__(self, Service):
        self.Service = Service


    def IsActive(self):
        """Return True if systemd service is running"""
        try:
            Command = f"sudo /bin/systemctl status {self.Service}.service"
            Completed = subprocess.run(Command, shell=True, check=True, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as Error:
            logger.exception(Error)
        else:
            for Line in Completed.stdout.decode('utf-8').splitlines():
                if 'Active:' in Line:
                    if '(running)' in Line:
                        logger.info(f"{self.Service}: active (running)")
                        return True
        logger.warning(f"{self.Service}: inactive (dead)")
        return False


    def Stop(self):
        ''' Stop systemd service.'''
        try:
            Command = f"sudo /bin/systemctl stop {self.Service}.service"
            Completed = subprocess.run(Command, shell=True, check=True, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as Error:
            logger.exception(Error)
        logger.info(f"{self.Service}: stop")


    def Start(self):
        ''' Start systemd service.'''
        try:
            Command = f"sudo /bin/systemctl start {self.Service}.service"
            Completed = subprocess.run(Command, shell=True, check=True, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as Error:
            logger.exception(Error)
        logger.info(f"{self.Service}: start")



def EnsurePlanetFile(FileName):
    if not FileName.exists():
        logger.error("File {filename} doesn't exist or is not a regular file.", filename=FileName)
        sys.exit(1)
    if FileName.stat().st_size == 0:
        logger.error("File {filename!s} is empty.", filename=FileName)
        sys.exit(1)


def FindUpdateDatabase(PathName):
    Candidate = Path(f"{PathName}/bin/update_database")
    if not Candidate.exists():
        logger.error("Expected update_database at {candidate} but it does not exist.", candidate=Candidate)
        sys.exit(1)
    if shutil.which(Candidate) is None:
        logger.error("File {candidate} is not executable.", candidate=Candidate)
        sys.exit(1)
    return Candidate


def OpenPlanetStream(FileName):
    if FileName.suffix == ".bz2":
        try:
            return bz2.open(FileName, "rb")
        except (OSError, EOFError) as Except:
            logger.exception("Failed to open or decompress {planet_file}: {exc}", planet_file=FileName, exc=Except)
            sys.exit(1)
    else:
        try:
            return open(FileName, "rb")
        except OSError as Except:
            logger.exception("Failed to open {planet_file!s}: {exc}", planet_file=FileName, exc=Except)
            sys.exit(1)


def RunUpdateDatabase(UpdateBin, DB, MetaFlag, CompressionStr, PlanetStream):
    # Build command
    Command = [str(UpdateBin), f"--db-dir={DB}"]
    if MetaFlag:
        Command.append("--meta")
    # compression_str may contain multiple tokens (e.g. "--something val"), so split safely:
    if CompressionStr:
        Command.extend(shlex.split(CompressionStr))
    #
    logger.info("Running: {cmd}", cmd=' '.join(shlex.quote(x) for x in Command))
    # Start the process with stdin pipe and forward decompressed data into it.
    try:
        Proc = subprocess.Popen(Command, stdin=subprocess.PIPE)
    except OSError as Except:
        logger.exception("Failed to start {update_bin}: {exc}", update_bin=UpdateBin, exc=Except)
        sys.exit(1)
    #
    try:
        while True:
            Chunk = PlanetStream.read(CHUNK_SIZE)
            if not Chunk:
                break
            try:
                Proc.stdin.write(Chunk)
            except BrokenPipeError:
                # update_database closed stdin early; exit loop and wait for process termination
                logger.exception("update_database closed stdin (BrokenPipe).")
                break
        # close the stdin to indicate EOF
        Proc.stdin.close()
        RC = Proc.wait()
        if RC != 0:
            logger.error("update_database exited with return code {rc}.", rc=RC)
            sys.exit(rc)
    except KeyboardInterrupt:
        logger.exception("Interrupted by user. Terminating update_database.")
        Proc.terminate()
        Proc.wait()
        sys.exit(1)
    finally:
        try:
            PlanetStream.close()
        except Exception:
            pass


def Delete(PathName, Mask):
    for FileName in Path(PathName).glob(Mask):
        FileName.unlink()


def Clear(DB):
    logger.info("clear")
    Delete(DB, "osm3s*")
    Delete(DB, "*.bin.idx")
    Delete(DB, "*.bin")
    Delete(DB, "*.map.idx")
    Delete(DB, "*.map")



# Decompress a planet file and pipe it to update_database.
# PlanetFile - path to the compressed planet file (including .bz2)
# DB - directory where the database should go
# Exec - directory that contains the executable update_database (bin/update_database)
# Meta - store_true - add this flag if you want to use meta data (passed through to update_database)
# Compression - "" - optional extra compression/flag string to append to update_database (can include multiple tokens).
def Generate(PlanetFile, DB, Exec, Meta=True, Compression=""):
    logger.info("init_osm3s.sh")
    EnsurePlanetFile(PlanetFile)
    DB.mkdir(parents=True, exist_ok=True)
    UpdateBin = FindUpdateDatabase(Exec)
    PlanetStream = OpenPlanetStream(PlanetFile)
    RunUpdateDatabase(UpdateBin, DB, Meta, Compression, PlanetStream)



#sudo systemctl stop overpass
#rm ../.overpass/osm3s_osm_base
#rm ../.overpass/*.bin.idx
#rm ../.overpass/*.bin
#rm ../.overpass/*.map.idx
#rm ../.overpass/*.map
#~/osm-3s/bin/init_osm3s.sh ../.data/belarus-latest-internal.osm.bz2 ../../db ~/osm-3s
#sudo systemctl start overpass
if __name__ == "__main__":
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    #
    logger.add(LOG)
    logger.info("Start init_osm3s.sh")
    #
    Monitor = SystemdService("overpass")
    PlanetFile = Path(f"{DATA}/belarus-latest-internal.osm.bz2")
    DB = Path("~/db/").expanduser() # ensure trailing slash like original
    Exec = Path("~/osm-3s").expanduser()
    #
    if Monitor.IsActive():
     Monitor.Stop()
    Clear(DB)
    Generate(PlanetFile, DB, Exec)
    Monitor.Start()
    Monitor.IsActive()
    logger.info("Done init_osm3s.sh")
