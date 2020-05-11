DROP TABLE IF EXISTS group_hosts;
DROP TABLE IF EXISTS hosts;
DROP TABLE IF EXISTS groups;

--groups table
CREATE SEQUENCE groups_id_seq as INTEGER;
CREATE TABLE IF NOT EXISTS groups
(
    id INTEGER PRIMARY KEY DEFAULT nextval('groups_id_seq'),
    parent_id INTEGER REFERENCES groups (id) DEFAULT NULL,
    name varchar(255) NOT NULL unique,
    vars JSONB default '{}'
);
ALTER SEQUENCE groups_id_seq OWNED BY groups.id;

--hosts table
CREATE SEQUENCE hosts_id_seq as INTEGER;
CREATE TABLE IF NOT EXISTS hosts
(
    id INTEGER PRIMARY KEY DEFAULT nextval('hosts_id_seq'),
    name varchar(255) NOT NULL unique,
    vars JSONB default '{}'
);
ALTER SEQUENCE hosts_id_seq OWNED BY hosts.id;

--group hosts table
CREATE TABLE group_hosts
(
    group_id INTEGER REFERENCES groups(id) ON DELETE CASCADE,
    host_id INTEGER REFERENCES hosts(id) ON DELETE CASCADE,
    PRIMARY KEY (group_id, host_id)
);
