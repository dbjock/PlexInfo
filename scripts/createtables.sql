--
-- File generated with SQLiteStudio v3.2.1 on Sat Sep 5 16:25:22 2020
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: t_libvals
CREATE TABLE t_libvals (
    srckey_id  REFERENCES t_libkeys (ID) ON DELETE CASCADE
                                         ON UPDATE CASCADE,
    s_value
);


-- Table: t_libkeys
CREATE TABLE t_libkeys (
    ID       INTEGER PRIMARY KEY AUTOINCREMENT
                     NOT NULL,
    server           NOT NULL,
    library          NOT NULL,
    filePath         NOT NULL,
    sKey             NOT NULL,
    uKey             NOT NULL
);


-- View: v_lib_AllKeys
CREATE VIEW v_lib_AllKeys AS
    SELECT uKey,
           library,
           filePath,
           sKey
      FROM t_libkeys AS k
     GROUP BY uKey
     ORDER BY filePath;


-- View: v_lib_DiffResults
CREATE VIEW v_lib_DiffResults AS
    SELECT library,
           filePath,
           skey,
           server1_val,
           server2_val,
           CASE WHEN server1_val = server2_val THEN '' ELSE '***Different***' END AS isDiff
      FROM v_lib_AllKeys
           LEFT JOIN
           v_lib_server1_2ALL ON v_lib_ALLKeys.ukey = v_lib_server1_2ALL.uKey
           LEFT JOIN
           v_lib_server2_2ALL ON v_lib_ALLKeys.ukey = v_lib_server2_2ALL.uKey
     ORDER BY library,
              filePath,
              skey;


-- View: v_lib_server1
CREATE VIEW v_lib_server1 AS
    SELECT uKey,
           library,
           filePath,
           sKey,
           s_value
      FROM t_libkeys AS k
           JOIN
           t_libvals AS v ON k.ID = v.srckey_id
     WHERE upper(k.server) = 'SERVER1';


-- View: v_lib_server1_2ALL
CREATE VIEW v_lib_server1_2ALL AS
    SELECT v_lib_AllKeys.uKey,
           CASE WHEN v_lib_server1.ukey IS NULL THEN '--Value missing--' WHEN s_value IS NULL THEN '--NULL VALUE--' ELSE s_value END AS server1_VAL
      FROM v_lib_AllKeys
           LEFT JOIN
           v_lib_server1 ON v_lib_AllKeys.uKey = v_lib_server1.ukey;


-- View: v_lib_server2
CREATE VIEW v_lib_server2 AS
    SELECT uKey,
           library,
           filePath,
           sKey,
           s_value
      FROM t_libkeys AS k
           JOIN
           t_libvals AS v ON k.ID = v.srckey_id
     WHERE upper(k.server) = 'SERVER2';


-- View: v_lib_server2_2ALL
CREATE VIEW v_lib_server2_2ALL AS
    SELECT v_lib_AllKeys.uKey,
           CASE WHEN v_lib_server2.ukey IS NULL THEN '--Value missing--' WHEN s_value IS NULL THEN '--NULL VALUE--' ELSE s_value END AS server2_VAL
      FROM v_lib_AllKeys
           LEFT JOIN
           v_lib_server2 ON v_lib_AllKeys.uKey = v_lib_server2.ukey;


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
