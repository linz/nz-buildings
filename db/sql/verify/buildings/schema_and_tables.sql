-- Verify buildings:buildings/schema_and_tables on pg

BEGIN;

SELECT pg_catalog.has_schema_privilege('buildings', 'usage');

SELECT
      lifecycle_stage_id
    , value
FROM buildings.lifecycle_stage
WHERE FALSE;

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings.lifecycle_stage', 'lifecycle_stage_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings" table '
        '"lifecycle_stage" and column "lifecycle_stage_id" is missing a sequence';
    END IF;
END;
$$;

SELECT
      use_id
    , value
FROM buildings.use
WHERE FALSE;

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings.use', 'use_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings" table '
        '"use" and column "use_id" is missing a sequence';
    END IF;
END;
$$;

SELECT
      building_id
    , begin_lifespan
    , end_lifespan
FROM buildings.buildings
WHERE FALSE;

DO $$
DECLARE
    seqname text;
    seqval integer;
BEGIN
    SELECT pg_get_serial_sequence('buildings.buildings', 'building_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings" table '
        '"buildings" and column "building_id" is missing a sequence';
    ELSE
        SELECT nextval(seqname) INTO seqval;
        IF seqval < 1000000 THEN
            RAISE EXCEPTION 'LOW SEQUENCE VALUE: Schema "buildings" with table '
            '"buildings" and column "building_id" has a low sequence value';
        END IF;
    END IF;
END;
$$;

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

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings'
    AND tablename = 'building_outlines'
    AND indexdef LIKE '%building_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings", table '
        '"building_outlines", column "building_id" has a missing index named '
        '"idx_building_outlines_building_id"';
    END IF;
END;
$$;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings'
    AND tablename = 'building_outlines'
    AND indexdef LIKE '%capture_method_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings", table '
        '"building_outlines", column "capture_method_id" has a missing index '
        'named "idx_building_outlines_capture_method_id"';
    END IF;
END;
$$;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings'
    AND tablename = 'building_outlines'
    AND indexdef LIKE '%capture_source_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings", table '
        '"building_outlines", column "capture_source_id" has a missing index '
        'named "idx_building_outlines_capture_source_id"';
    END IF;
END;
$$;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings'
    AND tablename = 'building_outlines'
    AND indexdef LIKE '%lifecycle_stage_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings", table '
        '"building_outlines", column "lifecycle_stage_id" has a missing index '
        'named "idx_building_outlines_lifecycle_stage_id"';
    END IF;
END;
$$;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings'
    AND tablename = 'building_outlines'
    AND indexdef LIKE '%shx_building_outlines%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings", table '
        '"building_outlines", column "shape" has a missing index named '
        '"shx_building_outlines"';
    END IF;
END;
$$;

DO $$
DECLARE
    seqname text;
    seqval integer;
BEGIN
    SELECT pg_get_serial_sequence('buildings.building_outlines', 'building_outline_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings" table '
        '"building_outlines" and column "building_outline_id" is missing a sequence';
    ELSE
        SELECT nextval(seqname) INTO seqval;
        IF seqval < 1000000 THEN
            RAISE EXCEPTION 'LOW SEQUENCE VALUE: Schema "buildings" with table '
            '"building_outlines" and column "building_outline_id" has a low sequence value';
        END IF;
    END IF;
END;
$$;

SELECT
      building_name_id
    , building_id
    , building_name
    , begin_lifespan
    , end_lifespan
FROM buildings.building_name
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings'
    AND tablename = 'building_name'
    AND indexdef LIKE '%building_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings", table '
        '"building_name", column "building_id" has a missing index named '
        '"idx_building_name_building_id"';
    END IF;
END;
$$;

DO $$
DECLARE
    seqname text;
    seqval integer;
BEGIN
    SELECT pg_get_serial_sequence('buildings.building_name', 'building_name_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings" table '
        '"building_name" and column "building_name_id" is missing a sequence';
    ELSE
        SELECT nextval(seqname) INTO seqval;
        IF seqval < 1000000 THEN
            RAISE EXCEPTION 'LOW SEQUENCE VALUE: Schema "buildings" with table '
            '"building_name" and column "building_name_id" has a low sequence value';
        END IF;
    END IF;
END;
$$;

SELECT
      building_use_id
    , building_id
    , use_id
    , begin_lifespan
    , end_lifespan
FROM buildings.building_use
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings'
    AND tablename = 'building_use'
    AND indexdef LIKE '%building_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings", table '
        '"building_use", column "building_id" has a missing index named '
        '"idx_building_use_building_id"';
    END IF;
END;
$$;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings'
    AND tablename = 'building_use'
    AND indexdef LIKE '%use_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings", table '
        '"building_use", column "use" has a missing index named '
        '"idx_building_use_use_id"';
    END IF;
END;
$$;

DO $$
DECLARE
    seqname text;
    seqval integer;
BEGIN
    SELECT pg_get_serial_sequence('buildings.building_use', 'building_use_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings" table '
        '"building_use" and column "building_use_id" is missing a sequence';
    ELSE
        SELECT nextval(seqname) INTO seqval;
        IF seqval < 1000000 THEN
            RAISE EXCEPTION 'LOW SEQUENCE VALUE: Schema "buildings" with table '
            '"building_use" and column "building_use_id" has a low sequence value';
        END IF;
    END IF;
END;
$$;

SELECT
      lifecycle_id
    , parent_building_id
    , building_id
FROM buildings.lifecycle
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings'
    AND tablename = 'lifecycle'
    AND indexdef LIKE '%building_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings", table '
        '"lifecycle", column "building_id" has a missing index named '
        '"idx_lifecycle_building_id"';
    END IF;
END;
$$;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings'
    AND tablename = 'lifecycle'
    AND indexdef LIKE '%parent_building_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings", table '
        '"lifecycle", column "parent_building_id" has a missing index named '
        '"idx_lifecycle_parent_building_id"';
    END IF;
END;
$$;

DO $$
DECLARE
    seqname text;
    seqval integer;
BEGIN
    SELECT pg_get_serial_sequence('buildings.lifecycle', 'lifecycle_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings" table '
        '"lifecycle" and column "lifecycle_id" is missing a sequence';
    ELSE
        SELECT nextval(seqname) INTO seqval;
        IF seqval < 1000000 THEN
            RAISE EXCEPTION 'LOW SEQUENCE VALUE: Schema "buildings" with table '
            '"lifecycle" and column "building_use_id" has a low sequence value';
        END IF;
    END IF;
END;
$$;

ROLLBACK;
