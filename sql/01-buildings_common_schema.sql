------------------------------------------------------------------------------
-- Create buildings common schema and tables
------------------------------------------------------------------------------

SET client_min_messages TO WARNING;


CREATE SCHEMA IF NOT EXISTS buildings_common;

-- LOOKUP TABLES

-- Capture Method

CREATE TABLE IF NOT EXISTS buildings_common.capture_method (
      capture_method_id serial PRIMARY KEY
    , value character varying(40) NOT NULL
);

-- Capture Source Group

CREATE TABLE IF NOT EXISTS buildings_common.capture_source_group (
      capture_source_group_id serial PRIMARY KEY
    , value character varying(80) NOT NULL
    , description character varying(400) NOT NULL
);

-- Capture Source

CREATE TABLE IF NOT EXISTS buildings_common.capture_source (
      capture_source_id serial PRIMARY KEY
    , capture_source_group_id integer NOT NULL REFERENCES buildings_common.capture_source_group (capture_source_group_id)
    , external_source_id character varying(250)
);

DROP INDEX IF EXISTS idx_capture_source_capture_source_group_id;
CREATE INDEX idx_capture_source_capture_source_group_id
    ON buildings_common.capture_source USING btree (capture_source_group_id);
