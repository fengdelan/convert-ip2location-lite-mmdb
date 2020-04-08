# Convert IP2Location LITE database to Maxmind MMDB database

This simple script will help you to convert IP2Location LITE CSV database to Maxmind MMDB database. You can get the free IP2Location LITE database from here: https://lite.ip2location.com/ip2location-lite.

## Requirements

1. Python 3.5 or above.
2. IP2Location LITE DB1 or DB11 database.

## Steps

1. Download free IP2Location LITE DB1 or DB11 database from https://lite.ip2location.com/ip2location-lite.

   Note: Download the database with **CSV** only.

2. After you have download this repository, open you terminal and type `'python convert.py <database_name>'` or `'python3 convert.py <database_name>'` for those who have Python 2 and 3 installed.

3. Now you can use Maxmind reader library to read the MMDB database.

## Disclaimer

IP2Location and Maxmind are trademarks of respective owners. This Python script is a project inspired by Perl script https://github.com/antonvlad999/convert-ip2location-geolite2