-- Verify nz-buildings:buildings_reference/schema_and_tables on pg

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

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_reference'
    AND tablename = 'suburb_locality'
    AND indexdef LIKE '%shx_suburb_locality%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_reference", table '
        '"suburb_locality", column "shape" has a missing index named '
        '"shx_suburb_locality"';
    END IF;
END;
$$;

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings_reference.suburb_locality', 'suburb_locality_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_reference" table '
        '"suburb_locality" and column "suburb_locality_id" is missing a sequence';
    END IF;
END;
$$;

SELECT
      town_city_id
    , external_city_id
    , name
    , shape
FROM buildings_reference.town_city
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_reference'
    AND tablename = 'town_city'
    AND indexdef LIKE '%shx_town_city%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_reference", table '
        '"town_city", column "shape" has a missing index named "shx_town_city"';
    END IF;
END;
$$;

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings_reference.town_city', 'town_city_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_reference" table '
        '"town_city" and column "town_city_id" is missing a sequence';
    END IF;
END;
$$;

SELECT
      territorial_authority_id
    , external_territorial_authority_id
    , name
    , shape
FROM buildings_reference.territorial_authority
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_reference'
    AND tablename = 'territorial_authority'
    AND indexdef LIKE '%shx_territorial_authority%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_reference", table '
        '"territorial_authority", column "shape" has a missing index named '
        '"shx_territorial_authority"';
    END IF;
END;
$$;

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings_reference.territorial_authority', 'territorial_authority_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_reference" table '
        '"territorial_authority" and column "territorial_authority_id" is missing a sequence';
    END IF;
END;
$$;

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

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_reference'
    AND tablename = 'coastlines_and_islands'
    AND indexdef LIKE '%shx_coastlines_and_islands%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_reference", table '
        '"coastlines_and_islands", column "shape" has a missing index named '
        '"shx_coastlines_and_islands"';
    END IF;
END;
$$;

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings_reference.coastlines_and_islands', 'coastline_and_island_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_reference" table '
        '"coastlines_and_islands" and column "coastline_and_island_id" is missing a sequence';
    END IF;
END;
$$;

SELECT
      lake_polygon_id
    , external_lake_polygon_id
    , shape
FROM buildings_reference.lake_polygons
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_reference'
    AND tablename = 'lake_polygons'
    AND indexdef LIKE '%shx_lake_polygons%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_reference", table '
        '"lake_polygons", column "shape" has a missing index named '
        '"shx_lake_polygons"';
    END IF;
END;
$$;

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings_reference.lake_polygons', 'lake_polygon_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_reference" table '
        '"lake_polygons" and column "lake_polygon_id" is missing a sequence';
    END IF;
END;
$$;

SELECT
      pond_polygon_id
    , external_pond_polygon_id
    , shape
FROM buildings_reference.pond_polygons
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_reference'
    AND tablename = 'pond_polygons'
    AND indexdef LIKE '%shx_pond_polygons%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_reference", table '
        '"pond_polygons", column "shape" has a missing index named '
        '"shx_pond_polygons"';
    END IF;
END;
$$;

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings_reference.pond_polygons', 'pond_polygon_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_reference" table '
        '"pond_polygons" and column "pond_polygon_id" is missing a sequence';
    END IF;
END;
$$;

SELECT
      swamp_polygon_id
    , external_swamp_polygon_id
    , shape
FROM buildings_reference.swamp_polygons
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_reference'
    AND tablename = 'swamp_polygons'
    AND indexdef LIKE '%shx_swamp_polygons%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_reference", table '
        '"swamp_polygons", column "shape" has a missing index named '
        '"shx_swamp_polygons"';
    END IF;
END;
$$;

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings_reference.swamp_polygons', 'swamp_polygon_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_reference" table '
        '"swamp_polygons" and column "swamp_polygon_id" is missing a sequence';
    END IF;
END;
$$;

SELECT
      lagoon_polygon_id
    , external_lagoon_polygon_id
    , shape
FROM buildings_reference.lagoon_polygons
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_reference'
    AND tablename = 'lagoon_polygons'
    AND indexdef LIKE '%shx_lagoon_polygons%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_reference", table '
        '"lagoon_polygons", column "shape" has a missing index named '
        '"shx_lagoon_polygons"';
    END IF;
END;
$$;

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings_reference.lagoon_polygons', 'lagoon_polygon_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_reference" table '
        '"lagoon_polygons" and column "lagoon_polygon_id" is missing a sequence';
    END IF;
END;
$$;

SELECT
      canal_polygon_id
    , external_canal_polygon_id
    , shape
FROM buildings_reference.canal_polygons
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_reference'
    AND tablename = 'canal_polygons'
    AND indexdef LIKE '%shx_canal_polygons%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_reference", table '
        '"canal_polygons", column "shape" has a missing index named '
        '"shx_canal_polygons"';
    END IF;
END;
$$;

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings_reference.canal_polygons', 'canal_polygon_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_reference" table '
        '"canal_polygons" and column "canal_polygon_id" is missing a sequence';
    END IF;
END;
$$;

SELECT
      area_polygon_id
    , external_area_polygon_id
    , area_title
    , shape
FROM buildings_reference.capture_source_area
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_reference'
    AND tablename = 'capture_source_area'
    AND indexdef LIKE '%shx_capture_source_area%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_reference", table '
        '"capture_source_area", column "shape" has a missing index named '
        '"shx_capture_source_area"';
    END IF;
END;
$$;

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings_reference.capture_source_area', 'area_polygon_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_reference" table '
        '"capture_source_area" and column "area_polygon_id" is missing a sequence';
    END IF;
END;
$$;

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

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings_reference.reference_update_log', 'update_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_reference" table '
        '"reference_update_log" and column "update_id" is missing a sequence';
    END IF;
END;
$$;

ROLLBACK;
