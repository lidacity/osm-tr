import os
import sys
import hashlib
import json
import re

import requests
from urllib.parse import urlencode
from datetime import datetime
#from dateutil.parser import parse as parsedate

from loguru import logger


sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')



class PBF:
 def __init__(self, URL="https://osm-internal.download.geofabrik.de/europe/belarus-latest-internal.osm.pbf", State="https://osm-internal.download.geofabrik.de/europe/belarus-updates/state.txt", Download=True):
  #URL="https://download.geofabrik.de/europe/belarus-latest.osm.pbf"
  #URL="https://osm-internal.download.geofabrik.de/europe/belarus-latest-internal.osm.pbf"
  #URL="http://osmosis.svimik.com/latest/BY.osm.pbf"
  self.Cookie = {}
  self.DateTime = None
  self.UserAgent = {"User-agent": "https://osm-tr.lidacity.by/"}
  self.StateFileName = os.path.join("..", ".data", "belarus-latest-internal.state.txt")
  self.FileName = os.path.join("..", ".data", "belarus-latest-internal.osm.pbf")
  if Download:
   PasswordFile = {'Type': "PasswordFile", 'FileName': os.path.join("..", ".data", ".passwd")}
   self.Cookie = self.GetCookie(Auth=PasswordFile, Header=self.UserAgent)
   #print(self.Cookie)
   self.Download(State, self.StateFileName)
   #
   self.Download(URL, self.FileName)
   self.CheckMD5(URL, self.FileName)


 def GetDateTime(self):
  return self.DateTime


 def GetCookieToken(self, CookieText):
  Pattern = r"(?<=gf_download_oauth=).*?(?=; )"
  Result = re.findall(Pattern, CookieText)
  if Result is None:
   logger.error(f"Could not find the gf_download_oauth in the cookie.")
  try:
   return {'gf_download_oauth': Result[0]}
  except IndexError:
   logger.error(f"Cookie not found")


 def FindAuthenticityToken(self, Response):
  Pattern = r"name=\"csrf-token\" content=\"([^\"]+)\""
  Result = re.search(Pattern, Response)
  if Result is None:
   logger.error(f"Could not find the authenticity_token in the website to be scraped.")
  try:
   return Result.group(1)
  except IndexError:
   logger.error(f"The login form does not contain an authenticity_token.")


 #https://github.com/geofabrik/sendfile_osm_oauth_protector/blob/master/oauth_cookie_client.py
 def GetCookie(self, ConsumerUrl="https://osm-internal.download.geofabrik.de/get_cookie", Auth=None, OSMHost="https://www.openstreetmap.org", Header={}):
  if Auth:
   Insecure = True
   Format = "http"
   match Auth['Type']:
    case "HTTPBasic":
     #HTTPBasic = {'UserName': "<username>", 'Password': "<password>", )
     UserName, Password = Auth['UserName'], Auth['Password']
    case "PasswordFile":
     #PasswordFile = {'FileName': "<filename>", )
     #PasswordFile = {'FileName': "<filename>", 'UserName': "<username>", )
     if 'UserName' in Auth:
      UserName = Auth['UserName']
     else:
      with open(Auth['FileName'], "r") as File:
       PassLine = next(File).strip()
      UserName = PassLine.split(":")[0].strip()
     for Line in open(Auth['FileName'], "r"):
      Line = Line.strip().split(":", 1)
      if Line[0] == UserName:
       Password = Line[1]
       break
     else:
      Password = ""
    case _:
     return {}
  else:
   logger.error(f"No OSM auth!")
  #
  # get request token
  Json = {'action': "get_authorization_url"}
  Arg = urlencode(Json)
  Url = f"{ConsumerUrl}?{Arg}"
  Data = {}
  Requests = requests.post(Url, data=Data, headers=Header, verify=Insecure)
  if Requests.status_code != 200:
   logger.error(f"POST {Url}, received HTTP status code {Requests.status_code} but expected 200")
  JsonResponse = json.loads(Requests.text)
  AuthorizationUrl = None
  State = None
  RedirectUri = None
  ClientID = None
  try:
   AuthorizationUrl = JsonResponse['authorization_url']
   State = JsonResponse['state']
   RedirectUri = JsonResponse['redirect_uri']
   ClientID = JsonResponse['client_id']
  except KeyError:
   logger.error(f"oauth_token was not found in the first response by the consumer")
  # get OSM session
  Json = {'cookie_test': "true"}
  Arg = urlencode(Json)
  LoginUrl = f"{OSMHost}/login?{Arg}"
  Session = requests.Session()
  Requests = Session.get(LoginUrl, headers=Header)
  if Requests.status_code != 200:
   logger.error(f"GET {LoginUrl}, received HTTP code {Requests.status_code}")
  # login
  AuthenticityToken = self.FindAuthenticityToken(Requests.text)
  LoginUrl = f"{OSMHost}/login"
  Data = {'username': UserName, 'password': Password, 'referer': "/", 'commit': "Login", 'authenticity_token': AuthenticityToken}
  Requests = Session.post(LoginUrl, data=Data, allow_redirects=False, headers=Header)
  if Requests.status_code != 302:
   logger.error(f"POST {LoginUrl}, received HTTP code {Requests.status_code} but expected 302")
  logger.debug(f"{Requests.request.url} -> {Requests.headers['location']}")
  # authorize
  Requests = Session.get(AuthorizationUrl, headers=Header, allow_redirects=False)
  if Requests.status_code != 302:
   # If authorization has been granted to the OAuth client yet, we will receive status 302. If not, status 200 should be returned and the form needs to be submitted.
   if Requests.status_code != 200:
    logger.error(f"GET {AuthorizationUrl}, received HTTP code {Requests.status_code} but expected 200")
   AuthenticityToken = self.FindAuthenticityToken(Requests.text)
   #
   PostData = {'client_id': ClientID, 'redirect_uri': RedirectUri, 'authenticity_token': AuthenticityToken, 'state': State, 'response_type': "code", 'scope': "read_prefs", 'nonce': "", 'code_challenge': "", 'code_challenge_method': "", 'commit': "Authorize"}
   Requests = Session.post(AuthorizationUrl, data=PostData, headers=Header, allow_redirects=False)
   if Requests.status_code != 302:
    logger.error(f"POST {AuthorizationUrl}, received HTTP code {Requests.status_code} but expected 302")
  else:
   logger.debug(f"{Requests.request.url} -> {Requests.headers['location']}")
  Location = None
  try:
   Location = Requests.headers["location"]
  except KeyError:
   logger.error(f"Response headers of authorization request did not contain a location header.")
  if "?" not in Location:
   logger.error(f"Redirect URL after authorization misses query string.")
  # logout
  LogoutUrl = f"{OSMHost}/logout"
  Requests = Session.get(LogoutUrl, headers=Header)
  if Requests.status_code != 200 and Requests.status_code != 302:
   logger.error(f"POST {LogoutUrl}, received HTTP code {Requests.status_code} but expected 200 or 302")
  # get final cookie
  Json = {'format': Format}
  Arg = urlencode(Json)
  Url = f"{Location}&{Arg}"
  Requests = requests.get(Url, headers=Header, verify=Insecure)
  #
  CookieText = Requests.text
  if not CookieText.endswith("\n"):
   CookieText += "\n"
  Result = self.GetCookieToken(CookieText)
  return Result


 def Download(self, URL, FileName):
  #logger.info(f"Check {FileName}")
  Requests = requests.head(URL, headers=self.UserAgent, cookies=self.Cookie)
  #print(Requests.headers)
  if not self.DateTime:
   self.DateTime = parsedate(Requests.headers['Last-Modified'])
  #
  if os.path.isfile(FileName):
   Result = datetime.fromtimestamp(os.path.getmtime(FileName)).astimezone() < self.DateTime
   if Result:
    os.remove(FileName)
  else:
   Result = True
  #
  if Result:
   logger.info(f"Download {URL}")
   Requests = requests.get(URL, headers=self.UserAgent, stream=True, cookies=self.Cookie)
   with open(FileName, 'wb') as File:
    for Buffer in Requests.iter_content(chunk_size=65536):
     File.write(Buffer)
   logger.info(f"Downloaded {URL}; size = {Requests.headers['Content-Length']}")
  #else:
  # logger.info(f"Skip download {URL}")
  Requests.close()
  return Result


 def md5(self, FileName):
  Result = hashlib.md5()
  with open(FileName, "rb") as File:
   for Chunk in iter(lambda: File.read(4096), b""):
    Result.update(Chunk)
  return Result.hexdigest()


 def CheckMD5(self, URL, FileName):
  self.Download(URL + ".md5", FileName + ".md5")
  logger.info(f"check md5")
  Result = ""
  for Line in open(FileName + ".md5", "r"):
   MD5, Name = Line.split()
   if Name == FileName[-len(Name):]:
    Result = self.md5(FileName)
    if MD5 == Result:
     logger.info(f"md5 Ok")
     return True
  logger.error(f"md5 failed: \"{MD5}\" != \"{Result}\"")
  return False


 def ReadState(self):
  Key = 'timestamp'
  for Line in open(self.StateFileName, "r"):
   if Line[:len(Key)] == Key:
    _, Value = Line.replace("\\", "").split("=")
    return Value.strip()
    #return parsedate(Value)
