------------------------------------------------------------------------------
-- Create buildings LDS schema and tables
------------------------------------------------------------------------------

SET client_min_messages TO WARNING;


CREATE SCHEMA IF NOT EXISTS buildings_lds;

-- NZ Building Outlines

CREATE TABLE IF NOT EXISTS buildings_lds.nz_building_outlines (
      building_outline_id integer NOT NULL
    , building_id integer NOT NULL
    , name character varying(250)
    , use character varying(40)
    , suburb_locality character varying(80)
    , town_city character varying(80)
    , territorial_authority character varying(80)
    , capture_method character varying(250) NOT NULL
    , capture_source character varying(250) NOT NULL
    , lifecycle_stage character varying(250) NOT NULL
    , outline_begin_lifespan timestamptz NOT NULL
    , building_begin_lifespan timestamptz NOT NULL
    , name_begin_lifespan timestamptz
    , use_begin_lifespan timestamptz
    , shape public.geometry(MultiPolygon, 2193) NOT NULL
);
