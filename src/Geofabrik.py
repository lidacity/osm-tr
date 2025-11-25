import os
import sys
import hashlib
import json
import re
from pathlib import Path

import requests
from loguru import logger
from dateutil.parser import parse as parsedate

from Settings import LOG, DOCS, DATA
from Utils import SetDate



def Generate(URL="https://osm-internal.download.geofabrik.de/europe/belarus-latest-internal.osm.pbf", URLState="https://osm-internal.download.geofabrik.de/europe/belarus-updates/state.txt"):
 #URL="https://download.geofabrik.de/europe/belarus-latest.osm.pbf"
 #URL="https://osm-internal.download.geofabrik.de/europe/belarus-latest-internal.osm.pbf"
 #URL="http://osmosis.svimik.com/latest/BY.osm.pbf"
 Headers = {"User-agent": "https://osm-tr.lidacity.by/"}
 #
 URLMD5 = f"{URL}.md5"
 StateFileName = Path(f"{DATA}/belarus-latest-internal.state.txt")
 FileName = Path(f"{DATA}/belarus-latest-internal.osm.pbf")
 FileNameMD5 = Path(f"{DATA}/belarus-latest-internal.osm.pbf.md5")
 PasswordFile = Path(f"{DATA}/.passwd")
 #
 Cookie = GetCookie(PasswordFile, Headers)
 Download(URLState, StateFileName, Cookie, Headers)
 Download(URL, FileName, Cookie, Headers)
 Download(URLMD5, FileNameMD5, Cookie, Headers)
 CheckMD5(FileName, FileNameMD5)
 return ReadState(StateFileName).isoformat()



def GetCookieToken(CookieText):
 Pattern = r"(?<=gf_download_oauth=).*?(?=; )"
 Result = re.findall(Pattern, CookieText)
 if Result is None:
  logger.error("Could not find the gf_download_oauth in the cookie.")
 try:
  return {'gf_download_oauth': Result[0]}
 except IndexError:
  logger.exception("Cookie not found")


def FindAuthenticityToken(Response):
 Pattern = r"name=\"csrf-token\" content=\"([^\"]+)\""
 Result = re.search(Pattern, Response)
 if Result is None:
  logger.error("Could not find the authenticity_token in the website to be scraped.")
 try:
  return Result.group(1)
 except IndexError:
  logger.exception("The login form does not contain an authenticity_token.")


