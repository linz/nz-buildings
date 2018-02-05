------------------------------------------------------------------------------
-- Create buildings LDS schema and tables
------------------------------------------------------------------------------


CREATE SCHEMA IF NOT EXISTS buildings_lds;

-- NZ Building Outlines

CREATE TABLE IF NOT EXISTS buildings_lds.nz_building_outlines (
      building_outline_id integer NOT NULL
    , capture_method character varying(250) NOT NULL
    , capture_source character varying(250) NOT NULL
    , lifecycle_stage character varying(250) NOT NULL
    , building_begin_lifespan timestamptz NOT NULL
    , parent_begin_lifespan timestamptz NOT NULL
    , attribute_modified timestamptz NOT NULL
    , geometry_modified timestamptz NOT NULL
    , shape public.geometry(MultiPolygon, 2193) NOT NULL
);
