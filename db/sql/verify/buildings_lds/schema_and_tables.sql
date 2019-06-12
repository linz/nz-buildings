-- Verify nz-buildings:buildings_lds/schema_and_tables on pg

BEGIN;

SELECT pg_catalog.has_schema_privilege('buildings_lds', 'usage');

SELECT
      building_id
    , name
    , use
    , suburb_locality
    , town_city
    , territorial_authority
    , capture_method
    , capture_source_group
    , capture_source_id
    , capture_source_name
    , capture_source_from
    , capture_source_to
    , last_modified
    , shape
FROM buildings_lds.nz_building_outlines
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_lds'
    AND tablename = 'nz_building_outlines'
    AND indexdef LIKE '%sidx_nz_building_outlines%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_lds", table '
        '"nz_building_outlines", column "shape" has a missing index named '
        '"sidx_nz_building_outlines"';
    END IF;
END;
$$;

SELECT
      building_outline_id
    , building_id
    , name
    , use
    , suburb_locality
    , town_city
    , territorial_authority
    , capture_method
    , capture_source_group
    , capture_source_id
    , capture_source_name
    , capture_source_from
    , capture_source_to
    , building_outline_lifecycle
    , begin_lifespan
    , end_lifespan
    , last_modified
    , shape
FROM buildings_lds.nz_building_outlines_all_sources
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_lds'
    AND tablename = 'nz_building_outlines_all_sources'
    AND indexdef LIKE '%sidx_nz_building_outlines_all_sources%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_lds", table '
        '"nz_building_outlines_all_sources", column "shape" has a missing '
        'index named "sidx_nz_building_outlines_all_sources"';
    END IF;
END;
$$;

SELECT
      lifecycle_id
    , parent_building_id
    , building_id
FROM buildings_lds.nz_building_outlines_lifecycle
WHERE FALSE;

ROLLBACK;
