-- Verify nz-buildings:buildings_bulk_load/schema_and_tables on pg

BEGIN;

SELECT pg_catalog.has_schema_privilege('buildings_bulk_load', 'usage');

SELECT
      organisation_id
    , value
FROM buildings_bulk_load.organisation
WHERE FALSE;

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings_bulk_load.organisation', 'organisation_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_bulk_load" table '
        '"organisation" and column "organisation_id" is missing a sequence';
    END IF;
END;
$$;

SELECT
      bulk_load_status_id
    , value
FROM buildings_bulk_load.bulk_load_status
WHERE FALSE;

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings_bulk_load.bulk_load_status', 'bulk_load_status_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_bulk_load" table '
        '"bulk_load_status" and column "bulk_load_status_id" is missing a sequence';
    END IF;
END;
$$;

SELECT
      qa_status_id
    , value
FROM buildings_bulk_load.qa_status
WHERE FALSE;

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings_bulk_load.qa_status', 'qa_status_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_bulk_load" table '
        '"qa_status" and column "qa_status_id" is missing a sequence';
    END IF;
END;
$$;

SELECT
      supplied_dataset_id
    , description
    , supplier_id
    , processed_date
    , transfer_date
FROM buildings_bulk_load.supplied_datasets
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_bulk_load'
    AND tablename = 'supplied_datasets'
    AND indexdef LIKE '%supplier_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_bulk_load", table '
        '"supplied_datasets", column "supplier_id" has a missing index named '
        '"idx_supplied_datasets_supplier_id"';
    END IF;
END;
$$;

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings_bulk_load.supplied_datasets', 'supplied_dataset_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_bulk_load" table '
        '"supplied_datasets" and column "supplied_dataset_id" is missing a sequence';
    END IF;
END;
$$;

SELECT
      supplied_outline_id
    , supplied_dataset_id
    , external_outline_id
    , begin_lifespan
    , shape
FROM buildings_bulk_load.supplied_outlines
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_bulk_load'
    AND tablename = 'supplied_outlines'
    AND indexdef LIKE '%supplied_dataset_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_bulk_load", table '
        '"supplied_outlines", column "supplied_dataset_id" has a missing index '
        'named "idx_supplied_outlines_supplied_dataset_id"';
    END IF;
END;
$$;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_bulk_load'
    AND tablename = 'supplied_outlines'
    AND indexdef LIKE '%shx_supplied_outlines%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_bulk_load", table '
        '"supplied_outlines", column "shape" has a missing index named '
        '"shx_supplied_outlines"';
    END IF;
END;
$$;

DO $$
DECLARE
    seqname text;
    seqval integer;
