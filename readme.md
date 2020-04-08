# Convert IP2Location Lite database to Maxmind MMDB database

This simple script will help you to convert IP2Location Lite CSV database to Maxmind MMDB database. You can get the free IP2Location Lite database from here: https://lite.ip2location.com/ip2location-lite.

## Requirements

1. Python 3.5 or above.
2. IP2Location Lite DB1 or DB11 database.

## Steps

1. Download free IP2Location Lite DB1 or DB11 database from https://lite.ip2location.com/ip2location-lite.

   Note: Download the database with **CSV** only.

2. After you have download this repository, open you terminal and type `'python convert.py <database_name>'` or `'python convert.py <database_name>'` for those who have Python 2 and 3 installed.

3. Now you can use Maxmind reader library to read the MMDB database.

