What is it?
-----------

This is a Scrapy-based web scraper for the California Department of Transportation website. It stores the results in an SQLite3 database. One table holds the text of the status, the other holds records of when each status was seen, when the server claimed it was last updated, etc.

Setup
-----

~~~bash
sqlite3 /path/to/output.db < roadinfo.sql
python3 -m pip -r requirements.txt
~~~
