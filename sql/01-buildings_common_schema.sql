------------------------------------------------------------------------------
-- Create buildings common schema and tables
------------------------------------------------------------------------------

SET client_min_messages TO WARNING;


CREATE SCHEMA IF NOT EXISTS buildings_common;

COMMENT ON SCHEMA buildings_common IS
'Schema that holds tables referenced in more than one other schema.';

-- LOOKUP TABLES

-- Capture Method

CREATE TABLE IF NOT EXISTS buildings_common.capture_method (
      capture_method_id serial PRIMARY KEY
    , value character varying(40) NOT NULL
);

COMMENT ON TABLE buildings_common.capture_method IS
'Lookup table that holds all of the methods by which the geometry was captured.';

COMMENT ON COLUMN buildings_common.capture_method.capture_method_id IS
'Unique identifier for the capture method.';
COMMENT ON COLUMN buildings_common.capture_methodvalue IS
'The method by which the geometry was captured.';

-- Capture Source Group

CREATE TABLE IF NOT EXISTS buildings_common.capture_source_group (
      capture_source_group_id serial PRIMARY KEY
    , value character varying(80) NOT NULL
    , description character varying(400) NOT NULL
);

COMMENT ON TABLE buildings_common.capture_source_group IS
'Lookup table that holds all of the capture source groups. Capture source '
'groups are categories of data sources, e.g. NZ Aerial Imagery';

COMMENT ON COLUMN buildings_common.capture_source_group.capture_source_group_id IS
'Unique identifier for the capture source group.';
COMMENT ON COLUMN buildings_common.capture_source_group.value IS
'The name of the capture source group e.g. NZ Aerial Imagery.';
COMMENT ON COLUMN buildings_common.capture_source_group.description IS
'The description of the capture source group e.g. external_source_id for this '
'group links to the primary key of the NZ Imagery Surveys layer, available '
'on LINZ Data Service at: https://data.linz.govt.nz/layer/nnnnn.';

-- Capture Source

CREATE TABLE IF NOT EXISTS buildings_common.capture_source (
      capture_source_id serial PRIMARY KEY
    , capture_source_group_id integer NOT NULL REFERENCES buildings_common.capture_source_group (capture_source_group_id)
    , external_source_id character varying(250)
);

COMMENT ON TABLE buildings_common.capture_source IS
'Lookup table that holds all of the methods by which the geometry was captured.';

COMMENT ON COLUMN buildings_common.capture_source.capture_source_id IS
'Unique identifier for the capture source.';
COMMENT ON COLUMN buildings_common.capture_source.capture_source_group_id IS
'Foreign key to the buildings_common.capture_source_group table.';
COMMENT ON COLUMN buildings_common.capture_source.external_source_id IS
'Stores a reference to an externally managed identifier that can be linked '
'in order to find out more information about the source.';

DROP INDEX IF EXISTS idx_capture_source_capture_source_group_id;
CREATE INDEX idx_capture_source_capture_source_group_id
    ON buildings_common.capture_source USING btree (capture_source_group_id);
