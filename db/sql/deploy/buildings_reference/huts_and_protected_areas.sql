-- Deploy nz-buildings:buildings_reference/huts_and_protected_areas to pg

BEGIN;

------------------------------------------------------------------------------
-- Create additional buildings reference tables

-- Tables:
-- hut_points
-- shelter_points
-- bivouac_points
-- protected_areas_polygons
-- Add columns to Update Reference Log table


-- Add huts table

CREATE TABLE IF NOT EXISTS buildings_reference.hut_points (
      hut_points_id serial PRIMARY KEY
    , external_hut_points_id integer
    , name character varying(254)
    , shape public.geometry(Point, 2193)
);

CREATE INDEX shx_hut_points
    ON buildings_reference.hut_points USING gist (shape);

COMMENT ON TABLE buildings_reference.hut_points IS
'http://apps.linz.govt.nz/topo-data-dictionary/index.aspx?page=class-building_pnt';

COMMENT ON COLUMN buildings_reference.hut_points.hut_points_id IS
'Unique identifier for the hut points.';
COMMENT ON COLUMN buildings_reference.hut_points.external_hut_points_id IS
'The id of the hut from the external provider.';
COMMENT ON COLUMN buildings_reference.hut_points.name IS
'Name of the hut.';

-- Add shelter table

CREATE TABLE IF NOT EXISTS buildings_reference.shelter_points (
      shelter_points_id serial PRIMARY KEY
    , external_shelter_points_id integer
    , name character varying(254)
    , shape public.geometry(Point, 2193)
);

CREATE INDEX shx_shelter_points
    ON buildings_reference.shelter_points USING gist (shape);

COMMENT ON TABLE buildings_reference.shelter_points IS
'http://apps.linz.govt.nz/topo-data-dictionary/index.aspx?page=class-building_pnt';

COMMENT ON COLUMN buildings_reference.shelter_points.shelter_points_id IS
'Unique identifier for the shelter points.';
COMMENT ON COLUMN buildings_reference.shelter_points.external_shelter_points_id IS
'The id of the shelter from the external provider.';
COMMENT ON COLUMN buildings_reference.shelter_points.name IS
'Name of the shelter.';

-- Add bivouac table

CREATE TABLE IF NOT EXISTS buildings_reference.bivouac_points (
      bivouac_points_id serial PRIMARY KEY
    , external_bivouac_points_id integer
    , name character varying(254)
    , shape public.geometry(Point, 2193)
);

CREATE INDEX shx_bivouac_points
    ON buildings_reference.bivouac_points USING gist (shape);

COMMENT ON TABLE buildings_reference.bivouac_points IS
'http://apps.linz.govt.nz/topo-data-dictionary/index.aspx?page=class-bivouac_pnt';

COMMENT ON COLUMN buildings_reference.bivouac_points.bivouac_points_id IS
'Unique identifier for the bivouac points.';
COMMENT ON COLUMN buildings_reference.bivouac_points.external_bivouac_points_id IS
'The id of the bivouac from the external provider.';
COMMENT ON COLUMN buildings_reference.bivouac_points.name IS
'Name of the bivouac.';

-- Add protected areas table

CREATE TABLE IF NOT EXISTS buildings_reference.protected_areas_polygons (
      protected_areas_polygon_id serial PRIMARY KEY
    , external_protected_areas_polygon_id integer
    , name character varying(254)
    , shape public.geometry(MultiPolygon, 2193)
);

CREATE INDEX shx_protected_areas_polygons
    ON buildings_reference.protected_areas_polygons USING gist (shape);

COMMENT ON TABLE buildings_reference.protected_areas_polygons IS
'https://data.linz.govt.nz/layer/53564-protected-areas/';

COMMENT ON COLUMN buildings_reference.protected_areas_polygons.protected_areas_polygon_id IS
'Unique identifier for the protected areas polygons.';
COMMENT ON COLUMN buildings_reference.protected_areas_polygons.external_protected_areas_polygon_id IS
'The id of the protected areas from the external provider.';
COMMENT ON COLUMN buildings_reference.protected_areas_polygons.name IS
'Name of the protected areas.';

-- Add columns to Update Reference Log table

ALTER TABLE buildings_reference.reference_update_log ADD hut boolean DEFAULT False;
ALTER TABLE buildings_reference.reference_update_log ADD shelter boolean DEFAULT False;
ALTER TABLE buildings_reference.reference_update_log ADD bivouac boolean DEFAULT False;
ALTER TABLE buildings_reference.reference_update_log ADD protected_areas boolean DEFAULT False;

COMMIT;
