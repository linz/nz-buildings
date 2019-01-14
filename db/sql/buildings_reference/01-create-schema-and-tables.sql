------------------------------------------------------------------------------
-- Create buildings reference schema and tables

-- Tables:
-- suburb_locality
-- town_city
-- territorial_authority
-- territorial_authority_grid
-- coastlines_and_islands
-- river polygons
-- lake polygons
-- pond polygons
-- swamp polygons
-- lagoon polygons
-- canal_polygons
-- capture_source_area
-- reference_update_log

------------------------------------------------------------------------------

-- Schemas

SET client_min_messages TO WARNING;


CREATE SCHEMA IF NOT EXISTS buildings_reference;

COMMENT ON SCHEMA buildings_reference IS
'Schema that holds the reference data used in checks and processing.';


-- Tables

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
DROP INDEX IF EXISTS shx_suburb_locality;
CREATE INDEX shx_suburb_locality
    ON buildings_reference.suburb_locality USING gist (shape);

COMMENT ON TABLE buildings_reference.suburb_locality IS
'suburbs/Localities of New Zealand';

COMMENT ON COLUMN buildings_reference.suburb_locality.suburb_locality_id IS
'Unique identifier for suburb_locality.';
COMMENT ON COLUMN buildings_reference.suburb_locality.external_suburb_locality_id IS
'The id given by the external source.';
COMMENT ON COLUMN buildings_reference.suburb_locality.suburb_4th IS
'name';
COMMENT ON COLUMN buildings_reference.suburb_locality.suburb_3rd IS
'name';
COMMENT ON COLUMN buildings_reference.suburb_locality.suburb_2nd IS
'name';
COMMENT ON COLUMN buildings_reference.suburb_locality.suburb_1st IS
'name';


-- Town / City
CREATE TABLE IF NOT EXISTS buildings_reference.town_city (
      town_city_id serial PRIMARY KEY
    , external_city_id integer
    , name character varying(60)
    , shape public.geometry(MultiPolygon, 2193)
);
DROP INDEX IF EXISTS shx_town_city;
CREATE INDEX shx_town_city
    ON buildings_reference.town_city USING gist (shape);

COMMENT ON TABLE buildings_reference.town_city IS
'towns/cities of New Zealand';

COMMENT ON COLUMN buildings_reference.town_city.town_city_id IS
'Unique identifier for town_city.';
COMMENT ON COLUMN buildings_reference.town_city.external_city_id IS
'The id given by the external source.';
COMMENT ON COLUMN buildings_reference.town_city.name IS
'The name of the town/city.';

-- Territorial Authority
CREATE TABLE IF NOT EXISTS buildings_reference.territorial_authority (
      territorial_authority_id serial PRIMARY KEY
    , external_territorial_authority_id integer
    , name character varying(100)
    , shape public.geometry(MultiPolygon, 2193)
);
DROP INDEX IF EXISTS shx_territorial_authority;
CREATE INDEX shx_territorial_authority
    ON buildings_reference.territorial_authority USING gist (shape);

COMMENT ON TABLE buildings_reference.territorial_authority IS
'territorial authorities of New Zealand';

COMMENT ON COLUMN buildings_reference.territorial_authority.territorial_authority_id IS
'Unique identifier for territorial_authority.';
COMMENT ON COLUMN buildings_reference.territorial_authority.external_territorial_authority_id IS
'The external_territorial_authority_id provided by the external source.';
COMMENT ON COLUMN buildings_reference.territorial_authority.name IS
'The name of the territorial authority.';

-- Territorial Authority Grid
-- For faster spatial operations
CREATE TABLE IF NOT EXISTS buildings_reference.territorial_authority_grid (
      territorial_authority_grid_id serial PRIMARY KEY
    , territorial_authority_id integer REFERENCES buildings_reference.territorial_authority (territorial_authority_id)
    , external_territorial_authority_id integer
    , name character varying(100)
    , shape public.geometry(MultiPolygon, 2193)
);
DROP INDEX IF EXISTS shx_territorial_authority_grid;
CREATE INDEX shx_territorial_authority_grid
    ON buildings_reference.territorial_authority_grid USING gist (shape);

COMMENT ON TABLE buildings_reference.territorial_authority_grid IS
'territorial_authority modified into grid to allow for faster spatial operations';

COMMENT ON COLUMN buildings_reference.territorial_authority_grid.territorial_authority_grid_id IS
'Unique identifier for the territorial_authority_grid.';
COMMENT ON COLUMN buildings_reference.territorial_authority_grid.territorial_authority_id IS
'The territorial_authority_id of the grid.';
COMMENT ON COLUMN buildings_reference.territorial_authority_grid.external_territorial_authority_id IS
'The external_territorial_authority_id of the grid.';
COMMENT ON COLUMN buildings_reference.territorial_authority_grid.name IS
'The name of the territorial authority of the grid.';

