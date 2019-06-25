-- Verify nz-buildings:buildings_reference/huts_and_protected_areas on pg

BEGIN;

-- verify hut_points table
-- verify shelter points table
-- verify bivouac points table
-- verify protected areas polygons table
-- verify columns added to reference_update_log table

SELECT
      hut_points_id
    , external_hut_points_id
    , name
    , shape
FROM buildings_reference.hut_points
WHERE FALSE;


DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_reference'
    AND tablename = 'hut_points'
    AND indexdef LIKE '%shx_hut_points%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_reference", table '
        '"hut_points", column "shape" has a missing index '
        'named "shx_hut_points"';
    END IF;
END;
$$;

SELECT
      shelter_points_id
    , external_shelter_points_id
    , name
    , shape
FROM buildings_reference.shelter_points
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_reference'
    AND tablename = 'shelter_points'
    AND indexdef LIKE '%shx_shelter_points%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_reference", table '
        '"shelter_points", column "shape" has a missing index '
        'named "shx_shelter_points"';
    END IF;
END;
$$;

SELECT
      bivouac_points_id
    , external_bivouac_points_id
    , name
    , shape
FROM buildings_reference.bivouac_points
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_reference'
    AND tablename = 'bivouac_points'
    AND indexdef LIKE '%shx_bivouac_points%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_reference", table '
        '"bivouac_points", column "shape" has a missing index '
        'named "shx_bivouac_points"';
    END IF;
END;
$$;

SELECT
      protected_areas_polygon_id
    , external_protected_areas_polygon_id
    , name
    , shape
FROM buildings_reference.protected_areas_polygons
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_reference'
    AND tablename = 'protected_areas_polygons'
    AND indexdef LIKE '%shx_protected_areas_polygons%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_reference", table '
        '"protected_areas_polygons", column "shape" has a missing index '
        'named "shx_protected_areas_polygons"';
    END IF;
END;
$$;

SELECT huts
FROM buildings_reference.reference_update_log
WHERE FALSE;

SELECT shelters
FROM buildings_reference.reference_update_log
WHERE FALSE;

SELECT bivouacs
FROM buildings_reference.reference_update_log
WHERE FALSE;

SELECT protected_areas
FROM buildings_reference.reference_update_log
WHERE FALSE;

ROLLBACK;
