e-pasluga.by 3.13.06
python ./Geofabrik.py
# https://nominatim.org/
python ./NominatimDB.py
#https://download.geofabrik.de/bz2.html
python ./PBFtoOSM.py
#https://wiki.openstreetmap.org/wiki/User:Breki/Overpass_API_Installation
#https://dev.overpass-api.de/overpass-doc/en/more_info/setup.html
python ./Init_Osm3s.py
# 0->1, один раз в месяц, при чтении нового торгового реестра
python ./TradeRegister.py
# 1->2, "" -> gray
python ./MTD.py
# 2->3, "" gray red orange -> red orange
python ./Nominatim.py
# 3->4, orange -> blue violet
python ./OverpassOrange.py
# 4->5 red orange blue violet | delete
python ./Check.py
#
python ./Stat.py
python ./oshCounter.py
# 5->6, один раз в час, all -> green gold black
python ./OverpassGreen.py
#
python ./Convert.py
python ./ConvertMapillaryBYShopsValidator.py
python ./Git.py


--allow-duplicate-queries=(yes|no)
user ALL=NOPASSWD:/bin/systemctl stop overpass.service,/bin/systemctl start overpass.service,/bin/systemctl status overpass.service
