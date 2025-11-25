import os
import sys

from haversine import haversine, Unit
from fake_useragent import UserAgent


Browser = UserAgent()
Headers = {
 'user-agent': Browser.random,
}


def GetCoord(Lat, Lon, Ref, Elements):
 if Ref:
  for Index, Item in enumerate(Elements):
   if 'ref:shop' in Item:
    if Item['ref:shop'] == Ref:
     return Elements.pop(Index)
 #
 Length, Index = sys.maxsize, -1
 for i, Item in enumerate(Elements):
  Lat2, Lon2 = Item['lat'], Item['lon']
  Length1 = haversine((Lat, Lon), (Lat2, Lon2), unit=Unit.METERS)
  if Length > Length1:
   Index, Length, Result = i, Length1, Item
 #
 if Length == sys.maxsize:
  return None
 elif Length < 500:
  return Elements.pop(Index)
 else:
  return None


def Check(Store, Shop):
 Tags = Store['tags']
 if 'ref:BY:trade_register' not in Tags:
  return False
 elif 'ref:vatin' not in Tags:
  return False
 elif Tags['shop'] != Shop['shop']:
  return False
 elif Tags['name:ru'] != Shop['name:ru']:
  return False
 elif Tags['name:be'] != Shop['name:be']:
  return False
 elif Tags.get('brand', "") != Shop['brand']:
  return False
 elif Tags.get('brand:wikidata', "") != Shop['brand:wikidata']:
  return False
 elif Tags.get('operator', "") != Shop['operator']:
  return False
 elif Tags.get('operator:wikidata', "") != Shop['operator:wikidata']:
  return False
 else:
  return True


def GetItemsWithVATin(Info, TR):
 Refs = [ Value['ref:vatin'] for _, Value in Info.items() if 'ref:vatin' in Value ]
 #
 Result = {}
 for Item in TR['features']:
  if 'id' in Item:
   Properties = Item['properties']
   if 'ref:vatin' in Properties:
    if Properties['ref:vatin'] in Refs:
     ID = Item['id']
     Result[ID] = Properties['ref:BY:trade_register']
 return Result
