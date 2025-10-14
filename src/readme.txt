	Utils.py
	Git.py
1	TradeRegister.py	1 раз в месяц (при чтении нового торгового реестра)
2	MTD.py			1 раз в месяц	"" -> violet
3	Nominantim.py		1 раз в неделю	"" violet red orange -> red orange
4	OverpassOrange.py	1 раз в неделю	orange -> blue gold
5       Check.py		1 раз в неделю	red orange blue gold violet green black | delete
6	OverpassGreen.py	1 раз в час	red orange blue gold violet -> green black


https://download.geofabrik.de/bz2.html
https://wiki.openstreetmap.org/wiki/User:Breki/Overpass_API_Installation
https://dev.overpass-api.de/overpass-doc/en/more_info/setup.html

osmium cat belarus-250924-internal.osm.pbf -o myfile.osm.bz2
osm-3s_v0.7.62.8/bin/init_osm3s.sh myfile.osm.bz2 osm-3s_v0.7.62.8/db osm-3s_v0.7.62.8
bunzip2 <myfile.osm.bz2 | osm-3s_v0.7.62.8/bin/update_database --db-dir="osm-3s_v0.7.62.8/db/"
./osm-3s_v0.7.62.8/bin/osm3s_query --db-dir=db

nohup osm-3s_v0.7.62.8/bin/dispatcher --osm-base --db-dir=db --meta &
./osm-3s_v0.7.62.8/bin/osm3s_query < my_query > my_query_result

--allow-duplicate-queries=(yes|no)