BEGIN
    SELECT pg_get_serial_sequence('buildings_bulk_load.supplied_outlines', 'supplied_outline_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_bulk_load" table '
        '"supplied_outlines" and column "supplied_outline_id" is missing a sequence';
    ELSE
        SELECT nextval(seqname) INTO seqval;
        IF seqval < 1000000 THEN
            RAISE EXCEPTION 'LOW SEQUENCE VALUE: Schema "buildings_bulk_load" with table '
            '"supplied_outlines" and column "supplied_outline_id" has a low sequence value';
        END IF;
    END IF;
END;
$$;

SELECT
      bulk_load_outline_id
    , supplied_dataset_id
    , external_outline_id
    , bulk_load_status_id
    , capture_method_id
    , capture_source_id
    , suburb_locality_id
    , town_city_id
    , territorial_authority_id
    , begin_lifespan
    , shape
FROM buildings_bulk_load.bulk_load_outlines
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_bulk_load'
    AND tablename = 'bulk_load_outlines'
    AND indexdef LIKE '%bulk_load_status_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_bulk_load", table '
        '"bulk_load_outlines", column "bulk_load_status_id" has a missing '
        'index named "idx_bulk_load_outlines_bulk_load_status_id"';
    END IF;
END;
$$;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_bulk_load'
    AND tablename = 'bulk_load_outlines'
    AND indexdef LIKE '%capture_method_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_bulk_load", table '
        '"bulk_load_outlines", column "capture_method_id" has a missing index '
        'named "idx_bulk_load_outlines_capture_method_id"';
    END IF;
END;
$$;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_bulk_load'
    AND tablename = 'bulk_load_outlines'
    AND indexdef LIKE '%capture_source_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_bulk_load", table '
        '"bulk_load_outlines", column "capture_source_id" has a missing index '
        'named "idx_bulk_load_outlines_capture_source_id"';
    END IF;
END;
$$;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_bulk_load'
    AND tablename = 'bulk_load_outlines'
    AND indexdef LIKE '%supplied_dataset_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_bulk_load", table '
        '"bulk_load_outlines", column "supplied_dataset_id" has a missing '
        'index named "idx_bulk_load_outlines_supplied_dataset_id"';
    END IF;
END;
$$;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_bulk_load'
    AND tablename = 'bulk_load_outlines'
    AND indexdef LIKE '%shx_bulk_load_outlines%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_bulk_load", table '
        '"bulk_load_outlines", column "shape" has a missing index named '
        '"shx_bulk_load_outlines"';
    END IF;
END;
$$;

DO $$
DECLARE
    seqname text;
    seqval integer;
BEGIN
    SELECT pg_get_serial_sequence('buildings_bulk_load.bulk_load_outlines', 'bulk_load_outline_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_bulk_load" table '
        '"bulk_load_outlines" and column "bulk_load_outline_id" is missing a sequence';
    ELSE
        SELECT nextval(seqname) INTO seqval;
        IF seqval < 1000000 THEN
            RAISE EXCEPTION 'LOW SEQUENCE VALUE: Schema "buildings_bulk_load" with table '
            '"bulk_load_outlines" and column "bulk_load_outline_id" has a low sequence value';
        END IF;
    END IF;
END;
$$;

SELECT
      building_outline_id
    , supplied_dataset_id
    , shape
FROM buildings_bulk_load.existing_subset_extracts
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_bulk_load'
    AND tablename = 'existing_subset_extracts'
    AND indexdef LIKE '%supplied_dataset_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_bulk_load", table '
        '"existing_subset_extracts", column "supplied_dataset_id" has a '
        'missing index named "idx_existing_subset_extracts_supplied_dataset_id"';
    END IF;
END;
$$;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_bulk_load'
    AND tablename = 'existing_subset_extracts'
    AND indexdef LIKE '%shx_existing_subset_extracts%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_bulk_load", table '
        '"existing_subset_extracts", column "shape" has a missing index named '
        '"shx_existing_subset_extracts"';
    END IF;
END;
$$;

SELECT
      bulk_load_outline_id
    , qa_status_id
FROM buildings_bulk_load.added
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_bulk_load'
    AND tablename = 'added'
    AND indexdef LIKE '%qa_status_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_bulk_load", table '
        '"added", column "qa_status_id" has a missing index named '
        '"idx_added_qa_status_id"';
    END IF;
END;
$$;

SELECT
      building_outline_id
    , qa_status_id
FROM buildings_bulk_load.removed
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_bulk_load'
    AND tablename = 'removed'
    AND indexdef LIKE '%qa_status_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_bulk_load", table '
        '"removed", column "qa_status_id" has a missing index named '
        '"idx_removed_qa_status_id"';
    END IF;
END;
$$;

SELECT
      related_group_id
FROM buildings_bulk_load.related_groups
WHERE FALSE;

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings_bulk_load.related_groups', 'related_group_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_bulk_load" table '
        '"related_groups" and column "related_group_id" is missing a sequence';
    END IF;
END;
$$;

SELECT
      related_id
    , related_group_id
    , bulk_load_outline_id
    , building_outline_id
    , qa_status_id
FROM buildings_bulk_load.related
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_bulk_load'
    AND tablename = 'related'
    AND indexdef LIKE '%building_outline_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_bulk_load", table '
        '"related", column "building_outline_id" has a missing index named '
        '"idx_related_building_outline_id"';
    END IF;
END;
$$;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_bulk_load'
    AND tablename = 'related'
    AND indexdef LIKE '%bulk_load_outline_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_bulk_load", table '
        '"related", column "bulk_load_outline_id" has a missing index named '
        '"idx_related_bulk_load_outline_id"';
    END IF;
END;
$$;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_bulk_load'
    AND tablename = 'related'
    AND indexdef LIKE '%qa_status_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_bulk_load", table '
        '"related", column "qa_status_id" has a missing index named '
        '"idx_related_qa_status_id"';
    END IF;
END;
$$;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_bulk_load'
    AND tablename = 'related'
    AND indexdef LIKE '%related_group_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_bulk_load", table '
        '"related", column "related_group_id" has a missing index named '
        '"idx_related_related_group_id"';
    END IF;
END;
$$;

DO $$
DECLARE
    seqname text;
BEGIN
    SELECT pg_get_serial_sequence('buildings_bulk_load.related', 'related_id') INTO seqname;
    IF seqname IS NULL THEN
        RAISE EXCEPTION 'MISSING SEQUENCE: Schema "buildings_bulk_load" table '
        '"related" and column "related_id" is missing a sequence';
    END IF;
END;
$$;

SELECT
      bulk_load_outline_id
    , building_outline_id
    , qa_status_id
FROM buildings_bulk_load.matched
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_bulk_load'
    AND tablename = 'matched'
    AND indexdef LIKE '%building_outline_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_bulk_load", table '
        '"matched", column "building_outline_id" has a missing index named '
        '"idx_matched_building_outline_id"';
    END IF;
END;
$$;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_bulk_load'
    AND tablename = 'matched'
    AND indexdef LIKE '%qa_status_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_bulk_load", table '
        '"matched", column "qa_status_id" has a missing index named '
        '"idx_matched_qa_status_id"';
    END IF;
END;
$$;

SELECT
      bulk_load_outline_id
    , new_building_outline_id
FROM buildings_bulk_load.transferred
WHERE FALSE;

DO $$
BEGIN
    PERFORM TRUE
    FROM pg_indexes
    WHERE schemaname = 'buildings_bulk_load'
    AND tablename = 'transferred'
    AND indexdef LIKE '%new_building_outline_id%';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'MISSING INDEX: Schema "buildings_bulk_load", table '
        '"transferred", column "new_building_outline_id" has a missing index '
        'named "idx_transferred_new_building_outline_id"';
    END IF;
END;
$$;

SELECT
      bulk_load_outline_id
    , description
FROM buildings_bulk_load.deletion_description
WHERE FALSE;

ROLLBACK;
