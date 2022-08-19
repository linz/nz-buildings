-- Deploy nz-buildings:facilities_lds/schema_and_tables to pg

BEGIN;

--Schema

CREATE SCHEMA IF NOT EXISTS facilities_lds;

COMMENT ON SCHEMA facilities_lds IS
'Schema that holds facilities data to publish on the LDS.';
-- Tables

-- nz_facilities

-- The nz_facilities table holds a copy of the facilities.facilities table
-- minus the internal and internal_comments fields.

CREATE TABLE IF NOT EXISTS facilities_lds.nz_facilities (
      facility_id integer PRIMARY KEY
    , source_facility_id character varying(80) DEFAULT ''
    , name character varying(250) DEFAULT ''
    , source_name character varying(250) DEFAULT ''
    , use character varying(40) NOT NULL DEFAULT ''
    , use_type character varying(150) DEFAULT ''
    , use_subtype character varying(150) DEFAULT ''
    , estimated_occupancy integer DEFAULT 0
    , last_modified date DEFAULT ('now'::text)::date
    , shape public.geometry(MultiPolygon, 2193) NOT NULL
);

CREATE INDEX shx_nz_facilities
    ON facilities_lds.nz_facilities USING gist (shape);

COMMENT ON TABLE facilities_lds.nz_facilities IS
'The facilities table holds geometries originating from authoritative source data.';
COMMENT ON COLUMN facilities_lds.nz_facilities.facility_id IS
'The unique identifier for each geometry.';
COMMENT ON COLUMN facilities_lds.nz_facilities.source_facility_id IS
'The unique identifier of this facility used by the authoritative source';
COMMENT ON COLUMN facilities_lds.nz_facilities.name IS
'The facility name which has consistent naming convention applied. This name may directly match the name provided by the authoritative source.';
COMMENT ON COLUMN facilities_lds.nz_facilities.source_name IS
'The name of the facility used by the authoritative source.';
COMMENT ON COLUMN facilities_lds.nz_facilities.use IS
'The generic use of the facility.';
COMMENT ON COLUMN facilities_lds.nz_facilities.use_type IS
'Type of use as defined by the authoritative source.';
COMMENT ON COLUMN facilities_lds.nz_facilities.use_subtype IS
'Sub-type of use as defined by the authoritative source.';
COMMENT ON COLUMN facilities_lds.nz_facilities.estimated_occupancy IS
'An approximation of the occupancy of the facility from the authoritative source, where it is known. It may not include staff.';
COMMENT ON COLUMN facilities_lds.nz_facilities.last_modified IS
'The most recent date on which any attribute or geometry that is part of the facility was modified.';
COMMENT ON COLUMN facilities_lds.nz_facilities.shape IS
'The geometry of the facility represented as a MultiPolygon using NZTM2000 / EPSG 2193.';

COMMIT;
