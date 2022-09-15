-- Deploy nz-buildings:facilities/schema_and_tables to pg

BEGIN;

--Schema

CREATE SCHEMA IF NOT EXISTS facilities;

COMMENT ON SCHEMA facilities IS
'Schema that holds facilities data.';
-- Tables

-- facilities

-- The facilities table holds a multipolygon geometry, originating from the authoritative source data
CREATE TABLE IF NOT EXISTS facilities.facilities (
      facility_id serial PRIMARY KEY
    , source_facility_id character varying(80) DEFAULT ''
    , name character varying(250) DEFAULT ''
    , source_name character varying(250) DEFAULT ''
    , use character varying(40) NOT NULL DEFAULT ''
    , use_type character varying(150) DEFAULT ''
    , use_subtype character varying(150) DEFAULT ''
    , estimated_occupancy integer DEFAULT 0
    , last_modified date DEFAULT ('now'::text)::date
    , internal boolean NOT NULL DEFAULT false
    , internal_comments character varying(250) DEFAULT ''
    , shape public.geometry(MultiPolygon, 2193) NOT NULL
);

CREATE INDEX shx_facilities
    ON facilities.facilities USING gist (shape);

COMMENT ON TABLE facilities.facilities IS
'The facilities table holds geometries originating from authoritative source data.';
COMMENT ON COLUMN facilities.facilities.facility_id IS
'The unique identifier for each geometry.';
COMMENT ON COLUMN facilities.facilities.source_facility_id IS
'The facility unique identifier used by the authoritative source';
COMMENT ON COLUMN facilities.facilities.name IS
'The facility name which has consistent naming convention applied. This name may directly match the name provided by the authoritative source.';
COMMENT ON COLUMN facilities.facilities.source_name IS
'The name of the facility used by the authoritative source.';
COMMENT ON COLUMN facilities.facilities.use IS
'The generic use of the facility.';
COMMENT ON COLUMN facilities.facilities.use_type IS
'Type of use as defined by the authoritative source.';
COMMENT ON COLUMN facilities.facilities.use_subtype IS
'Sub-type of use as defined by the authoritative source.';
COMMENT ON COLUMN facilities.facilities.estimated_occupancy IS
'An approximation of the occupancy of the facility from the authoritative source, where it is known. It may not include staff.';
COMMENT ON COLUMN facilities.facilities.last_modified IS
'The most recent date on which any attribute or geometry that is part of the facility was modified.';
COMMENT ON COLUMN facilities.facilities.internal IS
'Identifies features which will not be added to the LDS.';
COMMENT ON COLUMN facilities.facilities.internal_comments IS
'Internal information such as why being stored as internal only, when likely to open, where found information.';
COMMENT ON COLUMN facilities.facilities.shape IS
'The geometry of the facility represented as a MultiPolygon using NZTM2000 / EPSG 2193.';

COMMIT;
