CREATE TABLE if not exists status (
	status_id INTEGER PRIMARY KEY,
	sha2_hash VARCHAR(64),
    first_added_date INTEGER(4) NOT NULL DEFAULT (strftime('%s', 'now')),
	text TEXT NOT NULL
);

CREATE TABLE if not exists roadinfo (
	roadinfo_id INTEGER PRIMARY KEY,
	road_name VARCHAR(32) NOT NULL,
	crawl_date INTEGER(4) NOT NULL DEFAULT (strftime('%s', 'now')),
	last_modified INTEGER(4) NOT NULL DEFAULT (0),
	status_id VARCHAR(64) NOT NULL,
    CONSTRAINT fk_status_id
		FOREIGN KEY (status_id)
		REFERENCES status (status_id)
);
