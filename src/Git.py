#!.venv/bin/python

import os
import sys
from datetime import datetime
from pathlib import Path

from loguru import logger
import git

from Settings import LOG


#https://behai-nguyen.github.io/2022/06/25/synology-dsm-python.html
#https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
def GitPush(Message):
    try:
        PathName = Path("..") #os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
        Repo = git.Repo(PathName)
        Repo.git.add("docs")
        #Repo.git.add(update=True)
        Repo.index.commit(Message)
        Origin = Repo.remote(name='origin')
        Origin.push()
        return Repo.git.diff('HEAD~1')
    except:
        logger.exception('Some error occured while pushing the code')
    return None


if __name__ == "__main__":
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    logger.add(LOG)
    logger.info("Start git")
    Diff = GitPush(f"autogenerate tr {datetime.now().strftime('%Y-%m-%d')}")
    if Diff:
        pass #logger.info("git push complete:\n{diff}", diff=Diff)
    else:
        logger.error("Git error")
    logger.info("Done git")
