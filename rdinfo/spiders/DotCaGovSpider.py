# -*- coding: utf-8 -*-
import os
import logging
import scrapy
import sqlite3
import sys
import time
from hashlib import sha256
from scrapy import Request


class DotCaGovSpider(scrapy.Spider):
    name = "DotCaGovSpider"
    version = "0.0.1"
    allowed_domains = ["dot.ca.gov"]
    base_url = "http://www.dot.ca.gov/hq/roadinfo/"
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings)

    def __init__(self, settings):
        # Silence log messages we don't care about
        logging.getLogger("scrapy.middleware").setLevel(logging.WARNING)
        logging.getLogger("scrapy.statscollectors").setLevel(logging.WARNING)
        
        # Load sqlite DB from settings
        db_path = settings.get("SQLITE_DB", None)
        if db_path is None:
            self.logger.fatal("Please configure 'SQLITE_DB' before running this spider.")
            sys.exit(1)
        if not os.path.exists(db_path):
            self.logger.fatal(f"Unable to locate SQLITE_DB at '{db_path}'")
            sys.exit(1)
        self.conn = sqlite3.connect(db_path)

    def start_requests(self):
        self.logger.info(f"Starting {self.name} v{self.version}...")
        for road in ("sr88", "sr89", "us50", "i80", "sr267"):
            self.logger.debug(f"Scraping {road}")
            yield Request(self.base_url + road, meta={"road":road})

    def parse(self, response):
        status_txt = response.body
        road = response.meta["road"]
        self.logger.debug(f"Received response for {road}: {status_txt}")
        if response.status != 200:
            self.logger.error(f"Received HTTP Status {response.status} for road {road}")
            return
        status_id = self.get_or_insert_status(status_txt)
        try:
            last_modified_str = response.headers["Last-Modified"].decode("utf8")
            last_modified = time.strftime("%s", time.strptime(last_modified_str, "%a, %d %b %Y %H:%M:%S %Z"))
        except KeyError:
            last_modified = 0
        self.insert_roadinfo(road, status_id, last_modified)

    def insert_status(self, status_sha256, status_txt, cursor=None):
        if cursor is None:
            cursor = self.conn.cursor()
        self.logger.debug("Inserting new status")
        cursor.execute("INSERT INTO status (sha2_hash, text) VALUES (?, ?)", (status_sha256, status_txt))
        # return the rowID of the row we just inserted
        self.conn.commit()
        return cursor.lastrowid

    def get_or_insert_status(self, status_txt, cursor=None):
        status_sha256 = sha256(status_txt).hexdigest()
        if cursor is None:
            cursor = self.conn.cursor()
        self.logger.debug("Checking for existing status")
        existing_status = cursor.execute("SELECT * FROM status WHERE sha2_hash=?", (status_sha256,)).fetchone()
        if existing_status is None:
            self.logger.debug("New status found.")
            return self.insert_status(status_sha256, status_txt, cursor=cursor)
        else:
            self.logger.debug("Existing status found: " + str(existing_status[0]))
            return existing_status[0]
    
    def insert_roadinfo(self, road_name, status_id, last_modified, cursor=None):
        if cursor is None:
            cursor = self.conn.cursor()
        self.logger.debug("Inserting new roadinfo")
        cursor.execute("INSERT INTO roadinfo (road_name, status_id, last_modified) VALUES (?, ?, ?)", (road_name, status_id, last_modified))
        self.conn.commit()
        self.logger.debug("Finished inserting new roadinfo " + str(cursor.lastrowid))

