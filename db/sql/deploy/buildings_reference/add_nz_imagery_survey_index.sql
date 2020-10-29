-- Deploy nz-buildings:buildings_reference/add_nz_imagery_survey_index to pg

BEGIN;

CREATE TABLE buildings_reference.nz_imagery_survey_index (
      imagery_survey_id integer NOT NULL
    , shape public.geometry(MultiPolygon, 2193)
    , name character varying(100)
    , imagery_id integer
    , index_id integer
    , set_order integer
    , ground_sample_distance double precision
    , accuracy character varying(100)
    , supplier character varying(80)
    , licensor character varying(250)
    , flown_from date
    , flown_to date
);

CREATE INDEX sidx_nz_imagery_survey_index_shape
    ON buildings_reference.nz_imagery_survey_index USING gist (shape);

COMMENT ON TABLE buildings_reference.nz_imagery_survey_index IS
'A copy of the NZ Imagery Survey Index table that contains aerial imagery survey metadata';

COMMIT;
