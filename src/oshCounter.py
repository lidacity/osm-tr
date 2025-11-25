#!.venv/bin/python

#https://github.com/ThomasBarris/osmtagstats

import os
import sys
import time
from operator import itemgetter
from pathlib import Path

import osmium as osm
from jinja2 import Environment, FileSystemLoader
from loguru import logger

from Settings import LOG, DOCS, DATA


# Input handler for full history data
class OSMHistoryHandler(osm.SimpleHandler):
    def __init__(self, OsmTag="*"):
        osm.SimpleHandler.__init__(self)
        self.ProcessedID = set([]) # OSM IDs of objects we already have processed
        self.ProcessedUser = set([]) # OSM user names of users we already have in result list, check against a set is multiple times faster than using a list or dict
        self.ProcessedUserPos = {} # position for each user in UserList of already processed users, faster than check position every time by list iteration
        self.UserList = [] # result list with user name, node count, ways count, relation count
        self.CountNodes = 0 # count number of processed nodes, ways, relations
        self.CountWays = 0
        self.CountRelations = 0
        self.OsmTag = OsmTag

    # callback for nodes, ways and relations
    # count the total per object type and call the function to count given tag per user
    def node(self, n):
        self.CountTags(n, 'n')
        self.CountNodes += 1


    def way(self, n):
        self.CountTags(n, 'w')
        self.CountWays += 1


    def relation(self, n):
        self.CountTags(n, 'r')
        self.CountRelations += 1


    # position of a user in the result list of lists
    def UserInList(self, User, UserList):
        for Num, SubList in enumerate(UserList, start=0):
            if SubList[0] == User:
                return Num
        else:
            return 0


    # count the tags created per user
    def CountTags(self, OsmObject, OsmType):
     Name = f"{OsmType}{OsmObject.id}"
     if Name not in self.ProcessedID:
         if (self.OsmTag in OsmObject.tags) or (self.OsmTag == '*'):
             if OsmObject.user not in self.ProcessedUser:
                 self.UserList.append([OsmObject.user, 0, 0, 0])
                 self.ProcessedUser.add(OsmObject.user)
                 self.ProcessedUserPos.update({OsmObject.user: self.UserInList(OsmObject.user, self.UserList)})
             #
             UserPos = self.ProcessedUserPos[OsmObject.user]
             #
             if OsmType == 'n':
                 self.UserList[UserPos][1] += 1
             elif OsmType == 'w':
                 self.UserList[UserPos][2] += 1
             elif OsmType == 'r':
                 self.UserList[UserPos][3] += 1
             #
             self.ProcessedID.add(Name)


# design & javascript
# https://datatables.net
# header and column labels in_file and tag for introduction text, titles for column titles
def Html(HtmlFile, Tag, InFile, Titles, DataLine, NodeMulti, WayMulti, RelMulti):
    Context = {}
    Context['Tag'] = Tag
    Context['InputFile'] = InFile
    Context['TimeInputFile'] = time.ctime(os.path.getmtime(InFile))
    Context['NodeMulti'] = NodeMulti
    Context['WayMulti'] = WayMulti
    Context['RelMulti'] = RelMulti
    Context['Titles'] = Titles
    Context['DataLine'] = DataLine
    #
    Loader = FileSystemLoader(searchpath="./")
    Env = Environment(loader=Loader)
    Template = Env.get_template("oshCounter.htm")
    Render = Template.render(Context)
    with open(HtmlFile, mode="w", encoding="utf-8") as File:
        File.write(Render)



def Generate():
    InputFile = Path(f"{DATA}/belarus-latest-internal.osm.pbf")
    OutputFile = Path(f"{DOCS}/stat2.html")
    NodeMulti, WayMulti, RelMulti = 3, 2, 1
    MinScore = 25
    OsmTag = "ref:BY:trade_register"

    OshHandler = OSMHistoryHandler(OsmTag=OsmTag)
    OshHandler.apply_file(InputFile, locations=True, idx='sparse_mem_array')

    for Line in OshHandler.UserList:
        Line.append(Line[1] * NodeMulti + Line[2] * WayMulti + Line[3] * RelMulti)
        Line.append(Line[1] + Line[2] + Line[3])

    SortedResult = sorted(OshHandler.UserList, key=itemgetter(4), reverse=True)
 
    Result = []
    for Rank, Line in enumerate(SortedResult, start=1):
        if Line[5] >= MinScore:
            Result.append([Rank, Line[0], Line[1], Line[2], Line[3], Line[4], Line[5]]) 
            logger.info(Line)

    Titles = ['Рэйтынг', 'Карыстальнік', 'Вузлы', 'Лініі', 'Адносіны', 'Балы', 'Колькасць']
    Html(OutputFile, OsmTag, InputFile, Titles, Result, NodeMulti, WayMulti, RelMulti)

    logger.info("##########################")
    logger.info("Апрацавана node: {count:10.2f}", count=OshHandler.CountNodes)
    logger.info("Апрацавана way: {count:10.2f}", count=OshHandler.CountWays)
    logger.info("Апрацавана relation: {count:10.2f}", count=OshHandler.CountRelations)



if __name__ == '__main__':
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    #
    logger.add(LOG)
    logger.info("Start stat2")
    Generate()
    logger.info("Done stat2")
