------------------------------------------------------------------------------
-- Create buildings reference schema and tables
------------------------------------------------------------------------------

SET client_min_messages TO WARNING;


CREATE SCHEMA IF NOT EXISTS buildings_reference;

-- Suburb / Locality

CREATE TABLE IF NOT EXISTS buildings_reference.suburb_locality (
      suburb_locality_id serial PRIMARY KEY
    , external_suburb_locality_id integer
    , suburb_4th character varying(60)
    , suburb_3rd character varying(60)
    , suburb_2nd character varying(60)
    , suburb_1st character varying(60)
    , shape public.geometry(MultiPolygon, 2193)
);

-- Town / City

CREATE TABLE IF NOT EXISTS buildings_reference.town_city (
      town_city_id serial PRIMARY KEY
    , external_city_id integer
    , name character varying(60)
    , shape public.geometry(MultiPolygon, 2193)
);

-- Territorial Authority

CREATE TABLE IF NOT EXISTS buildings_reference.territorial_authority (
      territorial_authority_id serial PRIMARY KEY
    , external_territorial_authority_id integer
    , name character varying(100)
    , shape public.geometry(MultiPolygon, 2193)
);

-- Coastline

CREATE TABLE IF NOT EXISTS buildings_reference.coastlines (
      coastline_id serial PRIMARY KEY
    , shape public.geometry(MultiPolygon, 2193)
);

-- River Centrelines

CREATE TABLE IF NOT EXISTS buildings_reference.river_centrelines (
      river_centreline_id serial PRIMARY KEY
    , shape public.geometry(MultiLinestring, 2193)
);

-- River Polygons

CREATE TABLE IF NOT EXISTS buildings_reference.river_polygons (
      river_polygon_id serial PRIMARY KEY
    , shape public.geometry(MultiPolygon, 2193)
);

-- Lake Polygons

CREATE TABLE IF NOT EXISTS buildings_reference.lake_polygons (
      lake_polygon_id serial PRIMARY KEY
    , shape public.geometry(MultiPolygon, 2193)
);

-- Pond Polygons

CREATE TABLE IF NOT EXISTS buildings_reference.pond_polygons (
      pond_polygon_id serial PRIMARY KEY
    , shape public.geometry(MultiPolygon, 2193)
);

-- Swamp Polygons

CREATE TABLE IF NOT EXISTS buildings_reference.swamp_polygons (
      swamp_polygon_id serial PRIMARY KEY
    , shape public.geometry(MultiPolygon, 2193)
);

-- Lagoon Polygons

CREATE TABLE IF NOT EXISTS buildings_reference.lagoon_polygons (
      lagoon_polygon_id serial PRIMARY KEY
    , shape public.geometry(MultiPolygon, 2193)
);

-- Canal Centrelines

CREATE TABLE IF NOT EXISTS buildings_reference.canal_centrelines (
      canal_centreline_id serial PRIMARY KEY
    , shape public.geometry(MultiLinestring, 2193)
);

-- Canal Polygons

CREATE TABLE IF NOT EXISTS buildings_reference.canal_polygons (
      canal_polygon_id serial PRIMARY KEY
    , shape public.geometry(MultiPolygon, 2193)
);

