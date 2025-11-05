-- Deploy nz-buildings:buildings_reference/add_nz_imagery_survey_index to pg

BEGIN;

CREATE TABLE buildings_reference.nz_facilities (
      facility_id integer NOT NULL
    , source_facility_id character varying(80)
    , name character varying(250)
    , source_name character varying(250)
    , use character varying(40)
    , use_type character varying(150)
    , use_subtype character varying(150)
    , estimated_occupancy integer
    , last_modified date
    , shape public.geometry(MultiPolygon, 2193)
);

CREATE INDEX sidx_nz_facilities_shape
    ON buildings_reference.nz_facilities USING gist (shape);

COMMENT ON TABLE buildings_reference.nz_facilities IS
'A copy of the NZ Facilities table that contains hospitals and schools attributes';

COMMIT;