-- Coastline
CREATE TABLE IF NOT EXISTS buildings_reference.coastlines_and_islands (

      coastline_and_island_id serial PRIMARY KEY
    , external_coastline_and_island_id integer
    , shape public.geometry(MultiPolygon, 2193)
);
DROP INDEX IF EXISTS shx_coastlines_and_islands;
CREATE INDEX shx_coastlines_and_islands
    ON buildings_reference.coastlines_and_islands USING gist (shape);

COMMENT ON TABLE buildings_reference.coastlines_and_islands IS
'https://data.linz.govt.nz/layer/51153-nz-coastlines-and-islands-polygons-topo-150k/';

COMMENT ON COLUMN buildings_reference.coastlines_and_islands.coastline_and_island_id IS
'Unique identifier for the coastlines_and_islands.';
COMMENT ON COLUMN buildings_reference.coastlines_and_islands.external_coastline_and_island_id IS
'The id of the coastline or island from the external provider.';

-- River Polygons
CREATE TABLE IF NOT EXISTS buildings_reference.river_polygons (
      river_polygon_id serial PRIMARY KEY
    , external_river_polygon_id integer
    , shape public.geometry(Polygon, 2193)
);
DROP INDEX IF EXISTS shx_river_polygons;
CREATE INDEX shx_river_polygons
    ON buildings_reference.river_polygons USING gist (shape);

COMMENT ON TABLE buildings_reference.river_polygons IS
'http://apps.linz.govt.nz/topo-data-dictionary/index.aspx?page=class-river_poly';

COMMENT ON COLUMN buildings_reference.river_polygons.river_polygon_id IS
'Unique identifier for the river_polygons.';
COMMENT ON COLUMN buildings_reference.river_polygons.external_river_polygon_id IS
'The id of the river from the external provider.';

-- Lake Polygons
CREATE TABLE IF NOT EXISTS buildings_reference.lake_polygons (
      lake_polygon_id serial PRIMARY KEY
    , external_lake_polygon_id integer
    , shape public.geometry(Polygon, 2193)
);
DROP INDEX IF EXISTS shx_lake_polygons;
CREATE INDEX shx_lake_polygons
    ON buildings_reference.lake_polygons USING gist (shape);

COMMENT ON TABLE buildings_reference.lake_polygons IS
'http://apps.linz.govt.nz/topo-data-dictionary/index.aspx?page=class-lake_poly';

COMMENT ON COLUMN buildings_reference.lake_polygons.lake_polygon_id IS
'Unique identifier for the lake_polygons.';
COMMENT ON COLUMN buildings_reference.lake_polygons.external_lake_polygon_id IS
'The id of the lake from the external provider.';

-- Pond Polygons
CREATE TABLE IF NOT EXISTS buildings_reference.pond_polygons (
      pond_polygon_id serial PRIMARY KEY
    , external_pond_polygon_id integer
    , shape public.geometry(Polygon, 2193)
);
DROP INDEX IF EXISTS shx_pond_polygons;
CREATE INDEX shx_pond_polygons
    ON buildings_reference.pond_polygons USING gist (shape);

COMMENT ON TABLE buildings_reference.pond_polygons IS
'http://apps.linz.govt.nz/topo-data-dictionary/index.aspx?page=class-pond_poly';

COMMENT ON COLUMN buildings_reference.pond_polygons.pond_polygon_id IS
'Unique identifier for the pond_polygons.';
COMMENT ON COLUMN buildings_reference.pond_polygons.external_pond_polygon_id IS
'The id of the pond from the external provider.';

-- Swamp Polygons
CREATE TABLE IF NOT EXISTS buildings_reference.swamp_polygons (
      swamp_polygon_id serial PRIMARY KEY
    , external_swamp_polygon_id integer
    , shape public.geometry(Polygon, 2193)
);
DROP INDEX IF EXISTS shx_swamp_polygons;
CREATE INDEX shx_swamp_polygons
    ON buildings_reference.swamp_polygons USING gist (shape);

COMMENT ON TABLE buildings_reference.swamp_polygons IS
'http://apps.linz.govt.nz/topo-data-dictionary/index.aspx?page=class-swamp_poly';

COMMENT ON COLUMN buildings_reference.swamp_polygons.swamp_polygon_id IS
'Unique identifier for the swamp_polygons.';
COMMENT ON COLUMN buildings_reference.swamp_polygons.external_swamp_polygon_id IS
'The id of the swamp from the external provider.';

-- Lagoon Polygons
CREATE TABLE IF NOT EXISTS buildings_reference.lagoon_polygons (
      lagoon_polygon_id serial PRIMARY KEY
    , external_lagoon_polygon_id integer
    , shape public.geometry(Polygon, 2193)
);
DROP INDEX IF EXISTS shx_lagoon_polygons;
CREATE INDEX shx_lagoon_polygons
    ON buildings_reference.lagoon_polygons USING gist (shape);

COMMENT ON TABLE buildings_reference.lagoon_polygons IS
'http://apps.linz.govt.nz/topo-data-dictionary/index.aspx?page=class-lagoon_poly';

