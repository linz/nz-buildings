-- Verify buildings:buildings_reference/schema_and_tables on pg

BEGIN;

SELECT pg_catalog.has_schema_privilege('buildings_reference', 'usage');

SELECT
      suburb_locality_id
    , external_suburb_locality_id
    , suburb_4th
    , suburb_3rd
    , suburb_2nd
    , suburb_1st
    , shape 
FROM buildings_reference.suburb_locality
WHERE FALSE;

SELECT
      town_city_id
    , external_city_id
    , name
    , shape
FROM buildings_reference.town_city
WHERE FALSE;

SELECT
      territorial_authority_id
    , external_territorial_authority_id
    , name
    , shape
FROM buildings_reference.territorial_authority
WHERE FALSE;

SELECT
      territorial_authority_grid_id
    , territorial_authority_id
    , external_territorial_authority_id
    , name
    , shape
FROM buildings_reference.territorial_authority_grid
WHERE FALSE;

SELECT
      coastline_and_island_id
    , external_coastline_and_island_id
    , shape
FROM buildings_reference.coastlines_and_islands
WHERE FALSE;

SELECT
      lake_polygon_id
    , external_lake_polygon_id
    , shape
FROM buildings_reference.lake_polygons
WHERE FALSE;

SELECT
      pond_polygon_id
    , external_pond_polygon_id
    , shape
FROM buildings_reference.pond_polygons
WHERE FALSE;

SELECT
      swamp_polygon_id
    , external_swamp_polygon_id
    , shape
FROM buildings_reference.swamp_polygons
WHERE FALSE;

SELECT
      lagoon_polygon_id
    , external_lagoon_polygon_id
    , shape
FROM buildings_reference.lagoon_polygons
WHERE FALSE;

SELECT
      canal_polygon_id
    , external_canal_polygon_id
    , shape
FROM buildings_reference.canal_polygons
WHERE FALSE;

SELECT
      area_polygon_id
    , external_area_polygon_id
    , area_title
    , shape
FROM buildings_reference.capture_source_area
WHERE FALSE;

SELECT
      update_id
    , update_date
    , river
    , lake
    , pond
    , swamp
    , lagoon
    , canal
    , coastlines_and_islands
    , capture_source_area
    , territorial_authority
    , territorial_authority_grid
    , suburb_locality
    , town_city
FROM buildings_reference.reference_update_log
WHERE FALSE;

ROLLBACK;
