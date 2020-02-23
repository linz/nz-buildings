SET client_min_messages TO WARNING;


CREATE SCHEMA IF NOT EXISTS aerial_lds;

COMMENT ON SCHEMA aerial_lds IS
'This schema contains datasets related to aerial imagery to be published '
'on the LINZ Data Service.';

-- Imagery Surveys

CREATE TABLE IF NOT EXISTS aerial_lds.nz_imagery_survey_index (
      imagery_survey_id serial PRIMARY KEY
    , name character varying(100) NOT NULL
    , imagery_id integer
    , index_id integer
    , set_order integer
    , ground_sample_distance numeric(6,4)
    , accuracy character varying(100)
    , supplier character varying(80)
    , licensor character varying(250)
    , flown_from date CONSTRAINT after_first_flight CHECK (flown_from > '1903-12-17')
    , flown_to date CONSTRAINT survey_completed CHECK (flown_to < now())
    , shape public.geometry(MultiPolygon, 2193) NOT NULL
    , CONSTRAINT valid_flight_dates CHECK (flown_from <= flown_to)
);

-- Old Imagery Surveys (old but table still required to verify a full database migration)

CREATE TABLE IF NOT EXISTS aerial_lds.nz_imagery_surveys (
      imagery_survey_id serial PRIMARY KEY
    , name character varying(100) NOT NULL
    , imagery_id integer
    , index_id integer
    , set_order integer
    , ground_sample_distance numeric(6,4)
    , accuracy character varying(100)
    , supplier character varying(80)
    , licensor character varying(250)
    , flown_from date CONSTRAINT after_first_flight CHECK (flown_from > '1903-12-17')
    , flown_to date CONSTRAINT survey_completed CHECK (flown_to < now())
    , shape public.geometry(MultiPolygon, 2193) NOT NULL
    , CONSTRAINT valid_flight_dates CHECK (flown_from <= flown_to)
);