#https://github.com/geofabrik/sendfile_osm_oauth_protector/blob/master/oauth_cookie_client.py
def GetCookie(Auth, Header, ConsumerUrl="https://osm-internal.download.geofabrik.de/get_cookie", OSMHost="https://www.openstreetmap.org"):
 Insecure = True
 Format = "http"
 with open(Auth, "r") as File:
  PassLine = next(File).strip()
  UserName, Password = PassLine.strip().split(":")
 #
 # get request token
 Params = {'action': "get_authorization_url"}
 Data = {}
 Requests = requests.post(ConsumerUrl, params=Params, data=Data, headers=Header, verify=Insecure)
 if Requests.status_code != 200:
  logger.error("POST {url}, received HTTP status code {status_code} but expected 200", url=ConsumerUrl, status_code=Requests.status_code)
 JsonResponse = json.loads(Requests.text)
 try:
  AuthorizationUrl = JsonResponse['authorization_url']
  State = JsonResponse['state']
  RedirectUri = JsonResponse['redirect_uri']
  ClientID = JsonResponse['client_id']
 except KeyError:
  logger.exception("oauth_token was not found in the first response by the consumer")
 # get OSM session
 Params = {'cookie_test': "true"}
 Session = requests.Session()
 Requests = Session.get(OSMHost, params=Params, headers=Header)
 if Requests.status_code != 200:
  logger.error("GET {url}, received HTTP code {status_code}", url=OSMHost, status_code=Requests.status_code)
 # login
 AuthenticityToken = FindAuthenticityToken(Requests.text)
 Data = {'username': UserName, 'password': Password, 'referer': "/", 'commit': "Login", 'authenticity_token': AuthenticityToken}
 Requests = Session.post(f"{OSMHost}/login", data=Data, allow_redirects=False, headers=Header)
 if Requests.status_code != 302:
  logger.error("POST {url}, received HTTP code {status_code} but expected 302", url=f"{OSMHost}/login", status_code=Requests.status_code)
 logger.debug(f"{Requests.request.url} -> {Requests.headers['location']}")
 # authorize
 Requests = Session.get(AuthorizationUrl, headers=Header, allow_redirects=False)
 if Requests.status_code != 302:
  # If authorization has been granted to the OAuth client yet, we will receive status 302. If not, status 200 should be returned and the form needs to be submitted.
  if Requests.status_code != 200:
   logger.error("GET {url}, received HTTP code {status_code} but expected 200", url=AuthorizationUrl, status_code=Requests.status_code)
  AuthenticityToken = FindAuthenticityToken(Requests.text)
  #
  PostData = {'client_id': ClientID, 'redirect_uri': RedirectUri, 'authenticity_token': AuthenticityToken, 'state': State, 'response_type': "code", 'scope': "read_prefs", 'nonce': "", 'code_challenge': "", 'code_challenge_method': "", 'commit': "Authorize"}
  Requests = Session.post(AuthorizationUrl, data=PostData, headers=Header, allow_redirects=False)
  if Requests.status_code != 302:
   logger.error("POST {url}, received HTTP code {status_code} but expected 302", url=AuthorizationUrl, status_code=Requests.status_code)
 else:
  logger.debug(f"{Requests.request.url} -> {Requests.headers['location']}")
 try:
  Location = Requests.headers["location"]
 except KeyError:
  logger.exception("Response headers of authorization request did not contain a location header.")
 if "?" not in Location:
  logger.error("Redirect URL after authorization misses query string.")
 # logout
 Requests = Session.get(f"{OSMHost}/logout", headers=Header)
 if Requests.status_code != 200 and Requests.status_code != 302:
  logger.error("POST {url}, received HTTP code {status_code} but expected 200 or 302", url=f"{OSMHost}/logout", status_code=Requests.status_code)
 # get final cookie
 Params = {'format': Format}
 Requests = requests.get(Location, params=Params, headers=Header, verify=Insecure)
 #
 CookieText = Requests.text
 if not CookieText.endswith("\n"):
  CookieText += "\n"
 Result = GetCookieToken(CookieText)
 return Result


def Download(URL, FileName, Cookie, Headers):
 logger.info("Download {url}", url=URL)
 Requests = requests.get(URL, headers=Headers, stream=True, cookies=Cookie)
 with open(FileName, 'wb') as File:
  for Buffer in Requests.iter_content(chunk_size=65536):
   File.write(Buffer)
 logger.info("Downloaded {url}; size = {header}", url=URL, header=Requests.headers['Content-Length'])
 Requests.close()


def md5(FileName):
 Result = hashlib.md5()
 with open(FileName, "rb") as File:
  for Chunk in iter(lambda: File.read(4096), b""):
   Result.update(Chunk)
 return Result.hexdigest()


def CheckMD5(FileName, FileNameMD5):
 logger.info("check md5")
 Result = ""
 for Line in open(FileNameMD5, "r"):
  MD5, Name = Line.strip().split()
  if Name == FileName.name:
   Result = md5(FileName)
   if MD5 == Result:
    logger.info("md5 Ok")
    return True
 logger.error("md5 failed: '{MD5}' != '{Result}'", MD5=MD5, Result=Result)
 return False


def ReadState(FileName):
 Key = 'timestamp'
 for Line in open(FileName, "r"):
  if Line[:len(Key)] == Key:
   _, Value = Line.replace("\\", "").split("=")
   return parsedate(Value)



if __name__ == "__main__":
 sys.stdin.reconfigure(encoding="utf-8")
 sys.stdout.reconfigure(encoding="utf-8")
 #
 logger.add(LOG)
 logger.info("Start downloading pbf")
 Date = Generate()
 SetDate(f"{DOCS}/tr.date.js", 'Geofabrik', Date)
 logger.info("Done downloading pbf")
