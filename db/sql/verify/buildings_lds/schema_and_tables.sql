-- Verify buildings:buildings_lds/schema_and_tables on pg

BEGIN;

SELECT pg_catalog.has_schema_privilege('buildings_lds', 'usage');

SELECT
      building_outline_id
    , building_id
    , name
    , use
    , suburb_locality
    , town_city
    , territorial_authority
    , capture_method
    , capture_source
    , external_source_id
    , outline_begin_lifespan
    , building_begin_lifespan
    , name_begin_lifespan
    , use_begin_lifespan
    , shape
FROM buildings_lds.nz_building_outlines
WHERE FALSE;

SELECT
      extract_id
    , building_outline_id
    , building_id
    , name
    , use
    , suburb_locality
    , town_city
    , territorial_authority
    , capture_method
    , capture_source
    , external_source_id
    , building_lifecycle
    , record_begin_lifespan
    , record_end_lifespan
    , shape
FROM buildings_lds.nz_building_outlines_full_history
WHERE FALSE;

SELECT
      lifecycle_id
    , parent_building_id
    , building_id
FROM buildings_lds.nz_building_outlines_lifecycle
WHERE FALSE;

ROLLBACK;