COMMENT ON COLUMN buildings_reference.lagoon_polygons.lagoon_polygon_id IS
'Unique identifier for the lagoon_polygons.';
COMMENT ON COLUMN buildings_reference.lagoon_polygons.external_lagoon_polygon_id IS
'The id of the lagoon from the external provider.';

-- Canal Polygons
CREATE TABLE IF NOT EXISTS buildings_reference.canal_polygons (
      canal_polygon_id serial PRIMARY KEY
    , external_canal_polygon_id integer
    , shape public.geometry(Polygon, 2193)
);
DROP INDEX IF EXISTS shx_canal_polygons;
CREATE INDEX shx_canal_polygons
    ON buildings_reference.canal_polygons USING gist (shape);

COMMENT ON TABLE buildings_reference.canal_polygons IS
'http://apps.linz.govt.nz/topo-data-dictionary/index.aspx?page=class-canal_poly';

COMMENT ON COLUMN buildings_reference.canal_polygons.canal_polygon_id IS
'Unique identifier for the canal_polygons.';
COMMENT ON COLUMN buildings_reference.canal_polygons.external_canal_polygon_id IS
'The id of the canal from the external provider.';

-- Capture Source Area
CREATE TABLE IF NOT EXISTS buildings_reference.capture_source_area (
      area_polygon_id serial PRIMARY KEY
    , external_area_polygon_id varchar(250)
    , area_title varchar (250)
    , shape public.geometry(MultiPolygon, 2193)
);
DROP INDEX IF EXISTS shx_capture_source_area;
CREATE INDEX shx_capture_source_area
    ON buildings_reference.capture_source_area USING gist (shape);

COMMENT ON TABLE buildings_reference.capture_source_area IS
'https://nz-imagery-surveys.readthedocs.io/en/latest/?badge=latest';

COMMENT ON COLUMN buildings_reference.capture_source_area.area_polygon_id IS
'Unique identifier for the capture_source_area.';
COMMENT ON COLUMN buildings_reference.capture_source_area.external_area_polygon_id IS
'The id of the capture source area from the external provider.';
COMMENT ON COLUMN buildings_reference.capture_source_area.area_title IS
'The title/name of the capture source area provided by the external source.';


-- Reference Update Log
CREATE TABLE IF NOT EXISTS buildings_reference.reference_update_log (
      update_id serial PRIMARY KEY
    , update_date timestamp DEFAULT now()
    , rivers boolean DEFAULT False
    , lakes boolean DEFAULT False
    , ponds boolean DEFAULT False
    , swamps boolean DEFAULT False
    , lagoons boolean DEFAULT False
    , canals boolean DEFAULT False
    , coastlines_and_islands boolean DEFAULT False
    , capture_source_area boolean DEFAULT False
    , territorial_authority boolean DEFAULT False
    , territorial_authority_grid boolean DEFAULT False
    , suburb_locality boolean DEFAULT False
    , town_city boolean DEFAULT False
);

COMMENT ON TABLE buildings_reference.reference_update_log IS
'Log of when reference tables have been updated';

COMMENT ON COLUMN buildings_reference.reference_update_log.update_id IS
'Unique identifier for the log update';
COMMENT ON COLUMN buildings_reference.reference_update_log.update_date IS
'Date of the reference data update';
COMMENT ON COLUMN buildings_reference.reference_update_log.rivers IS
'True if river_polygons table was changed/checked in this update, defaults to False if not specified.';
COMMENT ON COLUMN buildings_reference.reference_update_log.lakes IS
'True if lake_polygons table was changed/checked in this update, defaults to False if not specified.';
COMMENT ON COLUMN buildings_reference.reference_update_log.ponds IS
'True if pond_polygons table was changed/checked in this update, defaults to False if not specified.';
COMMENT ON COLUMN buildings_reference.reference_update_log.swamps IS
'True if swamp_polygons table was changed/checked in this update, defaults to False if not specified.';
COMMENT ON COLUMN buildings_reference.reference_update_log.lagoons IS
'True if lagoon_polygons table was changed/checked in this update, defaults to False if not specified.';
COMMENT ON COLUMN buildings_reference.reference_update_log.canals IS
'True if canal_polygons table was changed/checked in this update, defaults to False if not specified.';
COMMENT ON COLUMN buildings_reference.reference_update_log.capture_source_area IS
'True if capture_source_area table was changed/checked in this update, defaults to False if not specified.';
COMMENT ON COLUMN buildings_reference.reference_update_log.territorial_authority IS
'True if territorial_authority table was changed/checked in this update, defaults to False if not specified.';
COMMENT ON COLUMN buildings_reference.reference_update_log.territorial_authority_grid IS
'True if territorial_authority_grid table was changed/checked in this update, defaults to False if not specified.';
COMMENT ON COLUMN buildings_reference.reference_update_log.suburb_locality IS
'True if suburb_locality table was changed/checked in this update, defaults to False if not specified.';
COMMENT ON COLUMN buildings_reference.reference_update_log.town_city IS
'True if town_city table was changed/checked in this update, defaults to False if not specified.';
