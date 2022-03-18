CREATE USER urlmgr WITH ENCRYPTED PASSWORD 'url@1234';
GRANT CONNECT ON DATABASE "malware-urls" TO urlmgr;
GRANT pg_read_all_data TO urlmgr;
GRANT pg_write_all_data TO urlmgr;

CREATE TABLE IF NOT EXISTS hosts (
    id SERIAL PRIMARY KEY,
    host VARCHAR(261) NOT NULL
);
CREATE UNIQUE INDEX idx_hosts_host ON hosts(host);

CREATE TABLE IF NOT EXISTS paths (
    id SERIAL PRIMARY KEY,
    hosts_id SERIAL,
    "url" VARCHAR(5000),
    is_safe BOOLEAN NOT NULL,
    FOREIGN KEY (hosts_id) REFERENCES hosts(id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX idx_paths_host_url ON paths(hosts_id, "url");

-- Sample Data
INSERT INTO hosts (host) VALUES ('facebook.com');
INSERT INTO hosts (host) VALUES ('google.com:5000');
INSERT INTO paths (hosts_id, "url", is_safe) VALUES ((SELECT id FROM hosts WHERE host = 'facebook.com'), 'api/v1/test', TRUE);
INSERT INTO paths (hosts_id, "url", is_safe) VALUES ((SELECT id FROM hosts WHERE host = 'facebook.com'), 'api/v1/test2', FALSE);
INSERT INTO paths (hosts_id, "url", is_safe) VALUES ((SELECT id FROM hosts WHERE host = 'google.com:5000'), 'api/v1/test', FALSE);
INSERT INTO paths (hosts_id, "url", is_safe) VALUES ((SELECT id FROM hosts WHERE host = 'google.com:5000'), 'api/v1/test2', FALSE);
INSERT INTO paths (hosts_id, "url", is_safe) VALUES ((SELECT id FROM hosts WHERE host = 'google.com:5000'), 'api/v1/test3', TRUE);
