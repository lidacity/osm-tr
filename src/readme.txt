--allow-duplicate-queries=(yes|no)

sudo visudo
user ALL=NOPASSWD:/bin/systemctl stop overpass.service,/bin/systemctl start overpass.service,/bin/systemctl status overpass.service
