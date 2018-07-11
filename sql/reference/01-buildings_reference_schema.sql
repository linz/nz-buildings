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

CREATE TABLE IF NOT EXISTS buildings_reference.coastlines_and_islands (

      coastline_and_island_id serial PRIMARY KEY
    , external_coastline_and_island_id integer
    , shape public.geometry(MultiPolygon, 2193)
);
DROP INDEX IF EXISTS shx_coastlines_and_islands;
CREATE INDEX shx_coastlines_and_islands
    ON buildings_reference.coastlines_and_islands USING gist (shape);

-- River Centrelines

CREATE TABLE IF NOT EXISTS buildings_reference.river_centrelines (
      river_centreline_id serial PRIMARY KEY
    , external_river_centreline_id integer
    , shape public.geometry(Linestring, 2193)
);
DROP INDEX IF EXISTS shx_river_centrelines;
CREATE INDEX shx_river_centrelines
    ON buildings_reference.river_centrelines USING gist (shape);

-- River Polygons

CREATE TABLE IF NOT EXISTS buildings_reference.river_polygons (
      river_polygon_id serial PRIMARY KEY
    , external_river_polygon_id integer
    , shape public.geometry(Polygon, 2193)
);
DROP INDEX IF EXISTS shx_river_polygons;
CREATE INDEX shx_river_polygons
    ON buildings_reference.river_polygons USING gist (shape);

-- Lake Polygons

CREATE TABLE IF NOT EXISTS buildings_reference.lake_polygons (
      lake_polygon_id serial PRIMARY KEY
    , external_lake_polygon_id integer
    , shape public.geometry(Polygon, 2193)
);
DROP INDEX IF EXISTS shx_lake_polygons;
CREATE INDEX shx_lake_polygons
    ON buildings_reference.lake_polygons USING gist (shape);

-- Pond Polygons

CREATE TABLE IF NOT EXISTS buildings_reference.pond_polygons (
      pond_polygon_id serial PRIMARY KEY
    , external_pond_polygon_id integer
    , shape public.geometry(Polygon, 2193)
);
DROP INDEX IF EXISTS shx_pond_polygons;
CREATE INDEX shx_pond_polygons
    ON buildings_reference.pond_polygons USING gist (shape);

-- Swamp Polygons

CREATE TABLE IF NOT EXISTS buildings_reference.swamp_polygons (
      swamp_polygon_id serial PRIMARY KEY
    , external_swamp_polygon_id integer
    , shape public.geometry(Polygon, 2193)
);
DROP INDEX IF EXISTS shx_swamp_polygons;
CREATE INDEX shx_swamp_polygons
    ON buildings_reference.swamp_polygons USING gist (shape);

-- Lagoon Polygons

CREATE TABLE IF NOT EXISTS buildings_reference.lagoon_polygons (
      lagoon_polygon_id serial PRIMARY KEY
    , external_lagoon_polygon_id integer
    , shape public.geometry(Polygon, 2193)
);
DROP INDEX IF EXISTS shx_lagoon_polygons;
CREATE INDEX shx_lagoon_polygons
    ON buildings_reference.lagoon_polygons USING gist (shape);

-- Canal Centrelines

CREATE TABLE IF NOT EXISTS buildings_reference.canal_centrelines (
      canal_centreline_id serial PRIMARY KEY
    , external_canal_centreline_id integer
    , shape public.geometry(Linestring, 2193)
);
DROP INDEX IF EXISTS shx_canal_centrelines;
CREATE INDEX shx_canal_centrelines
    ON buildings_reference.canal_centrelines USING gist (shape);

-- Canal Polygons

CREATE TABLE IF NOT EXISTS buildings_reference.canal_polygons (
      canal_polygon_id serial PRIMARY KEY
    , external_canal_polygon_id integer
    , shape public.geometry(Polygon, 2193)
);
DROP INDEX IF EXISTS shx_canal_polygons;
CREATE INDEX shx_canal_polygons
    ON buildings_reference.canal_polygons USING gist (shape);

-- Capture Source Area

CREATE TABLE IF NOT EXISTS buildings_reference.capture_source_area (
      area_polygon_id serial PRIMARY KEY
    , external_area_polygon_id integer
    , area_title varchar (250)
    , shape public.geometry(MultiPolygon, 2193)
);
