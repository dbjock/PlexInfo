--
-- File generated with SQLiteStudio v3.2.1 on Fri Sep 4 12:20:18 2020
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: t_keyvals
CREATE TABLE t_keyvals (
    srckey_id  REFERENCES t_srckeys (ID) ON DELETE CASCADE
                                         ON UPDATE CASCADE,
    s_key      NOT NULL,
    s_value
);


-- Table: t_srckeys
CREATE TABLE t_srckeys (
    ID       PRIMARY KEY
             NOT NULL,
    server,
    library,
    fileobj
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
