-- Verify nz-buildings:buildings_bulk_load/functions/bulk_load_outlines on pg

BEGIN;

SELECT has_function_privilege('buildings_bulk_load.bulk_load_outlines_insert(integer, integer, integer, integer, integer, integer, integer, geometry)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.bulk_load_outlines_insert_supplied(integer, integer, integer, integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.bulk_load_outlines_remove_small_buildings(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.bulk_load_outlines_update_attributes(integer, integer, integer, integer, integer, integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.bulk_load_outlines_update_capture_method(integer, integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.bulk_load_outlines_update_shape(geometry, integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.bulk_load_outlines_update_suburb(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.bulk_load_outlines_update_territorial_authority(integer)', 'execute');

SELECT has_function_privilege('buildings_bulk_load.bulk_load_outlines_update_all_territorial_authorities(integer[])', 'execute');

DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'bulk_load_outlines_insert'
    AND pronargs = 9;
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;

DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'bulk_load_outlines_update_attributes'
    AND pronargs = 7;
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;
DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'bulk_load_outlines_update_town_city'
    AND pronargs = 1;
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;
DO $$
BEGIN
    PERFORM *
    FROM pg_proc
    WHERE proname = 'bulk_load_outlines_update_all_town_cities'
    AND pronargs = 1;
    IF FOUND THEN
        RAISE EXCEPTION 'Dropped function found.';
    END IF;
END $$;
ROLLBACK;
