-- Verify buildings:buildings/schema_and_tables on pg

BEGIN;

SELECT pg_catalog.has_schema_privilege('buildings', 'usage');

SELECT
      lifecycle_stage_id
    , value
FROM buildings.lifecycle_stage
WHERE FALSE;

SELECT
      use_id
    , value
FROM buildings.use
WHERE FALSE;

SELECT
      building_id
    , begin_lifespan
    , end_lifespan
FROM buildings.buildings
WHERE FALSE;

SELECT
      building_outline_id
    , building_id
    , capture_method_id
    , capture_source_id
    , lifecycle_stage_id
    , suburb_locality_id
    , town_city_id
    , territorial_authority_id
    , begin_lifespan
    , end_lifespan
    , shape
FROM buildings.building_outlines
WHERE FALSE;

SELECT
      building_name_id
    , building_id
    , building_name
    , begin_lifespan
    , end_lifespan
FROM buildings.building_name
WHERE FALSE;

SELECT
      building_use_id
    , building_id
    , use_id
    , begin_lifespan
    , end_lifespan
FROM buildings.building_use
WHERE FALSE;

SELECT
      lifecycle_id
    , parent_building_id
    , building_id
FROM buildings.lifecycle
WHERE FALSE;

ROLLBACK;
