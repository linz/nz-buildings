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
    , building_begin_lifespan datetime NOT NULL
    , parent_begin_lifespan datetime NOT NULL
    , attribute_modified datetime NOT NULL
    , geometry_modified datetime NOT NULL
    , shape public.geometry(MultiPolygon, 2193) NOT NULL
);
