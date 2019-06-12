-- Verify nz-buildings:buildings_common/schema_and_tables on pg

BEGIN;

SELECT pg_catalog.has_schema_privilege('buildings_common', 'usage');

SELECT
      capture_method_id
    , value
FROM buildings_common.capture_method
WHERE FALSE;

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings_common.capture_method', 'capture_method_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_common" table '
        '"capture_method" and column "capture_method_id" is missing a sequence';
    END IF;
END;
$$;

SELECT
      capture_source_group_id
    , value
    , description
FROM buildings_common.capture_source_group
WHERE FALSE;

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings_common.capture_source_group', 'capture_source_group_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_common" table '
        '"capture_source_group" and column "capture_source_group_id" is missing a sequence';
    END IF;
END;
$$;

SELECT
      capture_source_id
    , capture_source_group_id
    , external_source_id
FROM buildings_common.capture_source
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_common'
    AND tablename = 'capture_source'
    AND indexdef LIKE '%capture_source_group_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_common", table '
        '"capture_source", column "capture_source_group_id" has a missing '
        'index named "idx_capture_source_capture_source_group_id"';
    END IF;
END;
$$;

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings_common.capture_source', 'capture_source_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_common" table '
        '"capture_source" and column "capture_source_id" is missing a sequence';
    END IF;
END;
$$;

ROLLBACK;
